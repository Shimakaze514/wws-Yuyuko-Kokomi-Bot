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
    REQUEST_TIMEOUT,
    API_URL,
    API_TOKEN,
    PIC_TYPE,
    BOT_VERSON
)
from .data_source import (
    img_to_b64,
    img_to_file,
    color_box,
    merge_img,
    x_coord,
    add_text,
    get_days_difference,
    formate_str
)
from .data_source import (
    font_list,
    cvc_list,
    cvc_color_list,
    role_dict
)
import logging
file_path = os.path.dirname(__file__)
# 配置日志输出到文件
logging.basicConfig(filename=os.path.join(
    file_path, 'log', 'error.log'), level=logging.ERROR)


def main(
    result: dict,
    clan_id: str,
    cvc_season: str,
    server: str
):
    text_list = []
    # Id卡
    text_list.append(
        [(158+14, 123+38), result['data']['clans']['info']['tag'], (0, 0, 0), 1, 100])
    text_list.append(
        [(185+14, 237+38), f'{server.upper()} -- {clan_id}', (163, 163, 163), 1, 45])

    fontStyle = font_list[1][55]
    clan_name = result['data']['clans']['info']['name']
    w = x_coord(clan_name, fontStyle)
    if w >= 1300:
        clan_name = clan_name[:int(1300/w*len(clan_name))-2] + ' ...'
    text_list.append([(602+14-150, 317+38), clan_name, (0, 0, 0), 1, 55])
    text_list.append(
        [(602+14-150, 405+38), f'第 {cvc_season} 赛季', (0, 0, 0), 1, 55])
    #
    if result['data']['clans']['info']['cyc_active']:
        cvc_png_path = os.path.join(
            file_path, 'png', 'clan', '{}-{}.png'.format(result['data']['clans']['info']['league'], result['data']['clans']['info']['division']))
    else:
        cvc_png_path = os.path.join(
            file_path, 'png', 'clan', '4-4.png')
    res_img = cv2.imread(os.path.join(
        file_path, 'png', 'background', 'wws_clan_season.png'), cv2.IMREAD_UNCHANGED)
    cvc_png = cv2.imread(cvc_png_path, cv2.IMREAD_UNCHANGED)
    x1 = 1912
    y1 = 131
    x2 = x1 + cvc_png.shape[1]
    y2 = y1 + cvc_png.shape[0]
    res_img = merge_img(res_img, cvc_png, y1, y2, x1, x2)
    division_rating = str(result['data']['clans']['info']['division_rating'])
    w = x_coord(division_rating, fontStyle)
    text_list.append(
        [(2122-w/2, 465), division_rating, (230, 230, 230), 1, 55])
    if cvc_season not in result['data']['clans']['season']:
        return {'status': 'info', 'message': '当前赛季无数据'}
    # cw数据
    rank_list = {
        1: 'I',
        2: 'II',
        3: 'III'
    }
    i = 0
    for index in ['1', '2']:
        if result['data']['clans']['season'][cvc_season][index] != {} and result['data']['clans']['season'][cvc_season][index]['battles_count'] != 0:
            max_rank = cvc_list[result['data']['clans']['season'][cvc_season][index]['league']] + '  ' + str(
                rank_list[result['data']['clans']['season'][cvc_season][index]['division']]) + '  ' + str(result['data']['clans']['season'][cvc_season][index]['division_rating'])
            w = x_coord(max_rank, fontStyle)
            text_list.append([(781-w/2, 810+89*i), max_rank, cvc_color_list[result['data']
                             ['clans']['season'][cvc_season][index]['league']], 1, 55])
            battles_count = result['data']['clans']['season'][cvc_season][index]['battles_count']
            w = x_coord(str(battles_count), fontStyle)
            text_list.append(
                [(1160-w/2, 810+89*i), str(battles_count), (0, 0, 0), 1, 55])
            win_rate = str(round(result['data']['clans']['season']
                           [cvc_season][index]['wins_count']/battles_count*100, 2))+'%'
            w = x_coord(win_rate, fontStyle)
            text_list.append(
                [(1570-w/2, 810+89*i), win_rate, (0, 0, 0), 1, 55])
            longest_winning_streak = str(
                result['data']['clans']['season'][cvc_season][index]['longest_winning_streak'])
            w = x_coord(longest_winning_streak, fontStyle)
            text_list.append(
                [(2002-w/2, 810+89*i), longest_winning_streak, (0, 0, 0), 1, 55])
        else:
            text_list.append([(781-w/2, 810+89*i), '-', (0, 0, 0), 1, 55])
            text_list.append([(1160-w/2, 810+89*i), '-', (0, 0, 0), 1, 55])
            text_list.append([(1570-w/2, 810+89*i), '-', (0, 0, 0), 1, 55])
            text_list.append([(2002-w/2, 810+89*i), '-', (0, 0, 0), 1, 55])
        i += 1

    filtered_members = [member for member in result['data']
                        ['clans']["members"] if member["battles_count"] is not None]
    sorted_members = sorted(
        filtered_members, key=lambda member: member["battles_count"], reverse=True)
    i = 0
    fontStyle = font_list[1][35]
    for member_data in sorted_members:
        battles_count = str(member_data['battles_count'])
        if battles_count == '0':
            continue
        w = x_coord(battles_count, fontStyle)
        text_list.append(
            [(1096-w/2, 1197.5+70*i+12), battles_count, (0, 0, 0), 1, 35])
        role = role_dict[member_data['role']]
        w = x_coord(role, fontStyle)
        text_list.append([(264-w/2, 1197.5+70*i+12), role, (0, 0, 0), 1, 35])
        nickname = member_data['name']
        w = x_coord(nickname, fontStyle)
        text_list.append(
            [(440, 1197.5+70*i+12), formate_str(nickname, w, 600), (0, 0, 0), 1, 35])
        win_rate = str(round(member_data['wins_percentage'], 2)) + '%'
        w = x_coord(win_rate, fontStyle)
        text_list.append([(1441-w/2, 1197.5+70*i+12),
                         win_rate, color_box(0, member_data['wins_percentage'])[1], 1, 35])
        days_in_clan = str(member_data['days_in_clan'])
        w = x_coord(days_in_clan, fontStyle)
        text_list.append(
            [(1790-w/2, 1197.5+70*i+12), days_in_clan, (0, 0, 0), 1, 35])
        last_battle_time = str(get_days_difference(
            member_data['last_battle_time']))
        w = x_coord(last_battle_time, fontStyle)
        text_list.append(
            [(2125-w/2, 1197.5+70*i+12), last_battle_time, (0, 0, 0), 1, 35])
        i += 1
    w = x_coord(BOT_VERSON, fontStyle)
    text_list.append(
        [(1214-w/2, 1197.5+70*(i+1)+12), BOT_VERSON, (174, 174, 174), 1, 45])
    if (isinstance(res_img, np.ndarray)):
        res_img = Image.fromarray(
            cv2.cvtColor(res_img, cv2.COLOR_BGR2RGB))
    res_img = add_text(text_list, res_img)
    res_img = res_img.crop((0, 0, 2429, 1197.5+70*(i+2)))
    res_img = res_img.resize((int(2429*0.5), int((1197.5+70*(i+2))*0.5)))
    return res_img


async def get_png(
    parameter: list,
):
    try:
        # [clan_id,season,server]
        async with httpx.AsyncClient() as client:
            url = API_URL + '/clan/cvc/' + \
                f'?token={API_TOKEN}&clan_id={parameter[0]}&cvc_season={parameter[1]}&server={parameter[2]}'
            res = await client.get(url, timeout=REQUEST_TIMEOUT)
            requset_code = res.status_code
            result = res.json()
            if requset_code == 200:
                pass
            else:
                return {'status': 'info', 'message': '数据接口请求失败'}
        if result['status'] != 'ok':
            return result
        if result['data']['clans']['info']['cyc_active'] == False:
            return {'status': 'info', 'message': '未有该赛季的数据'}
        res_img = main(
            result=result,
            clan_id=parameter[0],
            cvc_season=parameter[1],
            server=parameter[2]
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
        return {'status': 'error', 'message': f'程序内部错误,Error:{type(e).__name__}', 'error': str(type(e))}
