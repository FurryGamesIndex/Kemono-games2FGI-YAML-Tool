import argparse
from argparse import RawTextHelpFormatter

parser = argparse.ArgumentParser(description=
'''
Noun Explanation:
FGI path: https://github.com/FurryGamesIndex/games The folder downloaded from this URL.
KEMONO path: https://github.com/kemono-games/fgi The folder downloaded from this URL.
Usage example: py -m kemono_games2fgi_yaml_tool -i c:\\downloads\\games c:\\downloads\\fgi -o OUTPUT_FOLDER
''', formatter_class=RawTextHelpFormatter)
parser.add_argument('-i', '--input', type=str, required=True, nargs=2, metavar=('FGI_PATH', 'KEMONO_PATH'))
parser.add_argument('-o', '--output', type=str, required=True)

args = parser.parse_args()