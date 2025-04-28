from urllib.parse import urlparse


def normalized_urls(url:str)->str:
    data_url = urlparse(url)
    if data_url.netloc:
        result = data_url.scheme + '://' + data_url.netloc
    else:
        result = data_url.scheme + '://' + data_url.hostname
    return result
