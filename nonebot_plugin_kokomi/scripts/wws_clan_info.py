import os
import httpx
import time
import cv2
import numpy as np
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
    color_box,
    merge_img,
    x_coord,
    add_text,
    get_days_difference,
    formate_str
)
from .data_source import (
    font_list,
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
    #
    if result['data']['clans']['info']['cyc_active']:
        cvc_png_path = os.path.join(
            file_path, 'png', 'clan', '{}-{}.png'.format(result['data']['clans']['info']['league'], result['data']['clans']['info']['division']))
    else:
        cvc_png_path = os.path.join(
            file_path, 'png', 'clan', '4-4.png')
    res_img = cv2.imread(os.path.join(
        file_path, 'png', 'background', 'wws_clan.png'), cv2.IMREAD_UNCHANGED)
    cvc_png = cv2.imread(cvc_png_path, cv2.IMREAD_UNCHANGED)
    x1 = 1912
    y1 = 131
    x2 = x1 + cvc_png.shape[1]
    y2 = y1 + cvc_png.shape[0]
    res_img = merge_img(res_img, cvc_png, y1, y2, x1, x2)
    del cvc_png
    division_rating = str(result['data']['clans']['info']['division_rating'])
    w = x_coord(division_rating, fontStyle)
    text_list.append(
        [(2122-w/2, 465), division_rating, (230, 230, 230), 1, 55])

    # 军团建筑
    i = 0
    for build_name, build_data in result['data']['clans']['buildings'].items():
        build_msg = '{} / {} 级'.format(build_data['level'],
                                       build_data['max_level'])
        w = x_coord(build_msg, fontStyle)
        x = 555-w+int(i % 5)*410
        y = 757+int(i/5)*145
        text_list.append([(x, y), build_msg, (0, 0, 0), 1, 55])
        i += 1
    # 工会成就
    cw_ach_data = result['data']['clans']['achievements']
    cw_ach_png = False
    for ach_index in ['0', '1', '2', '3', '4']:
        if cw_ach_data[ach_index] != 0:
            if cw_ach_png != True:
                cw_png = cv2.imread(os.path.join(
                    file_path, 'png', 'cw', f'{ach_index}.png'), cv2.IMREAD_UNCHANGED)
                x1 = 98
                y1 = 1145
                x2 = x1 + cw_png.shape[1]
                y2 = y1 + cw_png.shape[0]
                res_img = merge_img(res_img, cw_png, y1, y2, x1, x2)
                cw_ach_png = True
                del cw_png
            text_list.append([(1125-200*int(ach_index), 1265), 'x' +
                             str(cw_ach_data[ach_index]), (30, 30, 30), 1, 45])
        else:
            continue

    # 工会基础数据
    user_battles_count = str(
        int(result['data']['clans']['statistics']['battles_count']))
    user_win_rate = str(
        round(result['data']['clans']['statistics']['wins_percentage'], 2))+'%'
    user_in_clan = str(result['data']['clans']['info']['members_count']) + \
        ' / ' + str(result['data']['clans']['info']['max_members_count'])
    user_exp = str(int(result['data']['clans']
                   ['statistics']['exp_per_battle']))
    user_damage = str(
        int(result['data']['clans']['statistics']['damage_per_battle']))
    fontStyle = font_list[1][80]
    w = x_coord(user_battles_count, fontStyle)
    text_list.append([(413-w/2, 1515), user_battles_count, (0, 0, 0), 1, 80])
    w = x_coord(user_win_rate, fontStyle)
    text_list.append([(813-w/2, 1515), user_win_rate, (0, 0, 0), 1, 80])
    w = x_coord(user_in_clan, fontStyle)
    text_list.append([(1216-w/2, 1515), user_in_clan, (0, 0, 0), 1, 80])
    w = x_coord(user_exp, fontStyle)
    text_list.append([(1613-w/2, 1515), user_exp, (0, 0, 0), 1, 80])
    w = x_coord(user_damage, fontStyle)
    text_list.append([(2013-w/2, 1515), user_damage, (0, 0, 0), 1, 80])

    # members
    role_list = [
        'commander',
        'executive_officer',
        'recruitment_officer',
        'commissioned_officer',
        'officer',
        'private'
    ]
    sorted_members = []
    for index in role_list:
        for member_data in result['data']['clans']['members']:
            if member_data['role'] == index:
                sorted_members.append(member_data)
            else:
                continue
    i = 0
    fontStyle = font_list[1][35]
    for member_data in sorted_members:
        role = role_dict[member_data['role']]
        w = x_coord(role, fontStyle)
        text_list.append([(264-w/2, 1778.5+70*i+12), role, (0, 0, 0), 1, 35])
        nickname = member_data['name']
        w = x_coord(nickname, fontStyle)
        text_list.append(
            [(403, 1778.5+70*i+12), formate_str(nickname, w, 470), (0, 0, 0), 1, 35])
        if member_data['battles_count'] != None:
            battles_count = str(member_data['battles_count'])
            w = x_coord(battles_count, fontStyle)
            text_list.append(
                [(956-w/2, 1778.5+70*i+12), battles_count, (0, 0, 0), 1, 35])
            win_rate = str(round(member_data['wins_percentage'], 2)) + '%'
            w = x_coord(win_rate, fontStyle)
            text_list.append([(1156-w/2, 1778.5+70*i+12),
                              win_rate, color_box(0, member_data['wins_percentage'])[1], 1, 35])
            exp_per_battle = str(int(member_data['exp_per_battle']))
            w = x_coord(exp_per_battle, fontStyle)
            text_list.append([(1356-w/2, 1778.5+70*i+12),
                             exp_per_battle, (0, 0, 0), 1, 35])
            damage_per_battle = str(int(member_data['damage_per_battle']))
            w = x_coord(damage_per_battle, fontStyle)
            text_list.append([(1555-w/2, 1778.5+70*i+12),
                              damage_per_battle, (0, 0, 0), 1, 35])
            frags_per_battle = str(round(member_data['frags_per_battle'], 2))
            w = x_coord(frags_per_battle, fontStyle)
            text_list.append([(1763-w/2, 1778.5+70*i+12),
                              frags_per_battle, (0, 0, 0), 1, 35])
            days_in_clan = str(member_data['days_in_clan'])
            w = x_coord(days_in_clan, fontStyle)
            text_list.append(
                [(1959-w/2, 1778.5+70*i+12), days_in_clan, (0, 0, 0), 1, 35])
            last_battle_time = str(get_days_difference(
                member_data['last_battle_time']))
            w = x_coord(last_battle_time, fontStyle)
            text_list.append(
                [(2165-w/2, 1778.5+70*i+12), last_battle_time, (0, 0, 0), 1, 35])
        else:
            battles_count = '-'
            w = x_coord(battles_count, fontStyle)
            text_list.append(
                [(956-w/2, 1778.5+70*i+12), battles_count, (0, 0, 0), 1, 35])
            win_rate = '-'
            w = x_coord(win_rate, fontStyle)
            text_list.append([(1156-w/2, 1778.5+70*i+12),
                              win_rate, (0, 0, 0), 1, 35])
            exp_per_battle = '-'
            w = x_coord(exp_per_battle, fontStyle)
            text_list.append([(1356-w/2, 1778.5+70*i+12),
                              exp_per_battle, (0, 0, 0), 1, 35])
            damage_per_battle = '-'
            w = x_coord(damage_per_battle, fontStyle)
            text_list.append([(1555-w/2, 1778.5+70*i+12),
                              damage_per_battle, (0, 0, 0), 1, 35])
            frags_per_battle = '-'
            w = x_coord(frags_per_battle, fontStyle)
            text_list.append([(1763-w/2, 1778.5+70*i+12),
                              frags_per_battle, (0, 0, 0), 1, 35])
            days_in_clan = '-'
            w = x_coord(days_in_clan, fontStyle)
            text_list.append(
                [(1959-w/2, 1778.5+70*i+12), days_in_clan, (0, 0, 0), 1, 35])
            last_battle_time = '-'
            w = x_coord(last_battle_time, fontStyle)
            text_list.append(
                [(2165-w/2, 1778.5+70*i+12), last_battle_time, (0, 0, 0), 1, 35])
        i += 1
    w = x_coord(BOT_VERSON, fontStyle)
    text_list.append(
        [(1214-w/2, 1778.5+70*(i+1)+12), BOT_VERSON, (174, 174, 174), 1, 45])
    if (isinstance(res_img, np.ndarray)):
        res_img = Image.fromarray(
            cv2.cvtColor(res_img, cv2.COLOR_BGR2RGB))
    res_img = add_text(text_list, res_img)
    res_img = res_img.crop((0, 0, 2429, 1778.5+70*(i+2)))
    res_img = res_img.resize((int(2429*0.5), int((1778.5+70*(i+3))*0.5)))
    return res_img


async def get_png(
    parameter: list,
):
    try:
        # [clan_id,server]
        async with httpx.AsyncClient() as client:
            url = API_URL + '/clan/info/' + \
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
