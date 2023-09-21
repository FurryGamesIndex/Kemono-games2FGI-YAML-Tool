import concurrent.futures
import threading
from io import BytesIO
from pathlib import Path
from time import time, sleep
from typing import Literal
from shutil import copy
from jsonschema import exceptions
from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate
from loguru import logger as log
from sm_ms_api import SMMS, ImageUploadError
from yaml import safe_load
from PIL import Image
from .exception import UnsupportedTagList, InvalidYAMLDataError
from .utils.setting import config
from .utils.spider import get_text
from .utils.yaml_tool import dump_to_yaml, load_yaml

schema_cache: dict = {}
tag_cache: dict = {}
folder_created = False


class RateLimiter:
    def __init__(self, max_calls=20, seconds=60):
        self.max_calls = max_calls
        self.seconds = seconds
        self.lock = threading.Lock()
        self.calls = 0
        self.last_reset = time()

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            with self.lock:
                current_time = time()
                elapsed_time = current_time - self.last_reset

                if elapsed_time >= self.seconds:
                    self.calls = 0
                    self.last_reset = current_time

                if self.calls >= self.max_calls:
                    time_to_wait = self.seconds - elapsed_time
                    if time_to_wait > 0:
                        sleep(time_to_wait)
                        self.calls = 0
                        self.last_reset = time()

                self.calls += 1
                return func(*args, **kwargs)

        return wrapper


def upload_img(path: str):
    print(path)
    smms = SMMS(token=config.sm_ms_token)
    # sleep(random.randint(1, 7))
    if Path(path).stat().st_size > 512 * 1024:
        img = Image.open(path)
        if img.format != "gif":
            img.thumbnail((1000, 1000))
            image_bytes = BytesIO()
            img.save(image_bytes, format="png")
        else:
            img.close()
            return smms.upload_image(path)
        res = smms.upload_image(image_bytes, Path(path).name)
        return res
    return smms.upload_image(path)


def logger(func):
    def wrapper(*args, **kwargs):  # 添加self参数
        log.info(f"正在{func.__doc__.strip()}中 ")
        result = func(*args, **kwargs)
        return result

    return wrapper


