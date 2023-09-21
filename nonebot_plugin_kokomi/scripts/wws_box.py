import numpy as np
import cv2
import os
import json
import time
from PIL import Image, ImageDraw
import gc
from .config import (
    PIC_TYPE,
    BOT_VERSON
)
from .data_source import (
    img_to_b64,
    img_to_file,
    merge_img,
    add_text,
    add_box,
    x_coord
)
from .data_source import (
    font_list,
    a_tier_dict
)
import logging

file_path = os.path.dirname(__file__)
parent_file_path = os.path.dirname(os.path.dirname(__file__))
# 配置日志输出到文件
logging.basicConfig(filename=os.path.join(
    file_path, 'log', 'error.log'), level=logging.ERROR)


def reward_x60(
    x0,
    y0,
    res_img,
    img_path
):
    # 200*125
    reward_img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    reward_img = cv2.resize(reward_img, None, fx=1.3, fy=1.3)
    x1 = x0 + 57
    y1 = y0 + 21
    x2 = x1 + reward_img.shape[1]
    y2 = y1 + reward_img.shape[0]
    res_img = merge_img(res_img, reward_img, y1, y2, x1, x2)
    return res_img


def reward_x80(
    x0,
    y0,
    res_img,
    img_path
):
    # 200*125
    reward_img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    reward_img = cv2.resize(reward_img, None, fx=1.25, fy=1.25)
    x1 = x0 + 50
    y1 = y0 + 11
    x2 = x1 + reward_img.shape[1]
    y2 = y1 + reward_img.shape[0]
    res_img = merge_img(res_img, reward_img, y1, y2, x1, x2)
    return res_img


def get_ship(
    reward_list,
    num
):
    result = {}
    for cyc_num in range(num):
        number = 1
        i = 0
        for index in reward_list:
            if len(index['rewards_list']) == 0:
                del reward_list[i]
            else:
                number += index['probability'] * 100
            i += 1
        if number == 1:
            return result
        random_num = list(np.random.randint(1, number, 1))[0]
        i = 0
        number = 0
        for index in reward_list:
            if random_num <= number + index['probability'] * 100:
                random_ship_num = list(np.random.randint(
                    0, len(index['rewards_list']), 1))[0]
                result[index['rewards_list'][random_ship_num]['id']
                       ] = index['rewards_list'][random_ship_num]['isPremium']
                del reward_list[i]['rewards_list'][random_ship_num]
                break
            number += index['probability'] * 100
            i += 1
    return result


