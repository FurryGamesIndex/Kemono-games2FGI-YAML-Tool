from typing import Union
from .utils.setting import config
from os.path import exists
from pathlib import Path


def get_real_path(game_name: str, path: str, type_path: str = Union['games', 'assets']):
    return Path(config.base_path) / type_path / game_name / path


def get_assets_path(author_name: str, file_type: str = Union["authors", "assets/_avatar"]):
    if file_type == "authors":
        return Path(config.base_path) / 'authors' / (author_name + '.yaml')
    else:
        ret = Path(config.base_path) / 'assets' / '_avatar' / (author_name + '.png')
        return ret if exists(ret) else Path(config.base_path) / 'assets' / '_avatar' / (author_name + '.jpg')
