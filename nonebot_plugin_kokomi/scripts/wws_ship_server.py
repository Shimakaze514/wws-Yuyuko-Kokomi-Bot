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
    result: dict,
    select: str
):
    text_list = []
    res_img = Image.open(os.path.join(
        file_path, 'png', 'background', 'wws_ship_servers.png'))
    ship_name_file_path = os.path.join(
        parent_file_path, 'json', 'ship_name.json')
    temp = open(ship_name_file_path, "r", encoding="utf-8")
    ship_name_data = json.load(temp)
    temp.close()
    # 船只数据
    ships_dmg_list = {}
    for ship_id, ship_data in result['data']['ships'].items():
        if ship_data == {}:
            continue
        else:
            ships_dmg_list[ship_id] = ship_data['average_damage_dealt']
    sorts_dmg_list = sorted(ships_dmg_list.items(),
                            key=lambda x: x[1], reverse=True)
    # 中间插一个筛选条件
    # select
    select_tier = f'{select[0]}'
    select_type = f'{select[1]}'
    select_nation = f'{select[2]}'
    select_num = str(len(sorts_dmg_list))
    fontStyle = font_list[1][55]
    w = x_coord(select_tier, fontStyle)
    text_list.append(
        [(1485-w/2, 595-50), select_tier, (0, 0, 0), 1, 55])
    w = x_coord(select_type, fontStyle)
    text_list.append(
        [(985-w/2, 595-50), select_type, (0, 0, 0), 1, 55])
    w = x_coord(select_nation, fontStyle)
    text_list.append(
        [(421-w/2, 595-50), select_nation, (0, 0, 0), 1, 55])
    w = x_coord(select_num, fontStyle)
    text_list.append(
        [(2010-w/2, 595-50), select_num, (0, 0, 0), 1, 55])
    i = 0
    for ship_id, ship_pr in sorts_dmg_list:
        x0 = 0
        y0 = 2101-1164-50
        if i >= 150:
            overflow_warming = '最多只能显示150条船只的数据'
            w = x_coord(overflow_warming, fontStyle)
            text_list.append(
                [(1214-w/2+x0, y0+90*i), overflow_warming, (160, 160, 160), 1, 50])
            break
        ship_name = ship_name_data[ship_id]['ship_name']['zh_sg']
        ship_tier = a_tier_dict[ship_name_data[ship_id]['tier']]
        ship_type = a_type_dict[ship_name_data[ship_id]['type']]
        win_rate = str(result['data']['ships'][ship_id]['win_rate']) + '%'
        average_damage_dealt = str(
            result['data']['ships'][ship_id]['average_damage_dealt'])
        average_frags = str(result['data']['ships'][ship_id]['average_frags'])

        fontStyle = font_list[1][50]
        w = x_coord(ship_name, fontStyle)
        text_list.append(
            [(369-w/2, y0+89*i), ship_name, (0, 0, 0), 1, 50])
        w = x_coord(ship_tier, fontStyle)
        text_list.append(
            [(751-w/2, y0+89*i), ship_tier, (0, 0, 0), 1, 50])
        w = x_coord(ship_type, fontStyle)
        text_list.append(
            [(1045-w/2, y0+89*i), ship_type, (0, 0, 0), 1, 50])
        w = x_coord(win_rate, fontStyle)
        text_list.append(
            [(1391-w/2, y0+89*i), win_rate, (0, 0, 0), 1, 50])
        w = x_coord(average_damage_dealt, fontStyle)
        text_list.append(
            [(1737-w/2, y0+89*i), average_damage_dealt, (0, 0, 0), 1, 50])
        w = x_coord(average_frags, fontStyle)
        text_list.append(
            [(2087-w/2, y0+89*i), average_frags, (0, 0, 0), 1, 50])
        i += 1

    w = x_coord(BOT_VERSON, fontStyle)
    text_list.append(
        [(1214-w/2, 923-50+89*(i+1)+14), BOT_VERSON, (174, 174, 174), 1, 50])
    res_img = add_text(text_list, res_img)
    res_img = res_img.crop((0, 0, 2429, 923-50+90*(i+2)))
    res_img = res_img.resize((int(2429*0.5), int((923-50+90*(i+2))*0.5)))

    return res_img


async def get_png(
    parameter: list
):
    select = parameter[0]

    try:
        # [select,]
        async with httpx.AsyncClient() as client:
            url = API_URL + '/server/ships/' + \
                f'?token={API_TOKEN}&select={parameter[0]}'
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
            result,
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
        return {'status': 'error', 'message': f'程序内部错误', 'error': str(type(e))}
