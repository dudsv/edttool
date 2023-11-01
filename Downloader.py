###########################################################
# Download all images from a list of pages                #
# Version : 2.0 (dez/2023)                                #
# Team    : IMS LATAM | Websites And SEO                  #
# Authors : Carlos Brito, Felipe Martins                  #
# E-mail  :                                               #
###########################################################

import os
import sys
import procpics_txt as txt
import procpics_helpers as hp
import time
import asyncio
import aiohttp
import requests
import helper_worksheet as helper_worksheet
import helper_html as helper_html
import helper_string as helper_str
from bs4 import BeautifulSoup
from PIL import Image as img

# Disable SSL verification
requests.packages.urllib3.disable_warnings()

if len(sys.argv) > 1:
  def_language = str(sys.argv[1]).strip()
else:
  def_language = "pt-br"

if not def_language in txt.phrases:
  def_language = "pt-br"
  print(txt.phrases[def_language]['input_mainpath'])

reducequalityfor = 100
permittedext = ['jpg', 'jpeg', 'webp', 'png']
sair = False

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

def prepare_folder():
    cod_timestamp = time.strftime("%Y%m%d%H%M%S")
    save_folder = input("Type the destination folder (press enter for \"tmp_" + cod_timestamp + "\"):\n")

    if save_folder == "":
        save_folder = "tmp_" + cod_timestamp

    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    return save_folder

def prepare_url_list_from_file():
    file_name = input("Insert listing file: (press enter for \"links.txt\"):\n")

    if file_name == "":
        file_name = "links.txt"

    if not os.path.isfile(file_name):
        print("This file doesn't exists.")
        exit()

    with open(file_name, 'r') as file:
        return file.readlines()

def prepare_url_list_from_keyboard():
    qt_continue = 'y'
    lines = []
    while qt_continue == 'y' or qt_continue == 'Y':
        current_url = input(f"Enter the URL ({len(lines)} URLs): ").strip()
        lines.append(current_url)
        qt_continue = input("Would you like to enter one more URL? (y/n): ")

    return lines

def processimage(mainpath, element, newformat, endfilename, maxwidth, foldernamefornewfiles):
    curfile = mainpath + element
    if not hp.isvalidimage(curfile):
        return

    (basename, ext) = os.path.splitext(curfile)
    pic = img.open(curfile)
    filetocreate = basename.replace(mainpath, f"{mainpath}{foldernamefornewfiles}")
    filetocreate = f"{filetocreate}{endfilename}.{newformat}"

    width, height = pic.size
    if width > maxwidth:
        newsize = (maxwidth, int(height / width * maxwidth))
        pic = pic.resize(newsize)
    else:
        newsize = (width, height)

    if newformat == 'jpg' and not pic.mode == 'RGB':
        pic_bg = img.new('RGB', newsize, (255, 255, 255))
        pic_bg.paste(pic, pic)
        pic = pic_bg

    try:
        pic.save(filetocreate, quality=reducequalityfor)
    except Exception as e:
        if str(e).find("RGBA") >= 0:
            processimage(mainpath, element, "png")
        else:
            print(txt.phrases[def_language]['warn_cant_save_file'].format(filetocreate=filetocreate), e)
    finally:
        print(txt.phrases[def_language]['print_filesaved'].format(filetocreate=filetocreate))

def decidewalk(mainpath, element, newformat, maxwidth, endfilename, foldernamefornewfiles, indsaveinotherdirectory):
    curpath = mainpath + element
    if os.path.isdir(curpath):
        pathtocreate = mainpath + foldernamefornewfiles + element

        if indsaveinotherdirectory:
            try:
                os.mkdir(pathtocreate)
            except:
                print(txt.phrases[def_language]['warn_cant_create_subfolder'])

        walkthroughtthepath(mainpath, newformat, maxwidth, endfilename, foldernamefornewfiles, indsaveinotherdirectory, element)
    elif hp.isvalidimage(curpath):
        processimage(mainpath, element, newformat, endfilename, maxwidth, foldernamefornewfiles)

def walkthroughtthepath(mainpath, newformat, maxwidth, endfilename, foldernamefornewfiles, indsaveinotherdirectory, element=""):
    curpath = mainpath + element
    if not os.path.isdir(curpath):
        return

    elements = os.listdir(curpath)

    for el in elements:
        if not el in foldernamefornewfiles:
            decidewalk(mainpath, f"{element}\\{el}", newformat, maxwidth, endfilename, foldernamefornewfiles, indsaveinotherdirectory)

