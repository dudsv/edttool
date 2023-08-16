import os
import time
import asyncio
import aiohttp
import requests
import re
import helper_worksheet as helper_worksheet
import helper_html as helper_html
import helper_string as helper_str
from urllib.parse import urlparse, urljoin
import string
import openpyxl
from bs4 import BeautifulSoup
from tqdm import tqdm
from aiohttp.client_exceptions import ClientConnectorError

# Disable SSL verification
requests.packages.urllib3.disable_warnings()

# Headers da requisição HTTP
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

file_name = input("Insert listing file (links.txt):\n")

if file_name == "":
    file_name = "links.txt"

cod_timestamp = time.strftime("%Y%m%d%H%M%S")
save_folder = input("Type the destination folder (tmp_" + cod_timestamp + "):\n")

if not os.path.exists(save_folder):
    os.makedirs(save_folder)

start_time = time.time()

workbook = openpyxl.Workbook()
error_workbook = openpyxl.Workbook()
error_sheet = error_workbook.active
error_sheet['A1'] = 'Page URL'
error_sheet['B1'] = 'Error Message'

with open(file_name, 'r') as file:
    lines = file.readlines()

async def process_url(session, url, pbar):
    try:
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            url = f"http://{url}"

        async with session.get(url, headers=HEADERS) as response:
            html_content = await response.text()

        soup = BeautifulSoup(html_content, 'html.parser')

        page_title = helper_html.get_title(soup)
        meta_description = helper_html.get_meta_description(soup)
        meta_og_title = helper_html.get_meta_og_title(soup)
        meta_og_description = helper_html.get_meta_og_description(soup)

        # Create a new folder with the page title
        foldername = helper_str.sanitize_foldername(page_title)
        page_folder = os.path.join(save_folder, foldername)
        if not os.path.exists(page_folder):
            os.makedirs(page_folder)

        # Create a new worksheet in the Excel file with the sanitized title
        sanitized_title = page_title[:31].replace('/', '_')  # Limit the title length to 31 characters and replace invalid character
        sanitized_title = helper_str.sanitize_filename(sanitized_title)  # Sanitize the title for the worksheet
        worksheet = workbook.create_sheet(title=sanitized_title)

        # Add column headers
        worksheet['A1'] = 'File name'
        worksheet['B1'] = 'Alt Text'

        sources = helper_html.get_img_sources(soup)

        for source, alt_text, title_text, media_text in sources:
            img_name = os.path.basename(urlparse(source).path)
            file_extension = os.path.splitext(img_name)[1]

            # Remove query string from the file name
            img_name = re.sub(r"\?.*$", "", img_name)

            # Sanitize the file name
            img_name = helper_str.sanitize_filename(img_name) + file_extension

            # Get the next empty row to insert the data
            next_row = len(worksheet['A']) + 1

            # Insert the file name and alt text in the corresponding columns
            helper_worksheet.write_worksheet_pagedata(worksheet, 'img', source, img_name, alt_text, title_text, media_text)

            # Save the image in the page folder
            img_path = os.path.join(page_folder, img_name)
            await helper_html.download_image(session, source, img_path)

            pbar.update(1)

    except aiohttp.ClientError as e:
        error_sheet.append([url, str(e)])
        pbar.update(1)

async def main():
    async with aiohttp.ClientSession() as session:
        pbar = tqdm(total=len(lines) * 100, desc='Total Progress', ncols=80)
        tasks = [process_url(session, url.strip(), pbar) for url in lines]
        await asyncio.gather(*tasks)
        pbar.close()

# Executa o processamento assíncrono
asyncio.run(main())

# Salva o arquivo Excel
excel_file = os.path.join(save_folder, 'images.xlsx')
workbook.save(excel_file)

# Salva o arquivo de erros
error_file = os.path.join(save_folder, 'errors.xlsx')
error_workbook.save(error_file)

end_time = time.time()
total_time = end_time - start_time

print(f"Done. Time to process: {total_time:.2f} seconds.")
print(f"Excel file generated: {excel_file}")
print(f"Error file generated: {error_file}")
