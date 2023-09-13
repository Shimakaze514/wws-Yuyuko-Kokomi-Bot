import httpx
import os
import gc
import time
from httpx import (
    TimeoutException,
    ConnectTimeout,
    ReadTimeout
)
from .config import (
    API_TOKEN,
    API_URL,
    REQUEST_TIMEOUT,
    PLATFORM
)
from .data_source import server_url
import logging

file_path = os.path.dirname(__file__)
text_list = []
# 配置日志输出到文件
logging.basicConfig(filename=os.path.join(
    file_path, 'log', 'error.log'), level=logging.ERROR)
parent_file_path = os.path.dirname(os.path.dirname(__file__))


async def main(
    parameter: list,
):
    try:
        # [user_id,use_pr]
        async with httpx.AsyncClient() as client:
            url = API_URL + '/database/pr/' + \
                f'?token={API_TOKEN}&user_id={parameter[0]}&use_pr={parameter[1]}&platform={PLATFORM}'

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
        return {'status': 'error', 'message': f'程序内部错误', 'error': str(type(e))}
