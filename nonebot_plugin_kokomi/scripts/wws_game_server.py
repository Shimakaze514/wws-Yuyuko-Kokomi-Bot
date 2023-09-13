import os
import httpx
import time
import datetime
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
    x_coord,
    merge_img,
    add_text
)
from .data_source import (
    font_list,
    server_table_list
)
import logging
file_path = os.path.dirname(__file__)
# 配置日志输出到文件
logging.basicConfig(filename=os.path.join(
    file_path, 'log', 'error.log'), level=logging.ERROR)


def int_to_str(num: int):
    str_num = str(num)
    if len(str_num) > 3:
        return str_num[:len(str_num)-3] + ' ' + str_num[len(str_num)-3:]
    else:
        return str_num


def main(
    result
):
    text_list = []
    color_server = {
        'asia': (254, 182, 77),
        'eu': (91, 196, 159),
        'na': (50, 211, 235),
        'ru': (255, 124, 124),
        'cn': (146, 135, 231)
    }
    res_img = cv2.imread(os.path.join(
        file_path, 'png', 'background', 'wws_game_servers.png'), cv2.IMREAD_UNCHANGED)

    all_online = 0
    max_online = None
    for online_number in result['data']['now'].values():
        if online_number is None:
            continue
        all_online += online_number
        if max_online == None or max_online <= online_number:
            max_online = online_number
    max_online += 2000
    fontStyle = font_list[2][90]
    text_list.append(
        [(208, 546), int_to_str(all_online), (0, 0, 0), 2, 90])
    i = 0
    for index in ['asia', 'eu', 'na', 'ru', 'cn']:
        if result['data']['now'][index] == None:
            continue
        num_len = int((result['data']['now'][index]/max_online)*1400)
        cv2.rectangle(res_img, (329, 732+92*i), (329+num_len, 770+92*i),
                      color_server[index], -1)
        fontStyle = font_list[1][35]
        w = x_coord(int_to_str(result['data']['now'][index]), fontStyle)
        text_list.append([(329+num_len-10-w, 734+92*i),
                         int_to_str(result['data']['now'][index]), (255, 255, 255), 1, 35])
        text_list.append(
            [(1873+20, 730+92*i), int_to_str(result['data']['max'][index]), (0, 0, 0), 1, 35])
        text_list.append(
            [(2142+20, 730+92*i), int_to_str(result['data']['min'][index]), (0, 0, 0), 1, 35])
        i += 1

    fontStyle = font_list[1][55]
    now_hour = datetime.datetime.now().hour
    if now_hour == 23:
        now_hour = 0
        date_str = time.strftime(
            "%Y-%m-%d", time.localtime(time.time()))
        time_str = "23:59:59"
        dt = datetime.datetime.strptime(
            date_str + ' ' + time_str, "%Y-%m-%d %H:%M:%S")
        end_time = dt.timestamp()
    else:
        now_hour = now_hour + 1
        date_str = time.strftime(
            "%Y-%m-%d", time.localtime(time.time()))
        time_str = "{}:00:00".format(
            f'0{now_hour}' if now_hour < 10 else f'{now_hour}')
        dt = datetime.datetime.strptime(
            date_str + ' ' + time_str, "%Y-%m-%d %H:%M:%S")
        end_time = dt.timestamp()
    hour_list = []
    i = 0
    while i <= 23:
        if now_hour == 0:
            hour_list.append(now_hour)
            now_hour = 23
        else:
            hour_list.append(now_hour)
            now_hour -= 1
        i += 1

    hour_list.reverse()
    max_member = []
    for index in ['asia', 'eu', 'na', 'ru', 'cn']:
        if result['data']['max'][index] == None:
            continue
        max_member.append(result['data']['max'][index])
    max_member = max(max_member)
    y_list = []
    for y_index in server_table_list:
        if y_index[0] < max_member:
            continue
        y_max = y_index[0]
        while y_max >= 0:
            y_list.append(y_max)
            y_max -= y_index[1]
        break
    fontStyle = font_list[1][25]
    i = 0
    for index in hour_list:
        w = x_coord(str(index), fontStyle)
        text_list.append(
            [(285-w/2+83*i, 2177 + 80), str(index), (84, 84, 84), 1, 25])
        i += 1
    i = 0
    for index in y_list:
        w = x_coord(str(index), fontStyle)
        text_list.append(
            [(188-w, 1447+70*i + 80), str(index), (84, 84, 84), 1, 25])
        i += 1

    for index in ['asia', 'eu', 'na', 'ru', 'cn']:
        if result['data']['hour'][index] == {}:
            continue
        asix_list = []
        for record_time, record_data in result['data']['hour'][index].items():
            time_diff = end_time-int(record_time)
            x = 2194 - (1992*time_diff)/(24*60*60)
            y = 1456 + (700/y_list[0])*(y_list[0] - record_data) + 80
            if x <= 202:
                continue
            asix_list.append((int(x), int(y)))
        asix_list = asix_list[::3]

        points = np.array(asix_list, np.int32)
        curve_pts = cv2.approxPolyDP(points, epsilon=1, closed=False)
        cv2.polylines(res_img, [curve_pts], isClosed=False,
                      color=color_server[index], thickness=5)

    fontStyle = font_list[1][50]
    i = 0
    for index in ['asia', 'eu', 'na', 'ru', 'cn']:
        if result['data']['day'][index] == {}:
            continue
        x_list = list(result['data']['day'][index].keys())
        y_list = list(result['data']['day'][index].values())
        max_y = int((max(y_list) + 1000)/100)*100
        min_y = int((min(y_list) - 1000)/100)*100
        if len(x_list) >= 27:
            x_list = x_list[len(x_list)-27:]
        asix_list = []
        data_list = []
        num_len_list = []
        t = 0
        for date in x_list:
            data = result['data']['day'][index][date]
            num_len = int(((data-min_y)/(max_y-min_y))*350)
            cv2.circle(res_img, (250+70*t, 3050-num_len+567*i),
                       4, color_server[index], 2)
            asix_list.append((250+70*t, 3050-num_len+567*i))
            data_list.append(data)
            num_len_list.append(num_len)
            if t % 2 == 0:
                text_list.append(
                    [(250+70*t-25, 3085+567*i), date[5:], (0, 0, 0), 1, 20])
            t += 1
        j = 0
        if len(data_list) <= 8:
            pass
        else:
            if len(data_list) < 14:
                last_wwek = sum(data_list[:len(data_list)-7])
                now_week = sum(data_list[7:])
                data_len = len(data_list[7:])
            else:
                last_wwek = sum(data_list[len(data_list)-14:len(data_list)-7])
                now_week = sum(data_list[len(data_list)-7:])
                data_len = 7
            if last_wwek <= now_week:
                server_path = os.path.join(file_path, 'png', 'server_up.png')
                server = cv2.imread(server_path, cv2.IMREAD_UNCHANGED)
                x1 = 1974
                y1 = 2584+567*i
                x2 = x1 + server.shape[1]
                y2 = y1 + server.shape[0]
                res_img = merge_img(res_img, server, y1, y2, x1, x2)
                w = x_coord(int_to_str(
                    int((now_week-last_wwek)/data_len)), fontStyle)
                text_list.append(
                    [(2180-w, 2584+567*i+8), int_to_str(int((now_week-last_wwek)/data_len)), (255, 255, 255), 1, 50])
            else:
                server_path = os.path.join(file_path, 'png', 'server_down.png')
                server = cv2.imread(server_path, cv2.IMREAD_UNCHANGED)
                x1 = 1974
                y1 = 2584+567*i
                x2 = x1 + server.shape[1]
                y2 = y1 + server.shape[0]
                res_img = merge_img(res_img, server, y1, y2, x1, x2)
                w = x_coord(int_to_str(
                    int((last_wwek-now_week)/data_len)), fontStyle)
                text_list.append(
                    [(2180-w, 2584+567*i+8), int_to_str(int((last_wwek-now_week)/data_len)), (255, 255, 255), 1, 50])

        points = np.array(asix_list, np.int32)
        curve_pts = cv2.approxPolyDP(points, epsilon=1, closed=False)
        cv2.polylines(res_img, [curve_pts], isClosed=False,
                      color=color_server[index], thickness=4)
        while j <= len(asix_list) - 1:
            if j == len(asix_list)-1 or asix_list[j][1] < asix_list[j+1][1]:
                text_list.append(
                    [(250+70*j+10, 3050-num_len_list[j]+567*i-30), int_to_str(data_list[j]), (0, 0, 0), 1, 20])
            else:
                text_list.append(
                    [(250+70*j+10, 3050-num_len_list[j]+567*i+10), int_to_str(data_list[j]), (0, 0, 0), 1, 20])
            j += 1
        i += 1

    now_time = '当前时间：'+time.strftime(
        "%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    text_list.append(
        [(329, 1156), now_time, (174, 174, 174), 1, 35])
    # Mat 转 ImageDraw
    if (isinstance(res_img, np.ndarray)):
        res_img = Image.fromarray(
            cv2.cvtColor(res_img, cv2.COLOR_BGR2RGB))

    fontStyle = font_list[1][80]
    w = x_coord(BOT_VERSON, fontStyle)
    text_list.append(
        [(1214-w/2, 4296), BOT_VERSON, (174, 174, 174), 1, 80])
    res_img = add_text(text_list, res_img)
    res_img = res_img.resize((1214, 2202))
    return res_img


async def get_png(
    parameter: list,
):
    parameter = ['1']
    try:
        async with httpx.AsyncClient() as client:
            url = API_URL + '/server/active/' + f'?token={API_TOKEN}'
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
            result=result
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
