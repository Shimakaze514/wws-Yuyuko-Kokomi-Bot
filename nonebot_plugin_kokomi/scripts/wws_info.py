import json
import os
import httpx
import time
import cv2
import numpy as np
import random
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
    PIC_TYPE
)
from .data_source import (
    img_to_b64,
    img_to_file,
    pr_info,
    color_box,
    merge_img,
    x_coord,
    add_text,
    add_box
)
from .data_source import (
    font_list,
    clan_color,
    a_tier_dict
)
import logging

file_path = os.path.dirname(__file__)
parent_file_path = os.path.dirname(os.path.dirname(__file__))
# 配置日志输出到文件
logging.basicConfig(filename=os.path.join(
    file_path, 'log', 'error.log'), level=logging.ERROR)


def main(
    result: dict,
    aid: str,
    server: str,
    use_pr: bool
):
    text_list = []
    box_list = []
    image_list = os.listdir(os.path.join(
        file_path, 'png', 'background_info'))
    random_image = random.choice(image_list)
    res_img = cv2.imread(os.path.join(
        file_path, 'png', 'background_info', random_image), cv2.IMREAD_UNCHANGED)
    res_img = cv2.resize(res_img, None, fx=0.8, fy=0.8)

    # Id卡
    fontStyle = font_list[1][100]
    if result['data']['clans']['clan'] == {}:
        tag = '[]'
        tag_color = (179, 179, 179)
    else:
        tag = '['+result['data']['clans']['clan']['tag']+']'
        tag_color = clan_color[result['data']['clans']['clan']['color']]
    text_list.append(
        [(160, 100), tag, tag_color, 1, 100])
    w = x_coord(tag, fontStyle)
    text_list.append(
        [(160+w+20, 100), result['nickname'], (0, 0, 0), 1, 100])
    id_w = w + x_coord(result['nickname'], fontStyle) + 40

    # 账号信息
    text_list.append(
        [(160+id_w, 95), str(result['data']['user']['karma']), (0, 0, 0), 1, 35])
    server_dict = {
        'asia': '亚服/asia',
        'eu': '欧服/eu',
        'na': '美服/na',
        'ru': '俄服/ru',
        'cn': '国服/cn'
    }
    text_list.append(
        [(400, 420), server_dict[server], (0, 0, 0), 1, 50])
    text_list.append(
        [(400, 500), str(aid), (0, 0, 0), 1, 50])
    creat_time = time.strftime(
        "%Y-%m-%d  %H:%M:%S", time.localtime(result['data']['user']['created_at']))
    text_list.append(
        [(400, 580), creat_time, (0, 0, 0), 1, 50])
    active_time = time.strftime(
        "%Y-%m-%d  %H:%M:%S", time.localtime(result['data']['user']['last_battle_time']))
    text_list.append(
        [(400, 660), active_time, (0, 0, 0), 1, 50])

    # pr
    pvp_battles_count = 0
    main_battles_count = 0
    fontStyle = font_list[1][30]
    i = 0
    for index in ['pvp', 'rank_solo']:
        temp_data = result['data']['pr']['battle_type'][index]
        if (
            temp_data == {} or
            temp_data['battles_count'] == 0 or
            result['data']['user']['leveling_points'] == 0
        ):
            text_list.append([(120+478*i, 940), '-', (0, 0, 0), 2, 80])
            text_list.append([(120+478*i, 1070), '-', (0, 0, 0), 2, 40])
            text_list.append([(120+478*i, 1183), '-', (0, 0, 0), 1, 50])
            text_list.append([(332+478*i, 1183), '-', (0, 0, 0), 1, 50])
            text_list.append([(120+478*i, 1286), '-', (0, 0, 0), 1, 50])
            text_list.append([(332+478*i, 1286), '-', (0, 0, 0), 1, 50])
        else:
            if index == 'pvp':
                pvp_battles_count += temp_data['battles_count']
            battles_count = '{:,}'.format(
                temp_data['battles_count']).replace(',', ' ')
            main_battles_count += temp_data['battles_count']
            battles_count_pro = '{:.2f}%'.format(
                temp_data['battles_count']/result['data']['user']['leveling_points']*100)
            avg_win = '{:.2f}%'.format(
                temp_data['wins']/temp_data['battles_count']*100)
            avg_wins = temp_data['wins'] / \
                temp_data['battles_count']*100
            avg_damage = '{:,}'.format(int(
                temp_data['damage_dealt']/temp_data['battles_count'])).replace(',', ' ')
            avg_frag = '{:.2f}'.format(
                temp_data['frags']/temp_data['battles_count'])
            avg_xp = '{:,}'.format(int(
                temp_data['original_exp']/temp_data['battles_count'])).replace(',', ' ')
            if temp_data['value_battles_count'] == 0:
                avg_pr = -1
                avg_n_damage = -1
                avg_n_frag = -1
                avg_wins = -1
            elif use_pr == False:
                avg_pr = -2
                avg_n_damage = -2
                avg_n_frag = -2
                avg_wins = -2
            else:
                avg_n_damage = temp_data['n_damage_dealt'] / \
                    temp_data['battles_count']
                avg_n_frag = temp_data['n_frags'] / \
                    temp_data['battles_count']
                avg_pr = temp_data['personal_rating'] / \
                    temp_data['battles_count']
            if use_pr:
                str_pr = pr_info(avg_pr)[5]
                w = x_coord(str_pr, fontStyle)
                text_list.append(
                    [(430+478*i-w/2, 817), str_pr, (255, 255, 255), 1, 30])
                box_list.append(
                    [(364+478*i, 816), (499+478*i, 849), pr_info(avg_pr)[1]])
                box_list.append(
                    [(80+478*i, 1395), (535+478*i, 1420), pr_info(avg_pr)[1]])
            else:
                str_pr = pr_info(-2)[5]
                w = x_coord(str_pr, fontStyle)
                text_list.append(
                    [(430+478*i, 820), str_pr, (255, 255, 255), 1, 30])
            text_list.append(
                [(120+478*i, 940), battles_count, (0, 0, 0), 2, 80])
            text_list.append(
                [(120+478*i, 1070), battles_count_pro, (0, 0, 0), 2, 40])
            text_list.append([(120+478*i, 1183), avg_win,
                             color_box(0, avg_wins)[1], 1, 45])
            text_list.append([(332+478*i, 1183), avg_damage,
                             color_box(1, avg_n_damage)[1], 1, 45])
            text_list.append([(120+478*i, 1286), avg_frag,
                             color_box(2, avg_n_frag)[1], 1, 45])
            text_list.append(
                [(332+478*i, 1286), avg_xp, (80, 80, 80), 1, 45])
        i += 1
    battles_count = '{:,}'.format(
        result['data']['user']['leveling_points']-main_battles_count).replace(',', ' ')
    battles_count_pro = '{:.2f}%'.format(
        (result['data']['user']['leveling_points']-main_battles_count)/result['data']['user']['leveling_points']*100)
    text_list.append(
        [(120+478*i, 940), battles_count, (0, 0, 0), 2, 80])
    text_list.append(
        [(120+478*i, 1070), battles_count_pro, (0, 0, 0), 2, 40])
    i = 0
    y0 = 665
    for index in ['pvp_solo', 'pvp_div2', 'pvp_div3']:
        temp_data = result['data']['pr']['battle_type'][index]
        if (
            temp_data == {} or
            temp_data['battles_count'] == 0 or
            result['data']['pr']['battle_type']['pvp']['battles_count'] == 0
        ):
            text_list.append([(120+478*i, 940+y0), '-', (0, 0, 0), 2, 80])
            text_list.append([(120+478*i, 1070+y0), '-', (0, 0, 0), 2, 40])
            text_list.append([(120+478*i, 1183+y0), '-', (0, 0, 0), 1, 50])
            text_list.append([(332+478*i, 1183+y0), '-', (0, 0, 0), 1, 50])
            text_list.append([(120+478*i, 1286+y0), '-', (0, 0, 0), 1, 50])
            text_list.append([(332+478*i, 1286+y0), '-', (0, 0, 0), 1, 50])
        else:
            battles_count = '{:,}'.format(
                temp_data['battles_count']).replace(',', ' ')
            main_battles_count += temp_data['battles_count']
            battles_count_pro = '{:.2f}%'.format(
                temp_data['battles_count']/result['data']['pr']['battle_type']['pvp']['battles_count']*100)
            avg_win = '{:.2f}%'.format(
                temp_data['wins']/temp_data['battles_count']*100)
            avg_wins = temp_data['wins'] / \
                temp_data['battles_count']*100
            avg_damage = '{:,}'.format(int(
                temp_data['damage_dealt']/temp_data['battles_count'])).replace(',', ' ')
            avg_frag = '{:.2f}'.format(
                temp_data['frags']/temp_data['battles_count'])
            avg_xp = '{:,}'.format(int(
                temp_data['original_exp']/temp_data['battles_count'])).replace(',', ' ')
            if temp_data['value_battles_count'] == 0:
                avg_pr = -1
                avg_n_damage = -1
                avg_n_frag = -1
                avg_wins = -1
            elif use_pr == False:
                avg_pr = -2
                avg_n_damage = -2
                avg_n_frag = -2
                avg_wins = -2
            else:
                avg_n_damage = temp_data['n_damage_dealt'] / \
                    temp_data['battles_count']
                avg_n_frag = temp_data['n_frags'] / \
                    temp_data['battles_count']
                avg_pr = temp_data['personal_rating'] / \
                    temp_data['battles_count']
            if use_pr:
                str_pr = pr_info(avg_pr)[5]
                w = x_coord(str_pr, fontStyle)
                text_list.append(
                    [(430+478*i-w/2, 817+y0), str_pr, (255, 255, 255), 1, 30])
                box_list.append(
                    [(364+478*i, 816+y0), (499+478*i, 849+y0), pr_info(avg_pr)[1]])
                box_list.append(
                    [(80+478*i, 1395+y0), (535+478*i, 1420+y0), pr_info(avg_pr)[1]])
            else:
                str_pr = pr_info(-2)[5]
                w = x_coord(str_pr, fontStyle)
                text_list.append(
                    [(430+478*i, 820+y0), str_pr, (255, 255, 255), 1, 30])
            text_list.append(
                [(120+478*i, 940+y0), battles_count, (0, 0, 0), 2, 80])
            text_list.append(
                [(120+478*i, 1070+y0), battles_count_pro, (0, 0, 0), 2, 40])
            text_list.append([(120+478*i, 1183+y0), avg_win,
                             color_box(0, avg_wins)[1], 1, 45])
            text_list.append([(332+478*i, 1183+y0), avg_damage,
                             color_box(1, avg_n_damage)[1], 1, 45])
            text_list.append([(120+478*i, 1286+y0), avg_frag,
                             color_box(2, avg_n_frag)[1], 1, 45])
            text_list.append(
                [(332+478*i, 1286+y0), avg_xp, (80, 80, 80), 1, 45])
        i += 1
    temp_data = result['data']['info']
    if temp_data == {} or temp_data['battles_count'] == 0:
        index_list = ['-', '-', '-', '-', '-', '-', '-',
                      '-', '-', '-', '-', '-', '-', '-', '-', '-', ]
    else:
        all_tier = 0
        all_count = 0
        for tier, data in result['data']['pr']['ship_tier'].items():
            if data == {}:
                continue
            all_tier += int(tier)*data['battles_count']
            all_count += data['battles_count']
        index_list = [
            '{:,}'.format(temp_data['battles_count']).replace(',', ' '),
            '{:,}'.format(temp_data['wins']).replace(',', ' '),
            '{:.1f}'.format(all_tier/all_count),
            '{:,}'.format(temp_data['frags']).replace(',', ' '),
            '{:.2f}'.format(temp_data['frags']/temp_data['battles_count']),
            '{:.2f}'.format(temp_data['frags']/(temp_data['battles_count']-temp_data['survived'])
                            ) if temp_data['battles_count']-temp_data['survived'] != 0 else '-',
            '{:.2f}'.format(temp_data['planes_killed'] /
                            temp_data['battles_count']),
            '{:,}'.format(
                int(temp_data['original_exp']/temp_data['battles_count'])).replace(',', ' '),
            '{:.2f}%'.format(temp_data['survived'] /
                             temp_data['battles_count']*100),
            '{:.2f}%'.format(
                temp_data['win_and_survived']/temp_data['survived']*100),
            '{:.2f}%'.format(temp_data['hits_by_main']/temp_data['shots_by_main']
                             * 100) if temp_data['shots_by_main'] != 0 else '0.0%',
            '{:.2f}%'.format(temp_data['hits_by_tpd']/temp_data['shots_by_tpd']
                             * 100) if temp_data['shots_by_tpd'] != 0 else '0.0%',
        ]

    i = 0
    fontStyle = font_list[1][50]
    for index in index_list:
        x = i % 4
        y = int(i / 4)
        w = x_coord(index, fontStyle)
        text_list.append(
            [(1725+317.6*x-w/2, 417+100.8*y), index, (0, 0, 0), 1, 50])
        i += 1
    i = 0
    for index in ['AirCarrier', 'Battleship', 'Cruiser', 'Destroyer', 'Submarine']:
        temp_data = result['data']['pr']['ship_type'][index]
        if (
            temp_data == {} or
            temp_data['battles_count'] == 0 or
            result['data']['pr']['ship_type'][index]['battles_count'] == 0
        ):
            text_list.append(
                [(2940*0.8, 1000*0.8+230*0.8*i), '-', (0, 0, 0), 1, 50])
            text_list.append(
                [(2940*0.8, 1083*0.8+230*0.8*i), '-', (0, 0, 0), 1, 50])
            text_list.append(
                [(3218*0.8, 1000*0.8+230*0.8*i), '-', (0, 0, 0), 1, 50])
            text_list.append(
                [(3218*0.8, 1083*0.8+230*0.8*i), '-', (0, 0, 0), 1, 50])
        else:
            battles_count = '{:,}'.format(
                temp_data['battles_count']).replace(',', ' ')
            battles_count_pro = '{:.2f}%'.format(
                temp_data['battles_count']/pvp_battles_count*100) if pvp_battles_count != 0 else '-%'
            avg_win = '{:.2f}%'.format(
                temp_data['wins']/temp_data['battles_count']*100)
            avg_wins = temp_data['wins'] / \
                temp_data['battles_count']*100
            avg_damage = '{:,}'.format(int(
                temp_data['damage_dealt']/temp_data['battles_count'])).replace(',', ' ')
            avg_frag = '{:.2f}'.format(
                temp_data['frags']/temp_data['battles_count'])
            if temp_data['value_battles_count'] == 0:
                avg_pr = -1
                avg_n_damage = -1
                avg_n_frag = -1
                avg_wins = -1
            elif use_pr == False:
                avg_pr = -2
                avg_n_damage = -2
                avg_n_frag = -2
                avg_wins = -2
            else:
                avg_n_damage = temp_data['n_damage_dealt'] / \
                    temp_data['battles_count']
                avg_n_frag = temp_data['n_frags'] / \
                    temp_data['battles_count']
                avg_pr = temp_data['personal_rating'] / \
                    temp_data['battles_count']
            if use_pr:
                str_pr = pr_info(avg_pr)[5]
                # w = x_coord(str_pr, fontStyle)
                text_list.append(
                    [(1836, 800+230*0.8*i), str_pr+'+('+str(pr_info(avg_pr)[4])+')', pr_info(avg_pr)[1], 1, 50])
                text_list.append(
                    [(1836, 868+230*0.8*i), '占比:', (74, 74, 74), 1, 40])
                text_list.append(
                    [(1836+105, 868+3+230*0.8*i), battles_count_pro, (0, 0, 0), 2, 50])
                box_list.append(
                    [(1532, 777+230*0.8*i), (1552, 937+230*0.8*i), pr_info(avg_pr)[1]])
            else:
                str_pr = pr_info(avg_pr)[5]
                text_list.append(
                    [(1836, 800+230*0.8*i), str_pr, pr_info(avg_pr)[1], 1, 50])
                text_list.append(
                    [(1836, 868+230*0.8*i), '占比:', (74, 74, 74), 1, 40])
                text_list.append(
                    [(1836+105, 868+3+230*0.8*i), battles_count_pro, (0, 0, 0), 2, 50])
            text_list.append([(2940*0.8, 1000*0.8+230*0.8*i),
                             battles_count, (0, 0, 0), 1, 40])
            text_list.append([(2940*0.8, 1083*0.8+230*0.8*i), avg_win,
                             color_box(0, avg_wins)[1], 1, 40])
            text_list.append([(3218*0.8, 1000*0.8+230*0.8*i), avg_damage,
                             color_box(1, avg_n_damage)[1], 1, 40])
            text_list.append([(3218*0.8, 1083*0.8+230*0.8*i), avg_frag,
                             color_box(2, avg_n_frag)[1], 1, 40])
        i += 1
    # achievement
    i = 0
    for index in result['data']['achievements']['battle']:
        x = i % 4
        y = int(i / 4)
        achievement_png_path = os.path.join(
            file_path, 'png', 'achievement', '{}.png'.format(index[0]))
        achievement_png = cv2.imread(
            achievement_png_path, cv2.IMREAD_UNCHANGED)
        achievement_png = cv2.resize(achievement_png, None, fx=1.4, fy=1.4)
        x1 = 2991+200*x
        y1 = 473+140*y
        x2 = x1 + achievement_png.shape[1]
        y2 = y1 + achievement_png.shape[0]
        res_img = merge_img(res_img, achievement_png, y1, y2, x1, x2)
        del achievement_png
        text_list.append(
            [(x1+100, y1+85), 'x'+str(index[1]), (0, 0, 0), 1, 35])
        i += 1
    i = 0
    for index in result['data']['achievements']['rank']:
        x = i % 4
        y = int(i / 4)
        achievement_png_path = os.path.join(
            file_path, 'png', 'achievement_plus', '{}.png'.format(index[0]))
        achievement_png = cv2.imread(
            achievement_png_path, cv2.IMREAD_UNCHANGED)
        achievement_png = cv2.resize(achievement_png, None, fx=1.4, fy=1.4)
        x1 = 2991+200*x
        y1 = 1394-160+135*y
        x2 = x1 + achievement_png.shape[1]
        y2 = y1 + achievement_png.shape[0]
        res_img = merge_img(res_img, achievement_png, y1, y2, x1, x2)
        del achievement_png
        text_list.append(
            [(x1+100, y1+85), 'x'+str(index[1]), (0, 0, 0), 1, 35])
        i += 1
    i = 0
    for index in result['data']['achievements']['cvc']:
        x = i % 4
        y = int(i / 4)
        achievement_png_path = os.path.join(
            file_path, 'png', 'achievement_plus', '{}.png'.format(index[0]))
        achievement_png = cv2.imread(
            achievement_png_path, cv2.IMREAD_UNCHANGED)
        achievement_png = cv2.resize(achievement_png, None, fx=1.4, fy=1.4)
        x1 = 2991+200*x
        y1 = 1596-160+135*y
        x2 = x1 + achievement_png.shape[1]
        y2 = y1 + achievement_png.shape[0]
        res_img = merge_img(res_img, achievement_png, y1, y2, x1, x2)
        del achievement_png
        if i <= 3:
            text_list.append(
                [(x1+100, y1+85), 'x'+str(index[1]), (0, 0, 0), 1, 35])
        i += 1
    # record
    ship_name_file_path = os.path.join(
        parent_file_path, 'json', 'ship_name.json')
    temp = open(ship_name_file_path, "r", encoding="utf-8")
    ship_name_data = json.load(temp)
    temp.close()
    index_list = [
        'battles_count',
        'max_damage_dealt',
        'max_frags',
        'max_planes_killed',
        'max_exp',
        'max_total_agro',
        'max_scouting_damage'
    ]
    fontStyle1 = font_list[1][45]
    fontStyle2 = font_list[1][30]
    i = 0
    for record_index in index_list:
        j = 0
        for index in result['data']['record'][record_index]:
            ship_data = '{:,}'.format(index[1]).replace(',', ' ')
            ship_name = a_tier_dict[ship_name_data[index[0]]['tier']] + \
                '    '+ship_name_data[index[0]]['ship_name']['zh_sg']
            w = x_coord(ship_data, fontStyle1)
            text_list.append(
                [(770-w/2+535*0.8*i, 2340+126*0.8*j), ship_data, (0, 0, 0), 1, 45])
            w = x_coord(ship_name, fontStyle2)
            text_list.append(
                [(770-w/2+535*0.8*i, 2392+126*0.8*j), ship_name, (104, 104, 104), 1, 30])
            j += 1
        i += 1
    # 图表
    max_num = 0
    for tier, num in result['data']['pr']['ship_tier'].items():
        if num == {}:
            continue
        if num['battles_count'] >= max_num:
            max_num = num['battles_count']
    max_index = (int(max_num/100) + 1)*100
    i = 0
    for index in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']:
        temp_data = result['data']['pr']['ship_tier'][index]
        if temp_data == {}:
            temp_data = {
                "battles_count": 0,
                "value_battles_count": 0,
                "personal_rating": 0
            }
        count = temp_data['battles_count']
        if temp_data['value_battles_count'] == 0:
            avg_pr = -1
        elif use_pr == False:
            avg_pr = -2
        else:
            avg_pr = temp_data['personal_rating'] / \
                temp_data['battles_count']
        pic_len = 280-count/max_index*280
        x1 = int(2086*.8+89*0.8*i)
        y1 = int(2180*0.8+pic_len)
        x2 = int(2141*0.8+89*0.8*i)
        y2 = int(2528*0.8)
        fontStyle = font_list[1][25]
        w = x_coord(str(count), fontStyle)
        text_list.append(
            [(1690-w/2+89*0.8*i, y1-30), str(count), (0, 0, 0), 1, 25])
        if pic_len <= 279:
            if avg_pr == -2:
                box_list.append(
                    [(x1, y1), (x2, y2), (174, 174, 174)])
            else:
                box_list.append(
                    [(x1, y1), (x2, y2), pr_info(avg_pr)[1]])

        i += 1
    if (isinstance(res_img, np.ndarray)):
        res_img = Image.fromarray(
            cv2.cvtColor(res_img, cv2.COLOR_BGR2RGB))
    res_img = add_box(box_list, res_img)
    res_img = add_text(text_list, res_img)
    res_img = res_img.resize((2640, 1376))
    return res_img


async def get_png(
    parameter: list,
):
    try:
        # [aid,server,use_pr,use_ac,ac]
        async with httpx.AsyncClient() as client:
            if parameter[3]:
                url = API_URL + '/user/info/' + \
                    f'?token={API_TOKEN}&aid={parameter[0]}&server={parameter[1]}&use_ac=True&ac={parameter[4]}'
            else:
                url = API_URL + '/user/info/' + \
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
        if result['data']['user'] == {}:
            return {'status': 'info', 'message': '该账号无战斗数据'}
        res_img = main(
            result=result,
            aid=parameter[0],
            server=parameter[1],
            use_pr=parameter[2]
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
