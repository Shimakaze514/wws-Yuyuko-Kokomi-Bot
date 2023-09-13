import sqlite3
import os
import httpx
import asyncio
import time
from io import BytesIO
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
    pr_info,
    color_box,
    x_coord,
    add_text,
    aid_to_server,
    formate_str
)
from .data_source import (
    font_list,
)
import logging
file_path = os.path.dirname(__file__)
# 配置日志输出到文件
logging.basicConfig(filename=os.path.join(
    file_path, 'log', 'error.log'), level=logging.ERROR)


async def fetch_data(url, qqid):
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(url, timeout=3)
            requset_code = res.status_code
            if requset_code == 200:
                image_data = res.content
                cache_db_path = os.path.join(file_path, 'db', 'user.db')
                conn = sqlite3.connect(cache_db_path)
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO images (id, time, img) VALUES (?, ?, ?)", (qqid, int(
                    time.time()), image_data))
                conn.commit()
                conn.close()
        except Exception:
            print('下载图片失败，请检查网络')


# async def fetch_group_data(url, qqid):
#     async with httpx.AsyncClient() as client:
#         try:
#             res = await client.get(url, timeout=REQUEST_TIMEOUT)
#             requset_code = res.status_code
#             if requset_code == 200:
#                 image_data = res.content
#                 cache_db_path = os.path.join(file_path, 'db', 'group.db')
#                 conn = sqlite3.connect(cache_db_path)
#                 cursor = conn.cursor()
#                 cursor.execute("INSERT INTO images (id, time, img) VALUES (?, ?, ?)", (qqid, int(
#                     time.time()), image_data))
#                 conn.commit()
#                 conn.close()
#         except Exception:
#             print('下载图片失败，请检查网络')


async def get_user_png(user_id_list):
    urls = []
    cache_db_path = os.path.join(file_path, 'db', 'user.db')
    # if os.path.exists(cache_db_path) != True:
    #     conn = sqlite3.connect(cache_db_path)
    #     cursor = conn.cursor()
    #     cursor.execute('''CREATE TABLE images
    #                     (id str PRIMARY KEY, time int, img str)''')
    #     conn.commit()
    #     conn.close()
    # else:
    conn = sqlite3.connect(cache_db_path)
    cursor = conn.cursor()
    for user_id in user_id_list:
        cursor.execute("SELECT * FROM images WHERE id=?", (user_id,))
        result = cursor.fetchone()
        if result == None or time.time() - result[1] >= 24*60*60:
            urls.append(
                (f'http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=100', user_id)
            )
        else:
            continue
    conn.close()
    if urls == []:
        return

    tasks = []
    async with asyncio.Semaphore(10):
        for url in urls:
            tasks.append(fetch_data(url[0], url[1]))
        await asyncio.gather(*tasks)


