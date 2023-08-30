from PIL import Image
from io import BytesIO
from .utils.setting import config
from .base_path import get_assets_path

# games/lvyunlu.yaml->authors/Ainro.yaml->assets/thumbnail.png->assets/_avatar/Ainro.jpg
# 1. Determine whether there is a corresponding yaml
# 2. Determine if the image is 360x168, if it is not, then it can be scaled,
# if it is still not possible, then logger.warning
# 3. Compress the avatar to 64x64.

def resize_image(input_data, output_path, size: tuple):
    with Image.open(BytesIO(input_data)) as img:
        img.thumbnail(size)
        img.save(output_path)


def can_resize_to(image, target_width, target_height):
    with Image.open(BytesIO(image)) as img:
        original_width, original_height = img.size
        width_ratio = target_width / original_width
        height_ratio = target_height / original_height
        if width_ratio <= 1 and height_ratio <= 1:
            return True
        else:
            return False

# With author file: compress the avatar file
# No author file: return as is
class AssetsConverter:
    def __init__(self, author_list: list,assets: dict):
        self.author_list = [i['name'] for i in author_list]

    def is_author_yaml_exist(self):
        pass

    def convert(self):
        pass
    def to_fgi_yaml(self):
        pass
