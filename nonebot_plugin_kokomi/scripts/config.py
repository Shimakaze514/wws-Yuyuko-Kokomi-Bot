import os
from nonebot import get_driver
import json

driver = get_driver()

token_data = json.load(
    open(
        os.path.join(
            os.path.dirname(
                os.path.dirname(__file__)
            ),
            'token.json'
        ),
        "r",
        encoding="utf-8"
    )
)

DOG_TAG = True  # 是否启用用户的徽章（狗牌）显示，关闭显示可以提高响应速度，请根据需要选择
SHIP_PREVIEW = True  # 是否启用船只图片显示，关闭显示可以提高响应速度，请根据需要选择
REQUEST_TIMEOUT = 15  # 请求接口超时时间
LAST_CW_MUNBER = '22'
BOT_VERSON = 'Nonebot-Plugin-Kokomi  3.3.0 + MioMeowBot'
BOT_AUTHOR = 'Powered by [TIF-K]SangonomiyaKokomi_(ASIA) & [ARP]Unterwasser_Mutter_Jager'
API_URL = token_data['kokomi_basic_api'].get('url', None)  # kkm数据接口
API_TOKEN = token_data['kokomi_basic_api'].get('token', None)  # 数据接口token
PLATFORM = 'qq'  # 平台代码（qq/qqguild/kook/discord）
# 群聊黑名单，如果群聊id再黑名单内则无法响应，默认屏蔽kkm和yyk的开发者群
BLACKLIST = driver.config.ban_group_list
WHITELIST = driver.config.allowed_group_list  # 群聊白名单，只有白名单内的群聊可触发，为[]表示无限制
PIC_TYPE = 'base64'  # 发送图片使用的协议（base64/file），qq平台请使用base64
# 如果消息未匹配到函数时的处理方式（default/info），default表示直接跳过无响应，info表示返回文字提示
NOTFOUND_STATUS = 'default'
FUNCTION_CONFIG = [
    # [是否启用对应的功能，是否使用本地数据接口]
    # 如果需要关闭指定功能，就将对应功能的第一个值True改为False，关闭后该功能将不会响应
    # 请不要调整list的顺序
    [True, False],  # wws help
    [True, False],  # wws me
    [True, False],  # wws me info
    [True, False],  # wws me rank
    [True, False],  # wws me cw
    [True, False],  # wws me recent
    [True, False],  # wws me rank recent
    [True, False],  # wws me ship
    [True, False],  # wws me ships
    [True, False],  # wws me rank ship
    [True, False],  # wws me rank season
    [True, False],  # wws me clan
    [True, False],  # wws me clan season
    [True, False],  # wws me clan season all
    [True, False],  # wws me clan cw
    [True, False],  # wws me sx
    [True, False],  # wws me ship rank
    [True, False],  # wws 服务器 ship rank
    [True, False],  # wws me group ship rank
    [True, False],  # wws group ship rank
    [True, False],  # wws roll
    [True, False],  # wws pr on/off
    [True, False],  # wws game server
    [True, False],  # wws ship server
    [True, False],  # wws search
    [True, False],  # wws 服务器 set id
    [True, False],  # wws bind
    [True, False],  # wws box
    [True, False],  # wws me recents
    [True, False]   # wws recents on
]
