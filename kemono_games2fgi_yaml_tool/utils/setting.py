from yaml import dump
from pathlib import Path

from .yaml_tool import load_yaml
from . import PathLike
from ..exception import FolderStructureError


class Config:
    sm_ms_token: str | None
    proxy: dict | None
    git_proxy: str | None
    base_path: PathLike = ""

    def load(self, setting: dict | PathLike):
        if isinstance(setting, dict):
            self.__dict__.update(setting)
        else:
            self.__dict__.update(load_yaml(setting))
        if not (Path(config.base_path) / "games").exists():
            raise FolderStructureError

    def __str__(self):
        return dump(
            {
                **self.__dict__,
                "base_path": str(self.base_path)
                if isinstance(self.base_path, Path)
                else self.base_path,
            }
        )

    def __getitem__(self, item):
        return self.__dict__[item]


default_config = {"proxy": None, "git_proxy": None}
config = Config()
config.__dict__.update(default_config)
