# coding:utf-8
import os

import jsonpath
from urllib.request import urlparse
import csv
import json
import threading

import pymongo
import requests
import sys

import time

sys.path.append("./../")
from logs.loggerDefine import loggerDefine

from db.mongodb import connectMongo
import random

webspiderDir = "./../logs/web/"
if not os.path.exists(webspiderDir):
    os.makedirs(webspiderDir)
loggerFile = webspiderDir + "googlesearch.log"
logging = loggerDefine(loggerFile)
holeurl = []
bullshit = {
    # "Connection": "keep-alive",
    # "Upgrade-Insecure-Requests": "1",
    # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    # "Accept-Encoding": "gzip, deflate",
}

words = {
    "阿拉伯": "ar-undefined",
    "希伯来": "iw-undefined",
    "波斯": "fa-undefined",
    "中文": "zh-TW-undefined",
    "中文繁体": "zh-CN-undefined",
    "日本": "ja-undefined",
    "朝鲜": "ko-undefined",
    "乌尔都": "ur-undefined",
    "孟加拉": "bn-undefined",
    "菲律宾": "tl-undefined",
    "印地": "hi-undefined",
    "印度尼西亚": "id-undefined",
    "马来": "ms-undefined",
    "泰国": "th-undefined",
    "越南": "vi-undefined",
    "保加利亚": "bg-undefined",
    "捷克": "cs-undefined",
    "丹麦": "da-undefined",
    "荷兰": "nl-undefined",
    "芬兰": "fi-undefined",
    "匈牙利": "hu-undefined",
    "冰岛": "is-undefined",
    "拉脱维亚": "lv-undefined",
    "立陶宛": "lt-undefined",
    "挪威": "no-undefined",
    "俄罗斯": "ru-undefined",
    "瑞典": "sv-undefined",
    "乌克兰": "uk-undefined",
    "加泰罗尼亚": "ca-undefined",
    "法国": "fr-undefined",
    "德国": "de-undefined",
    "希腊": "el-undefined",
    "意大利": "it-undefined",
    "波兰": "pl-undefined",
    "葡萄牙": "pt-PT-undefined",
    "土耳其": "tr-undefined",
    "克罗地亚": "hr-undefined",
    "爱沙尼亚": "et-undefined",
    "斯洛伐克": "sk-undefined",
    "罗马尼亚": "ro-undefined",
    "塞尔维亚": "sr-undefined",
    "斯洛文尼亚": "sl-undefined",
    "泰米尔": "ta-undefined",
    "泰卢固": "te-undefined",
    "巴西": "pt-BR-undefined",
    "英语": "en-undefined",
    "西班牙": "es-undefined"
}

db = connectMongo(True)
googleUrlCollection = db["googleUrl"]
webResourcescollection = db["webResources"]
keyWordsCollection = db["keyWords"]

domainListGB = []
domainListCL = []


def sendRequest(url):
    for i in range(3):
        try:
            response = requests.get(url=url, timeout=35, headers=bullshit)
            response.encoding = "utf-8"
            if response.status_code == 200:
                return response.text
        except Exception as e:
            print(e)


def getcms(keyword):
    # , language, resPeople
    result = keyWordsCollection.find_one({"originKey": keyword})
    language = result["language"]
    resPeople = result["resPeople"]
    part = result["part"]
    station = result["station"]

    word = words.get(language)
    if not word:
        word = "en-undefined"

    url = "http://api.serpprovider.com/5bfdf4cd7d33d1d77b9875d1/google/en-us/{}/{}".format(word, keyword)
    logging.info("请求数据,关键字:{},url:{}".format(keyword, url))
    html = sendRequest(url)  # 请求
    try:
        datas = json.loads(html)
    except Exception as e:
        return
    reslist = jsonpath.jsonpath(datas, "$..res")
    if reslist:
        reslist = reslist[0]
    else:
        logging.error("google搜索后没有数据:{}".format(url))
        return
    if not reslist:
        logging.error("google搜索后没有数据:{}".format(url))
        return
    for data in reslist:
        # 协议
        scheme = urlparse(data['url']).scheme
        # 域名
        domain = urlparse(data['url']).netloc
        if not scheme or not domain:
            continue
        link = scheme + '://' + domain  # 拼接链接
        # 判断是否在缓存中
        if part == "GB":
            domainList = domainListGB
        else:
            domainList = domainListCL
        if domain in domainList:
            logging.warn("该域名已经获取,存在缓存中,domain:{}".format(domain))
            continue

        # 判断是否在数据库中
        result = googleUrlCollection.find_one({"domain": domain})
        if result:
            logging.warn("该域名已经获取,存在数据库中中,domain:{}".format(domain))
            if result["part"] != part:
                webresultList = list(webResourcescollection.find({"url": link}))
                for result in webresultList:
                    if part == "clothes":
                        result["_id"] = result["_id"].replace("_GB_", "_clothes_")
                    else:
                        result["_id"] = result["_id"].replace("_clothes_", "_GB_")
                    try:
                        result["resPeople"] = resPeople
                        result["part"] = part
                        result["station"] = station
                        mongoResult = webResourcescollection.find_one({"_id": result["_id"]})
                        if not mongoResult:
                            webResourcescollection.insert(result)
                            logging.info("加入成功:{},_id:{}".format(part, result["_id"]))
                    except Exception as e:
                        logging.error(e)

            continue

        # 查询是否在GB中

        title = data['title']  # 获取标题
        describition = data['desc']  # 获取描述
        domainList.append(domain)
        sourceUrl = data["url"]
        insertItem(domain, link, sourceUrl, scheme, keyword, language, resPeople, title, describition, word, part,
                   station)

    # 改变关键词获取状态
    updateStatusKeyWord(keyword, part)


def updateStatusKeyWord(keyword, part):
    try:
        keyWordsCollection.update({"originKey": keyword, "part": part}, {"$set": {"isGet": True}}, multi=True)
        logging.info("关键字状态更改为已经获取:{}".format(keyword))
    except Exception as e:
        logging.error(e)


def insertItem(domain, url, sourceUrl, scheme, keyword, language, resPeople, title, describition, word, part, station):
    item = {
        "_id": domain,
        "url": url,
        "sourceUrl": sourceUrl,
        "domain": domain,
        "scheme": scheme,
        "keyWord": keyword,
        "language": language,
        "name": resPeople,
        "title": title,
        "desc": describition,
        "isData": False,
        "word": word,
        "insertTime": int(time.time()),
        "part": part,
        "station": station
    }
    try:
        googleUrlCollection.insert(item)
        logging.info("新增成功:{}".format(url))
    except Exception as e:
        logging.error(e)


def mainRunGet():
    # 循环获取关键字
    while True:
        resultList = keyWordsCollection.distinct("originKey", {"$or": [{"platId": 1}, {"platId": 3}], "isGet": False})
        for result in resultList:
            keyWord = result
            getcms(keyWord)


if __name__ == '__main__':
    mainRunGet()
