import random
import traceback
from nonebot import on_command, get_driver
from nonebot.adapters.onebot.v11 import (
    ActionFailed,
    Bot,
    MessageEvent,
    MessageSegment,
    GroupMessageEvent,
)
from nonebot.log import logger
from .scripts.config import BLACKLIST, WHITELIST

from .command_select import select_funtion

driver = get_driver()
wws_bot = on_command("wws")  # 以wws开头的消息将被触发


def group_data_formate(group_data: dict):
    # 处理群用户列表的信息，删除无用数据
    processed_data = {}
    for group_member in group_data:
        processed_data[group_member['user_id']] = group_member['nickname']
    return processed_data


@wws_bot.handle()
async def main(bot: Bot, ev: MessageEvent):
    if driver.config.pupu and random.randint(1, 1000) == 1:
        wws_bot.send('一天到晚惦记你那b水表，就nm离谱')
    else:
        try:
            session_id = str(ev.get_session_id())
            # 判断消息类型，私聊/群聊
            if 'group' in session_id:
                split_id = session_id.split('_')
                qq_id = split_id[2]
                gruop_id = split_id[1]
            else:
                qq_id = session_id
                gruop_id = None
            group_name = 'None'
            group_data = None
            # 黑名单
            if gruop_id in BLACKLIST:
                return
            # 白名单
            if gruop_id != None and WHITELIST != [] and gruop_id not in WHITELIST:
                return
            # 国服id带空格的特殊处理
            if 'wws cn set ' in str(ev.message) or 'wws 国服 set ' in str(ev.message):
                split_msg = ['wws', 'cn', 'set', str(ev.message)[11:]]
            else:
                split_msg = str(ev.message).split()  # 按空格分隔消息

            if len(split_msg) == 1:
                return
            # group rank 获取相关群聊数据
            if gruop_id != None and 'group' in split_msg:
                # 群聊用户列表
                group_data = await bot.get_group_member_list(group_id=gruop_id)
                group_data = group_data_formate(group_data)
                group_info = await bot.get_group_list()  # 群聊信息
                for index in group_info:
                    if str(index['group_id']) == gruop_id:
                        group_name = index['group_name']
                    else:
                        continue
            # 消息 -> 函数
            fun = await select_funtion.main(
                message=split_msg,
                user_id=qq_id,
                group_id=gruop_id,
                group_name=group_name,
                group_data=group_data
            )
            if fun['status'] != 'ok':
                await wws_bot.send(fun['message'])
            else:
                # 调用函数
                function = fun['function']
                result = await function(fun['parameter'])
                if result['status'] == 'ok':
                    await wws_bot.send(MessageSegment.image(result['img']))
                elif result['status'] == 'info':
                    await wws_bot.send(result['message'])
                else:
                    await wws_bot.send(result['message'])
        except ActionFailed:
            return False
        except Exception:
            logger.error(traceback.format_exc())
            await bot.send(ev, "error")
