import os
import time
import httpx
import logging
from PIL import Image
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
    number_color_box,
    x_coord,
    add_text
)
from .data_source import (
    font_list
)
file_path = os.path.dirname(__file__)
# 配置日志输出到文件
logging.basicConfig(filename=os.path.join(
    file_path, 'log', 'error.log'), level=logging.ERROR)


def main(
    result,
    ship_name,
    server
):
    text_list = []
    fontStyle = font_list[1][55]
    res_img = Image.open(os.path.join(
        file_path, 'png', 'background', 'wws_server_rank.png'))
    ship_name = ship_name + f'    ({server.upper()})'
    w = x_coord(ship_name, fontStyle)
    text_list.append(
        [(1214-w/2, 151), ship_name, (0, 0, 0), 1, 70])
    # 数据总览
    fontStyle = font_list[1][30]
    i = 0
    for index in result['data']['rank']:
        nickname = index['nickname']
        if len(nickname) >= 22:
            nickname = nickname[:21] + ' ...'
        rank_num = index['rank_num']
        battles_count = index['battles_count']
        avg_pr = index['personal_rating']
        avg_win = index['win_rate']
        avg_damage = index['damage_dealt']
        avg_frag = index['frag']
        avg_xp = index['exp']
        max_damage = index['max_damage']
        max_exp = index['max_exp']
        max_frag = index['max_frag']
        y0 = 485
        w = x_coord(rank_num, fontStyle)
        text_list.append(
            [(168-w/2, y0 + 67*i), rank_num, (0, 0, 0), 1, 30])
        text_list.append(
            [(220, y0 + 67*i), nickname, (0, 0, 0), 1, 30])
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
        [(1214-w/2, 3969), BOT_VERSON, (174, 174, 174), 1, 80])
    res_img = add_text(text_list, res_img)
    res_img = res_img.resize((1214, 2045))
    return res_img


async def get_png(
    parameter: list
):
    server = parameter[0]
    ship_name = parameter[2]

    try:
        async with httpx.AsyncClient() as client:
            url = API_URL + '/leaderboard/server/' + \
                f'?token={API_TOKEN}&server={parameter[0]}&ship_id={parameter[1]}'
            res = await client.get(url, timeout=REQUEST_TIMEOUT)
            requset_code = res.status_code
            result = res.json()
            if requset_code == 200:
                pass
            else:
                return {'status': 'info', 'message': '数据接口请求失败'}
        if result['status'] != 'ok':
            return result
        res_img = main(result, ship_name, server)
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
        return {'status': 'error', 'message': f'程序内部错误', 'error': str(type(e))}
