import string
import re

def sanitize_spaces(text):
    text = re.sub(r'[^\x00-\x7F]', '', text)  # Remove non-ASCII characters
    text = re.sub(r'\n', ' ', text)  # Remove non-ASCII characters
    text = re.sub(r'   ', ' ', text)  # Remove non-ASCII characters
    text = re.sub(r'   ', ' ', text)  # Remove non-ASCII characters
    text = re.sub(r'  ', ' ', text)  # Remove non-ASCII characters
    text = re.sub(r'  ', ' ', text)  # Remove non-ASCII characters

    return text

def sanitize_filename(filename):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    sanitized_filename = "".join(c for c in filename if c in valid_chars)
    return sanitized_filename