async def main(
    result: dict,
    group_id: str,
    group_name: str,
    ship_name: str,
    user_id: str
):
    text_list = []
    fontStyle = font_list[1][100]
    w = x_coord(group_name, fontStyle)
    text_list.append(
        [(1214-w/2+100, 170), group_name, (0, 0, 0), 1, 100])

    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url=f'https://apis.jxcxin.cn/api/quntx?qq={group_id}', timeout=3)
            requset_code = res.status_code
            if requset_code == 200:
                image_data = res.content
                qun_png = Image.open(BytesIO(image_data))
    except:
        qun_png = Image.open(os.path.join(file_path, 'png', 'default.png'))
    res_img = Image.open(os.path.join(
        file_path, 'png', 'background', 'wws_group_rank.png'))
    x1 = int(1214-w/2-50)-25
    y1 = 180-35
    qun_png = qun_png.resize((150, 150))
    res_img.paste(qun_png, (x1, y1))
    qun_png.close()
    fontStyle = font_list[1][70]
    w = x_coord(ship_name, fontStyle)
    text_list.append(
        [(1214-w/2, 360), ship_name, (0, 0, 0), 1, 70])
    pr_list = {}
    for aid, aid_data in result['data'].items():
        if aid_data['data'] == None:
            continue
        if aid_data['data']['value_battles_count'] == 0:
            continue
        pr_list[aid] = aid_data['data']['personal_rating'] / \
            aid_data['data']['value_battles_count']
    sorted_data = sorted(pr_list.items(), key=lambda x: x[1], reverse=True)
    user_id_list = []
    for aid, pr in sorted_data:
        qqid = result['data'][aid]['user_id']
        user_id_list.append(str(qqid))
    if user_id != None and user_id not in user_id_list:
        user_id_list.append(user_id)
    await get_user_png(user_id_list)
    cache_db_path = os.path.join(file_path, 'db', 'user.db')
    conn = sqlite3.connect(cache_db_path)  # 替换为你的数据库文件路径
    cursor = conn.cursor()

    i = 0
    is_user = False
    for aid, pr in sorted_data:
        userid = result['data'][aid]['user_id']
        if i <= 19:
            if str(user_id) == str(userid):
                is_user = True
            cursor.execute("SELECT img FROM images WHERE id=?", (userid,))
            png_result = cursor.fetchone()
            if png_result is not None:
                image_data = png_result[0]
                user_png = Image.open(BytesIO(image_data))
            else:
                user_png = Image.open(os.path.join(
                    file_path, 'png', 'default.png'))
            fontStyle = font_list[1][65]
            rank_num = str(i+1)
            w = x_coord(rank_num, fontStyle)
            text_list.append(
                [(259-w/2, 742+151*i), rank_num, (0, 0, 0), 1, 65])
            x1 = 431-30
            y1 = 734+151*i-7
            y0 = -7
            res_img.paste(user_png, (x1, y1))
            user_png.close()
            user_name = formate_str(result['data'][aid]['user_name'], x_coord(
                result['data'][aid]['user_name'], fontStyle), 630)
            text_list.append(
                [(555-30, 734+151*i+y0), str(user_name), (0, 0, 0), 1, 55])
            game_id = result['data'][aid]['game_id']
            text_list.append(
                [(555-30, 796+151*i+y0), str(game_id), (164, 164, 164), 1, 35])
            fontStyle = font_list[1][55]
            str_pr = str(int(pr))
            w = x_coord(str_pr, fontStyle)
            text_list.append([(1293-w/2, 760+151*i+y0), str_pr,
                              pr_info(int(pr))[1], 1, 55])
            server = aid_to_server(aid)
            w = x_coord(server, fontStyle)
            text_list.append(
                [(1612-w/2, 760+151*i+y0), server, (0, 0, 0), 1, 55])
            battles_count = result['data'][aid]['data']['battles_count']
            win_rate = round(result['data'][aid]['data']
                             ['wins']/battles_count*100, 2)
            damage = int(result['data'][aid]['data']
                         ['damage_dealt']/battles_count)
            n_damage = int(result['data'][aid]['data']
                           ['n_damage_dealt']/battles_count)
            frag = round(result['data'][aid]['data']['frags']/battles_count, 2)
            n_frag = round(result['data'][aid]['data']
                           ['n_frags']/battles_count, 2)
            text_list.append(
                [(1880, 734+151*i+y0), str(battles_count), (0, 0, 0), 1, 35])
            text_list.append([(1880, 795+151*i+y0), str(win_rate) +
                              '%', color_box(0, win_rate)[1], 1, 35])
            text_list.append([(2096, 734+151*i+y0), str(damage),
                              color_box(1, n_damage)[1], 1, 35])
            text_list.append([(2096, 795+151*i+y0), str(frag),
                              color_box(2, n_frag)[1], 1, 35])

        elif is_user == False and user_id != None:
            if str(user_id) == str(userid):
                is_user = True
                cursor.execute("SELECT img FROM images WHERE id=?", (userid,))
                png_result = cursor.fetchone()
                if png_result is not None:
                    image_data = png_result[0]
                    user_png = Image.open(BytesIO(image_data))
                else:
                    user_png = Image.open(os.path.join(
                        file_path, 'png', 'default.png'))
                fontStyle = font_list[1][65]
                rank_num = str(i+1)
                w = x_coord(rank_num, fontStyle)
                text_list.append(
                    [(259-w/2, 742+151*21), rank_num, (0, 0, 0), 1, 65])
                fontStyle = font_list[1][55]
                w = x_coord('. . . . . .', fontStyle)
                text_list.append(
                    [(1214-w/2, 744+151*20), '. . . . . .', (0, 0, 0), 1, 55])
                x1 = 431-30
                y1 = 734+151*21-7
                y0 = -7
                res_img.paste(user_png, (x1, y1))
                user_png.close()
                user_name = formate_str(result['data'][aid]['user_name'], x_coord(
                    result['data'][aid]['user_name'], fontStyle), 630)
                text_list.append(
                    [(555-30, 734+151*21+y0), str(user_name), (0, 0, 0), 1, 55])
                game_id = result['data'][aid]['game_id']
                text_list.append(
                    [(555-30, 796+151*21+y0), str(game_id), (164, 164, 164), 1, 35])
                str_pr = str(int(pr))
                w = x_coord(str_pr, fontStyle)
                text_list.append([(1293-w/2, 760+151*21+y0), str_pr,
                                  pr_info(int(pr))[1], 1, 55])
                server = aid_to_server(aid)
                w = x_coord(server, fontStyle)
                text_list.append(
                    [(1612-w/2, 760+151*21+y0), server, (0, 0, 0), 1, 55])
                battles_count = result['data'][aid]['data']['battles_count']
                win_rate = round(result['data'][aid]['data']
                                 ['wins']/battles_count*100, 2)
                damage = int(result['data'][aid]['data']
                             ['damage_dealt']/battles_count)
                frag = round(result['data'][aid]['data']
                             ['frags']/battles_count, 2)
                text_list.append(
                    [(1880, 734+151*21+y0), str(battles_count), (0, 0, 0), 1, 35])
                text_list.append([(1880, 795+151*21+y0), str(win_rate) +
                                  '%', color_box(0, win_rate)[1], 1, 35])
                text_list.append([(2096, 734+151*21+y0), str(damage),
                                  color_box(1, damage)[1], 1, 35])
                text_list.append([(2096, 795+151*21+y0), str(frag),
                                  color_box(2, frag)[1], 1, 35])
        else:
            break
        i += 1
    if is_user == False and user_id != None and i > 20:
        fontStyle = font_list[1][65]
        rank_num = '-'
        w = x_coord(rank_num, fontStyle)
        text_list.append(
            [(259-w/2, 742+151*21), rank_num, (0, 0, 0), 1, 65])
        fontStyle = font_list[1][55]
        w = x_coord('......', fontStyle)
        text_list.append(
            [(1214-w/2, 744+151*20), '......', (0, 0, 0), 1, 55])
        user_name = '没有您的排名数据'
        text_list.append(
            [(555-30, 758+151*21+y0), str(user_name), (0, 0, 0), 1, 55])
        str_pr = '-'
        w = x_coord(str_pr, fontStyle)
        text_list.append([(1293-w/2, 760+151*21+y0), str_pr,
                          pr_info(-1)[1], 1, 55])
        server = '-'
        w = x_coord(server, fontStyle)
        text_list.append(
            [(1612-w/2, 760+151*21+y0), server, (0, 0, 0), 1, 55])
        text_list.append(
            [(1880, 734+151*21+y0), '-', (0, 0, 0), 1, 35])
        text_list.append([(1880, 795+151*21+y0), '-', (0, 0, 0), 1, 35])
        text_list.append([(2096, 734+151*21+y0), '-', (0, 0, 0), 1, 35])
        text_list.append([(2096, 795+151*21+y0), '-', (0, 0, 0), 1, 35])
    conn.close()
    fontStyle = font_list[1][80]
    w = x_coord(BOT_VERSON, fontStyle)
    if i <= 20:
        text_list.append(
            [(1214-w/2, 3758), BOT_VERSON, (174, 174, 174), 1, 80])
        res_img = add_text(text_list, res_img)
        res_img = res_img.crop((0, 0, 2429, 3875))
        res_img = res_img.resize((int(2429*0.5), int(3875*0.5)))
    else:
        text_list.append(
            [(1214-w/2, 4056), BOT_VERSON, (174, 174, 174), 1, 80])
        res_img = add_text(text_list, res_img)
        res_img = res_img.resize((int(2429*0.5), int(4214*0.5)))
    # res_img = res_img.resize((1214, 1936))
    return res_img


async def get_png(
    parameter: list,
):
    # [ship_id,ship_name,group_id,group_name,data,user_id]
    try:
        async with httpx.AsyncClient() as client:
            url = API_URL + '/group/rank/'
            data = {
                'token': API_TOKEN,
                'ship_id': parameter[0],
                'data': parameter[4]
            }

            res = await client.post(url, timeout=REQUEST_TIMEOUT, json=data)
            requset_code = res.status_code
            result = res.json()
            if requset_code == 200:
                pass
            else:
                return {'status': 'info', 'message': '数据接口请求失败'}
        if result['status'] != 'ok':
            return result
        if result['data'] == {}:
            return {'status': 'info', 'message': '无数据'}
        res_img = await main(
            result=result,
            group_id=parameter[2],
            group_name=parameter[3],
            ship_name=parameter[1],
            user_id=parameter[5]
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
    except (TimeoutException, ConnectTimeout, ReadTimeout) as err:
        return {'status': 'info', 'message': f'网络请求超时,请稍后重试,{type(err).__name__}'}
    except Exception as e:
        logging.exception(
            f"Time:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}, Parameter:{parameter[:4]}")
        return {'status': 'error', 'message': f'程序内部错误', 'error': str(type(e))}
