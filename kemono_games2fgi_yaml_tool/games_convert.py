import random

from jsonschema import validate
from loguru import logger
from sm_ms_api import SMMS
from yaml import safe_load
from .base_path import get_real_path
from .utils.setting import config
from .utils.spider import get_text
from .utils.yaml_tool import dump_to_yaml
import concurrent.futures


def upload_img(path: str):
    smms = SMMS(token=config.sm_ms_token)
    # sleep(random.randint(1, 7))
    res = smms.upload_image(path)
    print(res)
    return res


class Converter:
    fgi_tags: dict = {}
    data: dict

    def __init__(self, name: str, yaml: dict = None, url: str = None):
        if not url:
            self.data = yaml
        else:
            self.data = safe_load(get_text(url))
        self.name = name

    def to_fgi_yaml(self) -> str:
        if not self.validate_it():
            self.replace_yaml()
        return dump_to_yaml(self.data)

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

        def handle_vid(chunk: dict):
            logger.warning("Unable to upload video, ignore...")
            return None

        def process_chunk(chunk):
            if 'type' in chunk and 'image:local' in chunk['type']:
                return handle_img(chunk)
            elif 'type' in chunk and 'video:local' in chunk['type']:
                return handle_vid(chunk)
            return chunk

        with concurrent.futures.ThreadPoolExecutor() as executor:
            new_screenshots = list(executor.map(process_chunk, self.data['screenshots']))
            self.data['screenshots'] = new_screenshots

    def validate_it(self) -> bool:
        try:
            validate(self.data,
                     safe_load(get_text('https://raw.githubusercontent.com/FurryGamesIndex/games/master/schemas/game'
                                        '.schema.yaml')))
            return True
        except:
            return False