def choice_downloadimages():
    give_list_infile = input("""
    Would you like to set a list of URLs in file or enter each one?
    (y = URLs file list | n = enter each URL): 
    """)

    if give_list_infile == 'y' or give_list_infile == 'Y':
        lines = prepare_url_list_from_file()
    else:
        lines = prepare_url_list_from_keyboard()

    qt_pages = len(lines)

    print(f"Links found: {qt_pages}")

    save_folder = prepare_folder()

    start_time = time.time()

    asyncio.run(main_downloader(lines, save_folder))

    end_time = time.time()
    total_time = end_time - start_time

    print(f"Done. Time to process: {total_time:.2f} seconds.")

def choice_resizeimages():
    mainpath = str(input(txt.phrases[def_language]['input_mainpath'])).strip()

    if mainpath == "":
        mainpath = os.getcwd()

    indsaveinotherdirectory = str(input(txt.phrases[def_language]['input_indsaveinotherdirectory']))

    if indsaveinotherdirectory == "y":
        foldernamefornewfiles = "\\__newfiles__"
        indsaveinotherdirectory = True
    else:
        foldernamefornewfiles = ""
        indsaveinotherdirectory = False

    if indsaveinotherdirectory:
        try:
            os.mkdir(mainpath + foldernamefornewfiles)
        except:
            if not os.path.isdir(mainpath + foldernamefornewfiles):
                print(txt.phrases[def_language]['warn_cant_create_folder'])
                exit(0)

    newformat = str(input(txt.phrases[def_language]['input_newformat'])).strip()

    if newformat == "":
        newformat = "jpg"

    while not newformat in permittedext:
        newformat = str(input(
            txt.phrases[def_language]['while_input_newformat'].format(permittedext=", ".join(permittedext)))).strip()

        if newformat == "":
            newformat = "jpg"

    if (newformat != "png"):

        reducequalityfor = str(input(txt.phrases[def_language]['input_reducequalityfor']))

        if reducequalityfor.isnumeric():
            reducequalityfor = int(reducequalityfor)
            if reducequalityfor < 0:
                reducequalityfor = 100
        else:
            reducequalityfor = 100

        if reducequalityfor == "":
            reducequalityfor = 100

        while reducequalityfor < 1 or reducequalityfor > 100:
            reducequalityfor = int(input(txt.phrases[def_language]['while_input_reducequalityfor']))

    else:
        print(txt.phrases[def_language]['print_advice_png_1'])
        print(txt.phrases[def_language]['print_advice_png_2'])

    maxwidth = str(input(txt.phrases[def_language]['input_maxwidth']).strip())

    if maxwidth.isnumeric():
        maxwidth = int(maxwidth)
        if maxwidth < 0:
            maxwidth = 0
    else:
        maxwidth = 0

    if maxwidth == "":
        maxwidth = 0

    endfilename = str(input(txt.phrases[def_language]['input_endfilename'])).strip()

    if endfilename == "" and not indsaveinotherdirectory:
        endfilename = "_alt"

    print(txt.phrases[def_language]['print_showpath'].format(mainpath=mainpath))
    os.chdir(mainpath)

    if hp.containsdir(mainpath):
        print(txt.phrases[def_language]['print_containsfolder'])

    print(txt.phrases[def_language]['print_reducequalityforset'].format(reducequalityfor=reducequalityfor))

    walkthroughtthepath(mainpath, newformat, maxwidth, endfilename, foldernamefornewfiles, indsaveinotherdirectory)

async def process_url(session, url, save_folder):
    print(f"Working on URL: {url}")
    (error_workbook, error_worksheet) = helper_worksheet.prepare_worksheet_erros()
    try:
        async with session.get(url, headers=HEADERS) as response:
            if response.status >= 400:
                return
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
    loaded_images = []

    for source, alt_text, title_text, media_text, img_name in sources:
        current_image += 1

        source_url = url_start + "/" + source
        img_path = os.path.join(page_folder, img_name)

        helper_worksheet.write_worksheet_pagedata(worksheet, 'img', source, img_name, alt_text, title_text, media_text)

        if img_name in loaded_images:
            continue

        loaded_images.append(img_name)
        await helper_html.download_image(session, source_url, img_path)

    for idx, (tag, content) in enumerate(helper_html.get_block_elements(soup), start=1):
        helper_worksheet.write_worksheet_pagedata(worksheet, tag, content, "", "", "", "")

    excel_file = os.path.join(page_folder, 'page_content.xlsx')
    error_file = os.path.join(page_folder, 'errors.xlsx')
    workbook.save(excel_file)
    error_workbook.save(error_file)

async def main_downloader(lines, save_folder):
    async with aiohttp.ClientSession() as session:
        tasks = [process_url(session, url.strip(), save_folder) for url in lines]
        await asyncio.gather(*tasks)

while sair == False:
    choice = str(input("""
    Would you like to download images or just resize images that you have in your computer?
    1 - Download | 2 - Resize : 
    """)).strip()

    if choice == "1":
        choice_downloadimages()
    elif choice == "2":
        choice_resizeimages()
    else:
        sair = True
