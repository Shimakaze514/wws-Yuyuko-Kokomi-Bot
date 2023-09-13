import json
import os
import httpx
import time
import gc
import random
import cv2
import numpy as np
from PIL import Image
from httpx import (
    TimeoutException,
    ConnectTimeout,
    ReadTimeout
)
from .data_source import (
    img_to_b64,
    img_to_file,
    merge_img,
    x_coord,
    add_text
)
from .config import (
    DOG_TAG,
    REQUEST_TIMEOUT,
    API_URL,
    API_TOKEN,
    PIC_TYPE,
    BOT_VERSON
)
from .data_source import (
    font_list,
    clan_color,
    background_color,
    border_color
)

import logging

file_path = os.path.dirname(__file__)
parent_file_path = os.path.dirname(os.path.dirname(__file__))
# 配置日志输出到文件
logging.basicConfig(filename=os.path.join(
    file_path, 'log', 'error.log'), level=logging.ERROR)


def dog_tag(
    img,
    response: dict
):
    '''dogtag'''
    dog_tag_json = open(os.path.join(
        file_path, 'png', 'dog_tags.json'), "r", encoding="utf-8")
    dog_tag_data = json.load(dog_tag_json)
    dog_tag_json.close()
    # 背景和符号id对应的图片名称
    background_id = dog_tag_data.get(str(response['background_id']), None)
    symbol_id = dog_tag_data.get(str(response['symbol_id']), None)
    if background_id == None and symbol_id == None:
        return img
    x1 = 1912
    y1 = 132
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


def main(
    result: dict,
    aid: str,
    server: str
):
    text_list = []
    # Id卡
    text_list.append(
        [(158+14, 123+38), result['nickname'], (0, 0, 0), 1, 100])
    text_list.append(
        [(185+14, 237+38), f'{server.upper()} -- {aid}', (163, 163, 163), 1, 45])
    if result['data']['clans']['clan'] == {}:
        tag = 'None'
        tag_color = (179, 179, 179)
    else:
        tag = '['+result['data']['clans']['clan']['tag']+']'
        tag_color = clan_color[result['data']['clans']['clan']['color']]
    text_list.append(
        [(602+14-150+2, 317+38+2), tag, (255, 255, 255), 1, 55])
    text_list.append(
        [(602+14-150, 317+38), tag, tag_color, 1, 55])
    text_list.append(
        [(602+14-150, 405+38), '12.8', (0, 0, 0), 1, 55])
    res_img = cv2.imread(os.path.join(
        file_path, 'png', 'background', 'wws_sx.png'), cv2.IMREAD_UNCHANGED)
    # dog_tag
    if DOG_TAG:
        if result['dog_tag'] == [] or result['dog_tag'] == {}:
            pass
        else:
            res_img = dog_tag(res_img, result['dog_tag'])

    ship_name_file_path = os.path.join(
        parent_file_path, 'json', 'ship_name.json')
    temp = open(ship_name_file_path, "r", encoding="utf-8")
    ship_name_data = json.load(temp)
    temp.close()
    useful_shipid_list = []
    for ship_id in result['data']['ships']:
        if (
            ship_id not in ship_name_data or
            '[' in ship_name_data[ship_id]['ship_name']['zh_sg'] or
            '(' in ship_name_data[ship_id]['ship_name']['zh_sg']
        ):
            continue

        useful_shipid_list.append(ship_id)
    special_ship_list = [
        '4076745936',
        '3751687984',
        '3751687376',
        '3741234640',
        '3762173136',
        '3730749392',
        '3762173776',
        '3751720912',
        '3762206704',
        '3762239312',
        '3762205904',
        '3741300720',
        '3762239440',
        '3762173936',
        '3730748880',
        '3730749424'
    ]
    owned_ship_list = []
    not_owned_ship_list = []
    for special_ship_id in special_ship_list:
        if special_ship_id in useful_shipid_list:
            owned_ship_list.append(
                'Ⅷ  ' + ship_name_data[special_ship_id]['ship_name']['zh_sg'])
        else:
            not_owned_ship_list.append(
                'Ⅷ  ' + ship_name_data[special_ship_id]['ship_name']['zh_sg'])
    all_code = 0
    all_ship_number = 0
    ship_number = [0, 0, 0, 0]
    for ship_id in useful_shipid_list:
        ship_tier = ship_name_data[ship_id]['tier']
        if ship_tier in [11]:
            ship_number[0] += 1
        elif ship_tier in [10]:
            ship_number[1] += 1
        elif ship_tier in [8, 9]:
            ship_number[2] += 1
        elif ship_tier in [5, 6, 7]:
            ship_number[3] += 1
        all_ship_number += 1
    ship_price = [200, 200, 75, 30]
    i = 0
    fontStyle = font_list[1][55]
    while i <= 3:
        w = x_coord(str(ship_number[i]), fontStyle)
        text_list.append(
            [(1524 - w/2, 716 + 98*i), str(ship_number[i]), (0, 0, 0), 1, 55])
        w = x_coord(str(ship_price[i]), fontStyle)
        text_list.append(
            [(1844 - w/2, 716 + 98*i), str(ship_price[i]), (0, 0, 0), 1, 55])
        all_code += ship_price[i]*ship_number[i]
        code = "{:,}".format(ship_price[i]*ship_number[i]).replace(",", " ")
        w = x_coord(code, fontStyle)
        text_list.append(
            [(2165 - w/2, 716 + 98*i), code, (0, 0, 0), 1, 55])
        i += 1
    all_code += 1250
    all_code = "{:,}".format(all_code).replace(",", " ")
    fontStyle = font_list[2][110]
    w = x_coord(str(all_ship_number), fontStyle)
    text_list.append(
        [(322 - w/2, 711), str(all_ship_number), (0, 0, 0), 2, 110])
    w = x_coord(all_code, fontStyle)
    text_list.append([(787 - w/2, 711), all_code, (0, 0, 0), 2, 110])

    i = 0
    while i <= 15:
        x = int(i % 3)
        y = int(i/3)
        if i <= len(owned_ship_list) - 1:
            text_list.append(
                [(234+680*x, 2450-160+80*y), owned_ship_list[i], (233, 188, 84), 1, 60])
        else:
            text_list.append([(234+680*x, 2450-160+80*y), not_owned_ship_list[i -
                             len(owned_ship_list)], (105, 105, 105), 1, 60])
        i += 1

    fontStyle = font_list[1][80]
    w = x_coord(BOT_VERSON, fontStyle)
    text_list.append(
        [(1214-w/2, 3252), BOT_VERSON, (174, 174, 174), 1, 80])
    if (isinstance(res_img, np.ndarray)):
        res_img = Image.fromarray(
            cv2.cvtColor(res_img, cv2.COLOR_BGR2RGB))
    res_img = add_text(text_list, res_img)
    res_img = res_img.resize((1214, 1717))
    return res_img


