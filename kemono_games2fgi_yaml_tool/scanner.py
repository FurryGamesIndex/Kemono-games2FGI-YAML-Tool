from os.path import exists, join, isfile, basename
from os import listdir
from loguru import logger


def compare(kemono, fgi):
    files1 = set(listdir(kemono))
    files2 = set(listdir(fgi))
    result1 = list(files1 - files2)
    result2=[fgi+missing_file for missing_file in result1]
    for i in result1:
        logger.info(f'Found {i} missing')
    return result2


