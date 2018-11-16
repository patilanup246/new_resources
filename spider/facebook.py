# coding:utf-8
import os
import sys

from selenium.common.exceptions import NoSuchElementException

sys.path.append("./..")
from db.mongodb import connectMongo
from logs.loggerDefine import loggerDefine

youtubeDir = "./../logs/facebook/"
if not os.path.exists(youtubeDir):
    os.makedirs(youtubeDir)
loggerFile = youtubeDir + "facebooklog.log"
logging = loggerDefine(loggerFile)
import time
from tools.option import getOption
import re
from selenium import webdriver
from lxml import etree
import traceback
import threading
import random

db = connectMongo(True)
collection = db["keyWords"]

errNode = 0

userPsdItem = {
    # "wuzeronger@live.com": "wuzeronger123",
    # "958905350@qq.com": "withyou1314",  # 已经被禁止搜索具体群组
    "2933219312@qq.com": "Citic231104",
    # "tanya.beleutova.beleutova@mail.ru": "yoan6SNoer",  # 需要验证手机号码
    # "huguangjing211@gmail.com": "hgj212816"  # 已经被禁止搜索小组,搜不到任何东西
}


def loginFB(driver, part, url, userName, psd):
    try:
        logging.info("开始起始地址:{}".format(url))
        driver.get(url)
        # 输入用户名
        driver.find_element_by_id("email").send_keys(userName)
        # 输入密码
        driver.find_element_by_id("pass").send_keys(psd)
        # 点击登录
        driver.find_element_by_id("loginbutton").click()
        logging.info("用户名:{},密码:{},输入用户名和密码后,当前页面url是:{}".format(userName, psd, driver.current_url))
        checkNum = 0
        while True:
            if driver.current_url == "https://www.facebook.com/checkpoint/?next":
                checkNum += 1
                logging.error("跳转到验证界面{}次".format(checkNum))
                driver.find_element_by_id("checkpointSubmitButton").click()
                if checkNum >= 10:
                    # 防止出现需要验证手机号码情况,直接切换账号重开线程
                    logging.warn("已经验证了{}次,可能出现需要验证手机情况,退出线程,重开账号进行验证".format(checkNum))
                    driver.quit()
                    return
                time.sleep(1)
            else:
                break
        # time.sleep(1)
        if driver.current_url != "https://www.facebook.com/":
            logging.warn("输入密码和用户名后,跳转的界面不是主页,{}".format(driver.current_url))
            driver.quit()
            return
        else:
            response = driver.page_source
            selector = etree.HTML(response)
            nodeResult = selector.xpath('//*[@id="pagelet_rhc_footer"]/div/div[1]/div/div/div[1]/div/span[1]/text()')
            if nodeResult:
                if nodeResult[0] != "中文(简体)":
                    logging.error("非中文页面")
                    driver.find_element_by_xpath('//a[@lang="zh_CN"]').click()
                    time.sleep(1)
                    """//div[@class="_4t2a"]//button"""
                    driver.find_element_by_xpath('//div[@class="_4t2a"]//button').click()
                    time.sleep(1)
        # keyWordList = list(collection.distinct("keyWord", {"getData": False}))[:1000]
        keyWordList = ["xiaomi","华为","apple"]

        # 跳转到小组界面
        keyWordDeal(keyWordList, driver, userName)
    except Exception as e:
        logging.error(traceback.format_exc())
        driver.quit()
        return


def keyWordDeal(keyWordList, driver, userName):
    global errNode
    try:
        for keyWord in keyWordList:
            keyWordNew = keyWord.replace(" ", "+")
            url = "https://www.facebook.com/search/str/{}/keywords_groups".format(keyWordNew)
            js = 'window.open("{}");'.format(url)
            driver.execute_script(js)
            time.sleep(2)
            driver.switch_to_window(driver.window_handles[1])
            logging.info("新开窗口,切换到小组窗口界面,url:{}".format(driver.current_url))

            responseBody = driver.page_source
            selector = etree.HTML(responseBody)

            logging.info("解析小组页面详细url,关键字:{}".format(keyWord))
            titleNode = selector.xpath('//div[@class="_gll"]/div//a/@href')
            if not titleNode:
                errNode += 1
                logging.error("没有搜索到相关信息,关键字:{},url:{}".format(keyWord, url))
                driver.close()
                driver.switch_to_window(driver.window_handles[0])
                # driver.switch_to.default_content()
                continue

            if errNode >= 100:
                logging.warn("搜索功能可能已经被已经被禁用,用户名:{}".format(userName))
                driver.quit()
                errNode = 0
                return

            # 处理具体的群组信息
            groupDeal(driver, keyWord, userName)
    except Exception as e:
        driver.quit()
        return


