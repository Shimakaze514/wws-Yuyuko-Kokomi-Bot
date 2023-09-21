import httpx
import logging
import time
import os
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
file_path = os.path.dirname(__file__)
# 配置日志输出到文件
logging.basicConfig(filename=os.path.join(
    file_path, 'log', 'error.log'), level=logging.ERROR)


async def search_id(
    user_id: str,
    platform: str
):
    if platform not in ['qq', 'kook', 'discord', 'qqguild']:
        return {'status': 'info', 'message': '暂时不支持当前平台'}
    parameter = [user_id, platform]
    try:
        async with httpx.AsyncClient() as client:
            url = API_URL + '/user/platform/' + \
                f'?token={API_TOKEN}&user_id={user_id}&platform={platform}'
            res = await client.get(url, timeout=REQUEST_TIMEOUT)
            requset_code = res.status_code
            result = res.json()
            if requset_code == 200:
                return result
            else:
                return {'status': 'info', 'message': '数据接口请求失败'}
    except (TimeoutException, ConnectTimeout, ReadTimeout):
        return {'status': 'info', 'message': '网络请求超时,请稍后重试'}
    except Exception as e:
        logging.exception(
            f"Time:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}, Parameter:{parameter}")
        return {'status': 'error', 'message': f'程序内部错误', 'error': str(type(e))}


async def search_clan(
    aid: str,
    server: str
):
    parameter = [aid, server]
    try:
        async with httpx.AsyncClient() as client:
            url = API_URL + '/user/clan/' + \
                f'?token={API_TOKEN}&aid={aid}&server={server}'
            res = await client.get(url, timeout=REQUEST_TIMEOUT)
            requset_code = res.status_code
            result = res.json()
            if requset_code == 200:
                return result
            else:
                return {'status': 'info', 'message': '数据接口请求失败'}
    except (TimeoutException, ConnectTimeout, ReadTimeout):
        return {'status': 'info', 'message': '网络请求超时,请稍后重试'}
    except Exception as e:
        logging.exception(
            f"Time:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}, Parameter:{parameter}")
        return {'status': 'error', 'message': f'程序内部错误', 'error': str(type(e))}


async def search_clan_id(
    clan_name: str,
    server: str
):
    parameter = [clan_name, server]
    try:
        async with httpx.AsyncClient() as client:
            url = API_URL + '/clan/search/' + \
                f'?token={API_TOKEN}&clan_name={clan_name}&server={server}'
            res = await client.get(url, timeout=REQUEST_TIMEOUT)
            requset_code = res.status_code
            result = res.json()
            if requset_code == 200:
                return result
            else:
                return {'status': 'info', 'message': '数据接口请求失败'}
    except (TimeoutException, ConnectTimeout, ReadTimeout):
        return {'status': 'info', 'message': '网络请求超时,请稍后重试'}
    except Exception as e:
        logging.exception(
            f"Time:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}, Parameter:{parameter}")
        return {'status': 'error', 'message': f'程序内部错误', 'error': str(type(e))}


async def search_user_id(
    name: str,
    server: str
):
    parameter = [name, server]
    try:
        async with httpx.AsyncClient() as client:
            url = API_URL + '/user/search/' + \
                f'?token={API_TOKEN}&name={name}&server={server}'
            res = await client.get(url, timeout=REQUEST_TIMEOUT)
            requset_code = res.status_code
            result = res.json()
            if requset_code == 200:
                return result
            else:
                return {'status': 'info', 'message': '数据接口请求失败'}
    except (TimeoutException, ConnectTimeout, ReadTimeout):
        return {'status': 'info', 'message': '网络请求超时,请稍后重试'}
    except Exception as e:
        logging.exception(
            f"Time:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}, Parameter:{parameter}")
        return {'status': 'error', 'message': f'程序内部错误,Error:{type(e).__name__}', 'error': str(type(e))}
