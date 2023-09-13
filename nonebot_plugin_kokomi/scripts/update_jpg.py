import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import json
import os
import httpx
import asyncio

file_path = os.path.dirname(__file__)
ship_icons_path = r''  # 该路径需要通过WoWSunpack获取


def add_alpha_channel(img):
    b_channel, g_channel, r_channel = cv2.split(img)
    alpha_channel = np.ones(
        b_channel.shape, dtype=b_channel.dtype) * 255

    img_new = cv2.merge(
        (b_channel, g_channel, r_channel, alpha_channel))
    return img_new


def merge_img(jpg_img, png_img, y1, y2, x1, x2):
    if jpg_img.shape[2] == 3:
        jpg_img = add_alpha_channel(jpg_img)
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
    x = font.getsize(in_str)[0]
    out_coord = x
    return out_coord


def add_text(img, text, left, top, textColor, textSize, on_right):
    if (isinstance(img, np.ndarray)):
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    fontStyle = ImageFont.truetype(os.path.join(
        os.path.dirname(file_path), 'wows', 'data', 'SourceHanSansCN-Bold.ttf'), textSize, encoding="utf-8")
    if on_right:
        w = x_coord(text, font=fontStyle)
        if w >= 300:
            del_len = int(((w-300)/w)*len(text))
            text = text[:(len(text)-del_len-1)]+'...'
            w = x_coord(text, font=fontStyle)
        left = left - w
    draw.text((left, top), text, textColor, font=fontStyle)
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)


async def update_name():
    async with httpx.AsyncClient() as client:
        url = 'https://vortex.worldofwarships.asia/api/encyclopedia/en/vehicles/'
        res = await client.get(url, timeout=3)
        return res.json()
tier_dict = {
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

userserverdata = asyncio.run(update_name())
ship_info = userserverdata['data']
img_jpg_path = os.path.join(file_path, 'png', 'white.jpg')
img_jpg = cv2.imread(img_jpg_path, cv2.IMREAD_UNCHANGED)
i = 1
res = None
all_dict = {}
for ship_id, ship_data in ship_info.items():
    all_dict[ship_id] = i
    tier = ship_data['level']
    name = ship_data['name'].split('_')[0]
    nickname = ship_data['localization']['shortmark']['zh_sg']
    nation = ship_data['nation']
    type = ship_data['tags'][0]
    ship_path = os.path.join(ship_icons_path, '{}.png'.format(name))
    if os.path.exists(ship_path):
        img_jpg2_path = os.path.join(file_path, 'icon', '00.png')
        img_png_path = os.path.join(file_path, 'icon', '{}.png'.format(type))
        img2_png_path = os.path.join(
            file_path, 'wows_ico', 'nation', 'large', 'flag_{}.png'.format(name))
        if os.path.exists(img2_png_path) != True:
            img2_png_path = os.path.join(
                file_path, 'wows_ico', 'nation', 'large', 'flag_{}.png'.format(nation))
        img3_png_path = ship_path
        img_jpg2 = cv2.imread(img_jpg2_path, cv2.IMREAD_UNCHANGED)
        img_png = cv2.imread(img_png_path, cv2.IMREAD_UNCHANGED)
        img2_png = cv2.imread(img2_png_path, cv2.IMREAD_UNCHANGED)
        img3_png = cv2.imread(img3_png_path, cv2.IMREAD_UNCHANGED)
        img2_png = cv2.resize(img2_png, None, fx=0.28, fy=0.28)
        img3_png = cv2.resize(img3_png, None, fx=2.85, fy=2.85)
        x = (i % 10) * 517
        y = int(i / 10) * 115
        # 设置叠加位置坐标
        if i == 1:
            i_jpg = img_jpg
        else:
            i_jpg = res
        x1 = 0 + x
        y1 = 0 + y
        x2 = x1 + img_jpg2.shape[1]
        y2 = y1 + img_jpg2.shape[0]
        res_img = merge_img(i_jpg, img_jpg2, y1, y2, x1, x2)
        x1 = 1 + x
        y1 = 1 + y
        x2 = x1 + img2_png.shape[1]
        y2 = y1 + img2_png.shape[0]
        res_img = merge_img(res_img, img2_png, y1, y2, x1, x2)
        x1 = 3 + x
        y1 = 74 + y
        x2 = x1 + img_png.shape[1]
        y2 = y1 + img_png.shape[0]
        res_img = merge_img(res_img, img_png, y1, y2, x1, x2)
        x1 = 170 + x
        y1 = 1 + y
        x2 = x1 + img3_png.shape[1]
        y2 = y1 + img3_png.shape[0]
        res_img = merge_img(res_img, img3_png, y1, y2, x1, x2)

        res_img = add_text(res_img, nickname, 482+x-3,
                           68+y, (0, 0, 0), 45, True)
        res_img = add_text(
            res_img, tier_dict[tier], 65+x, 77+y, (255, 255, 255), 30, False)
    i += 1
    res = res_img
    print(i)
cv2.imwrite(os.path.join(file_path, 'png', 'ship_preview.jpg'), res_img)
with open(os.path.join(file_path, 'png', 'ship_preview.json'), 'w', encoding='utf-8') as f:
    f.write(json.dumps(all_dict, ensure_ascii=False))
f.close()
