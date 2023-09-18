import requests

from .setting import config
from ..exception import InvalidHTTPStatusCodeError


def get_text(url: str) -> str:
    if config.git_proxy and "raw.githubusercontent.com" in url:
        url = config.git_proxy + url
    response = requests.get(url, proxies=config.proxy)
    if response.status_code == 200:
        return response.text
    else:
        raise InvalidHTTPStatusCodeError(response.status_code)
