# Kokomi + Yuyuko 杂交子一代（F1）

小孩子才在两个机器人之间做选择，我全都要。于是就有了这个项目
> [!NOTE]
> 本项目基于nonebot2，并默认你会搭建wws水表机器人。
> 
> 本项目旨在提供一个方便快捷的整合两个水表机器人的方式。


## 主要功能

 - 整合了HikariBot(Yuyuko)和Kokomi的全部功能。
 - 可以自定义两个水表插件的分工（例如wws me使用kkm，recent使用yyk）。
 - 为kkm添加了水表屏蔽功能，共享hikari的配置文件。可以屏蔽部分群聊，不响应水表查询。


## 安装
0. 去看看[hikari依赖的模块](https://github.com/benx1n/HikariBot#%E5%9C%A8windows%E7%B3%BB%E7%BB%9F%E4%B8%8A%E5%AE%8C%E6%95%B4%E9%83%A8%E7%BD%B2)和[kokomi依赖的模块](https://github.com/SangonomiyaKoko/nonebot_plugin_kokomi#%E7%AC%AC%E4%B8%80%E6%AD%A5-%E9%85%8D%E7%BD%AE%E7%8E%AF%E5%A2%83)并且全部安装好
1. 安装**hikari_core**
   - 解压你下载的wws-yuyuko-kokomi-bot-master.zip
   - 把解压出来的文件夹丢进你的nonebot2项目文件夹，然后在该目录下打开powershell（或者右键→用vscode打开，然后进入终端）
   - 运行以下命令（其实就是安装这个包而已）
     ```
     cd hikari_core
     pip install .
     ```
3. 用你喜欢的方式以插件的形式安装**hikari_bot**和**nonebot_plugin_kokomi** 
~~什么？你不会装插件？求求你百度或者Google亿下~~

4. ```nb run```


## 父母的git地址

[Hikari](https://github.com/benx1n/HikariBot)

[Kokomi_bot_plugin](https://github.com/SangonomiyaKoko/nonebot_plugin_kokomi)
