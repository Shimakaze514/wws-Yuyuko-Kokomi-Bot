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
    add_text
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
    cw_code: str,
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
        [(602+14-150, 405+38), f'第 22 赛季  |  第 {cw_code} 天', (0, 0, 0), 1, 55])
    #
    if result['data']['clans']['info']['cyc_active']:
        cvc_png_path = os.path.join(
            file_path, 'png', 'clan', '{}-{}.png'.format(result['data']['clans']['info']['league'], result['data']['clans']['info']['division']))
    else:
        cvc_png_path = os.path.join(
            file_path, 'png', 'clan', '4-4.png')
    res_img = cv2.imread(os.path.join(
        file_path, 'png', 'background', 'wws_clan_cw_day.png'), cv2.IMREAD_UNCHANGED)
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
    temp_result = {
        '1': {},
        '2': {}
    }

    # cw对局数据
    if (isinstance(res_img, np.ndarray)):
        res_img = Image.fromarray(
            cv2.cvtColor(res_img, cv2.COLOR_BGR2RGB))
    i = 0
    match_result = ImageDraw.ImageDraw(res_img)
    for match_time, match_data in result['data']['clans']['cw'].items():
        time_str = time.strftime(
            '%Y-%m-%d %H:%M:%S', time.localtime(int(match_time)))
        text_list.append(
            [(1036, 1272+130*i), time_str, (154, 154, 154), 1, 35])
        # my team
        team_number = match_data['my_clan'][0]['match_info']['team_number']
        if temp_result[team_number] == {}:
            temp_result[team_number] = {
                'battles_count': 0,
                'wins': 0,
                'battle_result': '0',
                'data_after_match': {}
            }
        temp_result[team_number]['battles_count'] += 1
        if match_data['my_clan'][0]['match_info']['result'] == 'victory':
            temp_result[team_number]['wins'] += 1
            temp_result[team_number]['battle_result'] += '1'
        else:
            temp_result[team_number]['battle_result'] += '0'
        temp_result[team_number]['data_after_match'] = match_data['my_clan'][0]['data_after_match']

        clan_tag = result['data']['clans']['tag']
        my_team_tag = '[' + \
            str(clan_tag[match_data['my_clan'][0]['clan_id']]) + ']'
        my_team_num = 'Alpha' if match_data['my_clan'][0]['match_info']['team_number'] == '1' else 'Bravo'
        my_team_result_color = (
            96, 185, 96) if match_data['my_clan'][0]['match_info']['result'] == 'victory' else (228, 15, 39)
        if match_data['my_clan'][0]['data_after_match']['stage'] == None:
            my_team_rating = cvc_list[match_data['my_clan'][0]['data_after_match']['league']] + '  ' + str(
                rank_list[match_data['my_clan'][0]['data_after_match']['division']]) + '  ' + str(match_data['my_clan'][0]['data_after_match']['division_rating'])
            div_rating = '+' if match_data['my_clan'][0]['match_info']['rating'] >= 0 else ''
            div_rating += str(match_data['my_clan'][0]['match_info']['rating'])
        else:
            if match_data['my_clan'][0]['data_after_match']['stage']['type'] == 'promotion':
                my_team_rating = cvc_list[match_data['my_clan'][0]
                                          ['data_after_match']['league']-1] + '晋级赛  '
            else:
                my_team_rating = cvc_list[match_data['my_clan'][0]
                                          ['data_after_match']['league']] + '保级赛  '
            last_battle = None
            for stage_index in match_data['my_clan'][0]['data_after_match']['stage']['progress']:
                if stage_index == 'victory':
                    my_team_rating += '★'
                    last_battle = '★'
                else:
                    my_team_rating += '☆'
                    last_battle = '☆'
            if match_data['my_clan'][0]['data_after_match']['stage']['progress'] == []:
                div_rating = '+' if match_data['my_clan'][0]['match_info']['rating'] >= 0 else ''
                div_rating += str(match_data['my_clan']
                                  [0]['match_info']['rating'])
            else:
                div_rating = last_battle
        match_result.rectangle(
            ((1214, 1209+130*i), (1216, 1273+130*i)), fill=(180, 180, 180), outline=None)
        match_result.rectangle(
            ((123, 1198+130*i), (148, 1318+130*i)), fill=my_team_result_color, outline=None)
        text_list.append([(176, 1205+130*i), my_team_tag,
                         cvc_color_list[match_data['my_clan'][0]['data_after_match']['league']], 1, 50])
        my_clan_info = my_team_num + '  ' + \
            my_team_rating + '  ('+div_rating+')'
        text_list.append(
            [(176, 1262+130*i), my_clan_info, (27, 27, 27), 1, 45])
        clan_server = id_to_url(match_data['my_clan'][0]['clan_id'])
        fontStyle = font_list[1][45]
        w = x_coord(clan_server, fontStyle)
        text_list.append(
            [(1195-w, 1221+130*i), clan_server, (154, 154, 154), 1, 45])
        # emeny team
        if len(match_data['emeny_clan']) != 1:
            text_list.append(
                [(1900, 1240+130*i), '未统计到对局数据', (27, 27, 27), 1, 45])
        else:
            emeny_team_tag = '[' + \
                str(clan_tag[match_data['emeny_clan'][0]['clan_id']]) + ']'
            emeny_team_num = 'Alpha' if match_data['emeny_clan'][
                0]['match_info']['team_number'] == '1' else 'Bravo'
            emeny_team_result_color = (
                96, 185, 96) if match_data['emeny_clan'][0]['match_info']['result'] == 'victory' else (228, 15, 39)
            if match_data['emeny_clan'][0]['data_after_match']['stage'] == None:
                emeny_team_rating = cvc_list[match_data['emeny_clan'][0]['data_after_match']['league']] + '  ' + str(
                    rank_list[match_data['emeny_clan'][0]['data_after_match']['division']]) + '  ' + str(match_data['emeny_clan'][0]['data_after_match']['division_rating'])
                div_rating = '+' if match_data['emeny_clan'][0]['match_info']['rating'] >= 0 else ''
                div_rating += str(
                    match_data['emeny_clan'][0]['match_info']['rating'])
            else:
                if match_data['emeny_clan'][0]['data_after_match']['stage']['type'] == 'promotion':
                    emeny_team_rating = cvc_list[match_data['emeny_clan'][0]
                                                 ['data_after_match']['league']-1] + '晋级赛  '
                else:
                    emeny_team_rating = cvc_list[match_data['emeny_clan'][0]
                                                 ['data_after_match']['league']] + '保级赛  '
                last_battle = None
                for stage_index in match_data['emeny_clan'][0]['data_after_match']['stage']['progress']:
                    if stage_index == 'victory':
                        emeny_team_rating += '★'
                        last_battle = '★'
                    else:
                        emeny_team_rating += '☆'
                        last_battle = '☆'
                if match_data['emeny_clan'][0]['data_after_match']['stage']['progress'] == []:
                    div_rating = '+' if match_data['emeny_clan'][0]['match_info']['rating'] >= 0 else ''
                    div_rating += str(
                        match_data['emeny_clan'][0]['match_info']['rating'])
                else:
                    div_rating = last_battle
            match_result.rectangle(
                ((2282, 1198+130*i), (2307, 1318+130*i)), fill=emeny_team_result_color, outline=None)
            fontStyle = font_list[1][50]
            w = x_coord(emeny_team_tag, fontStyle)
            text_list.append([(2252-w, 1205+130*i), emeny_team_tag,
                             cvc_color_list[match_data['emeny_clan'][0]['data_after_match']['league']], 1, 50])
            emeny_clan_info = '('+div_rating+')  ' + \
                emeny_team_rating + '  ' + emeny_team_num
            fontStyle = font_list[1][45]
            w = x_coord(emeny_clan_info, fontStyle)
            text_list.append(
                [(2252-w, 1262+130*i), emeny_clan_info, (27, 27, 27), 1, 45])
            clan_server = id_to_url(match_data['emeny_clan'][0]['clan_id'])
            text_list.append(
                [(1235, 1221+130*i), clan_server, (154, 154, 154), 1, 45])
        i += 1
    crop_i = i
    # cw
    i = 0
    fontStyle = font_list[1][55]
    for index in ['1', '2']:
        if temp_result[index] != {} and temp_result[index]['battles_count'] != 0:
            if temp_result[index]['data_after_match']['stage'] == None:
                my_team_rating = cvc_list[temp_result[index]['data_after_match']['league']] + '  ' + str(
                    rank_list[temp_result[index]['data_after_match']['division']]) + '  ' + str(temp_result[index]['data_after_match']['division_rating'])
            else:
                if temp_result[index]['data_after_match']['stage']['type'] == 'promotion':
                    my_team_rating = cvc_list[temp_result[index]
                                              ['data_after_match']['league']-1] + '晋级赛  '
                else:
                    my_team_rating = cvc_list[temp_result[index]
                                              ['data_after_match']['league']] + '保级赛  '
                for stage_index in temp_result[index]['data_after_match']['stage']['progress']:
                    if stage_index == 'victory':
                        my_team_rating += '★'
                    else:
                        my_team_rating += '☆'
            w = x_coord(my_team_rating, fontStyle)
            text_list.append([(781-w/2, 810+89*i), my_team_rating,
                             cvc_color_list[temp_result[index]['data_after_match']['league']], 1, 55])
            battles_count = temp_result[index]['battles_count']
            w = x_coord(str(battles_count), fontStyle)
            text_list.append(
                [(1160-w/2, 810+89*i), str(battles_count), (0, 0, 0), 1, 55])
            win_rate = str(
                round(temp_result[index]['wins']/battles_count*100, 2))+'%'
            w = x_coord(win_rate, fontStyle)
            text_list.append(
                [(1570-w/2, 810+89*i), win_rate, (0, 0, 0), 1, 55])
            longest_winning_streak = str(get_longest_ones_length(
                temp_result[index]['battle_result']))
            w = x_coord(longest_winning_streak, fontStyle)
            text_list.append(
                [(2002-w/2, 810+89*i), longest_winning_streak, (0, 0, 0), 1, 55])
        else:
            text_list.append([(781-10, 810+89*i), '-', (0, 0, 0), 1, 55])
            text_list.append([(1160-10, 810+89*i), '-', (0, 0, 0), 1, 55])
            text_list.append([(1570-10, 810+89*i), '-', (0, 0, 0), 1, 55])
            text_list.append([(2002-10, 810+89*i), '-', (0, 0, 0), 1, 55])
        i += 1
    fontStyle = font_list[1][80]
    notice = '特别注意：由于数据统计算法问题，存在统计错误或者未统计到数据，本数据【仅供参考】!'
    text_list.append(
        [(300, 1220+130*crop_i+1+12), notice, (44, 44, 44), 1, 45])
    w = x_coord(BOT_VERSON, fontStyle)
    text_list.append(
        [(1214-w/2, 1200+130*(crop_i+1)+12), BOT_VERSON, (174, 174, 174), 1, 80])
    res_img = add_text(text_list, res_img)
    res_img = res_img.crop((0, 0, 2429, 1260+130*(crop_i+2)))
    res_img = res_img.resize((int(2429*0.5), int((1260+130*(crop_i+2))*0.5)))
    return res_img


def get_longest_ones_length(s):
    max_len = 0
    cur_len = 0
    for char in s:
        if char == '1':
            cur_len += 1
        elif char == '0':
            max_len = max(max_len, cur_len)
            cur_len = 0

    max_len = max(max_len, cur_len)
    return max_len


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
        # [clan_id,cw_code,server]
        if parameter[2] == 'ru':
            return {'status': 'info', 'message': '暂时不支持俄服的数据'}
        async with httpx.AsyncClient() as client:
            url = API_URL + '/clan/cw/' + \
                f'?token={API_TOKEN}&clan_id={parameter[0]}&cw_code={parameter[1]}&server={parameter[2]}'
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
            cw_code=parameter[1],
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
