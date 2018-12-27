# coding:utf-8
import os
import sys

sys.path.append("./..")
from tools.checkurl import checkUrl

from db.mongoquery import mongoQuery
from tools.translate.translate_google import mainTranslate
from selenium.common.exceptions import NoSuchElementException

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
from tools.youtubetool.backcountry import readMongo as readMongoBackCountry

platId = 2
db = connectMongo(True)
keyCollection = db["keyWords"]
fbresourcesCollection = db["fbresources"]
blackwhitecoll = db["blackWhite"]
# blackUrlcoll = db["blackUrl"]
# invisibleUrlcoll = db["invisibleUrl"]

blackList = blackwhitecoll.distinct("word", {"isBlack": True, "platId": platId, "part": 'GB'})
clothesblackList = blackwhitecoll.distinct("word", {"isBlack": True, "platId": platId, "part": 'clothes'})

whiteList = blackwhitecoll.distinct("word", {"isWhite": True, "platId": platId, "part": 'GB'})
clotheswhiteList = blackwhitecoll.distinct("word", {"isWhite": True, "platId": platId, "part": 'clothes'})

errNode = 0
keyWordList = []

userPsdItem = {
    # "wuzeronger@live.com": "wuzeronger123",  # 需要验证身份
    "958905350@qq.com": "withyou1314",  # 已经被禁止搜索具体群组
    "2933219312@qq.com": "Citic231104",  # 操作太快没有搜索权限
    # # "tanya.beleutova.beleutova@mail.ru": "yoan6SNoer",  # 需要验证手机号码
    "huguangjing211@gmail.com": "hgj212816",
    # "brveo2166@inbox.ru": "B3Lt5zjlWk",
    # "DyachkovaEvridika89@inbox.ru": "OCRsw5VMth",
    # "EginaGuschina89.89@inbox.ru": "HfwxQpbMQP",
    "jordan.macduff.1982@list.ru": "ltcw4356",
    "13311631790": "ximalaya1"
}


def loginFB(driver, url, userName, psd, name):
    global userPsdItem
    global keyWordList
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
                    del userPsdItem[userName]
                    driver.quit()
                    return
                time.sleep(random.randint(2, 3))
            else:
                break
        # time.sleep(1)
        if driver.current_url != "https://www.facebook.com/":
            driver.get("https://www.facebook.com/")
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
                    time.sleep(random.randint(2, 3))
                    """//div[@class="_4t2a"]//button"""
                    driver.find_element_by_xpath('//div[@class="_4t2a"]//button').click()
                    time.sleep(random.randint(2, 3))
        # keyWordList = list(collection.distinct("keyWord", {"getData": False}))[:1000]
        keyWordList = mongoQuery(keyCollection, {"getData": False, "platId": platId})
        if not keyWordList:
            # keyWordList = mongoQuery(keyCollection, {"getData": False, "platId": platId, "resPeople": {"ne": "吴泽荣"}})
            # if not keyWordList:
            logging.warn("no keywords now")
            time.sleep(3600 * 24)
        # 跳转到小组界面
        keyWordDeal(keyWordList, driver, userName)
    except Exception as e:
        logging.error(traceback.format_exc())

    finally:
        if driver:
            driver.quit()
            return


