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
    BOT_VERSON,
    LAST_CW_MUNBER
)
from .data_source import (
    img_to_b64,
    img_to_file,
    merge_img,
    x_coord,
    add_text,
    color_box
)
from .data_source import (
    font_list,
    cvc_list,
    cvc_color_list
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
    text_list.append(
        [(602+14-150, 405+38), f'第 22 赛季', (0, 0, 0), 1, 55])
    #
    if result['data']['clans']['info']['cyc_active']:
        cvc_png_path = os.path.join(
            file_path, 'png', 'clan', '{}-{}.png'.format(result['data']['clans']['info']['league'], result['data']['clans']['info']['division']))
    else:
        cvc_png_path = os.path.join(
            file_path, 'png', 'clan', '4-4.png')
    res_img = cv2.imread(os.path.join(
        file_path, 'png', 'background', 'wws_clan_cw_all.png'), cv2.IMREAD_UNCHANGED)
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
    cvc_season = LAST_CW_MUNBER
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
    # cw对局数据
    if (isinstance(res_img, np.ndarray)):
        res_img = Image.fromarray(
            cv2.cvtColor(res_img, cv2.COLOR_BGR2RGB))
    active_num = 0
    time_dict = {
        '1': '08-23',
        '2': '08-24',
        '3': '08-26',
        '4': '08-27',
        '5': '08-30',
        '6': '08-31',
        '7': '09-01',
        '8': '09-02',
        '9': '09-06',
        '10': '09-07',
        '11': '09-09',
        '12': '09-10',
        '13': '09-13',
        '14': '09-14',
        '15': '09-16',
        '16': '09-17',
        '17': '09-20',
        '18': '09-21',
        '19': '09-23',
        '20': '09-24',
        '21': '09-27',
        '22': '09-28',
        '23': '09-30',
        '24': '10-01',
        '25': '10-04',
        '26': '10-05',
        '27': '10-07',
        '28': '10-08'
    }
    for cvc_code, cvc_data in result['data']['clans']['cw'].items():
        str_cvc = f'第 {cvc_code} 天 ( {time_dict[cvc_code]} )'
        text_list.append([(146, 813+408+89*3*active_num),
                         str_cvc, (0, 0, 0), 1, 55])
        i = 0
        for index in ['1', '2']:
            if cvc_data[index] != {} and cvc_data[index]['battles_count'] != 0:
                if cvc_data[index]['data_after_match']['stage'] == None:
                    my_team_rating = cvc_list[cvc_data[index]['data_after_match']['league']] + '  ' + str(
                        rank_list[cvc_data[index]['data_after_match']['division']]) + '  ' + str(cvc_data[index]['data_after_match']['division_rating'])
                else:
                    if cvc_data[index]['data_after_match']['stage']['type'] == 'promotion':
                        my_team_rating = cvc_list[cvc_data[index]
                                                  ['data_after_match']['league']-1] + '晋级赛  '
                    else:
                        my_team_rating = cvc_list[cvc_data[index]
                                                  ['data_after_match']['league']] + '保级赛  '
                    for stage_index in cvc_data[index]['data_after_match']['stage']['progress']:
                        if stage_index == 'victory':
                            my_team_rating += '★'
                        else:
                            my_team_rating += '☆'
                w = x_coord(my_team_rating, fontStyle)
                text_list.append([(884-w/2, 1307+89*(i+3*active_num)), my_team_rating,
                                 cvc_color_list[cvc_data[index]['data_after_match']['league']], 1, 55])
                battles_count = cvc_data[index]['battles_count']
                w = x_coord(str(battles_count), fontStyle)
                text_list.append(
                    [(1435-w/2, 1307+89*(i+3*active_num)), str(battles_count), (0, 0, 0), 1, 55])
                win_rate = str(
                    round(cvc_data[index]['wins']/battles_count*100, 2))+'%'
                w = x_coord(win_rate, fontStyle)
                text_list.append(
                    [(1929-w/2, 1307+89*(i+3*active_num)), win_rate, color_box(0, cvc_data[index]['wins']/battles_count*100)[1], 1, 55])

            else:
                text_list.append(
                    [(884-10, 1307+89*(i+3*active_num)), '-', (0, 0, 0), 1, 55])
                text_list.append(
                    [(1435-10, 1307+89*(i+3*active_num)), '-', (0, 0, 0), 1, 55])
                text_list.append(
                    [(1929-10, 1307+89*(i+3*active_num)), '-', (0, 0, 0), 1, 55])
            i += 1
        active_num += 1

    w = x_coord(BOT_VERSON, fontStyle)
    text_list.append(
        [(1214-w/2, 1307+89*(i+3*active_num)-89*3), BOT_VERSON, (174, 174, 174), 1, 45])
    res_img = add_text(text_list, res_img)
    res_img = res_img.crop((0, 0, 2429, 1307+89*(i+3*active_num)-89*2))
    res_img = res_img.resize(
        (int(2429*0.5), int((1307+89*(i+3*active_num)-89*2)*0.5)))
    return res_img


def id_to_url(
    clan_id: str
) -> str:
    if len(clan_id) == 10 and clan_id[0] == '1':
        return 'NA'
    if len(clan_id) == 10 and clan_id[0] == '2':
        return 'ASIA'
    if len(clan_id) == 9 and clan_id[0] == '5':
        return 'EU'
    if len(clan_id) == 10 and clan_id[0] == '7':
        return 'CN'
    return None


async def get_png(
    parameter: list,
):
    try:
        # [clan_id,server]
        if parameter[1] == 'ru':
            return {'status': 'info', 'message': '暂时不支持俄服的数据'}
        async with httpx.AsyncClient() as client:
            url = API_URL + '/clan/cw2/' + \
                f'?token={API_TOKEN}&clan_id={parameter[0]}&server={parameter[1]}'
            res = await client.get(url, timeout=REQUEST_TIMEOUT)
            requset_code = res.status_code
            result = res.json()
            if requset_code == 200:
                pass
            else:
                return {'status': 'info', 'message': '数据接口请求失败'}
        if result['status'] != 'ok':
            return result
        if result['data']['clans']['info']['cyc_active'] == False or result['data']['clans']['cw'] == {}:
            return {'status': 'info', 'message': '未有该赛季的数据'}
        res_img = main(
            result=result,
            clan_id=parameter[0],
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
