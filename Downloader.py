import os
import time
import asyncio
import aiohttp
import requests
import helper_worksheet as helper_worksheet
import helper_html as helper_html
import helper_string as helper_str
from bs4 import BeautifulSoup

# Disable SSL verification
requests.packages.urllib3.disable_warnings()

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

async def process_url(session, url):
    try:
        async with session.get(url, headers=HEADERS) as response:
            html_content = await response.text()
    except Exception as e:
        print(f"Not possible to reach the URL {url}\n", e)
        return

    soup = BeautifulSoup(html_content, 'html.parser')
    url_start = helper_str.get_url_start(url)

    page_title = helper_html.get_title(soup)
    meta_description = helper_html.get_meta_description(soup)
    meta_og_title = helper_html.get_meta_og_title(soup)
    meta_og_description = helper_html.get_meta_og_description(soup)

    foldername = helper_str.sanitize_foldername(page_title)
    page_folder = os.path.join(save_folder, foldername)
    if not os.path.exists(page_folder):
        os.makedirs(page_folder)

    (workbook, worksheet) = helper_worksheet.prepare_worksheet_pagedata(url, page_title, meta_description, meta_og_title, meta_og_description)

    sources = helper_html.get_img_sources(soup)
    current_image = 0
    downloaded_images = []

    for source, alt_text, title_text, media_text, img_name in sources:
        current_image += 1

        source_url = url_start + "/" + source
        img_path = os.path.join(page_folder, img_name)

        helper_worksheet.write_worksheet_pagedata(worksheet, 'img', source, img_name, alt_text, title_text, media_text)

        if img_name in downloaded_images:
            continue

        await helper_html.download_image(source_url, session, img_path)
        downloaded_images.append(img_name)

    for idx, (tag, content) in enumerate(helper_html.get_block_elements(soup), start=1):
        helper_worksheet.write_worksheet_pagedata(worksheet, tag, content, "", "", "", "")

    excel_file = os.path.join(page_folder, 'page_content.xlsx')
    workbook.save(excel_file)

async def download_and_process_images():
    if img_name in downloaded_images:
        return

    await helper_html.download_image(source_url, session, img_path)
    downloaded_images.append(img_name)

    return ""

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [process_url(session, url.strip()) for url in lines]
        await asyncio.gather(*tasks)

file_name = input("Insert listing file (links.txt):\n")

if file_name == "":
    file_name = "links.txt"

if not os.path.isfile(file_name):
    print("This file doesn't exists.")
    exit()

with open(file_name, 'r') as file:
    lines = file.readlines()

qt_pages = len(lines)

print(f"Pages found: {qt_pages}")

cod_timestamp = time.strftime("%Y%m%d%H%M%S")
save_folder = input("Type the destination folder (tmp_" + cod_timestamp + "):\n")

if save_folder == "":
    save_folder = "tmp_" + cod_timestamp

if not os.path.exists(save_folder):
    os.makedirs(save_folder)

start_time = time.time()

(error_workbook, error_sheet) = helper_worksheet.prepare_worksheet_erros()

# Executa o processamento assíncrono
asyncio.run(main())

# Salva o arquivo de erros
error_file = os.path.join(save_folder, 'errors.xlsx')
error_workbook.save(error_file)

end_time = time.time()
total_time = end_time - start_time

print(f"Done. Time to process: {total_time:.2f} seconds.")
