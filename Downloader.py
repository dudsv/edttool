import os
import time
import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, urljoin
import hashlib
import string
import openpyxl
from tqdm import tqdm
from aiohttp.client_exceptions import ClientConnectorError

# Disable SSL verification
requests.packages.urllib3.disable_warnings()

# Headers da requisição HTTP
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

async def download_image(session, url, img_path):
    async with session.get(url, headers=HEADERS) as response:
        img_data = await response.read()
        with open(img_path, 'wb') as handler:
            handler.write(img_data)

def sanitize_filename(filename):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    sanitized_filename = ''.join(c for c in filename if c in valid_chars)
    return sanitized_filename

def create_folder(title):
    invalid_chars = '\\/:*?"<>|/'
    for char in invalid_chars:
        title = title.replace(char, '_')
    return title

file_name = input("Insert listing file:\n")
save_folder = input("Type the destination folder:\n")

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

        # Get the title of the page
        title_tag = soup.find('title')
        if title_tag is not None:
            page_title = title_tag.get_text()
        else:
            page_title = "Untitled"

        # Create a new folder with the page title
        folder_name = create_folder(page_title)
        page_folder = os.path.join(save_folder, folder_name)
        if not os.path.exists(page_folder):
            os.makedirs(page_folder)

        # Create a new worksheet in the Excel file with the sanitized title
        sanitized_title = page_title[:31].replace('/', '_')  # Limit the title length to 31 characters and replace invalid character
        sanitized_title = sanitize_filename(sanitized_title)  # Sanitize the title for the worksheet
        worksheet = workbook.create_sheet(title=sanitized_title)

        # Add column headers
        worksheet['A1'] = 'File name'
        worksheet['B1'] = 'Alt Text'

        img_tags = soup.find_all('img')
        img_urls = []

        for img_tag in img_tags:
            srcset = img_tag.get('srcset')
            src = img_tag.get('src')
            alt_text = img_tag.get('alt', '')

            # Verifica se o atributo "src" não está presente, mas há o atributo "srcset"
            if not src and srcset:
                srcset_urls = srcset.split(',')
                for srcset_url in srcset_urls:
                    srcset_url_parts = srcset_url.strip().split()
                    if len(srcset_url_parts) == 2:
                        srcset_url, size = srcset_url_parts
                        if 'x' in size:
                            width, height = size.split('x')
                            width = int(width)
                            # Verifica se o tamanho é menor ou igual a 440, que é considerado mobile
                            if width <= 440:
                                src = srcset_url
                                break

            if src and re.match(r'^.*\.(jpg|jpeg|png|gif|webp).*$', src):
                parsed_src = urlparse(src)
                if not parsed_src.scheme:
                    src = urljoin(url, src)
                img_urls.append((src, alt_text))

        # Verifica se há a tag <picture>
        picture_tags = soup.find_all('picture')
        for picture_tag in picture_tags:
            source_tags = picture_tag.find_all('source')
            for source_tag in source_tags:
                srcset = source_tag.get('srcset')
                if srcset:
                    srcset_urls = srcset.split(',')
                    for srcset_url in srcset_urls:
                        srcset_url_parts = srcset_url.strip().split()
                        if len(srcset_url_parts) >= 2:
                            srcset_url = srcset_url_parts[0]
                            src = srcset_url
                            alt_text = img_tag.get('alt', '')
                            img_urls.append((src, alt_text))

        for img_url, alt_text in img_urls:
            img_name = os.path.basename(urlparse(img_url).path)
            file_extension = os.path.splitext(img_name)[1]

            # Remove query string from the file name
            img_name = re.sub(r"\?.*$", "", img_name)

            # Sanitize the file name
            img_name = sanitize_filename(img_name) + file_extension

            # Get the next empty row to insert the data
            next_row = len(worksheet['A']) + 1

            # Insert the file name and alt text in the corresponding columns
            worksheet.cell(row=next_row, column=1, value=img_name)
            worksheet.cell(row=next_row, column=2, value=alt_text)

            # Save the image in the page folder
            img_path = os.path.join(page_folder, img_name)
            await download_image(session, img_url, img_path)

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