def keyWordDeal(keyWordList, driver, userName):
    global userPsdItem
    global errNode
    try:
        startTime = int(time.time())
        for result in keyWordList:
            endTime = int(time.time())
            # 控制账户访问频率：
            if endTime - startTime >= random.randint(1800, 3600):
                del userPsdItem[userName]
                driver.quit()
            keyWord = result["keyWord"]

            resPeople = result["resPeople"]
            language = result['language']
            part = result["part"]
            keyWordNew = keyWord.replace(" ", "+").replace("?", "")
            url = "https://www.facebook.com/search/str/{}/keywords_groups".format(keyWordNew)
            js = 'window.open("{}");'.format(url)
            driver.execute_script(js)
            time.sleep(random.randint(2, 3))
            driver.switch_to_window(driver.window_handles[1])
            logging.info("新开窗口,切换到小组窗口界面,url:{}".format(driver.current_url))

            responseBody = driver.page_source
            selector = etree.HTML(responseBody)

            logging.info("解析小组页面详细url,关键字:{}".format(keyWord))
            titleNode = selector.xpath('//div[@class="_gll"]/div//a/@href')
            if not titleNode:
                logging.error("没有搜索到相关信息,关键字:{},url:{}".format(keyWord, url))
                driver.close()
                driver.switch_to_window(driver.window_handles[0])
                # 没有搜索到数据的话 减少长度搜索 如果有数据  代表搜多引擎可用
                if "+" in keyWordNew:
                    word = keyWordNew.split("+")[0].replace("?", "")
                else:
                    word = "xiaomi"
                url = "https://www.facebook.com/search/str/{}/keywords_groups".format(word)
                js = 'window.open("{}");'.format(url)
                driver.execute_script(js)
                time.sleep(random.randint(2, 3))
                driver.switch_to_window(driver.window_handles[1])
                logging.info("新开窗口,切换到小组窗口界面,url:{}".format(driver.current_url))

                responseBody = driver.page_source
                selector = etree.HTML(responseBody)

                logging.info("解析小组页面详细url,关键字:{}".format(word))
                titleNode = selector.xpath('//div[@class="_gll"]/div//a/@href')
                # if titleNode:
                #     logging.info("搜索到东西了关键字,关键字:{}".format(keyWordNew))
                if not titleNode:
                    logging.info("确实没有搜索到任何东西,关键字:{}".format(keyWordNew))
                    keyCollection.update_one({"keyWord": keyWord, "platId": platId, "part": part},
                                             {"$set": {"getData": True}})
                else:
                    # 再确认一次 搜索小米
                    logging.info("没有搜索到相关信息,关键字:{}".format(keyWordNew))
                    driver.close()
                    driver.switch_to_window(driver.window_handles[0])
                    wordList = ["Apple", "Mac", "Microsoft"]
                    word = random.choice(wordList)
                    url = "https://www.facebook.com/search/str/{}/keywords_groups".format(word)
                    js = 'window.open("{}");'.format(url)
                    driver.execute_script(js)
                    time.sleep(random.randint(2, 3))
                    driver.switch_to_window(driver.window_handles[1])
                    logging.info("新开窗口,切换到小组窗口界面,url:{}".format(driver.current_url))
                    responseBody = driver.page_source
                    selector = etree.HTML(responseBody)

                    logging.info("解析小组页面详细url,关键字:{}".format(word))
                    titleNode = selector.xpath('//div[@class="_gll"]/div//a/@href')
                    if titleNode:
                        logging.info("搜索到东西了关键字:{}".format(keyWordNew))
                        keyCollection.update_one({"keyWord": keyWord, "platId": platId, "part": part},
                                                 {"$set": {"getData": True}})
                    else:
                        errNode += 1
                        logging.error("搜索引擎被禁止,name:{}".format(userName))
                        del userPsdItem[userName]
                        driver.quit()
                        return
                driver.switch_to_window(driver.window_handles[0])
                # driver.switch_to.default_content()
                continue

            # if errNode >= 100:
            #     logging.warn("搜索功能可能已经被已经被禁用,用户名:{}".format(userName))
            #     errNode = 0
            #     driver.quit()
            #     return

            # 处理具体的群组信息
            groupDeal(driver, keyWord, userName, resPeople, language, part)
    except Exception as e:
        driver.quit()
        return


