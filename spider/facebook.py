# coding:utf-8
import os
import sys

sys.path.append("./..")
from logs.loggerDefine import loggerDefine

youtubeDir = "./../logs/facebook/"
if not os.path.exists(youtubeDir):
    os.makedirs(youtubeDir)
loggerFile = youtubeDir + "facebook.log"
logging = loggerDefine(loggerFile)
import time
from tools.option import getOption
import re
from selenium import webdriver
from lxml import etree
import traceback


def login(driver):
    driver.get("https://www.facebook.com/login")
    # 通过执行js语句为元素添加target="_blank"属性
    if sys.argv[1] == "debug":
        # 输入用户名
        # driver.find_element_by_id("email").send_keys("tanya.beleutova.beleutova@mail.ru")
        driver.find_element_by_id("email").send_keys("huguangjing211@gmail.com")
        # 输入密码
        # driver.find_element_by_id("pass").send_keys("yoan6SNoer")
        driver.find_element_by_id("pass").send_keys("hgj212816")
        # 点击登录
        driver.find_element_by_id("loginbutton").click()
    else:
        driver.find_element_by_id("email").send_keys("958905350@qq.com")
        driver.find_element_by_id("pass").send_keys("withyou1314")
        driver.find_element_by_id("loginbutton").click()
    logging.info("登录成功")
    logging.info(driver.current_url)
    time.sleep(5)
    for keyWord in ["小米", "华为", "oppo", "vivo", "Apple", "三星"]:
        url = "https://www.facebook.com/search/groups/?q={}".format(keyWord)
        js = 'window.open("{}");'.format(url)
        driver.execute_script(js)
        time.sleep(2)
        driver.switch_to_window(driver.window_handles[1])

        # print(driver.page_source)
        search(driver)


def search(driver):
    driver.switch_to.window(driver.window_handles[1])
    try:
        cc = 1
        js = 'window.scrollTo(0, document.body.scrollHeight)'
        # flag = True
        linkList = []
        # while flag and cc < 0:
        #     driver.execute_script(js)
        #     try:
        #         driver.find_element_by_xpath('//div[contains(text(),"已经到底啦~")]')
        #         flag = False
        #         print("已经到底啦")
        #     except NoSuchElementException:
        #         flag = True
        #     cc += 1
        #     time.sleep(5)
        responseBody = driver.page_source
        selector = etree.HTML(responseBody)

        titleNode = selector.xpath('//div[@class="_gll"]')
        for title in titleNode:
            try:
                # 链接
                link = "https://www.facebook.com" + title.xpath("./div//a/@href")[0]
                link = re.match(r"(https://www.facebook.com/groups/.+/)", link).group(1) + "about"
                linkList.append(link)
            except Exception as e:
                print(e)
        for url in linkList:
            js = 'window.open("{}");'.format(url)
            driver.execute_script(js)

        handles = driver.window_handles
        driver.switch_to_window(handles[0])
        currentHandle = driver.current_window_handle
        for handle in handles:
            if handle != currentHandle:
                driver.switch_to_window(handle)
                if "search" not in driver.current_url:
                    time.sleep(1)
                    text = checkText(driver.page_source.encode("utf-8", "ignore"), driver.current_url)
                    if not text:
                        time.sleep(1)
                    parsePage(driver.page_source.encode("utf-8", "ignore"), driver.current_url)
                driver.close()
                driver.switch_to_window(handles[0])
        driver.switch_to.default_content()

    except Exception as e:
        print(traceback.format_exc())


def checkText(response, url):
    url = re.match(r"(https://www.facebook.com/groups/.+?)/.*", url).group(1)
    selector = etree.HTML(response)
    text = selector.xpath('//div[@id="pagelet_group_about"]//text()')
    textStr = ""
    for i in text:
        textStr += i.strip()
    textStr = textStr.replace("\n", "")
    if not textStr:
        logging.info("没有text,url:{}".format(url))
        return ""
    else:
        return textStr


def parsePage(response, url):
    url = re.match(r"(https://www.facebook.com/groups/.+?)/.*", url).group(1)
    selector = etree.HTML(response)

    text = selector.xpath('//div[@id="pagelet_group_about"]//text()')
    textStr = ""
    for i in text:
        textStr += i.strip() + "_"
    textStr = textStr.replace("\n", "")
    if not textStr:
        return

    # 小组说明
    try:
        description = re.search(r"小组说明(.+?)查看更多", textStr).group(1)
    except Exception as e:
        description = ""
    logging.info("description:{}".format(description))

    # 群名称
    groupName = selector.xpath('//h1[@id="seo_h1_tag"]/a/text()')
    if not groupName:
        logging.warn("没有获取到groupName,  url:{}".format(url))
        return
    groupName = groupName[0]
    logging.info("groupName:{},url:{}".format(groupName, url))

    # 群成员
    groupNum = selector.xpath('//div[@id="pagelet_group_about"]/div[2]/div[1]//text()')
    try:
        groupNum = re.search(r"(\d+.*?\d+)", groupNum[0]).group(1)
    except Exception as e:
        print(url)
        print(e)
        return
    logging.info("groupNum:{},url:{}".format(groupNum, url))
    # 小组类型
    groupType = selector.xpath('//div[@id="pagelet_group_about"]/div[1]/div[2]//div[2]/text()')
    if not groupType:
        return
    groupType = groupType[0]
    logging.info("groupType:{}".format(groupType))

    # 过去 30 天内有 228 篇
    postNum = selector.xpath('//div[@id="pagelet_group_about"]/div[3]/div[2]//div[last()]/text()')
    if not postNum:
        return
    try:
        postNum = re.search(r"有(.+?)篇", postNum[0]).group(1).strip()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    if sys.argv[1] == "debug":
        options = getOption(False)
        driver = webdriver.Chrome(chrome_options=options)
    else:
        options = getOption(True)
        driver = webdriver.Chrome(executable_path="./chromedriver", chrome_options=options)
    login(driver)
    while True:
        time.sleep(5)
