import unittest
from pathlib import Path

from yaml import safe_load

from kemono_games2fgi_yaml_tool.converter import Converter
from kemono_games2fgi_yaml_tool.utils.setting import config
from kemono_games2fgi_yaml_tool.utils.spider import get_text

config.load(
    {
        "sm_ms_token": "T0E5I2je6EL1Q61Gp7vATUUfxziYJMZK",
        "git_proxy": "https://ghproxy.com/",
        "base_path": "/media/Data/Project/fgi-master/",
    }
)


class Test(unittest.TestCase):
    def test_cmp(self):
        from kemono_games2fgi_yaml_tool.scanner import compare

        compare(fgi="/media/Data/Project/games/games")

    def test_convert_game(self):
        Converter(
            yaml="/home/askirin/Desktop/changes/games/Shared_House.yaml",
            output="/home/askirin/Desktop/test/",
        ).convert()