async def get_png(
    parameter: list,
):
    try:
        # [aid,server,user_ac,ac]
        async with httpx.AsyncClient() as client:
            if parameter[2]:
                url = API_URL + '/user/sx/' + \
                    f'?token={API_TOKEN}&aid={parameter[0]}&server={parameter[1]}&use_ac=True&ac={parameter[3]}'
            else:
                url = API_URL + '/user/sx/' + \
                    f'?token={API_TOKEN}&aid={parameter[0]}&server={parameter[1]}'
            res = await client.get(url, timeout=REQUEST_TIMEOUT)
            requset_code = res.status_code
            result = res.json()
            if requset_code == 200:
                pass
            else:
                return {'status': 'info', 'message': '数据接口请求失败'}
        if result['status'] != 'ok':
            return result
        if result['hidden'] == True:
            return {'status': 'info', 'message': '该玩家隐藏战绩'}
        res_img = main(
            result=result,
            aid=parameter[0],
            server=parameter[1]
        )
        res = {'status': 'ok', 'message': 'SUCCESS', 'img': None}
        if PIC_TYPE == 'base64':
            res['img'] = img_to_b64(res_img)
        elif PIC_TYPE == 'file':
            res['img'] = img_to_file(res_img)
        else:
            return {'status': 'error', 'message': '程序内部错误', 'error': 'PIC_TYPE 配置错误!'}
        del res_img
        gc.collect()
        return res
    except (TimeoutException, ConnectTimeout, ReadTimeout):
        return {'status': 'info', 'message': '网络请求超时,请稍后重试'}
    except Exception as e:
        logging.exception(
            f"Time:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}, Parameter:{parameter}")
        return {'status': 'error', 'message': f'程序内部错误', 'error': str(type(e))}
