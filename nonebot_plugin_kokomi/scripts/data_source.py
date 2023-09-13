
import datetime
import base64
from io import BytesIO
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import time
import platform
from .config import PIC_PATH

isWin = True if platform.system().lower() == 'windows' else False
file_path = os.path.dirname(__file__)

font1_path = os.path.join(file_path, 'fonts', 'NasalizationRgFZ-BOLD.ttf') if isWin else os.path.join(
    '/usr/share/fonts', 'spaceAge.ttf')
font2_path = os.path.join(file_path, 'fonts', 'NZBZ.ttf') if isWin else os.path.join(
    '/usr/share/fonts', 'NZBZ.ttf')
font_list = {
    1: {
        20: ImageFont.truetype(font1_path, 20, encoding="utf-8"),
        25: ImageFont.truetype(font1_path, 25, encoding="utf-8"),
        30: ImageFont.truetype(font1_path, 30, encoding="utf-8"),
        35: ImageFont.truetype(font1_path, 35, encoding="utf-8"),
        40: ImageFont.truetype(font1_path, 40, encoding="utf-8"),
        45: ImageFont.truetype(font1_path, 45, encoding="utf-8"),
        50: ImageFont.truetype(font1_path, 50, encoding="utf-8"),
        55: ImageFont.truetype(font1_path, 55, encoding="utf-8"),
        60: ImageFont.truetype(font1_path, 60, encoding="utf-8"),
        65: ImageFont.truetype(font1_path, 65, encoding="utf-8"),
        70: ImageFont.truetype(font1_path, 70, encoding="utf-8"),
        80: ImageFont.truetype(font1_path, 80, encoding="utf-8"),
        100: ImageFont.truetype(font1_path, 100, encoding="utf-8")
    },
    2: {
        40: ImageFont.truetype(font2_path, 40, encoding="utf-8"),
        50: ImageFont.truetype(font2_path, 40, encoding="utf-8"),
        80: ImageFont.truetype(font2_path, 80, encoding="utf-8"),
        90: ImageFont.truetype(font2_path, 90, encoding="utf-8"),
        110: ImageFont.truetype(font2_path, 110, encoding="utf-8")
    }
}
clan_color = {
    13477119: (121, 61, 182),
    12511165: (144, 223, 143),
    14931616: (234, 197, 0),
    13427940: (147, 147, 147),
    11776947: (147, 147, 147),
    13408614: (184, 115, 51)
}

rank_list = {
    1: '黄金联盟',
    2: '白银联盟',
    3: '青铜联盟'
}

cvc_list = {
    0: '紫金',
    1: '白金',
    2: '黄金',
    3: '白银',
    4: '青铜'
}

role_dict = {
    'commander': '指挥官',
    'executive_officer': '副指挥官',
    'recruitment_officer': '征募官',
    'commissioned_officer': '现役军官',
    'officer': '前线军官',
    'private': '军校见习生'
}

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

cvc_color_list = {
    0: (121, 61, 182),
    1: (144, 223, 143),
    2: (234, 197, 0),
    3: (147, 147, 147),
    4: (184, 115, 51)
}

rank_color_list = {
    1: (209, 163, 77),
    2: (169, 169, 169),
    3: (192, 127, 114)
}


def server_url(server: str) -> str:
    url_list = {
        'asia': 'http://vortex.worldofwarships.asia',
        'eu': 'http://vortex.worldofwarships.eu',
        'na': 'http://vortex.worldofwarships.com',
        'ru': 'http://vortex.korabli.su',
        'cn': 'http://vortex.wowsgame.cn'
    }
    return url_list[server]


def add_box(box_list, res_img):
    img = ImageDraw.ImageDraw(res_img)
    for index in box_list:
        try:
            img.rectangle((index[0], index[1]), fill=index[2], outline=None)
        except:
            print(index)
    return res_img


def add_text(text_list, res_img):
    # 为图片添加文字
    draw = ImageDraw.Draw(res_img)
    for index in text_list:
        fontStyle = font_list[index[3]][index[4]]
        draw.text(index[0], index[1], index[2], font=fontStyle)
    return res_img


def formate_str(in_str, str_len, max_len):
    if str_len <= max_len:
        return in_str
    else:
        return in_str[:int(max_len/str_len*len(in_str))-2] + '...'


def get_days_difference(past_timestamp: int):
    past_datetime = datetime.datetime.fromtimestamp(past_timestamp)
    current_datetime = datetime.datetime.now()
    time_difference = current_datetime - past_datetime
    days_difference = time_difference.days
    return days_difference


def img_to_b64(pic: Image.Image) -> str:
    buf = BytesIO()
    pic.save(buf, format="PNG")
    base64_str = base64.b64encode(buf.getbuffer()).decode()
    return "base64://" + base64_str


def img_to_file(pic: Image.Image) -> str:
    file_name = os.path.join(PIC_PATH, str(time.time()*1000) + '.png')
    pic.save(file_name)
    return file_name
    # file:////home/.../temp.png


