import json
import os
import httpx
import logging
import time
from PIL import Image
import platform
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
    pr_info,
    color_box,
    merge_img,
    x_coord,
    add_text
)
from .data_source import (
    a_tier_dict,
    a_type_dict,
    font_list
)

file_path = os.path.dirname(__file__)
parent_file_path = os.path.dirname(os.path.dirname(__file__))
isWin = True if platform.system().lower() == 'windows' else False
# 配置日志输出到文件
logging.basicConfig(filename=os.path.join(
    file_path, 'log', 'error.log'), level=logging.ERROR)


def main(
    select: str
):
    text_list = []
    res_img = Image.open(os.path.join(
        file_path, 'png', 'background', 'wws_ship_info.png'))
    ship_name_file_path = os.path.join(
        parent_file_path, 'json', 'ship_name.json')
    temp = open(ship_name_file_path, "r", encoding="utf-8")
    ship_name_data = json.load(temp)
    temp.close()
    # 船只数据
    ships_tier_list = {}
    for ship_id, ship_data in ship_name_data.items():
        if (
            (select[0] == [] or ship_name_data[ship_id]['tier'] in select[0]) and
            (select[1] == [] or ship_name_data[ship_id]['type'] in select[1]) and
            (select[2] == [] or ship_name_data[ship_id]['nation'] in select[2])
        ):
            ships_tier_list[ship_id] = ship_name_data[ship_id]['tier']
    sorts_tier_list = sorted(ships_tier_list.items(),
                             key=lambda x: x[1], reverse=True)
    i = 0
    for ship_id, ship_pr in sorts_tier_list:
        x0 = 0
        y0 = 2101-1164-375-50
        if i >= 150:
            overflow_warming = '最多只能显示150条船只的数据'
            w = x_coord(overflow_warming, fontStyle)
            text_list.append(
                [(1214-w/2, y0+90*i), overflow_warming, (160, 160, 160), 1, 50])
            break
        ship_name_zh = ship_name_data[ship_id]['ship_name']['zh_sg']
        if '[' in ship_name_zh and ']' in ship_name_zh:
            continue
        ship_name_en = ship_name_data[ship_id]['ship_name']['en']
        ship_name_nick = str(ship_name_data[ship_id]['ship_name']['nick'][:4])
        ship_tier = a_tier_dict[ship_name_data[ship_id]['tier']]
        ship_type = a_type_dict[ship_name_data[ship_id]['type']]
        ship_nation = ship_name_data[ship_id]['nation']

        fontStyle = font_list[1][50]

        w = x_coord(ship_tier, fontStyle)
        text_list.append(
            [(251-w/2, y0+89*i), ship_tier, (0, 0, 0), 1, 45])
        w = x_coord(ship_type, fontStyle)
        text_list.append(
            [(405-w/2, y0+89*i), ship_type, (0, 0, 0), 1, 45])
        w = x_coord(ship_nation, fontStyle)
        text_list.append(
            [(654-w/2, y0+89*i), ship_nation, (0, 0, 0), 1, 45])
        text_list.append(
            [(863, y0+89*i), ship_name_zh, (0, 0, 0), 1, 45])
        text_list.append(
            [(1315, y0+89*i), ship_name_en, (0, 0, 0), 1, 45])
        if ship_name_nick != '[]':
            text_list.append(
                [(1710, y0+89*i), ship_name_nick.replace('\'', ''), (0, 0, 0), 1, 35])

        i += 1

    w = x_coord(BOT_VERSON, fontStyle)
    text_list.append(
        [(1214-w/2, 548-50+89*(i+1)+14), BOT_VERSON, (174, 174, 174), 1, 50])
    res_img = add_text(text_list, res_img)
    res_img = res_img.crop((0, 0, 2429, 548-50+90*(i+2)))
    res_img = res_img.resize((int(2429*0.5), int((548-50+90*(i+2))*0.5)))

    return res_img


async def get_png(
    parameter: list
):
    select = parameter[0]

    try:
        # [select,]
        res_img = main(
            select
        )
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
