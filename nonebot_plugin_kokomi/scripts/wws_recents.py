import json
import os
import httpx
import logging
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
    DOG_TAG,
    SHIP_PREVIEW,
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
    add_text,
    add_box,
    formate_str
)
from .data_source import (
    font_list,
    clan_color,
    background_color,
    border_color,
    a_tier_dict
)

file_path = os.path.dirname(__file__)
parent_file_path = os.path.dirname(os.path.dirname(__file__))
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
    battle_type: str,
    use_pr: bool
):
    text_list = []
    box_list = []
    # Id卡
    text_list.append(
        [(158+14, 123+38), result['nickname'], (0, 0, 0), 1, 100])
    text_list.append(
        [(185+14, 237+38), f'{server.upper()} -- {aid}', (163, 163, 163), 1, 45])
    fontStyle = font_list[1][50]
    if result['data']['clans']['clan'] == {}:
        tag = 'None'
        tag_color = (179, 179, 179)
    else:
        tag = '['+result['data']['clans']['clan']['tag']+']'
        tag_color = clan_color[result['data']['clans']['clan']['color']]
    text_list.append(
        [(602+14-150+2, 317+38+2), tag, (255, 255, 255), 1, 50])
    text_list.append(
        [(602+14-150, 317+38), tag, tag_color, 1, 50])
    data_type = battle_type.upper()
    w = x_coord(data_type, fontStyle)
    text_list.append(
        [(602+14-150, 405+38), data_type, (0, 0, 0), 1, 50])
    # 主要数据
    if battle_type == 'pvp':
        index = 'pvp'
    else:
        index = 'rank_solo'
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
        file_path, 'png', 'background', 'wws_recents.png'), cv2.IMREAD_UNCHANGED)
    pr_png = cv2.imread(pr_png_path, cv2.IMREAD_UNCHANGED)
    pr_png = cv2.resize(pr_png, None, fx=0.787, fy=0.787)
    x1 = 118+14
    y1 = 590+38
    x2 = x1 + pr_png.shape[1]
    y2 = y1 + pr_png.shape[0]
    res_img = merge_img(res_img, pr_png, y1, y2, x1, x2)
    del pr_png
    text_list.append(
        [(545+100*pr_data[3]+14, 653+38), pr_data[2]+str(pr_data[4]), (255, 255, 255), 1, 35])
    str_pr = '{:,}'.format(int(avg_pr))
    fontStyle = font_list[1][80]
    w = x_coord(str_pr, fontStyle)
    text_list.append(
        [(2270-w+14, 605+38), str_pr, (255, 255, 255), 1, 80])
    x0 = 310+14
    y0 = 823+38
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

    # dog_tag
    if DOG_TAG:
        if result['dog_tag'] == [] or result['dog_tag'] == {}:
            pass
        else:
            res_img = dog_tag(res_img, result['dog_tag'])
    # 数据总览

    index_list = ['pvp_solo', 'pvp_div2', 'pvp_div3', 'rank_solo']

    i = 0
    for index in index_list:
        x0 = 0
        y0 = 1592-333
        temp_data = result['data']['pr']['battle_type'][index]
        if temp_data == {} or temp_data['battles_count'] == 0:
            fontStyle = font_list[1][50]
            w = x_coord('-', fontStyle)
            text_list.append(
                [(572-w/2+x0, y0+90*i), '-', (128, 128, 128), 1, 50])
            w = x_coord('-', fontStyle)
            text_list.append(
                [(937-w/2+x0, y0+90*i), '-', (128, 128, 128), 1, 50])
            w = x_coord('-', fontStyle)
            text_list.append(
                [(1291-w/2+x0, y0+90*i), '-', (128, 128, 128), 1, 50])
            w = x_coord('-', fontStyle)
            text_list.append(
                [(1595-w/2+x0, y0+90*i), '-', (128, 128, 128), 1, 50])
            w = x_coord('-', fontStyle)
            text_list.append(
                [(1893-w/2+x0, y0+90*i), '-', (128, 128, 128), 1, 50])
            w = x_coord('-', fontStyle)
            text_list.append(
                [(2160-w/2+x0, y0+90*i), '-', (128, 128, 128), 1, 50])
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
            if use_pr:
                str_pr = pr_info(
                    avg_pr)[5] + '(+'+str(pr_info(avg_pr)[4])+')'
            else:
                str_pr = '-'

            fontStyle = font_list[1][50]
            w = x_coord(battles_count, fontStyle)
            text_list.append(
                [(572-w/2+x0, y0+90*i), battles_count, (0, 0, 0), 1, 50])
            w = x_coord(str_pr, fontStyle)
            text_list.append(
                [(937-w/2+x0, y0+90*i), str_pr, pr_info(avg_pr)[1], 1, 50])
            w = x_coord(avg_win, fontStyle)
            text_list.append(
                [(1291-w/2+x0, y0+90*i), avg_win, color_box(0, avg_wins)[1], 1, 50])
            w = x_coord(avg_damage, fontStyle)
            text_list.append(
                [(1595-w/2+x0, y0+90*i), avg_damage, color_box(1, avg_n_damage)[1], 1, 50])
            w = x_coord(avg_frag, fontStyle)
            text_list.append(
                [(1893-w/2+x0, y0+90*i), avg_frag, color_box(2, avg_n_frag)[1], 1, 50])
            w = x_coord(avg_xp, fontStyle)
            text_list.append(
                [(2160-w/2+x0, y0+90*i), avg_xp, (0, 0, 0), 1, 50])
            i += 1
    time_str = f'数据统计区间: [ 过去24h ]'
    fontStyle = font_list[1][25]
    w = x_coord(time_str, fontStyle)
    text_list.append(
        [(1214-w/2, 963), time_str, (75, 75, 75), 1, 25])
    # 船只数据
    if SHIP_PREVIEW:
        all_png_path = os.path.join(file_path, 'png', 'ship_preview.jpg')
        all_png = Image.open(all_png_path)
        all_json = open(os.path.join(file_path, 'png', 'ship_preview.json'),
                        "r", encoding="utf-8")
        all_dict = json.load(all_json)
        all_json.close()
    else:
        ship_name_file_path = os.path.join(
            parent_file_path, 'json', 'ship_name.json')
        temp = open(ship_name_file_path, "r", encoding="utf-8")
        ship_name_data = json.load(temp)
        temp.close()
    # 中间插一个筛选条件
    if (isinstance(res_img, np.ndarray)):
        res_img = Image.fromarray(
            cv2.cvtColor(res_img, cv2.COLOR_BGR2RGB))
    i = 0
    fontStyle = font_list[1][50]
    for ship_data in result['data']['recents']:
        ship_id = ship_data['ship_id']
        ship_type = ship_data['type']
        temp_data = ship_data
        if temp_data == {} or temp_data['battles_count'] == 0:
            continue
        x0 = 0
        y0 = 1851
        if i >= 100:
            overflow_warming = '最多只能显示100条数据'
            w = x_coord(overflow_warming, fontStyle)
            text_list.append(
                [(1214-w/2+x0, y0+90*i), overflow_warming, (160, 160, 160), 1, 50])
            break
        # ship 图片
        if SHIP_PREVIEW:
            if ship_id in all_dict:
                pic_code = all_dict[ship_id]
                x = (pic_code % 10)
                y = int(pic_code / 10)
                ship_png = all_png.crop(
                    ((0+517*x), (0+115*y), (517+517*x), (115+115*y)))
                ship_png = ship_png.resize((360, 80))
                res_img.paste(ship_png, (110+10, 1837+89*i))
            else:
                text_list.append(
                    [(140+16, y0+89*i), 'Undefined Png', (160, 160, 160), 1, 50])
        else:
            ship_tier = a_tier_dict[ship_name_data[ship_id]['tier']]
            ship_name = ship_name_data[ship_id]['ship_name']['zh_sg']
            w = x_coord(ship_tier, fontStyle)
            text_list.append(
                [(190+16-w/2, y0+89*i), ship_tier, (0, 0, 0), 1, 50])
            w = x_coord(ship_name, fontStyle)
            ship_name = formate_str(ship_name, w, 290)
            text_list.append([(230+16, y0+89*i), ship_name, (0, 0, 0), 1, 50])
        # ship 数据
        battle_time = time.strftime("%H:%M", time.localtime(temp_data['time']))
        battle_type_dict = {
            'pvp': '随机',
            'pvp_solo': '单野',
            'pvp_div2': '双排',
            'pvp_div3': '三排',
            'rank_solo': '排位'
        }
        if temp_data['wins'] == 1:
            battle_result_color = (96, 185, 96)
        else:
            battle_result_color = (228, 15, 39)
        box_list.append(
            [(98+2, 1837+90*i), (112+2, 1916+90*i), battle_result_color])
        box_list.append(
            [(2318-2, 1837+90*i), (2332-2, 1916+90*i), battle_result_color])
        battle_type = battle_type_dict[ship_type]
        avg_damage = '{:,}'.format(temp_data['damage_dealt']).replace(',', ' ')
        avg_frag = '{:,}'.format(temp_data['frags'])
        avg_planes_killed = '{:,}'.format(temp_data['planes_killed'])
        avg_xp = '{:,}'.format(temp_data['original_exp']).replace(',', ' ')
        avg_hit_rate_by_main = '{:.2f}%'.format(
            0.00 if temp_data['shots_by_main'] == 0 else temp_data['hits_by_main']/temp_data['shots_by_main']*100)
        avg_art_agro = temp_data['art_agro']
        if avg_art_agro >= 10000:
            avg_art_agro = str(int(avg_art_agro/10000)) + 'w'
        else:
            avg_art_agro = '< 1w'
        avg_scouting_damage = '{:,}'.format(
            temp_data['scouting_damage']).replace(',', ' ')
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
            avg_n_damage = temp_data['n_damage_dealt']
            avg_n_frag = temp_data['n_frags']
            avg_pr = temp_data['personal_rating']

        if use_pr:
            str_pr = '{:,}'.format(int(avg_pr)).replace(',', ' ')
        else:
            str_pr = '-'
        if time.strftime("%m-%d", time.localtime(temp_data['time'])) != time.strftime("%m-%d", time.localtime(int(time.time()))):
            text_list.append([(635+x0, y0+89*i), '-1', (0, 0, 0), 1, 25])
        w = x_coord(battle_time, fontStyle)
        text_list.append(
            [(560-w/2+x0, y0+89*i), battle_time, (0, 0, 0), 1, 50])
        w = x_coord(battle_type, fontStyle)
        text_list.append(
            [(728-w/2+x0, y0+89*i), battle_type, (0, 0, 0), 1, 50])
        w = x_coord(str_pr, fontStyle)
        text_list.append(
            [(904-w/2+x0, y0+89*i), str_pr, pr_info(avg_pr)[1], 1, 50])
        w = x_coord(avg_damage, fontStyle)
        text_list.append(
            [(1121-w/2+x0, y0+89*i), avg_damage, color_box(1, avg_n_damage)[1], 1, 50])
        w = x_coord(avg_frag, fontStyle)
        text_list.append(
            [(1306-w/2+x0, y0+89*i), avg_frag, color_box(2, avg_n_frag)[1], 1, 50])
        w = x_coord(avg_planes_killed, fontStyle)
        text_list.append(
            [(1434-w/2+x0, y0+89*i), avg_planes_killed, (0, 0, 0), 1, 50])
        w = x_coord(avg_xp, fontStyle)
        text_list.append(
            [(1594-w/2+x0, y0+89*i), avg_xp, (0, 0, 0), 1, 50])
        w = x_coord(avg_hit_rate_by_main, fontStyle)
        text_list.append(
            [(1806-w/2+x0, y0+89*i), avg_hit_rate_by_main, (0, 0, 0), 1, 50])
        w = x_coord(avg_art_agro, fontStyle)
        text_list.append(
            [(2020-w/2+x0, y0+89*i), avg_art_agro, (0, 0, 0), 1, 50])
        w = x_coord(avg_scouting_damage, fontStyle)
        text_list.append(
            [(2210-w/2+x0, y0+89*i), avg_scouting_damage, (0, 0, 0), 1, 50])
        i += 1
    w = x_coord(BOT_VERSON, fontStyle)
    text_list.append(
        [(1214-w/2, 1837+89*(i+1)+14), BOT_VERSON, (174, 174, 174), 1, 50])
    #
    res_img = add_box(box_list, res_img)
    res_img = add_text(text_list, res_img)
    res_img = res_img.crop((0, 0, 2429, 1837+90*(i+2)))
    res_img = res_img.resize((int(2429*0.5), int((1837+90*(i+2))*0.5)))
    if SHIP_PREVIEW:
        del all_png
    return res_img