def groupDeal(driver, keyWord, userName):
    try:
        scroll = 1
        js = 'window.scrollTo(0, document.body.scrollHeight)'
        linkList = []
        while True:
            try:
                driver.find_element_by_xpath('//div[contains(text(),"已经到底啦~")]')
                logging.info("已经到底啦")
                break
            except NoSuchElementException:
                logging.info("滚动滚动条{}次,关键字:{}".format(scroll, keyWord))
                scroll += 1
                driver.execute_script(js)
                time.sleep(1)
        responseBody = driver.page_source
        selector = etree.HTML(responseBody)

        logging.info("解析小组页面详细url,关键字:{}".format(keyWord))
        # titleNodeList = selector.xpath('//div[@class="_gll"]/div//a/@href')
        titleNodeList = selector.xpath('//div[@class="_gll"]')
        groupNodeList = selector.xpath('//div[@class="_glm"]')
        descrNodeList = selector.xpath('//div[@class="_glo"]')

        for titleNode, groupNode, descrNode in zip(titleNodeList, groupNodeList, descrNodeList):
            try:
                descriptionList = descrNode.xpath('./div/div/div/text()')
                if not descriptionList:
                    # 没有评论信息
                    description = ""
                elif len(descriptionList) == 1:
                    # 代表只有描述信息
                    description = descriptionList[0].strip()
                else:
                    description = descriptionList[-1].strip()

                if description.endswith("小组"):
                    description = ""

                # 链接
                groupNumStr = groupNode.xpath('./div//text()')[0]
                if "万位成员" in groupNumStr:
                    pass
                else:
                    groupNum = int(re.search(r"(.*?)位成员", groupNumStr).group(1).replace(",", "").strip())
                    if groupNum < 1000:
                        continue
                link = "https://www.facebook.com" + titleNode.xpath('./div//a/@href')[0]
                link = re.match(r"(https://www.facebook.com/groups/.+/)", link).group(1) + "about"
                if link not in linkList:
                    linkList.append(link)
            except Exception as e:
                logging.error(traceback.format_exc())
        if not linkList:
            logging.error("没有查到相关数据,keyWord:{}".format(keyWord))
            return
        else:
            time.sleep(1)

        # 每次打开五个页面
        if len(linkList) <= 5:
            for url in linkList:
                js = 'window.open("{}");'.format(url)
                driver.execute_script(js)
                time.sleep(1)

            handles = driver.window_handles
            driver.switch_to_window(handles[0])
            currentHandle = driver.current_window_handle
            for handle in handles:
                if handle != currentHandle:
                    driver.switch_to_window(handle)
                    try:
                        url = re.match(r"(https://www.facebook.com/groups/.+?)/.*", driver.current_url).group(1)
                    except Exception as e:
                        url = ""
                    if url:
                        text = checkText(driver.page_source.encode("utf-8", "ignore"), url)
                        if not text:
                            time.sleep(3)
                        parsePage(driver.page_source.encode("utf-8", "ignore"), url)
                    driver.close()
                    driver.switch_to_window(handles[0])
            driver.switch_to.default_content()
        else:
            # 每次处理五个
            while True:
                fiveList = linkList[:5]
                if not fiveList:
                    break

                for url in fiveList:
                    js = 'window.open("{}");'.format(url)
                    linkList.remove(url)
                    driver.execute_script(js)
                    time.sleep(1)

                handles = driver.window_handles
                driver.switch_to_window(handles[0])
                currentHandle = driver.current_window_handle
                for handle in handles:
                    if handle != currentHandle:
                        driver.switch_to_window(handle)
                        if "操作过快" in driver.page_source:
                            logging.warn('操作过快,导致没有搜索详情权限,用户名:{}'.format(userName))
                            driver.quit()
                            return
                        try:
                            url = re.match(r"(https://www.facebook.com/groups/.+?)/.*", driver.current_url).group(1)
                        except Exception as e:
                            url = ""
                        if url:
                            text = checkText(driver.page_source.encode("utf-8", "ignore"), url)
                            if not text:
                                time.sleep(3)
                            parsePage(driver.page_source.encode("utf-8", "ignore"), url)
                        driver.close()
                        driver.switch_to_window(handles[0])
                driver.switch_to.default_content()


    except Exception as e:
        driver.quit()
        logging.error(traceback.format_exc())
        return


