from os.path import exists, join, isfile, basename
from os import listdir
from loguru import logger
from .utils.setting import config
from pathlib import Path


def compare(fgi: str, kemono: str = Path(config.base_path) / 'games'):
    files1 = set(listdir(kemono))
    files2 = set(listdir(fgi))
    result1 = list(files1 - files2)
    result2 = [fgi + missing_file for missing_file in result1]
    for i in result1:
        logger.info(f'Found {i} missing')
    return result2