async def get_png(
    parameter: list
):
    aid = parameter[0]
    server = parameter[1]
    use_pr = parameter[2]

    try:
        # [aid,server,use_pr,use_ac,ac]
        async with httpx.AsyncClient() as client:
            if parameter[3]:
                url = API_URL + '/recents/query/' + \
                    f'?token={API_TOKEN}&aid={parameter[0]}&server={parameter[1]}&use_ac=True&ac={parameter[4]}'
            else:
                url = API_URL + '/recents/query/' + \
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
        if result['data']['pr']['battle_type']['pvp'] != {}:
            battle_type = 'pvp'
        elif result['data']['pr']['battle_type']['rank_solo'] != {}:
            battle_type = 'rank_solo'
        else:
            return {'status': 'info', 'message': '没有数据'}
        res_img = main(
            result,
            aid,
            server,
            battle_type,
            use_pr
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


async def bind_recents(
    parameter: list
):
    try:
        # [aid,server,use_ac,ac]
        async with httpx.AsyncClient() as client:
            if parameter[2]:
                url = API_URL + '/recents/bind/' + \
                    f'?token={API_TOKEN}&aid={parameter[0]}&server={parameter[1]}&use_ac=True&ac={parameter[3]}'
            else:
                url = API_URL + '/recents/bind/' + \
                    f'?token={API_TOKEN}&aid={parameter[0]}&server={parameter[1]}'
            res = await client.get(url, timeout=REQUEST_TIMEOUT)
            requset_code = res.status_code
            result = res.json()
            if requset_code == 200:
                pass
            else:
                return {'status': 'info', 'message': '数据接口请求失败'}
        gc.collect()
        return result
    except (TimeoutException, ConnectTimeout, ReadTimeout):
        return {'status': 'info', 'message': '网络请求超时,请稍后重试'}
    except Exception as e:
        logging.exception(
            f"Time:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}, Parameter:{parameter}")
        return {'status': 'error', 'message': f'程序内部错误,Error:{type(e).__name__}', 'error': str(type(e))}
