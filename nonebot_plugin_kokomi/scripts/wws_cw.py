import json
import os
import httpx
import time
import cv2
import numpy as np
from PIL import Image, ImageDraw
import gc
from httpx import (
    TimeoutException,
    ConnectTimeout,
    ReadTimeout
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
    img_to_b64,
    img_to_file,
    pr_info,
    color_box,
    merge_img,
    x_coord,
    add_text
)
from .data_source import (
    font_list,
    clan_color,
    background_color,
    border_color
)
import logging

file_path = os.path.dirname(__file__)
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

    fontStyle = font_list[1][55]
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
    creat_time = time.strftime(
        "%Y-%m-%d", time.localtime(result['data']['user']['created_at']))
    text_list.append(
        [(602+14-150, 405+38), creat_time, (0, 0, 0), 1, 55])

    res_img = cv2.imread(os.path.join(
        file_path, 'png', 'background', 'wws_cw.png'), cv2.IMREAD_UNCHANGED)
    # dog_tag
    if DOG_TAG:
        if result['dog_tag'] == [] or result['dog_tag'] == {}:
            pass
        else:
            res_img = dog_tag(res_img, result['dog_tag'])
    i = 0
    for ach_id, ach_num in result['data']['achievements'].items():
        achievement_png_path = os.path.join(
            file_path, 'png', 'achievement_plus', '{}.png'.format(ach_id))
        achievement_png = cv2.imread(
            achievement_png_path, cv2.IMREAD_UNCHANGED)
        achievement_png = cv2.resize(achievement_png, None, fx=1.75, fy=1.75)
        x1 = 215+200*i
        y1 = 720
        x2 = x1 + achievement_png.shape[1]
        y2 = y1 + achievement_png.shape[0]
        res_img = merge_img(res_img, achievement_png, y1, y2, x1, x2)
        del achievement_png
        text_list.append(
            [(x1+130, y1+100), 'x'+str(ach_num), (0, 0, 0), 1, 45])
        i += 1
    i = 0
    for index in range(25, 0, -1):
        x0 = 0
        y0 = 1137+14
        if str(index) in result['data']['season']:
            temp_data = result['data']['season'][str(index)]
            battles_count = '{:,}'.format(temp_data['battles'])
            avg_win = '{:.2f}%'.format(
                temp_data['wins']/temp_data['battles']*100)
            avg_wins = temp_data['wins'] / \
                temp_data['battles']*100
            avg_damage = '{:,}'.format(int(
                temp_data['damage_dealt']/temp_data['battles'])).replace(',', ' ')
            avg_frag = '{:.2f}'.format(
                temp_data['frags']/temp_data['battles'])
            avg_xp = '{:,}'.format(int(
                temp_data['xp']/temp_data['battles'])).replace(',', ' ')
            fontStyle = font_list[1][55]
            w = x_coord(f'第 {index} 赛季', fontStyle)
            text_list.append(
                [(286-w/2+x0, y0+89*i), f'第 {index} 赛季', (0, 0, 0), 1, 55])
            w = x_coord(battles_count, fontStyle)
            text_list.append(
                [(664-w/2+x0, y0+89*i), battles_count, (0, 0, 0), 1, 55])
            w = x_coord(avg_win, fontStyle)
            text_list.append(
                [(993-w/2+x0, y0+89*i), avg_win, color_box(0, avg_wins)[1], 1, 55])
            w = x_coord(avg_damage, fontStyle)
            text_list.append(
                [(1358-w/2+x0, y0+89*i), avg_damage, (0, 0, 0), 1, 55])
            w = x_coord(avg_frag, fontStyle)
            text_list.append(
                [(1745-w/2+x0, y0+89*i), avg_frag, (0, 0, 0), 1, 55])
            w = x_coord(avg_xp, fontStyle)
            text_list.append(
                [(2084-w/2+x0, y0+89*i), avg_xp, (0, 0, 0), 1, 55])
        else:
            continue
        i += 1

    if (isinstance(res_img, np.ndarray)):
        res_img = Image.fromarray(
            cv2.cvtColor(res_img, cv2.COLOR_BGR2RGB))

    w = x_coord(BOT_VERSON, fontStyle)
    text_list.append(
        [(1214-w/2, 1137+14+89*(i+1)+14), BOT_VERSON, (174, 174, 174), 1, 50])
    # 图表
    res_img = add_text(text_list, res_img)
    res_img = res_img.crop((0, 0, 2429, 1137+14+89*(i+2)))
    res_img = res_img.resize((int(2429*0.5), int((1137+14+89*(i+2))*0.5)))
    return res_img


async def get_png(
    parameter: list,
):
    try:
        # [aid,server]
        if parameter[1] in ['cn', 'ru']:
            return {'status': 'info', 'message': '非常抱歉，由于国服和俄服并未开放相关数据接口，无法查询到数据'}
        async with httpx.AsyncClient() as client:
            url = API_URL + '/user/cw/' + \
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
        if result['data']['season'] == {}:
            return {'status': 'info', 'message': '无cw赛季数据'}
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
