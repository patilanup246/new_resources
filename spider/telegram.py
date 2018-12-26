import sys
import os

sys.path.append("./../")
from db.mongodb import connectMongo
import requests
from lxml import etree
from tools.translate.translate_google import mainTranslate
import time
import logging

# 全局变量  类对象
telegramObj = None
telegramResourcecollection = None
telegramUrlColletion = None


class MongoDB():
    def __init__(self):
        pass

    def connectMongo(self):
        mongodb = connectMongo(True)
        return mongodb


class Telegram():
    def __init__(self):
        pass

    def dealResult(self, result):
        url = result["url"]
        responseHtml = sendRequest(url)
        if not responseHtml:
            logging.error("访问url:{}没有响应文本".format(url))
            return
        self.dealResponse(responseHtml, result)

    def dealResponse(self, responseHtml, result):
        url = result["url"]
        selector = etree.HTML(responseHtml)
        # 标题
        title = selector.xpath("//title/text()")
        if title:
            title = title[0]
        else:
            logging.error("没有获取到标题:{}".format(url))
            title = ""

        # page title
        pageTitle = selector.xpath('//div[@class="tgme_page_title"]/text()')
        if not pageTitle:
            logging.error("没有获取到网页标题:{}".format(url))
            pageTitle = ""
        else:
            pageTitle = pageTitle[0].strip()

        # 成员信息
        memberInfo = selector.xpath('//div[@class="tgme_page_extra"]/text()')
        if not memberInfo:
            logging.error("没有获取到成员信息:{}".format(url))
            memberInfo = ""
        else:
            memberInfo = memberInfo[0].strip()

        # 描述信息
        descInfo = selector.xpath('//div[@class="tgme_page_description"]//text()')
        if descInfo:
            descInfo = "\n".join(descInfo).strip()
        else:
            logging.error("没有获取到描述信息{}".format(url))
            descInfo = ""
        self.dealItem(title, pageTitle, memberInfo, descInfo, result)

    def dealItem(self, title, pageTitle, memberInfo, descInfo, result):
        # 翻译描述信息
        if descInfo:
            descInfoCN = mainTranslate(descInfo)
        else:
            descInfoCN = ""

        item = {
            "_id": result["part"] + "_" + result["url"],
            "url": result["url"],
            "keyWord": result["keyWord"],
            "language": result["language"],
            "name": result["name"],
            "part": result["part"],
            "station": result["station"],
            "title": title,
            "pageTitle": pageTitle,
            "memberInfo": memberInfo,
            "descInfo": descInfo,
            "descInfoCN": descInfoCN,
            "country": ""
        }
        self.insertItem(item)

    def insertItem(self, item):
        global telegramResourcecollection
        global telegramUrlColletion
        try:
            telegramResourcecollection.insert(dict(item))
            logging.info("新增telegram信息成功,url:{}".format(item["url"]))
            # 更新 url状态
        except Exception as e:
            logging.exception(e)
        telegramUrlColletion.update_one({"url": item["url"], "part": item["part"]}, {"$set": {"isData": True}})


def sendRequest(url):
    for i in range(3):
        try:
            response = requests.get(url=url, timeout=10)
            response.encoding == "utf-8"
            if response.status_code == 200:
                return response.content
            else:
                logging.warn("访问url:{}状态码:{}".format(url, response.status_code))
        except Exception as e:
            logging.exception(e)


def readMongo(mongodb):
    global telegramObj
    global telegramResourcecollection
    global telegramUrlColletion
    telegramUrlColletion = mongodb["telegramUrl"]
    telegramResourcecollection = mongodb["telegramResource"]
    while True:
        resultList = list(telegramUrlColletion.find({"isData": False}).limit(100))
        if not resultList:
            logging.error("没有需要搜索的tele数据:{}".format(int(time.time())))
            time.sleep(60)
            continue
        for result in resultList:
            telegramObj.dealResult(result)


def mainRun():
    global telegramObj
    # 创建telegram对象
    telegramObj = Telegram()

    # 创建mongo对象 并生成数据库
    mongoObj = MongoDB()
    mongodb = mongoObj.connectMongo()
    # 读取数据库,查询未被搜索的数据
    readMongo(mongodb)


if __name__ == '__main__':
    mainRun()
