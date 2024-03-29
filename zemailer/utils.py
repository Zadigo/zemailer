import secrets
from urllib.parse import urlparse

import unidecode


def random_file_name(current_value=None, size=5):
    new_name = secrets.token_hex(size)
    if current_value is None:
        return new_name
    return f'{current_value.lower()}_{new_name}'


def extract_domain(url):
    return urlparse(url).netloc


def remove_accents(text):
    """Remove accents from the text"""
    return unidecode.unidecode(text)