def main(
    box_type,
    box_num
):
    text_list = []
    box_list = []
    result = {
        'ship_icons': {
            'count': 0
        },
        'reward_icons': {},
        'eco_boosts_icons': {},
        'signal_flags': {}
    }
    box_file_path = os.path.join(
        file_path, 'png', 'box', 'json', 'box.json')
    temp = open(box_file_path, "r", encoding="utf-8")
    sc_box = json.load(temp)
    temp.close()
    if box_type == '1':
        box_reward_list = sc_box
    else:
        box_reward_list = sc_box
    random_num_list = list(np.random.randint(1, 10001, box_num))
    # 保底机制
    x_ = 200
    y_ = 200
    i = 0
    num = 0
    for index in random_num_list:
        # 保底
        if num >= box_reward_list['minimum_guarantee']-1:
            random_num_list[i] = 1
            num = 0
            i += 1
            continue
        if index <= box_reward_list['rewards'][0]['probability'] * 100:
            num = 0
        else:
            num += 1
        i += 1
    random_num_list.sort()
    res_img = cv2.imread(os.path.join(
        file_path, 'png', 'box', 'bg.png'), cv2.IMREAD_UNCHANGED)
    fontStyle = font_list[1][35]
    w = x_coord('您已获得的奖励', fontStyle)
    text_list.append(
        [(800-w/2, 70), '您已获得的奖励', (255, 255, 255), 1, 35])
    fontStyle = font_list[1][25]
    if box_type == '1':
        box_name = '超级补给箱'
    else:
        box_name = '超级补给箱'
    w = x_coord(f'已开启 {box_num} 个 {box_name}', fontStyle)
    text_list.append(
        [(800-w/2, 120), f'已开启 {box_num} 个 {box_name}', (200, 200, 200), 1, 25])
    box_list.append(
        [(200-10, 200-30-1), (1400+10, 200-30), (200, 200, 200)])
    # res_img = cv2.resize(res_img, None, fx=0.35, fy=0.35)
    number = 0
    for index in box_reward_list['rewards']:
        if len(random_num_list) == 0:
            break
        while len(random_num_list) != 0 and random_num_list[0] <= number + index['probability'] * 100:
            if index['reward_type'] == 'ship_icons':
                result['ship_icons']['count'] += 1
            else:
                if index['reward_name'] not in result[index['reward_type']]:
                    result[index['reward_type']
                           ][index['reward_name']] = index['count']
                else:
                    result[index['reward_type']
                           ][index['reward_name']] += index['count']
            del random_num_list[0]
        number += index['probability'] * 100
    result['ship_icons'] = get_ship(
        box_reward_list['rewards'][0]['reward_list'],
        result['ship_icons']['count']
    )
    i = 0
    ship_name_file_path = os.path.join(
        parent_file_path, 'json', 'ship_name.json')
    temp = open(ship_name_file_path, "r", encoding="utf-8")
    ship_name_data = json.load(temp)
    temp.close()
    fontStyle = font_list[1][20]
    for ship_id, is_premium in result['ship_icons'].items():
        x = int(i % 6)
        y = int(i/6)
        ship_tier = ship_name_data[str(ship_id)]['tier']
        ship_type = ship_name_data[str(ship_id)]['type'].lower()
        name = ship_name_data[str(ship_id)]['name']
        nation = ship_name_data[str(ship_id)]['nation']
        ship_name = ship_name_data[str(ship_id)]['ship_name']['zh_sg']
        if len(ship_name) > 7:
            ship_name = ship_name[:7] + '...'
        nation_path = os.path.join(
            file_path, 'png', 'box', 'nation', f'flag_{nation}.png')
        nation_png = cv2.imread(nation_path, cv2.IMREAD_UNCHANGED)
        nation_png = cv2.resize(nation_png, None, fx=0.25, fy=0.25)
        x1 = 200*x+5+x_
        y1 = 140*y+10+y_
        x2 = x1 + nation_png.shape[1]
        y2 = y1 + nation_png.shape[0]
        res_img = merge_img(res_img, nation_png, y1, y2, x1, x2)
        ship_path = os.path.join(
            file_path, 'png', 'box', 'ship_icons', f'{name}.png')
        ship_png = cv2.imread(ship_path, cv2.IMREAD_UNCHANGED)
        ship_png = cv2.resize(ship_png, None, fx=0.78, fy=0.78)
        x1 = 200*x+5+x_
        y1 = 140*y+15+y_
        x2 = x1 + ship_png.shape[1]
        y2 = y1 + ship_png.shape[0]
        res_img = merge_img(res_img, ship_png, y1, y2, x1, x2)
        if is_premium:
            type_path = os.path.join(
                file_path, 'png', 'box', 'ship_classes_icons', f'icon_default_{ship_type}_premium.png')
        else:
            type_path = os.path.join(
                file_path, 'png', 'box', 'ship_classes_icons', f'icon_default_{ship_type}_special.png')
        type_png = cv2.imread(type_path, cv2.IMREAD_UNCHANGED)
        type_png = cv2.resize(type_png, None, fx=1.6, fy=1.6)
        x1 = 200*x+7+x_
        y1 = 140*y+7+y_
        x2 = x1 + type_png.shape[1]
        y2 = y1 + type_png.shape[0]
        res_img = merge_img(res_img, type_png, y1, y2, x1, x2)
        w = x_coord(ship_name, fontStyle)
        text_list.append(
            [(200*x+53+1+x_, 140*y+18+1+y_), a_tier_dict[ship_tier], (150, 150, 150), 1, 20])
        text_list.append(
            [(200*x+53+x_, 140*y+18+y_), a_tier_dict[ship_tier], (233, 189, 99), 1, 20])
        text_list.append(
            [(200*x+180-w+1+x_, 140*y+100+1+y_), ship_name, (150, 150, 150), 1, 20])
        text_list.append(
            [(200*x+180-w+x_, 140*y+100+y_), ship_name, (242, 206, 104), 1, 20])
        i += 1
    for index in ['reward_icons', 'eco_boosts_icons', 'signal_flags']:
        for reward_name, reward_count in result[index].items():
            x = int(i % 6)
            y = int(i/6)
            if index == 'reward_icons':
                res_img = reward_x80(
                    x0=200*x+x_,
                    y0=140*y+y_,
                    res_img=res_img,
                    img_path=os.path.join(
                        file_path, 'png', 'box', index, reward_name+'.png')
                )
            else:
                res_img = reward_x60(
                    x0=200*x+x_,
                    y0=140*y+y_,
                    res_img=res_img,
                    img_path=os.path.join(
                        file_path, 'png', 'box', index, reward_name+'.png')
                )
            reward_count_str = '{:,}'.format(
                int(reward_count)).replace(',', ' ')
            if reward_name == 'gold':
                font_color = (216, 190, 137)
            elif reward_name == 'wows_premium':
                reward_count_str += ' 天'
                font_color = (216, 190, 137)
            elif reward_name == 'freeXP':
                font_color = (186, 214, 161)
            elif reward_name == 'eliteXP':
                font_color = (161, 201, 197)
            else:
                font_color = (255, 255, 255)
            w = x_coord(reward_count_str, fontStyle)
            box_list.append(
                [(200*x+150-w-5-2+x_, 140*y+90-2+2+y_), (200*x+150-w+w+3-1+x_, 140*y+90+20+1+2+y_), (40, 40, 40)])
            text_list.append(
                [(200*x+150-w-2+x_, 140*y+90+2+y_), reward_count_str, font_color, 1, 20])
            i += 1

    box_list.append(
        [(200-10, 200+30-1+140*(int(i/6)+1)), (1400+10, 200+30+140*(int(i/6)+1)), (200, 200, 200)])
    fontStyle = font_list[1][25]
    w = x_coord(BOT_VERSON, fontStyle)
    text_list.append(
        [(800-w/2, 200+60+140*(int(i/6)+1)), BOT_VERSON, (174, 174, 174), 1, 25])
    if (isinstance(res_img, np.ndarray)):
        res_img = Image.fromarray(
            cv2.cvtColor(res_img, cv2.COLOR_BGR2RGB))
    if i <= 12:
        i = 13
    res_img = res_img.crop((0, 0, 1600, 140*(int(i/6)+1)+330))
    res_img = add_box(box_list, res_img)
    res_img = add_text(text_list, res_img)
    return res_img


async def get_png(
    parameter: list,
):
    try:
        # [box_type,box_num]
        res_img = main(
            box_type=parameter[0],
            box_num=parameter[1]
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
    except Exception as e:
        logging.exception(
            f"Time:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}, Parameter:{parameter}")
        return {'status': 'error', 'message': f'程序内部错误,Error:{type(e).__name__}', 'error': str(type(e))}