def groupDeal(driver, keyWord, userName, resPeople, language, part):
    global userPsdItem
    global keyWordList
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
                if scroll >= 20:
                    break
                driver.execute_script(js)
                time.sleep(random.randint(2, 3))
        responseBody = driver.page_source
        selector = etree.HTML(responseBody)

        logging.info("解析小组页面详细url,关键字:{}".format(keyWord))
        # titleNodeList = selector.xpath('//div[@class="_gll"]/div//a/@href')
        titleNodeList = selector.xpath('//div[@class="_gll"]')
        groupNodeList = selector.xpath('//div[@class="_glm"]')
        descrNodeList = selector.xpath('//div[@class="_glo"]')

        for titleNode, groupNode, descrNode in zip(titleNodeList, groupNodeList, descrNodeList):
            try:
                # 成员数量
                try:
                    groupNumStr = groupNode.xpath('./div//text()')[0]
                    if "万位成员" in groupNumStr:
                        pass
                    else:
                        groupNum = int(re.search(r"(.*?)位成员", groupNumStr).group(1).replace(",", "").strip())

                        # if language == "英语":
                        #     if groupNum < 1000:
                        #         logging.error("{},成员少于1000人".format(language))
                        #         continue
                        # else:
                        #     if groupNum < 500:
                        #         logging.error("{},成员少于500人".format(language))
                        #         continue
                except Exception as e:
                    logging.error(e)
                    continue

                # 正则提取出链接出来
                try:
                    link = "https://www.facebook.com" + titleNode.xpath('./div//a/@href')[0]
                    link = re.match(r"(https://www.facebook.com/groups/.+/)", link).group(1) + "about"
                except Exception as e:
                    logging.error(traceback.format_exc())
                    continue

                # 通过描述信息过滤黑名单
                descriptionList = descrNode.xpath('./div/div/div/text()')
                if not descriptionList:
                    # 没有评论信息
                    logging.error("没有描述信息,url:{}".format(link))
                    description = ""
                elif len(descriptionList) == 1:
                    # 代表只有描述信息
                    description = descriptionList[0].strip()
                else:
                    description = descriptionList[-1].strip()

                if description.endswith("小组"):
                    description = ""

                # 判断是否在黑名单中
                # resultMongo = blackUrlcoll.find_one(
                #     {"url": link.replace("/about", ""), "platId": platId, "part": part})
                # if resultMongo:
                #     logging.error("存在黑名单中,url:{}".format(link.replace("/about", "")))
                #     continue
                # 是否存在黑名单中
                # if description:
                #     isExists, blackWord = black(description, part)
                #     if isExists:
                #         logging.error("存在非中文黑名单中,word:{},url:{}".format(blackWord, link.replace("/about", "")))
                #         try:
                #             blackUrlcoll.insert({
                #                 "_id": str(platId) + "_" + part + "_" + link.replace("/about", ""),
                #                 "url": link.replace("/about", ""),
                #                 "platId": platId,
                #                 "blackWord": blackWord,
                #                 "part": part,
                #                 "insertTime": int(time.time())
                #             })
                #         except Exception as e:
                #             logging.error(e)
                #         continue

                if link in linkList:
                    continue

                # 是否在数据库中
                result = fbresourcesCollection.find_one(
                    {"url": link.replace("/about", ""), "platId": platId, "part": part})
                if result:
                    if result["groupName"]:
                        logging.error("存在数据库中,url:{}".format(link))
                        continue

                # 是否存在mms中
                if part == "GB":
                    domain = "http://mms.gloapi.com/"
                else:
                    domain = "http://cmms.gloapi.com/"
                isExists = checkUrl(link.replace("/about", ""), domain)
                if isExists:
                    logging.warn("存在{}中,name:{},url:{}".format(domain, resPeople, link.replace("/about", "")))
                    # 代表存在接口中
                    continue

                # 是否存在存在发帖数不满足条件的苦中
                # result = invisibleUrlcoll.find_one({"url": link.replace("/about", ""), "platId": platId})
                # if result:
                #     logging.error("过去 30 天内发帖数没有达标,url:{}".format(link.replace("/about", "")))
                #     continue
                # 最终有效的url
                linkList.append(link)
            except Exception as e:
                logging.error(traceback.format_exc())
        if not linkList:
            if titleNodeList:
                keyCollection.update_one({"keyWord": keyWord, "platId": platId, "part": part},
                                         {"$set": {"getData": True}})
                logging.error("没有查到相关数据,keyWord:{}".format(keyWord))
            driver.close()
            driver.switch_to_window(driver.window_handles[0])
            time.sleep(random.randint(2, 3))
            return
        else:
            time.sleep(random.randint(2, 3))

        while True:
            fiveList = linkList[:3]
            if not fiveList:
                keyCollection.update_one({"keyWord": keyWord, "platId": platId, "part": part},
                                         {"$set": {"getData": True}})
                break

            for url in fiveList:
                js = 'window.open("{}");'.format(url)
                linkList.remove(url)
                driver.execute_script(js)
                time.sleep(random.randint(2, 3))

            handles = driver.window_handles
            driver.switch_to_window(handles[0])
            currentHandle = driver.current_window_handle
            for handle in handles:
                if handle != currentHandle:
                    try:
                        time.sleep(random.randint(2, 3))
                        driver.switch_to_window(handle)
                        if "操作过快" in driver.page_source:
                            logging.warn('操作过快,导致没有搜索详情权限,用户名:{}'.format(userName))
                            del userPsdItem[userName]
                            driver.quit()
                            return
                        try:
                            url = re.match(r"(https://www.facebook.com/groups/.+?)/.*", driver.current_url).group(1)
                        except Exception as e:
                            url = ""
                        if url:
                            text = checkText(driver.page_source.encode("utf-8", "ignore"), url)
                            if not text:
                                time.sleep(random.randint(2, 3))
                            parsePage(driver.page_source, url, resPeople, keyWord, language, part)
                        driver.close()
                        driver.switch_to_window(handles[0])
                    except Exception as e:
                        logging.error(traceback.format_exc())

                        # driver.switch_to.default_content()

    except Exception as e:
        logging.error(traceback.format_exc())