def aid_to_server(aid: str):
    if len(aid) == 10 and (aid[0] == '2' or aid[0] == '3'):
        return 'ASIA'
    elif len(aid) == 9 and (aid[0] == '5' or aid[0] == '6'):
        return 'EU'
    elif len(aid) == 10 and aid[0] == '1':
        return 'NA'
    elif len(aid) == 10 and aid[0] == '7':
        return 'CN'
    else:
        return 'RU'


def pr_info(pr: int):
    '''pr info'''
    if pr == -1:
        # [pic_num ,color_box, 描述, 字数差（add_text用），pr差值，评级]
        return [0, (128, 128, 128), '水平未知：', 0, -1, '水平未知']
    elif pr == -2:
        return [0, (0, 0, 0), '', 0, '', '-']
    elif pr >= 0 and pr < 750:
        return [1, (205, 51, 51), '距离下一评级：+', 0, int(750-pr), '还需努力']
    elif pr >= 750 and pr < 1100:
        return [2, (254, 121, 3), '距离下一评级：+', 0, int(1100-pr), '低于平均']
    elif pr >= 1100 and pr < 1350:
        return [3, (255, 193, 7), '距离下一评级：+', 0, int(1350-pr), '平均水平']
    elif pr >= 1350 and pr < 1550:
        return [4, (68, 179, 0), '距离下一评级：+', -3, int(1550-pr), '好']
    elif pr >= 1550 and pr < 1750:
        return [5, (49, 128, 0), '距离下一评级：+', -2, int(1750-pr), '很好']
    elif pr >= 1750 and pr < 2100:
        return [6, (52, 186, 211), '距离下一评级：+', -1, int(2100-pr), '非常好']
    elif pr >= 2100 and pr < 2450:
        return [7, (121, 61, 182), '距离下一评级：+', 0, int(2450-pr), '大佬平均']
    elif pr >= 2450:
        return [8, (88, 43, 128), '已超过最高评级：+', 0, int(pr-2450), '神佬平均']


def color_box(index: int, num: float):
    '''avg/server 自上向下为 win dmg frag xp plane_kill'''
    index_list = [
        [70, 60, 55, 52.5, 51, 49, 45],
        [1.7, 1.4, 1.2, 1.1, 1.0, 0.95, 0.8],
        [2, 1.5, 1.3, 1.0, 0.6, 0.3, 0.2],
        [1.7, 1.5, 1.3, 1.1, 0.9, 0.7, 0.5],
        [2.0, 1.7, 1.5, 1.3, 1.0, 0.9, 0.7]
    ]
    data = index_list[index]
    if num == -1:
        return [0, (128, 128, 128)]
    elif num == -2:
        return [0, (0, 0, 0)]
    elif num >= data[0]:
        return [8, (88, 43, 128)]
    elif num >= data[1] and num < data[0]:
        return [7, (121, 61, 182)]
    elif num >= data[2] and num < data[1]:
        return [6, (52, 186, 211)]
    elif num >= data[3] and num < data[2]:
        return [5, (49, 128, 0)]
    elif num >= data[4] and num < data[3]:
        return [4, (68, 179, 0)]
    elif num >= data[5] and num < data[4]:
        return [3, (255, 193, 7)]
    elif num >= data[6] and num < data[5]:
        return [2, (254, 121, 3)]
    elif num < data[6]:
        return [1, (205, 51, 51)]


def number_color_box(num: str):
    if num == 'color: #A00DC5':
        color_box = (160, 13, 197)
    elif num == 'color: #D042F3':
        color_box = (208, 66, 243)
    elif num == 'color: #02C9B3':
        color_box = (2, 201, 179)
    elif num == 'color: #318000':
        color_box = (49, 128, 0)
    elif num == 'color: #44B300':
        color_box = (68, 179, 0)
    elif num == 'color: #FFC71F':
        color_box = (255, 199, 31)
    elif num == 'color: #FE7903':
        color_box = (254, 121, 3)
    elif num == 'color: #FE0E00':
        color_box = (254, 14, 0)
    else:
        color_box = (96, 125, 139)
    return color_box


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


def x_coord(in_str: str, font: ImageFont.FreeTypeFont):
    # 获取文字的像素长度
    x = font.getsize(in_str)[0]
    out_coord = x
    return out_coord


a_tier_dict = {
    1: 'Ⅰ',
    2: 'Ⅱ',
    3: 'Ⅲ',
    4: 'Ⅳ',
    5: 'Ⅴ',
    6: 'Ⅵ',
    7: 'Ⅶ',
    8: 'Ⅷ',
    9: 'Ⅸ',
    10: 'Ⅹ',
    11: '★',
}
a_type_dict = {
    'AirCarrier': 'CV',
    'Battleship': 'BB',
    'Cruiser': 'CA',
    'Destroyer': 'DD',
    'Submarine': 'SS',
}

server_table_list = [
    [10000, 1000],
    [15000, 1500],
    [20000, 2000],
    [25000, 2500],
    [30000, 3000],
    [35000, 3500],
    [40000, 4000],
    [45000, 4500],
    [50000, 5000],
    [55000, 3500],
    [60000, 4000],
    [65000, 4500],
    [70000, 5000]
]
