import httpx
import os
import sqlite3
import time
from httpx import (
    TimeoutException,
    ConnectTimeout,
    ReadTimeout
)
from .config import (
    API_TOKEN,
    API_URL,
    REQUEST_TIMEOUT
)
from .data_source import server_url
import logging

file_path = os.path.dirname(__file__)
text_list = []
# 配置日志输出到文件
logging.basicConfig(filename=os.path.join(
    file_path, 'log', 'error.log'), level=logging.ERROR)
parent_file_path = os.path.dirname(os.path.dirname(__file__))


def creat_db(
    new_db_path
):
    con = sqlite3.connect(new_db_path)
    cursorObj = con.cursor()
    cursorObj.execute('''CREATE TABLE bind_db
    (
        ID str PRIMARY KEY, 
        UID str,
        SERVER str,
        USEPR bool,
        USEAC bool,
        AC str
    )'''
                      )
    con.commit()
    con.close()


async def post_id(
    user_id: str,
    aid: str,
    server: str,
    platform: str
):
    async with httpx.AsyncClient() as client:
        url = API_URL + '/database/bind/' + \
            f'?token={API_TOKEN}&user_id={user_id}&aid={aid}&server={server}&platform={platform}'
        res = await client.get(url, timeout=REQUEST_TIMEOUT)
        requset_code = res.status_code
        result = res.json()
        if requset_code == 200:
            return result
        else:
            return {'status': 'info', 'message': '数据接口请求失败'}


async def search_id(
    game_id: str,
    server: str
):
    async with httpx.AsyncClient() as client:
        url = API_URL + '/user/search/' + \
            f'?token={API_TOKEN}&name={game_id}&server={server}'
        res = await client.get(url, timeout=REQUEST_TIMEOUT)
        requset_code = res.status_code
        result = res.json()
        if requset_code == 200:
            return result
        else:
            return {'status': 'info', 'message': '数据接口请求失败'}


async def main(
    parameter: list
):
    try:
        user_id = parameter[0]
        server = parameter[1]
        game_id = parameter[2]
        platform = parameter[3]
        search_data = await search_id(game_id=game_id, server=server)
        if search_data['status'] != 'ok':
            return search_data
        else:
            accountid = search_data['data']

        res = await post_id(
            user_id=str(user_id),
            aid=str(accountid),
            server=server,
            platform=platform
        )
        if res['status'] == 'ok':
            pass
        else:
            return res
    except (TimeoutException, ConnectTimeout, ReadTimeout):
        return {'status': 'info', 'message': '网络请求超时,请稍后重试'}
    except Exception as e:
        logging.exception(
            f"Time:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}, Parameter:{parameter}")
        return {'status': 'error', 'message': f'程序内部错误,Error:{type(e).__name__}', 'error': str(type(e))}