def checkText(response, url):
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
    selector = etree.HTML(response)
    text = selector.xpath('//div[@id="pagelet_group_about"]//text()')
    textStr = ""
    for i in text:
        textStr += i.strip() + "#"
    textStr = textStr.replace("\n", "")
    if not textStr:
        logging.warn("二次没有数据,url:{}".format(url))
        return

    # 小组说明
    try:
        description = re.search(r"小组说明(.+?)查看更多", textStr).group(1)
        description = description.replace("#", "\n").strip()
    except Exception as e:
        description = "have no description"

    # 群名称
    groupName = selector.xpath('//h1[@id="seo_h1_tag"]/a/text()')
    if not groupName:
        logging.warn("没有获取到groupName,  url:{}".format(url))
        return
    groupName = groupName[0]
    logging.info("groupName:{},url:{}".format(groupName, url))

    # 群成员
    try:
        groupNum = re.search(r"成员(.+?)#", textStr).group(1).replace(",", "")
        groupNum = re.search(r"(\d+)", groupNum).group(1)
    except Exception as e:
        groupNum = 0
    logging.info("groupNum:{},url:{}".format(groupNum, url))

    # 小组类型
    try:
        groupType = re.search(r"小组类型#(.*?)#", textStr).group(1).replace(",", "")
    except Exception as e:
        groupType = "have no group type"
    logging.info("groupType:{},url:{}".format(groupType, url))

    # 过去 30 天内有 228 篇
    try:
        postNum = int(re.search(r"天内有(.+?)篇", textStr).group(1).strip().replace(",", ""))
    except Exception as e:
        postNum = 0
    logging.info("postNum:{},url:{}".format(postNum, url))

    # 管理员链接
    node = selector.xpath('//div[@class="_1m1x"]/div/text()')
    manager = ""
    if node:
        nodeName = node[0].strip()
        if nodeName == "管理员和版主":
            managerNode = selector.xpath('//div[@class="_1m1x"]/div[last()-1]//a/@href')
            if managerNode:
                managerNode = managerNode[:-1]
                for i in managerNode:
                    manager += i + "\n"
        elif nodeName == "管理员":
            managerNode = selector.xpath('//div[@class="_1m1x"]/div[last()-1]//a/@href')
            if managerNode:
                for i in managerNode:
                    manager += i + "\n"
    manager = manager.strip()
    if not manager:
        manager = 'have no manager link'
    logging.info("manager:{},    url:{}".format(manager, url))


def mainR(url, userName, psd):
    if sys.argv[1] == "debug":
        # 非正式环境
        options = getOption(True)
        driver = webdriver.Chrome(chrome_options=options)
    else:
        # 正式环境
        options = getOption(True)
        driver = webdriver.Chrome(executable_path="./chromedriver", chrome_options=options)

    loginFB(driver, "GB", url, userName, psd)


if __name__ == '__main__':
    # 构建线程
    threads = []
    urls = []
    for i in range(1):
        url = 'https://www.facebook.com/login'
        if list(userPsdItem.keys()):
            userName = random.choice(list(userPsdItem.keys()))
            psd = userPsdItem[userName]
            del userPsdItem[userName]
            th = threading.Thread(target=mainR, args=(url, userName, psd))
            th.setDaemon(True)
            th.start()
            threads.append(th)
            urls.append(url)
            # 启动所有线程
    while True:
        for th, url in zip(threads, urls):
            if not th.is_alive():
                logging.warn("线程停止{}".format(th.name))
                threads.remove(th)
                urls.remove(url)
                if list(userPsdItem.keys()):
                    userName = random.choice(list(userPsdItem.keys()))
                    psd = userPsdItem[userName]
                    del userPsdItem[userName]
                    th = threading.Thread(target=mainR, args=(url, userName, psd))
                    th.start()
                    threads.append(th)
                    urls.append(url)
        time.sleep(10)
