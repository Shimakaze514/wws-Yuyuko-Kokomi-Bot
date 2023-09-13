import httpx
import logging
import os
import asyncio
import traceback
import cv2
import json
import numpy as np
from PIL import Image
'''
接口返回值
"dog_tag": {
    "texture_id": 0,                # 背景纹理
    "symbol_id": 4079963056,        # 符号
    "border_color_id": 0,           # 镶边颜色
    "background_color_id": 0,       # 背景颜色
    "background_id": 4240427952     # 背景
    }

id -> color
"border_color":{
    "4293348272": "0x282828",
    "4292299696": "0x23325d",
    "4291251120": "0x15668c",
    "4290202544": "0x213f47",
    "4289153968": "0x3a4a23",
    "4288105392": "0x553b16",
    "4287056816": "0x6d4f29",
    "4286008240": "0x8a763a",
    "4284959664": "0xd9d9d9",
    "4283911088": "0xf3c612",
    "4282862512": "0xcb7208",
    "4281813936": "0xa73a1c",
    "4280765360": "0xa32323",
    "4279716784": "0x7f1919",
    "4278668208": "0x382c4f"
}

"background_color":{
    "4293577648": "0x252525",
    "4292529072": "0x25355d",
    "4291480496": "0x2b6e91",
    "4290431920": "0x22454a",
    "4289383344": "0x3f4d2c",
    "4288334768": "0x8f7e44",
    "4287286192": "0x8b6932",

    "4286237616": "0xc9c9c9",
    "4285189040": "0xcfa40f",
    "4284140464": "0xd98815",
    "4283091888": "0xb74522",
    "4282043312": "0xad1d1d",
    "4280994736": "0x771d27",
    "4279946160": "0x3b2f4e"
}

'''


file_path = os.path.dirname(__file__)


url_list = {
    'asia': 'http://vortex.worldofwarships.asia',
    'eu': 'http://vortex.worldofwarships.eu',
    'na': 'http://vortex.worldofwarships.com',
    'ru': 'http://vortex.korabli.su',
    'cn': 'http://vortex.wowsgame.cn'
}


async def fetch_data(
    url: str,
    account_id: str
):
    '''请求获取数据'''
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(url=url, timeout=5)
            requset_result = res.json()
            return requset_result['data'][account_id]['dog_tag']
        except:
            logging.error(traceback.format_exc())
            return None


def add_alpha_channel(img):
    '''给图片添加alpha通道'''
    b_channel, g_channel, r_channel = cv2.split(img)
    alpha_channel = np.ones(
        b_channel.shape, dtype=b_channel.dtype) * 255

    img_new = cv2.merge(
        (b_channel, g_channel, r_channel, alpha_channel))
    return img_new


def merge_img(jpg_img, png_img, y1, y2, x1, x2):
    '''图片叠加'''
    if jpg_img.shape[2] == 3:
        jpg_img = add_alpha_channel(jpg_img)
    if png_img.shape[2] == 3:
        png_img = add_alpha_channel(png_img)
    yy1 = 0
    yy2 = png_img.shape[0]
    xx1 = 0
    xx2 = png_img.shape[1]

    if x1 < 0:
        xx1 = -x1
        x1 = 0
    if y1 < 0:
        yy1 = - y1
        y1 = 0
    if x2 > jpg_img.shape[1]:
        xx2 = png_img.shape[1] - (x2 - jpg_img.shape[1])
        x2 = jpg_img.shape[1]
    if y2 > jpg_img.shape[0]:
        yy2 = png_img.shape[0] - (y2 - jpg_img.shape[0])
        y2 = jpg_img.shape[0]

    alpha_png = png_img[yy1:yy2, xx1:xx2, 3] / 255.0
    alpha_jpg = 1 - alpha_png

    for c in range(0, 3):
        jpg_img[y1:y2, x1:x2, c] = (
            (alpha_jpg*jpg_img[y1:y2, x1:x2, c]) + (alpha_png*png_img[yy1:yy2, xx1:xx2, c]))

    return jpg_img