class Converter:
    tags: dict = {}
    paths: dict = {
        "cn": "games/l10n/zh-cn",
        "ja": "games/l10n/ja",
        "tw": "games/l10n/zh-tw",
        "assets": "assets",
        "authors": "authors",
        "_avatar": "assets/_avatar",
    }

    def __init__(self, yaml: str, output: str):
        self.data = load_yaml(yaml)
        self.yaml = yaml
        self.game_name = Path(yaml).stem
        self.output = Path(output)
        self.base_path = Path(yaml).parent.parent
        log.info(f"转换{self.game_name}中")

    @logger
    def copy_thumbnail(self):
        """
        转换缩略图
        """

        def get_thumbnail(game_name: str):
            if (self.path("assets") / game_name / "thumbnail.jpg").exists():
                return self.path("assets") / game_name / "thumbnail.jpg"
            else:
                return self.path("assets") / game_name / "thumbnail.png"

        thumbnail_path = get_thumbnail(self.game_name)
        img = Image.open(thumbnail_path)
        if img.size != (460, 215):
            copy(
                thumbnail_path,
                self.output
                / self.paths["assets"]
                / self.game_name
                / thumbnail_path.name,
            )
            img.close()
            return
        img.resize((360, 168))
        img.save(
            self.output / self.paths["assets"] / self.game_name / thumbnail_path.name,
            optimize=True,
            quality=100,
        )
        img.close()

    @logger
    def copy_author(self):
        """
        转换作者YAML文件
        """

        def get_image(author_name: str):
            if (self.path("_avatar") / (i["name"] + ".jpg")).exists():
                return self.path("_avatar") / (author_name + ".jpg")
            elif (self.path("_avatar") / (i["name"] + ".png")).exists():
                return self.path("_avatar") / (author_name + ".png")

        def process_avatar(input_path: Path, output: Path):
            with Image.open(input_path) as img:
                img.thumbnail((64, 64))
                img.save(output)

        for i in self.data["authors"]:
            author_path = self.path("authors") / (i["name"] + ".yaml")
            if author_path.exists():
                copy(
                    author_path,
                    self.output / self.paths["authors"] / (i["name"] + ".yaml"),
                )
                path = get_image(i["name"])
                if path is not None:
                    process_avatar(
                        get_image(i["name"]),
                        self.output / self.paths["_avatar"] / path.name,
                    )

    @logger
    def copy_i18n(self):
        """
        转换多国语言翻译
        """
        for i in ["cn", "ja", "tw"]:
            if (self.base_path / self.paths[i] / (self.game_name + ".yaml")).exists():
                copy(
                    self.path(i) / (self.game_name + ".yaml"),
                    self.output / self.paths[i] / (self.game_name + ".yaml"),
                )

    @logger
    def convert_yaml(self):
        """
        转换YAML
        """
        with open(
            self.output / "games" / (self.game_name + ".yaml"), "w", encoding="utf-8"
        ) as f:
            for i in self.data["authors"]:
                temp = []

                for ii in i["role"]:
                    if (
                        ii
                        in schema_cache["properties"]["authors"]["items"]["properties"][
                            "role"
                        ]["items"]["enum"]
                    ):
                        temp.append(ii)
                i["role"] = temp

            try:
                validate(self.data, schema_cache)
            except ValidationError as e:
                raise InvalidYAMLDataError from e
            f.write(dump_to_yaml(self.data))

    @logger
    def mkdirs(self):
        """
        新建文件夹
        """
        for i in self.paths.values():
            Path(self.output / i).mkdir(parents=True, exist_ok=True)

    def convert(self):
        global folder_created
        if (self.output / "games" / (self.game_name + ".yaml")).exists():
            log.info("YAML文件已经存在，跳过")
            return
        self.compare_tags()
        log.success("没有冲突的标签")
        is_ok = self.validate_it()
        if not is_ok:
            self.process_screenshots()
        if not folder_created:
            self.mkdirs()
            folder_created = True
        Path(self.output / self.paths["assets"] / self.game_name).mkdir(
            parents=True, exist_ok=True
        )
        if "authors" in self.data:
            self.copy_author()
        self.copy_i18n()
        self.copy_thumbnail()
        if not is_ok:
            self.convert_yaml()
        else:
            copy(
                self.base_path / "games" / (self.game_name + ".yaml"),
                self.output / "games" / (self.game_name + ".yaml"),
            )

    def path(
        self, location: str = Literal["cn", "ja", "tw", "assets", "authors", "_avatar"]
    ) -> Path:
        return self.base_path / self.paths[location]

    def parse_tags(
        self,
        type_tag: str,
        website: str = Literal["FurryGamesIndex/games", "kemono-games/fgi"],
    ):
        global tag_cache
        if not tag_cache:
            tag_cache = safe_load(
                get_text(
                    f"https://raw.githubusercontent.com/{website}/master/tags.yaml"
                )
            )
        if website not in self.tags:
            self.tags[website] = tag_cache
        return [
            key
            for key, value in self.tags[website].items()
            if type_tag in value.get("namespaces", [])
        ]

    @logger
    def process_screenshots(self):
        """
        处理游戏截图
        """

        @RateLimiter(max_calls=10, seconds=60)
        def handle_img(chunk: dict | str, retry: int = 0) -> dict | str:
            try:
                if "type" in chunk and "path" in chunk:
                    if "sensitive" in chunk and chunk["sensitive"]:
                        return {
                            "sensitive": True,
                            "uri": upload_img(
                                self.path("assets") / self.game_name / chunk["path"]
                            ),
                        }
                    else:
                        return upload_img(
                            self.path("assets") / self.game_name / chunk["path"]
                        )
            except Exception as e:
                if retry == 3:
                    log.error(self.path("assets") / self.game_name / chunk["path"])
                    raise e
                if type(e) != ImageUploadError:
                    log.warning(
                        f"Image upload error({e.__class__.__name__}),retrying..."
                    )
                else:
                    log.warning(e)
                sleep(3)
                retry += 1
                return handle_img(chunk, retry)

        # noinspection PyUnusedLocal
        def handle_vid(chunk: dict):
            log.warning("Unable to upload video, ignore...")
            return []

        def process_chunk(chunk):
            if "type" in chunk and "image:local" in chunk["type"]:
                return handle_img(chunk)
            elif "type" in chunk and "video:local" in chunk["type"]:
                return handle_vid(chunk)
            return chunk

        with concurrent.futures.ThreadPoolExecutor() as executor:
            new_screenshots = list(
                executor.map(process_chunk, self.data["screenshots"])
            )
            self.data["screenshots"] = new_screenshots

    # noinspection PyBroadException
    def validate_it(self) -> bool:
        global schema_cache
        try:
            if not schema_cache:
                schema_cache = safe_load(
                    get_text(
                        "https://raw.githubusercontent.com/FurryGamesIndex/games/master/schemas/game"
                        ".schema.yaml"
                    )
                )
            validate(self.data, schema_cache),
            return True
        except exceptions.ValidationError:
            return False

    def compare_tags(self):
        cmp_list: list = [
            "type",
            "species",
            "fetish",
            "misc",
            "lang",
            "publish",
            "platform",
            "sys",
        ]
        for i in cmp_list:
            fgi = set(self.parse_tags(i, "FurryGamesIndex/games"))
            kemono = set(self.parse_tags(i, "kemono-games/fgi"))
            if fgi != kemono:
                raise UnsupportedTagList(", ".join(kemono - fgi))