def checkText(response, url):
    try:
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
    except Exception as e:
        logging.error(traceback.format_exc())


def black(desc, part, url):
    blackWord = ""
    blackNum = 0
    if part == "GB":
        blackListall = blackList
    else:
        blackListall = clothesblackList
    try:
        for word in blackListall:
            if word in desc:
                blackWord += word + " "
                blackNum += 1
                logging.error("存在黑名单中,word:{}    {}".format(word, url))
        return blackWord.strip(), blackNum
    except Exception as e:
        logging.error(traceback.format_exc())


# 白名单处理：
def white(desc, part, url):
    whiteWord = ""
    whiteNum = 0
    if part == "GB":
        whiteListall = whiteList
    else:
        whiteListall = clotheswhiteList
    try:
        for word in whiteListall:
            if word in desc:
                whiteWord += word + " "
                whiteNum += 1
                logging.error("存在白名单中,word:{},   {}".format(word, url))
        return whiteWord.strip(), whiteNum
    except Exception as e:
        logging.error(traceback.format_exc())


def parsePage(response, url, resPeople, keyWord, language, part):
    try:
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
            description = ""

        descriptionUn = description

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
            groupNum = int(re.search(r"(\d+)", groupNum).group(1))
        except Exception as e:
            groupNum = 0
            return
        # if language == "英语":
        #     if groupNum < 1000:
        #         logging.error("{},成员少于1000人".format(language))
        #         return
        # else:
        #     if groupNum < 500:
        #         logging.error("{},成员少于500人".format(language))
        #         return
        logging.info("groupNum:{},url:{}".format(groupNum, url))

        # 小组类型
        try:
            groupType = re.search(r"小组类型#(.*?)#", textStr).group(1).replace(",", "")
        except Exception as e:
            groupType = ""
        logging.info("groupType:{},url:{}".format(groupType, url))

        # 过去 30 天内有 228 篇
        try:
            postNum = int(re.search(r"天内有(.+?)篇", textStr).group(1).strip().replace(",", ""))
        except Exception as e:
            return
        # 处理过滤信息
        # if language == "英语":
        #     if postNum < 100:
        #         try:
        #             invisibleUrlcoll.insert({
        #                 "_id": str(platId) + "_" + url,
        #                 "url": url,
        #                 "platId": 2,
        #                 "postNum": postNum,
        #                 "insertTime": int(time.time())
        #             })
        #         except Exception as e:
        #             logging.error(e)
        #         return
        # else:
        #     if postNum < 50:
        #         try:
        #             invisibleUrlcoll.insert({
        #                 "_id": str(platId) + "_" + url,
        #                 "url": url,
        #                 "platId": 2,
        #                 "postNum": postNum,
        #                 "insertTime": int(time.time())
        #             })
        #         except Exception as e:
        #             logging.error(e)
        #         return
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
            manager = ''
        logging.info("manager:{},    url:{}".format(manager, url))
        if description:
            # 翻译
            description = mainTranslate(description)
        blackWord, blackNum = black(description + descriptionUn, part, url)
        whiteWord, whiteNum = white(description + descriptionUn, part, url)
        fbresourcesCollection.insert_one({
            "_id": str(platId) + "_" + part + "_" + url,
            "description": description,
            "descriptionUn": descriptionUn,
            "groupNum": groupNum,
            "url": url,
            "platId": platId,
            "groupName": groupName,
            "groupType": groupType,
            "postNum": postNum,
            "manager": manager,
            "csvLoad": False,
            "name": resPeople,
            "part": part,
            "keyWord": keyWord,
            "language": language,
            "lastUpdate": int(time.time()),
            "blackWord": blackWord,
            "blackNum": blackNum,
            "whiteWord": whiteWord,
            "whiteNum": whiteNum
        })
    except Exception as e:
        logging.error(traceback.format_exc())


