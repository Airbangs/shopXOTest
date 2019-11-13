#!/usr/local/bin/python3
# -*- coding: UTF-8 -*-
"""
适用在线、local版靶机，注册时均需输入文字验证码
"""

__author__ = 'Alina'

from selenium.common.exceptions import TimeoutException
import time,json,random,requests,pyautogui
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from NumSet import params
from selenium.webdriver.common.action_chains import ActionChains


"""
根据是否使用代理选择不同的驱动方式
"""
if params.chioceProxy == 1:
    print("已选择使用代理，速度会较慢，请知悉。")
    # 初始化webdriver
    chromeOptions = webdriver.ChromeOptions()
    # 设置代理
    chromeOptions.add_argument("--proxy-server=http://"+requests.get(params.proxyUrl).text)
    # 修改window.navigator.webdriver：在启动Chromedriver之前，为Chrome开启实验性功能参数
    chromeOptions.add_experimental_option('excludeSwitches', ['enable-automation'])
    # 设置不启动chrome的自动保存密码
    prefs = {"": ""}
    prefs["credentials_enable_service"] = False
    prefs["profile.password_manager_enabled"] = False
    chromeOptions.add_experimental_option("prefs", prefs)
    browser = webdriver.Chrome(chrome_options=chromeOptions)
else:
    print("已选择不使用代理")
    # 初始化webdriver
    chromeOptions = webdriver.ChromeOptions()
    # 修改window.navigator.webdriver：在启动Chromedriver之前，为Chrome开启实验性功能参数
    chromeOptions.add_experimental_option('excludeSwitches', ['enable-automation'])
    # 设置不启动chrome的自动保存密码
    prefs = {"": ""}
    prefs["credentials_enable_service"] = False
    prefs["profile.password_manager_enabled"] = False
    chromeOptions.add_experimental_option("prefs", prefs)
    browser = webdriver.Chrome(chrome_options=chromeOptions)

"""
根据测试站点情况选择是否 执行 关闭广告：连网时（即值为0时）进行操作 -> 关闭广告，未连网时不操作关闭广告；
"""
if params.chioceTargetDrone == 0:
    # 打开在线版靶机
    browser.get(params.demoOnlineUrl)
    browser.refresh()
    try:
        # 关闭广告
        adEle = WebDriverWait(browser, 10).until(lambda browser: browser.find_element_by_css_selector(
            "a.am-close.am-close-alt.am-close-spin.am-icon-times.am-fr.submit-ajax"))
        browser.execute_script("arguments[0].click();", adEle)
    except TimeoutException as msg:
        print("打开广告失败，直接进行下一步。")

else:
    # 打开本地版靶机
    browser.get(params.localUrl)
    browser.refresh()

# 轮询字典中的username
file = open(params.filePath_regist)
context = file.readlines()
users = []
pwords = []
for i in context:
    username = i.split(',')[0]
    password = i.split(',')[1]
    users.append(username)
    pwords.append(password)
    file.close()

# 调用第三方识别验证码
def base64_api(uname, pwd, softid, b64):

    data = {"username": uname, "password": pwd, "softid": softid, "image": b64}
    result = json.loads(requests.post("http://api.ttshitu.com/base64", json=data).text)
    if result['success']:
        return result["data"]["result"]
    else:
        return result["message"]
    return ""

# 模拟鼠标随机移动-不带轨迹
def mov_mouse_byxy():
    for i in range(10):
        x = random.randint(1, 1000)
        y = random.randint(1, 600)
        ActionChains(browser).move_by_offset(x, y)
        print("鼠标随机移动到坐标：", x, y)
    return ""

# 模拟鼠标随机移动-带轨迹（mac需在安全设置中开启脚本应用软件的支持）
def mov_mouse_random():
    for i in range(3):
        x = random.randint(1, 1000)
        y = random.randint(1, 600)
        pyautogui.moveTo(x, y, duration=0.25)
        # print("鼠标随机移动到坐标：", x, y)
    return ""

"""
模拟手动注册->自动登录->模拟手动退出
"""
def regist(username,password):
    browser.refresh()
    # 点击注册
    regEle = WebDriverWait(browser, 10).until(
        lambda browser: browser.find_element_by_css_selector("ul.top-nav-left>div>div>a:nth-child(4)"))
    browser.execute_script("arguments[0].click();", regEle)
    # 输入用户名
    usernameEle = WebDriverWait(browser, 10).until(lambda browser: browser.find_element_by_css_selector(
        "body > div.am-g.my-content.user-register-container > div > div > div > div.register-content > div.am-tabs.am-tabs-d2.am-no-layout > div > div.am-tab-panel.am-active > form > div:nth-child(1) > input"))
    usernameEle.send_keys(username)
    # 输入登录密码
    pwEle = WebDriverWait(browser, 10).until(lambda browser: browser.find_element_by_css_selector(
        ".am-form.form-validation-username>div:nth-child(2)>div>input"))
    pwEle.send_keys(password)
    """
    获取并输入验证码
    """
    # 获取验证码code: 打码平台 http://www.ttshitu.com/ 
    result = base64_api('username', 'password', 'pid',
                        browser.find_element_by_id('form-verify-img').screenshot_as_base64)
    # browser.find_element_by_id('form-verify-img').screenshot('%s.png' % time.time())
    print(result)
    # 输入验证码
    yzEle = WebDriverWait(browser, 10).until(
        lambda browser: browser.find_element_by_css_selector(
            ".am-form.form-validation-username>div:nth-child(3)>div>input"))
    yzEle.send_keys(result)
    # 随机移动鼠标
    mov_mouse_random()
    # 勾选同意
    browser.find_element_by_css_selector(
        "form.am-form.form-validation-username>div:nth-child(4)>label>span>i:nth-child(2)").click()
    # 随机移动鼠标
    mov_mouse_random()
    # 点击【注册】
    browser.find_element_by_css_selector("form.am-form.form-validation-username>div:nth-child(5)>button").click()
    time.sleep(1)
    """
    注意：这边的等待时长不可省略，因为跳转需要时间。否则会校验失败
    """
    if WebDriverWait(browser, 10).until(lambda browser: browser.find_element_by_css_selector("ul.top-nav-left a")).is_displayed():
        browser.refresh()
        print(browser.find_element_by_css_selector("ul.top-nav-left a").text)
        assert browser.find_element_by_css_selector("ul.top-nav-left a").text == "退出"
        print(username, "断言通过，注册成功。")
    else:
        print("注册可能失败。")
    time.sleep(2)
    # 点击退出以便进行下一次循环
    browser.execute_script("arguments[0].click();", browser.find_element_by_css_selector("ul.top-nav-left a"))

"""
调用自动注册
"""
for i,j in zip(users,pwords):
    regist(i,j)

# 退出浏览器
browser.quit()

