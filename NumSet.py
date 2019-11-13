#!/usr/local/bin/python3
# -*- coding: UTF-8 -*-
__author__ = 'Alina'

class params:

    """
    配置是否使用代理: 1 = 使用代理，0 = 不用代理，默认为0
    """
    chioceProxy = 0
    # 获取代理ip地址：芝麻代理 http://www.zhimaruanjian.com/ 
    proxyUrl = '****'

    """
    配置靶机为在线版 or 本地版：1 = 本地版，0 = 在线版，默认为0
    """
    chioceTargetDrone = 1
    # 在线版靶机url
    demoOnlineUrl = 'https://demo.shopxo.net/'
    # 本地版靶机url
    localUrl = 'http://172.24.24.102:8080'   # 仅内网可访问

    # 登录时的用户名字典文件路径
    filePath_login = "./dict_login.txt"
    filePath_regist = "./dict_regist.txt"


