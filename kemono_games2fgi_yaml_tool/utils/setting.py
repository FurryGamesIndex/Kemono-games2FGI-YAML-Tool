from yaml import safe_load


class Config:
    sm_ms_token: str | None = None
    proxy: dict | None = None
    git_proxy: str | None = None
    base_path: str = ''

    def load(self, setting: dict | str):
        if isinstance(setting, dict):
            self.__dict__.update(setting)
        else:
            self.__dict__.update(safe_load(setting))


config = Config()
