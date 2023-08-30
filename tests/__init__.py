import unittest
from kemono_games2fgi_yaml_tool.games_convert import Converter
from kemono_games2fgi_yaml_tool.utils.setting import config
from kemono_games2fgi_yaml_tool.base_path import get_assets_path
from os.path import exists
config.load({'sm_ms_token': 'YOUR_TOKEN',
             'git_proxy': 'https://ghproxy.com/',
             'base_path': 'D:\\Project\\fgi-master\\'})


class Test(unittest.TestCase):

    def test_cmp(self):
        from kemono_games2fgi_yaml_tool.scanner import compare
        compare(fgi="D:\\Project\\games\\games\\")

    def test_convert(self):
        convert = Converter(
            url="https://raw.githubusercontent.com/kemono-games/fgi/ff8306f2e2ff6f70bbd08e85564c87d226229d5b/games"
                "/Beast_Beat.yaml",name="Beast_Beat")
        print(convert.to_fgi_yaml())

    def test_get_author(self):
        print(exists(get_assets_path("Ainro",'authors')))
        print(get_assets_path("Ainro",'authors'))
        print(exists(get_assets_path("Ainro",'assets\_avatar')))
        print(get_assets_path("Ainro",'assets\_avatar'))

