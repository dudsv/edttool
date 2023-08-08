import re
import helper_string as helper_str
from urllib.parse import urlparse, urljoin
from urllib.parse import urlparse

async def get_content(url, session):
    parsed_url = urlparse(url)

    if not parsed_url.scheme:
        url = f"http://{url}"

    url = url.replace("https://", "http://")
    print(f"Trying to reach {url}...")
    async with session.get(url) as response:
        return await response.text(encoding="utf-8")

    return ""

def get_title(soup):
    title_tag = soup.find("title")

    if title_tag is not None:
        return title_tag.get_text()
    else:
        return "Untitled"

def get_meta_description(soup):
    meta_tag = soup.find("meta", attrs={"name": "description"})
    if meta_tag is not None:
        return meta_tag.get("content")
    else:
        return ""

def get_meta_og_title(soup):
    meta_tag = soup.find("meta", attrs={"property": "og:title"})
    if meta_tag is not None:
        return meta_tag.get("content")
    else:
        return ""

def get_meta_og_description(soup):
    meta_tag = soup.find("meta", attrs={"property": "og:description"})
    if meta_tag is not None:
        return meta_tag.get("content")
    else:
        return ""

def get_imgs(soup, url=""):
    img_tags = soup.find_all('img')
    img_urls = []

    for img_tag in img_tags:
        src = img_tag.get('src', "")

        if src == "":
            src = img_tag.get('href', "")

        if src == "":
            src = "Not found"

        alt_text = img_tag.get('alt', "")

        if alt_text == "":
            alt_text = img_tag.get('title', "")

        if alt_text == "":
            alt_text = "-"

        if src is not None and re.match(r'^.*\.(jpg|jpeg|png|gif|webp).*$', src):
            parsed_src = urlparse(src)
            if not parsed_src.scheme:
                src = urljoin(url, src)
            img_urls.append((src, alt_text))

    return img_urls

def get_block_elements(soup):
    block_elements = []

    for element in soup.find_all(is_desired_tag):
        for link in element.find_all('a'):
            link.replace_with(f" <a href=\"{link.get('href')}\">{link.get_text()}</a> ")

        text = helper_str.sanitize_spaces(element.get_text().strip())
        block_elements.append((element.name, text))

    return block_elements

def is_navigation(element):
    """
    Check if the element is a navigation menu based on its tag name.
    You might need to adjust this function to suit the specific structure of the pages you"re processing.
    """
    return element.name == "nav"

def is_desired_tag(tag):
    """
    Check if the tag is a desired block element (e.g., <p>, <h1>, <h2>, etc.).
    You can adjust this function to include any other elements you want to collect.
    """
    return tag.name in ["p", "h1", "h2", "h3", "h4", "h5", "h6", "li"]

async def download_image(url, session, img_local_path):
    async with session.get(url) as response:
        img_data = await response.read()
        with open(img_local_path, "wb") as handler:
            handler.write(img_data)