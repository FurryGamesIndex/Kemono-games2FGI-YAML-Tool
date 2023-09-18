from os import listdir
from pathlib import Path

from loguru import logger


def compare(kemono: Path, fgi: Path):
    from .utils.setting import config

    if kemono is None:
        kemono = Path(config.base_path) / "games"
    files1 = set(listdir(kemono))
    files2 = set(listdir(fgi))
    result1 = list(files1 - files2)
    result2 = [kemono / missing_file for missing_file in result1]
    for i in result1:
        logger.info(f"发现 {i} 不存在")
    return result2
