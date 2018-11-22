# _*_ coding:utf-8 _*_
import csv

import sys

import requests
from fake_useragent import UserAgent

sys.path.append("./..")
from logs.loggerDefine import loggerDefine

loggerFile = "log.log"
logging = loggerDefine(loggerFile)
from db.mongodb import connectMongo
import jsonpath
from tools.translate.translate_google import mainTranslate
from multiprocessing.pool import ThreadPool

db = connectMongo(True)
collection = db["resources"]
import json
import logging


def sendRequest(url):
    for i in range(3):
        try:
            headers = {
                "accept-language": "zh-CN,zh;q=0.9",
                "user-agent": UserAgent().random,
                "x-youtube-client-name": "1",
                "x-youtube-client-version": "2.20181204",
            }
            response = requests.get(url=url, headers=headers, timeout=5, verify=False)
            response.encoding = "utf-8"
            if response.status_code == 200:
                return response.text
        except Exception as e:
            if repr(e).find("timed out") > 0:
                logging.error("请求超时{}次,url:{}".format(i + 1, videoUrl))
            else:
                logging.error(e)


def main_process(result):
    url = result["url"]
    videotitleUn = result["videotitleUn"]
    videoTittle = mainTranslate(videotitleUn)
    collection.update({"url": url}, {"$set": {"videoTittle": videoTittle}},multi=True)
    logging.info(url)


def readMongo():
    reslitList = list(
        collection.find({"videoTittle": "", "videotitleUn": {"$ne": ""}}))
    for result in reslitList:
        main_process(result)
    # pool = ThreadPool(5)
    # pool.map_async(main_process, reslitList)
    # pool.close()
    # pool.join()


if __name__ == '__main__':
    readMongo()
