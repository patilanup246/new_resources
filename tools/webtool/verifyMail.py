# coding:utf-8


import sys

sys.path.append('./../')
import json
import requests
import logging
import traceback
from db.mongodb import connectMongo
import time

db = connectMongo(True)
collection = db["webResources"]
emailheader = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
}
cmsListErro = [
    "bigcommerce",
    "shopper approved",
    "shopify",
    "prestashop",
    "oscommerce",
    "openCart",
    "magento",
    "demandware",
    "craft cms",
    "qubit opentag",
    "3dcart",
    "vtex enterprise",
    "prestashop",
    "demandware",
]


def sendRequest(url):
    for i in range(3):
        try:
            response = requests.get(url=url, timeout=20, headers=emailheader, verify=False)
            if response.status_code == 200:
                response.encoding = "utf-8"
                return response.text
            else:
                print("验证邮箱状态码:{}".format(response.status_code))
        except Exception as e:
            logging.error(e)
            logging.error("url:{}".format(url))


def verifyMail(email):
    emailData = getemaildata(email)
    if not emailData:
        return
    if emailData["status"] == 1:
        # 可用
        logging.info("通过验证邮箱可用{}".format(email))
        collection.update({"emailStr": email}, {"$set": {"isRight": True}}, upsert=True, multi=True)
    else:
        # 不可用
        logging.info("通过验证邮箱不可用{}".format(email))
        collection.update({"emailStr": email}, {"$set": {"isRight": False}}, upsert=True, multi=True)


def getemaildata(email):  # 获取邮箱状态
    data = {}
    url = 'https://app.verify-email.org/api/v1/6fxKTc8hd5CCnUTV74OWN2dWBdWBO5FFcqXwYmv71vzQnbgpWG/verify/' + email  # 拼接email的url参数

    responseStr = sendRequest(url)
    if not responseStr:
        return

    jsondata = json.loads(responseStr)
    data['email'] = jsondata['email']  # 获取邮箱
    data['status'] = jsondata['status']  # 获取邮箱状态吗
    data['status_description'] = jsondata['status_description']  # 获取邮箱状态
    data['smtp_code'] = jsondata['smtp_code']  # 获取smpt状态
    return data


def readMongo():
    while True:
        # 把没有邮箱的更新为
        collection.update({"$or": [{"ismms": True, "part": {"$ne": "clothes"}}, {"iscmms": True, "part": "clothes"},
                                   {"emailStr": ""}]}, {"$set": {"isRight": False}},
                          multi=True)

        resultList = list(
            collection.find({"emailStr": {"$ne": ""}, "isRight": {"$exists": 0}, "whiteNum": {"$gte": 3},
                             "fhBlackWordCount": {"$lte": 1}, "blackNum": {"$lte": 1}, "ismms": False,
                             "viewCount": {"$gte": 10000}, "whatRun": {"$exists": 1}}).limit(100))
        if not resultList:
            resultList = list(
                collection.find(
                    {"emailStr": {"$ne": ""}, "isRight": {"$exists": 0}, "whiteNum": {"$gte": 2}, "ismms": False,
                     "viewCount": {"$gte": 10000}}).limit(
                    100))
            if not resultList:
                time.sleep(60)
                continue
        emails = []
        for result in resultList:
            email = result["emailStr"]
            if email in emails:
                continue
            emails.append(email)

            whatRun = result.get("whatRun")
            if whatRun:
                for word in cmsListErro:
                    if str(whatRun).lower().find(word.lower()) >= 0:
                        collection.update({"url": result["url"]}, {"$set": {"isRight": False}}, upsert=True, multi=True)

            status = result.get("status")
            if status == "verified":
                logging.info("已经验证,标记为可用{}".format(email))
                collection.update({"emailStr": email}, {"$set": {"isRight": True}}, upsert=True, multi=True)
                continue
            verifyMail(email)


if __name__ == '__main__':
    readMongo()
