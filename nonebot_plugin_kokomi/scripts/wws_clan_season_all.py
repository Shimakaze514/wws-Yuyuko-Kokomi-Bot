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
    x_coord,
    add_text
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
    creat_time = result['data']['clans']['info']['created_at']
    text_list.append(
        [(602+14-150, 405+38), creat_time[:19], (0, 0, 0), 1, 55])

    res_img = Image.open(os.path.join(
        file_path, 'png', 'background', 'wws_clan_season_all.png'))
    division_rating = str(result['data']['clans']['info']['division_rating'])
    w = x_coord(division_rating, fontStyle)
    text_list.append(
        [(2122-w/2, 465), division_rating, (230, 230, 230), 1, 55])
    if result['data']['clans']['season'] == []:
        return {'status': 'info', 'message': '无赛季数据'}
    # cw数据
    rank_list = {
        1: 'Ⅰ',
        2: 'Ⅱ',
        3: 'Ⅲ'
    }
    active_num = 0
    for cvc_season, season_data in result['data']['clans']['season'].items():
        str_cvc = f'-- 第 {cvc_season} 赛季 -- '
        text_list.append([(146, 813+89*3*active_num),
                         str_cvc, (0, 0, 0), 1, 55])
        i = 0
        for index in ['1', '2']:
            if season_data[index] != {} and season_data[index]['battles_count'] != 0:
                max_rank = cvc_list[season_data[index]['league']] + '  ' + str(
                    rank_list[season_data[index]['division']]) + '  ' + str(season_data[index]['division_rating'])
                w = x_coord(max_rank, fontStyle)
                text_list.append([(781-w/2, 899+89*(i+3*active_num)), max_rank, cvc_color_list[result['data']
                                                                                               ['clans']['season'][cvc_season][index]['league']], 1, 55])
                battles_count = season_data[index]['battles_count']
                w = x_coord(str(battles_count), fontStyle)
                text_list.append(
                    [(1160-w/2, 899+89*(i+3*active_num)), str(battles_count), (0, 0, 0), 1, 55])
                win_rate = str(round(result['data']['clans']['season']
                                     [cvc_season][index]['wins_count']/battles_count*100, 2))+'%'
                w = x_coord(win_rate, fontStyle)
                text_list.append(
                    [(1570-w/2, 899+89*(i+3*active_num)), win_rate, color_box(0, result['data']['clans']['season']
                                                                              [cvc_season][index]['wins_count']/battles_count*100)[1], 1, 55])
                longest_winning_streak = str(
                    season_data[index]['longest_winning_streak'])
                w = x_coord(longest_winning_streak, fontStyle)
                text_list.append(
                    [(2002-w/2, 899+89*(i+3*active_num)), longest_winning_streak, (0, 0, 0), 1, 55])
            else:
                text_list.append(
                    [(781-w/2, 899+89*(i+3*active_num)), '-', (0, 0, 0), 1, 55])
                text_list.append(
                    [(1160-w/2, 899+89*(i+3*active_num)), '-', (0, 0, 0), 1, 55])
                text_list.append(
                    [(1570-w/2, 899+89*(i+3*active_num)), '-', (0, 0, 0), 1, 55])
                text_list.append(
                    [(2002-w/2, 899+89*(i+3*active_num)), '-', (0, 0, 0), 1, 55])
            i += 1
        active_num += 1

    w = x_coord(BOT_VERSON, fontStyle)
    text_list.append(
        [(1214-w/2, 899+89*(i+3*active_num)-89*3), BOT_VERSON, (174, 174, 174), 1, 45])
    res_img = add_text(text_list, res_img)
    res_img = res_img.crop((0, 0, 2429, 899+89*(i+3*active_num)-89*2))
    res_img = res_img.resize(
        (int(2429*0.5), int((899+89*(i+3*active_num)-89*2)*0.5)))
    return res_img


async def get_png(
    parameter: list,
):
    try:
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
        res_img = main(
            result=result,
            clan_id=parameter[0],
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
