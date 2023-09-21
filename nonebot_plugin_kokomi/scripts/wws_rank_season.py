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
    formate_str

)
from .data_source import (
    font_list,
    clan_color,
    background_color,
    border_color,
    a_tier_dict
)
import logging

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
    use_pr: bool,
    season: str
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
    text_list.append(
        [(602+14-150, 405+38), f'第 {season[2:]} 赛季', (0, 0, 0), 1, 55])
    if (
        result['data']['pr']['battle_type']['rank_solo'] == {} or
        result['data']['pr']['battle_type']['rank_solo']['value_battles_count'] == 0
    ):
        avg_pr = -1
    elif use_pr == False:
        avg_pr = -2
    else:
        avg_pr = int(result['data']['pr']['battle_type']['rank_solo']['personal_rating'] /
                     result['data']['pr']['battle_type']['rank_solo']['value_battles_count']) + 1
    pr_data = pr_info(avg_pr)
    pr_png_path = os.path.join(
        file_path, 'png', 'pr', '{}.png'.format(pr_data[0]))
    res_img = cv2.imread(os.path.join(
        file_path, 'png', 'background', 'wws_rank_season.png'), cv2.IMREAD_UNCHANGED)
    pr_png = cv2.imread(pr_png_path, cv2.IMREAD_UNCHANGED)
    pr_png = cv2.resize(pr_png, None, fx=0.787, fy=0.787)
    x1 = 118+14
    y1 = 590+38
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
        [(545+100*pr_data[3]+14, 653+38), pr_data[2]+str(pr_data[4]), (255, 255, 255), 1, 35])
    str_pr = '{:,}'.format(int(avg_pr))
    fontStyle = font_list[1][80]
    w = x_coord(str_pr, fontStyle)
    text_list.append(
        [(2270-w+14, 605+38), str_pr, (255, 255, 255), 1, 80])
    index = 'rank_solo'
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
    # 船只数据
    i = 0
    for index in ['AirCarrier', 'Battleship', 'Cruiser', 'Destroyer', 'Submarine']:
        x0 = 0+14
        y0 = 1239+10
        temp_data = result['data']['pr']['ship_type'][index]
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

    # 船只数据
    ships_pr_list = {}
    for ship_id, ship_data in result['data']['ships'].items():
        ships_pr_list[ship_id] = 1
        # if ship_data['pvp'] == {}:
        #     ships_pr_list[ship_id] = -1
        # else:
        #     if ship_data['pvp']['value_battles_count'] == 0:
        #         ships_pr_list[ship_id] = -1
        #     else:
        #         ships_pr_list[ship_id] = ship_data['pvp']['personal_rating'] / \
        #             ship_data['pvp']['value_battles_count']
    sorts_pr_list = ships_pr_list.items()
    # sorts_pr_list = sorted(ships_pr_list.items(),
    #                        key=lambda x: x[1], reverse=True)
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
    for ship_id, ship_pr in sorts_pr_list:
        temp_data = result['data']['ships'][ship_id]['rank_solo']
        if temp_data == {} or temp_data['battles_count'] == 0:
            continue
        x0 = 0
        y0 = 1912+14
        if i >= 150:
            overflow_warming = '最多只能显示150条船只的数据'
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
                res_img.paste(ship_png, (110, 1912+89*i))
            else:
                text_list.append(
                    [(140, y0+89*i), 'Undefined Png', (160, 160, 160), 1, 50])
        else:
            ship_tier = a_tier_dict[ship_name_data[ship_id]['tier']]
            ship_name = ship_name_data[ship_id]['ship_name']['zh_sg']
            w = x_coord(ship_tier, fontStyle)
            text_list.append(
                [(195-w/2, y0+89*i), ship_tier, (0, 0, 0), 1, 50])
            w = x_coord(ship_name, fontStyle)
            ship_name = formate_str(ship_name, w, 290)
            text_list.append([(235, y0+89*i), ship_name, (0, 0, 0), 1, 50])
        # ship 数据
        battles_count = '{:,}'.format(temp_data['battles_count'])
        avg_win = '{:.2f}%'.format(
            temp_data['wins']/temp_data['battles_count']*100)
        avg_wins = temp_data['wins'] / \
            temp_data['battles_count']*100
        avg_damage = '{:,}'.format(int(
            temp_data['damage_dealt']/temp_data['battles_count'])).replace(',', ' ')
        avg_frag = '{:.2f}'.format(
            temp_data['frags']/temp_data['battles_count'])
        avg_xp = '{:,}'.format(
            int(temp_data['original_exp']/temp_data['battles_count'])).replace(',', ' ')
        avg_survived = '{:.2f}%'.format(
            temp_data['survived']/temp_data['battles_count']*100)
        avg_hit_rate_by_main = '{:.2f}%'.format(
            0.00 if temp_data['shots_by_main'] == 0 else temp_data['hits_by_main']/temp_data['shots_by_main']*100)
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
        w = x_coord(battles_count, fontStyle)
        text_list.append(
            [(551-w/2+x0, y0+89*i), battles_count, (0, 0, 0), 1, 50])
        w = x_coord(str_pr, fontStyle)
        text_list.append(
            [(834-w/2+x0, y0+89*i), str_pr, pr_info(avg_pr)[1], 1, 50])
        w = x_coord(avg_win, fontStyle)
        text_list.append(
            [(1160-w/2+x0, y0+89*i), avg_win, color_box(0, avg_wins)[1], 1, 50])
        w = x_coord(avg_damage, fontStyle)
        text_list.append(
            [(1396-w/2+x0, y0+89*i), avg_damage, color_box(1, avg_n_damage)[1], 1, 50])
        w = x_coord(avg_frag, fontStyle)
        text_list.append(
            [(1596-w/2+x0, y0+89*i), avg_frag, color_box(2, avg_n_frag)[1], 1, 50])
        w = x_coord(avg_xp, fontStyle)
        text_list.append(
            [(1770-w/2+x0, y0+89*i), avg_xp, (0, 0, 0), 1, 50])
        w = x_coord(avg_survived, fontStyle)
        text_list.append(
            [(1978-w/2+x0, y0+89*i), avg_survived, (0, 0, 0), 1, 50])
        w = x_coord(avg_hit_rate_by_main, fontStyle)
        text_list.append(
            [(2209-w/2+x0, y0+89*i), avg_hit_rate_by_main, (0, 0, 0), 1, 50])
        i += 1
    fontStyle = font_list[1][50]
    w = x_coord(BOT_VERSON, fontStyle)
    text_list.append(
        [(1214-w/2, 1912+14+89*(i+1)), BOT_VERSON, (174, 174, 174), 1, 50])
    # 图表
    res_img = add_text(text_list, res_img)
    res_img = res_img.crop((0, 0, 2429, 1912+14+90*(i+2)))
    res_img = res_img.resize((int(2429*0.5), int((1912+14+90*(i+2))*0.5)))
    if SHIP_PREVIEW:
        del all_png
    return res_img


async def get_png(
    parameter: list,
):
    try:
        # [aid,server,use_pr,season]
        if parameter[1] in ['cn', 'ru']:
            return {'status': 'info', 'message': '非常抱歉，由于国服和俄服并未开放相关数据接口，无法查询到数据'}
        async with httpx.AsyncClient() as client:
            url = API_URL + '/rank/season/' + \
                f'?token={API_TOKEN}&aid={parameter[0]}&server={parameter[1]}&season={parameter[3]}'
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
            season=parameter[3]
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