def dog_tag(
    response: dict
):
    print(response)
    '''dogtag'''
    border_color = {
        "4293348272": "0x282828",
        "4292299696": "0x23325d",
        "4291251120": "0x15668c",
        "4290202544": "0x213f47",
        "4289153968": "0x3a4a23",
        "4288105392": "0x553b16",
        "4287056816": "0x6d4f29",
        "4286008240": "0x8a763a",
        "4284959664": "0xd9d9d9",
        "4283911088": "0xf3c612",
        "4282862512": "0xcb7208",
        "4281813936": "0xa73a1c",
        "4280765360": "0xa32323",
        "4279716784": "0x7f1919",
        "4278668208": "0x382c4f"
    }

    background_color = {
        "4293577648": "0x252525",
        "4292529072": "0x25355d",
        "4291480496": "0x2b6e91",
        "4290431920": "0x22454a",
        "4289383344": "0x3f4d2c",
        "4288334768": "0x8f7e44",
        "4287286192": "0x8b6932",

        "4286237616": "0xc9c9c9",
        "4285189040": "0xcfa40f",
        "4284140464": "0xd98815",
        "4283091888": "0xb74522",
        "4282043312": "0xad1d1d",
        "4280994736": "0x771d27",
        "4279946160": "0x3b2f4e"
    }
    # 测试用的黑底背景
    img = cv2.imread(os.path.join(file_path, 'png',
                     'test_dogtag.png'), cv2.IMREAD_UNCHANGED)
    # 读取dogtag.josn数据
    dog_tag_json = open(os.path.join(
        file_path, 'png', 'dog_tags.json'), "r", encoding="utf-8")
    dog_tag_data = json.load(dog_tag_json)
    dog_tag_json.close()
    # 背景和符号id对应的图片名称
    background_id = dog_tag_data.get(
        str(response.get('background_id', 0)), None)
    symbol_id = dog_tag_data.get(str(response.get('symbol_id', 0)), None)
    if background_id == None and symbol_id == None:
        return img
    x1 = 0
    y1 = 0
    # 判断dogtag是否为自定义
    if os.path.isdir(os.path.join(file_path, 'png', 'dogTags', f'{background_id}')):
        # 背景
        texture_id = dog_tag_data[str(
            response['texture_id'])][6:]  # 获取背景纹理图片的类型
        background_color_id = background_color[str(
            response['background_color_id'])]  # 获取背景的颜色
        background_png_path = os.path.join(
            file_path, 'png', 'new_dogTags', f'{background_id}_background_{texture_id}_{background_color_id}.png')
        background = cv2.imread(background_png_path, cv2.IMREAD_UNCHANGED)
        background = cv2.resize(background, None, fx=0.818, fy=0.818)
        x2 = x1 + background.shape[1]
        y2 = y1 + background.shape[0]
        img = merge_img(img, background, y1, y2, x1, x2)
        del background
        # 镶边
        border_color_id = border_color[str(
            response['border_color_id'])]  # 获取镶边的颜色
        border_png_path = os.path.join(
            file_path, 'png', 'new_dogTags', f'{background_id}_border_{border_color_id}.png')
        border = cv2.imread(border_png_path, cv2.IMREAD_UNCHANGED)
        border = cv2.resize(border, None, fx=0.818, fy=0.818)
        x2 = x1 + border.shape[1]
        y2 = y1 + border.shape[0]
        img = merge_img(img, border, y1, y2, x1, x2)
        del border
        # 符号
        symbol_png_path = os.path.join(
            file_path, 'png', 'dogTags', f'{symbol_id}.png')
        symbol = cv2.imread(symbol_png_path, cv2.IMREAD_UNCHANGED)
        symbol = cv2.resize(symbol, None, fx=0.818, fy=0.818)
        x2 = x1 + symbol.shape[1]
        y2 = y1 + symbol.shape[0]
        img = merge_img(img, symbol, y1, y2, x1, x2)
        del symbol
    elif background_id == None and symbol_id != None:
        # 符号
        symbol_png_path = os.path.join(
            file_path, 'png', 'dogTags', f'{symbol_id}.png')
        symbol = cv2.imread(symbol_png_path, cv2.IMREAD_UNCHANGED)
        symbol = cv2.resize(symbol, None, fx=0.818, fy=0.818)
        x2 = x1 + symbol.shape[1]
        y2 = y1 + symbol.shape[0]
        img = merge_img(img, symbol, y1, y2, x1, x2)
        del symbol
    else:
        # 背景
        background_png_path = os.path.join(
            file_path, 'png', 'dogTags', f'{background_id}.png')
        background = cv2.imread(background_png_path, cv2.IMREAD_UNCHANGED)
        background = cv2.resize(background, None, fx=0.818, fy=0.818)
        x2 = x1 + background.shape[1]
        y2 = y1 + background.shape[0]
        img = merge_img(img, background, y1, y2, x1, x2)
        del background
        # 符号
        symbol_png_path = os.path.join(
            file_path, 'png', 'dogTags', f'{symbol_id}.png')
        symbol = cv2.imread(symbol_png_path, cv2.IMREAD_UNCHANGED)
        symbol = cv2.resize(symbol, None, fx=0.818, fy=0.818)
        x2 = x1 + symbol.shape[1]
        y2 = y1 + symbol.shape[0]
        img = merge_img(img, symbol, y1, y2, x1, x2)
        del symbol

    return img


