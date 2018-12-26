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

from db.mongodb import connectMongo
import random
import logging

holeurl = []
bullshit = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "AlexaToolbar-ALX_NS_PH": "AlexaToolbar/alx-4.0.3",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Cookie": "_ga=GA1.2.1213406101.1543890929",
    "Host": "api.serpprovider.com",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
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
googleUrlCollection = db["telegramUrl"]
keyWordsCollection = db["keyWords"]

urlList = []


def sendRequest(url):
    for i in range(3):
        try:
            response = requests.get(url=url, timeout=100, headers=bullshit)
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
    # 改变关键词获取状态
    # if " " in keyword:
    #     updateStatusKeyWord(keyword, part)
    #     return

    word = words.get(language)
    if not word:
        updateStatusKeyWord(keyword, part)
        logging.error("没有匹配的语言:{}".format(language))
        return

    keywordnew = "inurl:telegram.me " + keyword
    keywordnew = keywordnew.replace(" ", "%20")
    url = "http://api.serpprovider.com/5bfdf4cd7d33d1d77b9875d1/google/en-us/{}/{}".format(word, keywordnew)
    logging.info("请求数据,关键字:{},url:{}".format(keywordnew, url))
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
        updateStatusKeyWord(keyword, part)
        return
    if not reslist:
        updateStatusKeyWord(keyword, part)
        logging.error("google搜索后没有数据:{}".format(url))
        return
    for data in reslist:
        url = data["url"]
        # 协议
        scheme = urlparse(data['url']).scheme
        # 域名
        domain = urlparse(data['url']).netloc
        if not scheme or not domain:
            continue
        link = scheme + '://' + domain  # 拼接链接

        if domain != "telegram.me":
            logging.error("域名不为telegram.me     :{}".format(domain))
            continue

        # 此时域名已经是telegram.me
        if url.split("telegram.me")[-1] == "/":
            logging.error("url为{}".format(url))
            continue

        if url.endswith("telegram.me"):
            logging.error("url为{}".format(url))
            continue
        url = link + url.split("telegram.me")[-1]
        if url.endswith("/"):
            url = url[:-1]
        if url in urlList:
            logging.warn("该地址已经获取,存在缓存中,url:{}".format(url))
            continue

        # 判断是否在数据库中
        result = googleUrlCollection.find_one({"url": url, "part": part})
        if result:
            logging.warn("该url已经获取,存在数据库中中,url:{}".format(url))
            continue

        title = data['title']  # 获取标题
        describition = data['desc']  # 获取描述
        urlList.append(url)
        sourceUrl = data["url"]
        insertItem(domain, url, sourceUrl, scheme, keyword, language, resPeople, title, describition, word, part,
                   station)
    updateStatusKeyWord(keyword, part)


def updateStatusKeyWord(keyword, part):
    try:
        keyWordsCollection.update({"originKey": keyword, "part": part}, {"$set": {"istelegram": True}}, multi=True)
        logging.info("关键字状态更改为已经获取:{}".format(keyword))
    except Exception as e:
        logging.error(e)


def insertItem(domain, url, sourceUrl, scheme, keyword, language, resPeople, title, describition, word, part, station):
    _id = part + "_" + url
    item = {
        "_id": _id,
        "url": url,
        "sourceUrl": "",
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
        resultList = keyWordsCollection.distinct("originKey",
                                                 {"$or": [{"platId": 1}, {"platId": 3}], "istelegram": False,
                                                  "language": "希伯来"})

        if not resultList:
            logging.error("没有需要搜索telegram的关键字:{}".format(int(time.time())))
        for result in resultList:
            keyWord = result
            getcms(keyWord)


if __name__ == '__main__':
    mainRunGet()