def mainR(url, userName, psd, name):
    if sys.argv[1] == "debug":
        # 非正式环境
        options = getOption(False)
        driver = webdriver.Chrome(chrome_options=options)
    else:
        # 正式环境
        options = getOption(True)
        driver = webdriver.Chrome(executable_path="./chromedriver", chrome_options=options)
    loginFB(driver, url, userName, psd, name)


if __name__ == '__main__':
    # 回补国家信息
    query = {"country": {"$exists": 0}}
    backcountryTh = threading.Thread(target=readMongoBackCountry, args=(fbresourcesCollection, query,))
    backcountryTh.start()
    # 构建线程
    nameList = []
    # nameList = keyCollection.distinct("resPeople", {"platId": 2, "getData": False})
    nameList = [1]
    threads = []
    urls = []
    names = []
    for name in nameList:
        url = 'https://www.facebook.com/login'
        if list(userPsdItem.keys()):
            time.sleep(5)
            userName = random.choice(list(userPsdItem.keys()))
            psd = userPsdItem[userName]
            # del userPsdItem[userName]
            th = threading.Thread(target=mainR, args=(url, userName, psd, name))
            th.setDaemon(True)
            th.start()
            threads.append(th)
            urls.append(url)
            names.append(name)
    # 启动所有线程
    while True:
        time.sleep(10)
        for th, url, name in zip(threads, urls, names):
            if not th.is_alive():
                logging.warn("线程停止{}".format(th.name))
                logging.info("有效fb用户:{}".format(list(userPsdItem.keys())))
                threads.remove(th)
                urls.remove(url)
                names.remove(name)
                if not list(userPsdItem.keys()):
                    userPsdItem = {
                        # "wuzeronger@live.com": "wuzeronger123",  # 需要验证身份
                        "958905350@qq.com": "withyou1314",  # 已经被禁止搜索具体群组
                        "2933219312@qq.com": "Citic231104",  # 操作太快没有搜索权限
                        # "tanya.beleutova.beleutova@mail.ru": "yoan6SNoer",  # 需要验证手机号码
                        "huguangjing211@gmail.com": "hgj212816",
                        # "brveo2166@inbox.ru": "B3Lt5zjlWk",
                        # "DyachkovaEvridika89@inbox.ru": "OCRsw5VMth",
                        # "EginaGuschina89.89@inbox.ru": "HfwxQpbMQP",
                        "jordan.macduff.1982@list.ru": "ltcw4356",
                        "13311631790": "ximalaya1"
                    }
                userName = random.choice(list(userPsdItem.keys()))
                psd = userPsdItem[userName]
                # del userPsdItem[userName]
                th = threading.Thread(target=mainR, args=(url, userName, psd, name))
                th.start()
                threads.append(th)
                urls.append(url)
                names.append(name)
