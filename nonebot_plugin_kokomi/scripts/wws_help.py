import os
from PIL import Image
from .config import (
    PIC_TYPE
)
from .data_source import (
    img_to_b64,
    img_to_file
)
file_path = os.path.dirname(__file__)


async def get_help_msg(
    extra: None
):
    res = {'status': 'ok', 'message': 'SUCCESS', 'img': None}
    if PIC_TYPE == 'base64':
        res['img'] = img_to_b64(Image.open(
            os.path.join(file_path, 'png', 'help.png')))
    elif PIC_TYPE == 'file':
        res['img'] = os.path.join(file_path, 'png', 'help.png')
    return res
