import requests
from loguru import logger
from sm_ms_api import SMMS
from jsonschema import validate
from yaml import safe_load
import functools,threading
from .utils.setting import config
from .exception import InvalidHTTPStatusCodeError
from .utils.spider import get_text
from .base_path import get_real_path


def wait_and_return_result(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result_container = [None]
        exception_container = [None]

        def worker():
            try:
                result_container[0] = func(*args, **kwargs)
            except Exception as e:
                exception_container[0] = e

        thread = threading.Thread(target=worker)
        thread.start()
        thread.join()

        if exception_container[0]:
            raise exception_container[0]

        return result_container[0]

    return wrapper


@wait_and_return_result
def upload_img(path: str):
    smms = SMMS(token=config.sm_ms_token)
    res=smms.upload_image(path)
    print(res)
    return res


class Converter:
    fgi_tags: dict = {}

    def __init__(self, name: str, yaml: dict = None, url: str = None):
        if not url:
            self.data = yaml
        else:
            self.data = safe_load(get_text(url))
        self.name = name

    def to_fgi_yaml(self) -> dict:
        if not self.validate_it():
            self.replace_yaml()
        return self.data

    def parse_tags(self, type_tag: str):
        if not self.fgi_tags:
            self.fgi_tags = safe_load(get_text('https://raw.githubusercontent.com/FurryGamesIndex/games/master/tags'
                                               '.yaml'))
        return [key for key, value in self.fgi_tags.items() if type_tag in value.get('namespaces', [])]

    def replace_yaml(self):
        def handle_img(chunk: dict | str) -> dict | str:
            if 'type' in chunk and 'path' in chunk:
                if 'sensitive' in chunk and chunk['sensitive']:
                    return {
                        'sensitive': True,
                        'uri': upload_img(get_real_path(path=chunk['path'], type_path='assets', game_name=self.name))
                    }
                else:
                    return upload_img(get_real_path(path=chunk['path'], type_path='assets', game_name=self.name))

        def handle_vid(chunk: dict) -> dict | list:
            logger.warning("Unable to upload video, ignore...")
            return []

        for i in self.data['screenshots']:
            handle_item: dict | str = None
            if 'type' in i and 'image:local' in i['type']:
                handle_item = handle_img(i)
            elif 'type' in i and 'video:local' in i['type']:
                handle_item = handle_vid(i)
            if handle_item is not None:
                self.data['screenshots'][self.data['screenshots'].index(i)] = handle_item

    def validate_it(self) -> bool:
        try:
            validate(self.data,
                     safe_load(get_text('https://raw.githubusercontent.com/FurryGamesIndex/games/master/schemas/game'
                                        '.schema.yaml')))
            return True
        except:
            return False
