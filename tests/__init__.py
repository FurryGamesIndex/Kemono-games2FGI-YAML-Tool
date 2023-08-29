import unittest
from kemono_games2fgi_yaml_tool.games_convert import Converter
from kemono_games2fgi_yaml_tool.utils.setting import config

config.load({'sm_ms_token': '', 'git_proxy': 'https://ghproxy.com/',
             'base_path': 'D:\\Project\\fgi-master\\'})


class Test(unittest.TestCase):

    def test_cmp(self):
        from kemono_games2fgi_yaml_tool.scanner import compare
        compare("D:\\Project\\fgi-master\\games", "D:\\Project\\games\\games\\")

    def test_convert(self):
        convert = Converter(
            url="https://raw.githubusercontent.com/kemono-games/fgi/ff8306f2e2ff6f70bbd08e85564c87d226229d5b/games/Beast_Beat.yaml",name="Beast_Beat")
        print(convert.to_fgi_yaml())
