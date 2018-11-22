import sys
from lxml import etree

sys.path.append("./..")
from db.mongoquery import mongoQuery
from spider.webspider import getMailPage
from db.mongodb import connectMongo
import threading
import time
import requests

db = connectMongo(True)
resourcesCollection = db["webResources"]
import threading


def readMongo():
    resultList = list(resourcesCollection.find({"emailStr": "", "title": {"$ne": ""}}))
    for result in resultList:
        time.sleep(1)
        th = threading.Thread(target=dealItem, args=(result,))
        th.start()


def sendRequest(url):
    for i in range(3):
        try:
            response = requests.get(url=url, timeout=5, verify=False)
            if response.status_code == 200:
                return response.content
        except Exception as e:
            pass


def dealItem(result):
    try:
        url = result["url"]
        responseBody = sendRequest(url)
        if responseBody:
            try:
                selector = etree.HTML(responseBody)
            except Exception as e:
                selector = etree.HTML(responseBody.decode())
            # 获取邮箱信息
            emailStr = getMailPage(responseBody, selector)
            if emailStr:
                print("有邮箱:{}".format(result["url"]))
                resourcesCollection.update_one({"_id": result["_id"]}, {"$set": {"emailStr": emailStr}})
            else:
                print("没有邮箱:{}".format(result["url"]))
        else:
            print("没有响应:{}".format(result["url"]))
    except Exception as e:
        print(e)


if __name__ == '__main__':
    readMongo()
