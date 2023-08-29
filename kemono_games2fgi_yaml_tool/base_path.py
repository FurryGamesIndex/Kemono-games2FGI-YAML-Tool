from typing import Union
from .utils.setting import config


def get_real_path(game_name: str,path: str, type_path: str = Union['games', 'assets']):
    return f'{config.base_path}{type_path}\\{game_name}\\{path}'
