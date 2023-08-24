import re
import helper_string as helper_str
import os
from urllib.parse import urlparse, urljoin

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

def get_source_from_tags(soup, tag, url=""):
    article = remove_ignored_parts(soup.find("article"))

    elements = article.find_all(tag)
    urls = []

    for element in elements:
        src = element.get('src', "")

        if src == "":
            src = element.get('href', "")

        if src == "":
            src = element.get('srcset', "")

        if src == "":
            src = "Not found"

        alt_text = element.get('alt', "")

        if alt_text == "":
            alt_text = "-"

        title_text = element.get('title', "")

        if title_text == "":
            title_text = "-"

        media_text = element.get('media', "")

        if media_text == "":
            media_text = "-"

        img_name = os.path.basename(urlparse(src).path)
        img_name = re.sub(r"\?.*$", "", img_name)
        img_name = helper_str.sanitize_filename(img_name)

        if src is not None and re.match(r'^.*\.(jpg|jpeg|png|gif|webp).*$', src):
            parsed_src = urlparse(src)
            if not parsed_src.scheme:
                src = urljoin(url, src)
            urls.append((src, alt_text, title_text, media_text, img_name))

    return urls

def get_img_sources(soup, url=""):
    img_urls = get_source_from_tags(soup, 'img')
    picture_urls = get_source_from_tags(soup, 'picture')
    source_urls = get_source_from_tags(soup, 'source')

    urls = img_urls + picture_urls + source_urls

    return urls

def get_block_elements(soup):
    article = remove_ignored_parts(soup.find("article"))
    block_elements = []

    for element in article.find_all(is_desired_tag):
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

def remove_ignored_parts(soup):
    classes_in_divs_to_be_ignored = [
        "component--contact-us", "component--newsletter", "component--age-calculator",
        "component--products-list", "component--articles-list", "component--signposting-single",
        "component--brand-carousel",
        "hero--content-wrapper",
        "article--progressbar", "article--utility-bar"
    ]

    for div in soup.find_all("div"):
        if div.has_attr('class'):
            for class_in_div in div["class"]:
                if class_in_div in classes_in_divs_to_be_ignored:
                    div.extract()

    return soup

async def download_image(url, session, img_local_path):
    async with session.get(url) as response:
        try:
            img_data = await response.read()
            with open(img_local_path, "wb") as handler:
                handler.write(img_data)
        except Exception as e:
            print(f"Not possible to download the image {img_local_path}", e)

