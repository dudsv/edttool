import string
import re

def sanitize_spaces(text):
    text = re.sub(r'[^\x00-\x7F]', '', text) # Remove non-ASCII characters
    text = re.sub(r'\n', ' ', text) # Remove non-ASCII characters
    text = re.sub(r'   ', ' ', text) # Remove non-ASCII characters
    text = re.sub(r'   ', ' ', text) # Remove non-ASCII characters
    text = re.sub(r'  ', ' ', text) # Remove non-ASCII characters
    text = re.sub(r'  ', ' ', text) # Remove non-ASCII characters

    return text

def sanitize_underscore(text):
    text = re.sub(r'[^\x00-\x7F]', '', text) # Remove non-ASCII characters
    text = re.sub(r'___', '_', text)
    text = re.sub(r'___', '_', text)
    text = re.sub(r'__', '_', text)
    text = re.sub(r'__', '_', text)
    text = re.sub(r'__', '_', text)

    return text

def sanitize_filename(filename):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    sanitized_filename = ''.join(c for c in filename if c in valid_chars)
    return sanitized_filename

def sanitize_foldername(foldername):
    invalid_chars = '\\/:*?"<>|/'
    for char in invalid_chars:
        foldername = foldername.replace(char, '_')
    foldername = foldername.replace(" ", '_')
    foldername = sanitize_underscore(foldername)
    return foldername

def get_url_start(url):
    url_split = url.split("/", 3)
    hostname = url_split[2]
    protocol = url_split[0]
    return protocol + "//" + hostname