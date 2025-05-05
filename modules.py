from urllib.parse import urlparse

import validators


def normalized_urls(url: str) -> str:
    data_url = urlparse(url)
    if data_url.netloc:
        result = data_url.scheme + '://' + data_url.netloc
    else:
        result = data_url.scheme + '://' + data_url.hostname
    return result


def not_correct_url(url: str) -> str:
    if not url:
        return 'URL обязателен'
    if len(url) > 255 or not validators.url(url):
        return 'Некорректный URL'
    return None