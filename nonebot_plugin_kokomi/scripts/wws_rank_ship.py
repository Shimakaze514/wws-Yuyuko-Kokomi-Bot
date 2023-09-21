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
    color_box,
    merge_img,
    x_coord,
    add_text
)
from .data_source import (
    font_list,
    clan_color,
    rank_list,
    rank_color_list,
    background_color,
    border_color
)
import logging

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
    result: dict,
    aid: str,
    server: str,
    use_pr: bool,
    ship_id: str,
    ship_name: str
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
    index = 'rank_solo'
    text_list.append([(602+14-150, 405+38), 'RANK(新)', (0, 0, 0), 1, 55])

    fontStyle = font_list[1][70]
    w = x_coord(ship_name, fontStyle)
    text_list.append(
        [(1214-w/2, 602), ship_name, (0, 0, 0), 1, 70])
    #

    if (
        result['data']['pr']['battle_type'][index] == {} or
        result['data']['pr']['battle_type'][index]['value_battles_count'] == 0
    ):
        avg_pr = -1
    elif use_pr == False:
        avg_pr = -2
    else:
        avg_pr = int(result['data']['pr']['battle_type'][index]['personal_rating'] /
                     result['data']['pr']['battle_type'][index]['value_battles_count']) + 1
    pr_data = pr_info(avg_pr)
    pr_png_path = os.path.join(
        file_path, 'png', 'pr', '{}.png'.format(pr_data[0]))
    res_img = cv2.imread(os.path.join(
        file_path, 'png', 'background', 'wws_rank_ship.png'), cv2.IMREAD_UNCHANGED)
    pr_png = cv2.imread(pr_png_path, cv2.IMREAD_UNCHANGED)
    pr_png = cv2.resize(pr_png, None, fx=0.787, fy=0.787)
    x1 = 118+14
    y1 = 590+38+129
    x2 = x1 + pr_png.shape[1]
    y2 = y1 + pr_png.shape[0]
    res_img = merge_img(res_img, pr_png, y1, y2, x1, x2)
    del pr_png
    # dog_tag
    if DOG_TAG:
        if result['dog_tag'] == [] or result['dog_tag'] == {}:
            pass
        else:
            res_img = dog_tag(res_img, result['dog_tag'])

    text_list.append(
        [(545+100*pr_data[3]+14, 653+38+129), pr_data[2]+str(pr_data[4]), (255, 255, 255), 1, 35])
    str_pr = '{:,}'.format(int(avg_pr))
    fontStyle = font_list[1][80]
    w = x_coord(str_pr, fontStyle)
    text_list.append(
        [(2270-w+14, 605+38+129), str_pr, (255, 255, 255), 1, 80])

    x0 = 310+14
    y0 = 823+38+129
    temp_data = result['data']['pr']['battle_type'][index]
    if temp_data == {} or temp_data['battles_count'] == 0:
        battles_count = '{:,}'.format(0)
        avg_win = '{:.2f}%'.format(0.00)
        avg_wins = 0.00
        avg_damage = '{:,}'.format(0).replace(',', ' ')
        avg_frag = '{:.2f}'.format(0.00)
        avg_xp = '{:,}'.format(0).replace(',', ' ')
    else:
        battles_count = '{:,}'.format(temp_data['battles_count'])
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
    if temp_data == {} or temp_data['value_battles_count'] == 0:
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

    fontStyle = font_list[1][80]
    w = x_coord(battles_count, fontStyle)
    text_list.append(
        [(x0+446*0-w/2, y0), battles_count, (0, 0, 0), 1, 80])
    w = x_coord(avg_win, fontStyle)
    text_list.append(
        [(x0+446*1-w/2, y0), avg_win, color_box(0, avg_wins)[1], 1, 80])
    w = x_coord(avg_damage, fontStyle)
    text_list.append(
        [(x0+446*2-w/2, y0), avg_damage, color_box(1, avg_n_damage)[1], 1, 80])
    w = x_coord(avg_frag, fontStyle)
    text_list.append(
        [(x0+446*3-w/2, y0), avg_frag, color_box(2, avg_n_frag)[1], 1, 80])
    w = x_coord(avg_xp, fontStyle)
    text_list.append(
        [(x0+446*4-w/2, y0), avg_xp, (0, 0, 0), 1, 80])
    # 数据总览
    i = 0
    for index in ['rank_solo']:
        x0 = 0 + 14
        y0 = 1213+38+129
        temp_data = result['data']['pr']['battle_type'][index]
        if temp_data == {} or temp_data['battles_count'] == 0:
            fontStyle = font_list[1][55]
            w = x_coord('-', fontStyle)
            text_list.append(
                [(572-w/2+x0, y0+90*i), '-', (128, 128, 128), 1, 55])
            w = x_coord('-', fontStyle)
            text_list.append(
                [(937-w/2+x0, y0+90*i), '-', (128, 128, 128), 1, 55])
            w = x_coord('-', fontStyle)
            text_list.append(
                [(1291-w/2+x0, y0+90*i), '-', (128, 128, 128), 1, 55])
            w = x_coord('-', fontStyle)
            text_list.append(
                [(1595-w/2+x0, y0+90*i), '-', (128, 128, 128), 1, 55])
            w = x_coord('-', fontStyle)
            text_list.append(
                [(1893-w/2+x0, y0+90*i), '-', (128, 128, 128), 1, 55])
            w = x_coord('-', fontStyle)
            text_list.append(
                [(2160-w/2+x0, y0+90*i), '-', (128, 128, 128), 1, 55])
            i += 1
        else:
            battles_count = '{:,}'.format(temp_data['battles_count'])
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
                str_pr = pr_info(
                    avg_pr)[5] + '(+'+str(pr_info(avg_pr)[4])+')'
            else:
                str_pr = '-'
            fontStyle = font_list[1][55]
            w = x_coord(battles_count, fontStyle)
            text_list.append(
                [(572-w/2+x0, y0+90*i), battles_count, (0, 0, 0), 1, 55])
            w = x_coord(str_pr, fontStyle)
            text_list.append(
                [(937-w/2+x0, y0+90*i), str_pr, pr_info(avg_pr)[1], 1, 55])
            w = x_coord(avg_win, fontStyle)
            text_list.append(
                [(1291-w/2+x0, y0+90*i), avg_win, color_box(0, avg_wins)[1], 1, 55])
            w = x_coord(avg_damage, fontStyle)
            text_list.append(
                [(1595-w/2+x0, y0+90*i), avg_damage, color_box(1, avg_n_damage)[1], 1, 55])
            w = x_coord(avg_frag, fontStyle)
            text_list.append(
                [(1893-w/2+x0, y0+90*i), avg_frag, color_box(2, avg_n_frag)[1], 1, 55])
            w = x_coord(avg_xp, fontStyle)
            text_list.append(
                [(2160-w/2+x0, y0+90*i), avg_xp, (0, 0, 0), 1, 55])
            i += 1
    #
    if result['data']['pr']['battle_type']['pvp'] == {}:
        index = 'rank_solo'
    else:
        index = 'pvp'
    x0 = 0
    y0 = 1954+12-267
    temp_data = result['data']['ships'][ship_id][index]
    if temp_data == {} or temp_data['battles_count'] == 0:
        avg_survived = '{:.2f}%'.format(0.00)
        avg_planes_kill = '{:.2f}'.format(0.00)
        avg_art_agro = '{:,}'.format(0)
        avg_scouting_damage = '{:,}'.format(0)
        avg_captured = '{:.2f}%'.format(0.00)
        avg_dropped = '{:.2f}%'.format(0.00)
        max_damage = '{:,}'.format(0)
        max_art_agro = '{:,}'.format(0)
        max_frags = '{:,}'.format(0)
        max_exp = '{:,}'.format(0)
        max_scouting_damage = '{:,}'.format(0)
        max_planes_kill = '{:,}'.format(0)
        hr_main = '{:.2f}%'.format(0.00)
        hr_atba = '{:.2f}%'.format(0.00)
        hr_tpd = '{:.2f}%'.format(0.00)
        hr_rocket = '{:.2f}%'.format(0.00)
        hr_bomb = '{:.2f}%'.format(0.00)
        hr_skip = '{:.2f}%'.format(0.00)

    else:
        avg_survived = '{:.2f}%'.format(
            temp_data['survived']/temp_data['battles_count']*100)
        avg_planes_kill = '{:.2f}'.format(
            temp_data['planes_killed']/temp_data['battles_count'])
        avg_art_agro = '{:,}'.format(int(
            temp_data['art_agro']/temp_data['battles_count']))
        avg_scouting_damage = '{:,}'.format(int(
            temp_data['scouting_damage']/temp_data['battles_count']))
        avg_captured = '{:.2f}%'.format(
            temp_data['control_captured_points']/temp_data['team_control_captured_points']*100) if temp_data['team_control_captured_points'] != 0 else '0.00%'
        avg_dropped = '{:.2f}%'.format(
            temp_data['control_dropped_points']/temp_data['team_control_dropped_points']*100) if temp_data['team_control_dropped_points'] != 0 else '0.00%'
        max_damage = '{:,}'.format(temp_data['max_damage_dealt'])
        max_art_agro = '{:,}'.format(temp_data['max_total_agro'])
        max_frags = '{:,}'.format(temp_data['max_frags'])
        max_exp = '{:,}'.format(temp_data['max_exp'])
        max_scouting_damage = '{:,}'.format(temp_data['max_scouting_damage'])
        max_planes_kill = '{:,}'.format(temp_data['max_planes_killed'])
        hr_main = '{:.2f}%'.format(
            temp_data['hits_by_main']/temp_data['shots_by_main']*100) if temp_data['shots_by_main'] != 0 else '-'
        hr_atba = '{:.2f}%'.format(
            temp_data['hits_by_atba']/temp_data['shots_by_atba']*100) if temp_data['shots_by_atba'] != 0 else '-'
        hr_tpd = '{:.2f}%'.format(
            temp_data['hits_by_tpd']/temp_data['shots_by_tpd']*100) if temp_data['shots_by_tpd'] != 0 else '-'
        hr_rocket = '{:.2f}%'.format(
            temp_data['hits_by_rocket']/temp_data['shots_by_rocket']*100) if temp_data['shots_by_rocket'] != 0 else '-'
        hr_bomb = '{:.2f}%'.format(
            temp_data['hits_by_bomb']/temp_data['shots_by_bomb']*100) if temp_data['shots_by_bomb'] != 0 else '-'
        hr_skip = '{:.2f}%'.format(
            temp_data['hits_by_skip']/temp_data['shots_by_skip']*100) if temp_data['shots_by_skip'] != 0 else '-'

    fontStyle = font_list[1][55]
    w = x_coord(avg_survived, fontStyle)
    text_list.append(
        [(807-w, y0+89*0), avg_survived, (0, 0, 0), 1, 55])
    w = x_coord(avg_planes_kill, fontStyle)
    text_list.append(
        [(807-w, y0+89), avg_planes_kill, (0, 0, 0), 1, 55])
    w = x_coord(avg_art_agro, fontStyle)
    text_list.append(
        [(807-w, y0+89*2), avg_art_agro, (0, 0, 0), 1, 55])
    w = x_coord(avg_scouting_damage, fontStyle)
    text_list.append(
        [(807-w, y0+89*3), avg_scouting_damage, (0, 0, 0), 1, 55])
    w = x_coord(avg_captured, fontStyle)
    text_list.append(
        [(807-w, y0+89*4), avg_captured, (0, 0, 0), 1, 55])
    w = x_coord(avg_dropped, fontStyle)
    text_list.append(
        [(807-w, y0+89*5), avg_dropped, (0, 0, 0), 1, 55])

    w = x_coord(max_damage, fontStyle)
    text_list.append(
        [(2201-w, y0+89*1), max_damage, (0, 0, 0), 1, 55])
    w = x_coord(max_art_agro, fontStyle)
    text_list.append(
        [(2201-w, y0+89*2), max_art_agro, (0, 0, 0), 1, 55])
    w = x_coord(max_frags, fontStyle)
    text_list.append(
        [(2201-w, y0+89*0), max_frags, (0, 0, 0), 1, 55])
    w = x_coord(max_exp, fontStyle)
    text_list.append(
        [(2201-w, y0+89*3), max_exp, (0, 0, 0), 1, 55])
    w = x_coord(max_scouting_damage, fontStyle)
    text_list.append(
        [(2201-w, y0+89*4), max_scouting_damage, (0, 0, 0), 1, 55])
    w = x_coord(max_planes_kill, fontStyle)
    text_list.append(
        [(2201-w, y0+89*5), max_planes_kill, (0, 0, 0), 1, 55])

    w = x_coord(hr_main, fontStyle)
    text_list.append(
        [(1503-w, y0+89*0), hr_main, (0, 0, 0), 1, 55])
    w = x_coord(hr_atba, fontStyle)
    text_list.append(
        [(1503-w, y0+89*1), hr_atba, (0, 0, 0), 1, 55])
    w = x_coord(hr_tpd, fontStyle)
    text_list.append(
        [(1503-w, y0+89*2), hr_tpd, (0, 0, 0), 1, 55])
    w = x_coord(hr_rocket, fontStyle)
    text_list.append(
        [(1503-w, y0+89*3), hr_rocket, (0, 0, 0), 1, 55])
    w = x_coord(hr_bomb, fontStyle)
    text_list.append(
        [(1503-w, y0+89*4), hr_bomb, (0, 0, 0), 1, 55])
    w = x_coord(hr_skip, fontStyle)
    text_list.append(
        [(1503-w, y0+89*5), hr_skip, (0, 0, 0), 1, 55])
    # 船只数据
    season_list = []
    for index in result['data']['seasons'].keys():
        if len(index) != 4:
            continue
        season_list.append(int(index))
    season_list.sort(reverse=True)
    i = 0

    for index in season_list:
        x0 = 0+14
        y0 = 2452+10
        temp_data = result['data']['seasons'][str(index)]
        if temp_data == {} or temp_data['battles_count'] == 0:
            fontStyle = font_list[1][55]
            w = x_coord(f'第 {index%1000} 赛季', fontStyle)
            text_list.append(
                [(286-w/2+x0, y0+90*i), f'第 {index%1000} 赛季', (0, 0, 0), 1, 55])
            w = x_coord('-', fontStyle)
            text_list.append(
                [(572-w/2+x0, y0+90*i), '-', (128, 128, 128), 1, 55])
            w = x_coord('-', fontStyle)
            text_list.append(
                [(937-w/2+x0, y0+90*i), '-', (128, 128, 128), 1, 55])
            w = x_coord('-', fontStyle)
            text_list.append(
                [(1291-w/2+x0, y0+90*i), '-', (128, 128, 128), 1, 55])
            w = x_coord('-', fontStyle)
            text_list.append(
                [(1595-w/2+x0, y0+90*i), '-', (128, 128, 128), 1, 55])
            w = x_coord('-', fontStyle)
            text_list.append(
                [(1893-w/2+x0, y0+90*i), '-', (128, 128, 128), 1, 55])
            w = x_coord('-', fontStyle)
            text_list.append(
                [(2160-w/2+x0, y0+90*i), '-', (128, 128, 128), 1, 55])
            i += 1
        else:
            battles_count = '{:,}'.format(temp_data['battles_count'])
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
                str_pr = pr_info(
                    avg_pr)[5] + '(+'+str(pr_info(avg_pr)[4])+')'
            else:
                str_pr = '-'

            fontStyle = font_list[1][55]
            w = x_coord(f'第 {index%1000} 赛季', fontStyle)
            text_list.append(
                [(286-w/2+x0, y0+90*i), f'第 {index%1000} 赛季', (0, 0, 0), 1, 55])
            w = x_coord(battles_count, fontStyle)
            text_list.append(
                [(572-w/2+x0, y0+90*i), battles_count, (0, 0, 0), 1, 55])
            w = x_coord(str_pr, fontStyle)
            text_list.append(
                [(937-w/2+x0, y0+90*i), str_pr, pr_info(avg_pr)[1], 1, 55])
            w = x_coord(avg_win, fontStyle)
            text_list.append(
                [(1291-w/2+x0, y0+90*i), avg_win, color_box(0, avg_wins)[1], 1, 55])
            w = x_coord(avg_damage, fontStyle)
            text_list.append(
                [(1595-w/2+x0, y0+90*i), avg_damage, color_box(1, avg_n_damage)[1], 1, 55])
            w = x_coord(avg_frag, fontStyle)
            text_list.append(
                [(1893-w/2+x0, y0+90*i), avg_frag, color_box(2, avg_n_frag)[1], 1, 55])
            w = x_coord(avg_xp, fontStyle)
            text_list.append(
                [(2160-w/2+x0, y0+90*i), avg_xp, (0, 0, 0), 1, 55])
            i += 1

    if (isinstance(res_img, np.ndarray)):
        res_img = Image.fromarray(
            cv2.cvtColor(res_img, cv2.COLOR_BGR2RGB))
    w = x_coord(BOT_VERSON, fontStyle)
    text_list.append(
        [(1214-w/2, 2452+10+89*(i+2)+14), BOT_VERSON, (174, 174, 174), 1, 50])
    # 图表
    res_img = add_text(text_list, res_img)
    res_img = res_img.crop((0, 0, 2429, 2452+10+90*(i+3)))
    res_img = res_img.resize((int(2429*0.5), int((2452+10+90*(i+3))*0.5)))
    return res_img


async def get_png(
    parameter: list,
):
    try:
        # [aid,server,use_pr,ship_id,ship_name]
        if parameter[1] in ['cn', 'ru']:
            return {'status': 'info', 'message': '非常抱歉，由于国服和俄服并未开放相关数据接口，无法查询到数据'}
        async with httpx.AsyncClient() as client:
            url = API_URL + '/rank/ship/' + \
                f'?token={API_TOKEN}&aid={parameter[0]}&server={parameter[1]}&ship_id={parameter[3]}'
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
        res_img = main(
            result=result,
            aid=parameter[0],
            server=parameter[1],
            use_pr=parameter[2],
            ship_id=parameter[3],
            ship_name=parameter[4]
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