async def main(
    account_id: str,
    server: str
):
    api_url = f'{url_list[server]}/api/accounts/{account_id}/'
    print(api_url)
    response = await fetch_data(
        url=api_url,
        account_id=account_id
    )
    if response:
        img = dog_tag(response=response)
    else:
        print('网络请求失败')
        exit()
    if (isinstance(img, np.ndarray)):
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    img.show()

if __name__ == "__main__":
    asyncio.run(
        main(
            account_id='7049809565',
            server='cn'
        )
    )

'''
分割 _PCNA00X.png 图片

'''
# border_color = {
#     "1": "0x282828",
#     "2": "0x23325d",
#     "3": "0x15668c",
#     "4": "0x213f47",
#     "5": "0x3a4a23",
#     "6": "0x553b16",
#     "7": "0x6d4f29",
#     "8": "0x8a763a",
#     "9": "0xd9d9d9",
#     "10": "0xf3c612",
#     "11": "0xcb7208",
#     "12": "0xa73a1c",
#     "13": "0xa32323",
#     "14": "0x7f1919",
#     "15": "0x382c4f"
# }

# background_color = {
#     "1": "0x252525",
#     "2": "0x25355d",
#     "3": "0x2b6e91",
#     "4": "0x22454a",
#     "5": "0x3f4d2c",
#     "6": "0x8f7e44",
#     "7": "0x8b6932",

#     "8": "0x8a763a",

#     "9": "0xc9c9c9",
#     "10": "0xcfa40f",
#     "11": "0xd98815",
#     "12": "0xb74522",
#     "13": "0xad1d1d",
#     "14": "0x771d27",
#     "15": "0x3b2f4e"
# }
# png_type = '_PCNA009'
# t = png_type.replace('_', '')
# all_png_path = os.path.join(file_path, 'png', 'new_dogTags', F'{png_type}.png')
# all_png = Image.open(all_png_path)
# i = 0
# while i <= 14:
#     index = str(i+1)
#     ship_png = all_png.crop(
#         ((512*0), (512*0+512*i), (512*1), (512*1+512*i)))
#     ship_png.save(os.path.join(file_path, 'png', 'new_dogTags',
#                   f'{t}_border_{border_color[index]}.png'))
#     ship_png = all_png.crop(
#         ((512*1), (512*0+512*i), (512*2), (512*1+512*i)))
#     ship_png.save(os.path.join(file_path, 'png', 'new_dogTags',
#                   f'{t}_background_1_{background_color[index]}.png'))
#     ship_png = all_png.crop(
#         ((512*2), (512*0+512*i), (512*3), (512*1+512*i)))
#     ship_png.save(os.path.join(file_path, 'png', 'new_dogTags',
#                   f'{t}_background_2_{background_color[index]}.png'))
#     ship_png = all_png.crop(
#         ((512*3), (512*0+512*i), (512*4), (512*1+512*i)))
#     ship_png.save(os.path.join(file_path, 'png', 'new_dogTags',
#                   f'{t}_background_3_{background_color[index]}.png'))
#     ship_png = all_png.crop(
#         ((512*4), (512*0+512*i), (512*5), (512*1+512*i)))
#     ship_png.save(os.path.join(file_path, 'png', 'new_dogTags',
#                   f'{t}_background_4_{background_color[index]}.png'))
#     i += 1
