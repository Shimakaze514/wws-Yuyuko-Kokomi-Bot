import os
from nonebot import get_driver

driver = get_driver()

DOG_TAG = True  # 是否启用用户的徽章（狗牌）显示
SHIP_PREVIEW = True
POST_ID = True  # 测试环境遗留配置，默认请改为True
REQUEST_TIMEOUT = 10  # 请求接口超时时间
LAST_CW_MUNBER = '22'
BOT_VERSON = 'KokomiBot 3.2.9 @Maoyu'
API_URL = 'http://www.wows-coral.com:443'  # 默认数据接口
API_TOKEN = ''
PLATFORM = 'qq'
BLACKLIST = driver.config.ban_group_list  # 群聊黑名单，如果群聊id再黑名单内则无法响应，参数为 str 类型
WHITELIST = driver.config.allowed_group_list  # 群聊白名单，只有白名单内的群聊可触发，为[]表示无限制，参数为 str 类型
PIC_TYPE = 'base64'  # 发送图片使用的协议（base64/file），qq平台请使用base64
# 如果图片类型为file则需要配置,默认为上一目录中的temp文件
PIC_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp')
