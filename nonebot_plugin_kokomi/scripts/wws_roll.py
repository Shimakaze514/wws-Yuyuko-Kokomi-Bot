import json
import os
import httpx
import time
import gc
import random
from httpx import (
    TimeoutException,
    ConnectTimeout,
    ReadTimeout
)
from .config import (
    REQUEST_TIMEOUT,
    API_URL,
    API_TOKEN
)
from .data_source import (
    a_tier_dict,
    a_type_dict
)

import logging

file_path = os.path.dirname(__file__)
parent_file_path = os.path.dirname(os.path.dirname(__file__))
# 配置日志输出到文件
logging.basicConfig(filename=os.path.join(
    file_path, 'log', 'error.log'), level=logging.ERROR)


def main(
    result: dict
):
    ship_name_file_path = os.path.join(
        parent_file_path, 'json', 'ship_name.json')
    temp = open(ship_name_file_path, "r", encoding="utf-8")
    ship_name_data = json.load(temp)
    temp.close()
    res_list = []
    for ship_id in result['data']['ships']:
        if (
            ship_id not in ship_name_data or
            '[' in ship_name_data[ship_id]['ship_name']['zh_sg'] or
            '(' in ship_name_data[ship_id]['ship_name']['zh_sg']
        ):
            continue

        ship_name = a_tier_dict[ship_name_data[ship_id]['tier']]+'  ' + \
            a_type_dict[ship_name_data[ship_id]['type']]+'  ' + \
            ship_name_data[ship_id]['ship_name']['zh_sg']
        res_list.append(ship_name)
    if res_list == []:
        return '该范围下没有查询到数据'
    else:
        return random.choice(res_list)


async def get_png(
    parameter: list,
):
    try:
        # [aid,server,select,use_pr,use_ac,ac]
        async with httpx.AsyncClient() as client:
            if parameter[4]:
                url = API_URL + '/user/roll/' + \
                    f'?token={API_TOKEN}&aid={parameter[0]}&server={parameter[1]}&select={parameter[2]}&use_ac=True&ac={parameter[5]}'
            else:
                url = API_URL + '/user/roll/' + \
                    f'?token={API_TOKEN}&aid={parameter[0]}&server={parameter[1]}&select={parameter[2]}'
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
            result=result
        )
        res = {'status': 'info', 'message': res_img}
        del res_img
        gc.collect()
        return res
    except (TimeoutException, ConnectTimeout, ReadTimeout):
        return {'status': 'info', 'message': '网络请求超时,请稍后重试'}
    except Exception as e:
        logging.exception(
            f"Time:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}, Parameter:{parameter}")
        return {'status': 'error', 'message': f'程序内部错误', 'error': str(type(e))}
