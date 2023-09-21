import json
import os
import time
import httpx
import cv2
import logging
import numpy as np
from PIL import Image
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
    number_color_box,
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
    result,
    aid,
    ship_name,
    server
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
    fontStyle = font_list[1][70]
    w = x_coord(ship_name, fontStyle)
    text_list.append(
        [(1214-w/2, 602), ship_name, (0, 0, 0), 1, 70])

    # 主要数据
    avg_pr = int((result['data']['rank']['user']
                  ['personal_rating']).replace(' ', ''))
    pr_data = pr_info(avg_pr)
    pr_png_path = os.path.join(
        file_path, 'png', 'pr', '{}.png'.format(pr_data[0]))
    res_img = cv2.imread(os.path.join(
        file_path, 'png', 'background', 'wws_me_rank.png'), cv2.IMREAD_UNCHANGED)
    pr_png = cv2.imread(pr_png_path, cv2.IMREAD_UNCHANGED)
    pr_png = cv2.resize(pr_png, None, fx=0.787, fy=0.787)
    x1 = 118+14
    y1 = 590+38+129
    x2 = x1 + pr_png.shape[1]
    y2 = y1 + pr_png.shape[0]
    res_img = merge_img(res_img, pr_png, y1, y2, x1, x2)
    del pr_png
    text_list.append(
        [(545+100*pr_data[3]+14, 653+38+129), pr_data[2]+str(pr_data[4]), (255, 255, 255), 1, 35])
    str_pr = '{:,}'.format(int(avg_pr))
    fontStyle = font_list[1][80]
    w = x_coord(str_pr, fontStyle)
    text_list.append(
        [(2270-w+14, 605+38+129), str_pr, (255, 255, 255), 1, 80])
    x0 = 310+14
    y0 = 823+38+129
    battles_count = result['data']['rank']['user']['battles_count']
    avg_win = result['data']['rank']['user']['win_rate']
    avg_damage = result['data']['rank']['user']['damage_dealt']
    avg_frag = result['data']['rank']['user']['frag']
    avg_xp = result['data']['rank']['user']['exp']
    fontStyle = font_list[1][80]
    w = x_coord(battles_count, fontStyle)
    text_list.append(
        [(x0+446*0-w/2, y0), battles_count, (0, 0, 0), 1, 80])
    w = x_coord(avg_win, fontStyle)
    text_list.append(
        [(x0+446*1-w/2, y0), avg_win, number_color_box(result['data']['rank']['user']['win_rate_color']), 1, 80])
    w = x_coord(avg_damage, fontStyle)
    text_list.append(
        [(x0+446*2-w/2, y0), avg_damage, number_color_box(result['data']['rank']['user']['damage_dealt_color']), 1, 80])
    w = x_coord(avg_frag, fontStyle)
    text_list.append(
        [(x0+446*3-w/2, y0), avg_frag, number_color_box(result['data']['rank']['user']['frag_color']), 1, 80])
    w = x_coord(avg_xp, fontStyle)
    text_list.append(
        [(x0+446*4-w/2, y0), avg_xp, (0, 0, 0), 1, 80])
    user_rank = result['data']['rank']['user']['rank_num']
    if user_rank == '1':
        user_percent = '100.0%'
    else:
        user_percent = '{:.2f}%'.format((1-int(result['data']['rank']['user']['rank_num'])/float(
            result['data']['rank']['user']['all_rank_num'])/100)*100)
    w = x_coord(user_rank, fontStyle)
    text_list.append(
        [(802+60-w/2, 1305), user_rank, (0, 0, 0), 1, 80])
    w = x_coord(user_percent, fontStyle)
    text_list.append(
        [(633+60-w/2, 1404), user_percent, (0, 0, 0), 1, 80])
    # dog_tag
    if DOG_TAG:
        if result['dog_tag'] == [] or result['dog_tag'] == {}:
            pass
        else:
            res_img = dog_tag(res_img, result['dog_tag'])

    # 数据总览
    fontStyle = font_list[1][30]
    i = 0
    for index in result['data']['rank']['other']:
        nickname = index['nickname']
        if len(nickname) >= 22:
            nickname_str = nickname[:21] + ' ...'
        else:
            nickname_str = nickname
        rank_num = index['rank_num']
        if rank_num == user_rank and result['nickname'] in nickname:
            bg_png_path = os.path.join(file_path, 'png', 'red.png')
            bg = cv2.imread(bg_png_path, cv2.IMREAD_UNCHANGED)
            x1 = 134
            y1 = 1620 + 67*i
            x2 = x1 + bg.shape[1]
            y2 = y1 + bg.shape[0]
            res_img = merge_img(res_img, bg, y1, y2, x1, x2)
        battles_count = index['battles_count']
        avg_pr = index['personal_rating']
        avg_win = index['win_rate']
        avg_damage = index['damage_dealt']
        avg_frag = index['frag']
        avg_xp = index['exp']
        max_damage = index['max_damage']
        max_exp = index['max_exp']
        max_frag = index['max_frag']
        x0 = 0
        y0 = 1637
        w = x_coord(rank_num, fontStyle)
        text_list.append(
            [(168-w/2, y0 + 67*i), rank_num, (0, 0, 0), 1, 30])
        text_list.append(
            [(220, y0 + 67*i), nickname_str, (0, 0, 0), 1, 30])
        w = x_coord(battles_count, fontStyle)
        text_list.append(
            [(792-w/2, y0 + 67*i), battles_count, (0, 0, 0), 1, 30])
        w = x_coord(avg_pr, fontStyle)
        text_list.append(
            [(919-w/2, y0 + 67*i), avg_pr, number_color_box(index['personal_rating_color']), 1, 30])
        w = x_coord(avg_win, fontStyle)
        text_list.append(
            [(1041-w/2, y0 + 67*i), avg_win, number_color_box(index['win_rate_color']), 1, 30])
        w = x_coord(avg_frag, fontStyle)
        text_list.append(
            [(1197-w/2, y0 + 67*i), avg_frag, number_color_box(index['frag_color']), 1, 30])
        w = x_coord(avg_xp, fontStyle)
        text_list.append(
            [(1360-w/2, y0 + 67*i), avg_xp, (0, 0, 0), 1, 30])
        w = x_coord(avg_damage, fontStyle)
        text_list.append(
            [(1540-w/2, y0 + 67*i), avg_damage, number_color_box(index['damage_dealt_color']), 1, 30])
        w = x_coord(max_frag, fontStyle)
        text_list.append(
            [(1735-w/2, y0 + 67*i), max_frag, (0, 0, 0), 1, 30])
        w = x_coord(max_damage, fontStyle)
        text_list.append(
            [(1949-w/2, y0 + 67*i), max_damage, (0, 0, 0), 1, 30])
        w = x_coord(max_exp, fontStyle)
        text_list.append(
            [(2181-w/2, y0 + 67*i), max_exp, (0, 0, 0), 1, 30])

        i += 1
    fontStyle = font_list[1][80]
    w = x_coord(BOT_VERSON, fontStyle)
    text_list.append(
        [(1214-w/2, 2398), BOT_VERSON, (174, 174, 174), 1, 80])
    if (isinstance(res_img, np.ndarray)):
        res_img = Image.fromarray(
            cv2.cvtColor(res_img, cv2.COLOR_BGR2RGB))
    res_img = add_text(text_list, res_img)
    res_img = res_img.resize((1214, 1259))
    return res_img


async def get_png(
    parameter: list
):
    aid = parameter[0]
    server = parameter[1]
    ship_name = parameter[3]

    try:
        # [aid,server,ship_id,ship_name]
        async with httpx.AsyncClient() as client:
            url = API_URL + '/leaderboard/search/' + \
                f'?token={API_TOKEN}&aid={parameter[0]}&server={parameter[1]}&ship_id={parameter[2]}'
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
        res_img = main(result, aid, ship_name, server)
        res = {'status': 'ok', 'message': 'SUCCESS', 'img': None}
        if PIC_TYPE == 'base64':
            res['img'] = img_to_b64(res_img)
        elif PIC_TYPE == 'file':
            res['img'] = img_to_file(res_img)
        else:
            return {'status': 'info', 'message': '程序内部错误', 'error': 'PIC_TYPE 配置错误!'}
        del res_img
        gc.collect()
        return res
    except (TimeoutException, ConnectTimeout, ReadTimeout):
        return {'status': 'info', 'message': '网络请求超时,请稍后重试'}
    except Exception as e:
        logging.exception(
            f"Time:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}, Parameter:{parameter}")
        return {'status': 'error', 'message': f'程序内部错误,Error:{type(e).__name__}', 'error': str(type(e))}
