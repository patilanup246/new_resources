# coding:utf-8
import sys

sys.path.append('./../')
from tools.getip import getIp
import json
import requests
import logging
import traceback
from db.mongodb import connectMongo
import time
import pymongo

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
    "vtex integrated itore"
]
proxy = {}


def sendRequest(url, emailstr):
    data = {
        "usr": "wuzeronger@163.com",
        "pwd": "wuzeronger123",
        "emailaddresslist": emailstr
    }
    for i in range(3):
        try:
            response = requests.post(url=url, timeout=300, verify=False, data=data)
            if response.status_code == 200:
                response.encoding = "utf-8"
                return response.text
            else:
                print("验证邮箱状态码:{}".format(response.status_code))
        except Exception as e:
            logging.error(e)
            logging.error("url:{}".format(url))


def verifyMail(email):
    # {'domain': 'hallohaus.com', 'remaining_requests': 97, 'mx': True, 'alias': False, 'disposable': False, 'status': 200, 'email': 'customer@hallohaus.com', 'did_you_mean': None}
    emailData = getemaildata(email)
    if not emailData:
        return
    if emailData["verify_status"] == "success":
        verify_emailaddresslist_result = emailData["verify_emailaddresslist_result"]
        for emailResult in verify_emailaddresslist_result:
            # {"address":"1132372453@qqq.com","result":"invalid"}
            address = emailResult["address"]
            result = emailResult["result"]
            if result == "valid":
                logging.info("通过验证邮箱可用{}".format(address))
                collection.update({"emailStr": email}, {"$set": {"emailStr": address, "isRight": True}}, upsert=True,
                                  multi=True)
            else:
                logging.error("通过验证邮箱不可用{}".format(email))
                collection.update({"emailStr": email}, {"$set": {"isRight": False}}, upsert=True, multi=True)
    else:
        # 不可用
        logging.warn(
            "验证邮箱出现问题{},{},{}".format(emailData["verify_status"], emailData["fail_code"], emailData["fail_msg"]))


def getemaildata(email):  # 获取邮箱状态
    url = "http://www.emailcamel.com/api/batch/validate"
    responseStr = sendRequest(url, email)
    if not responseStr:
        return

    jsondata = json.loads(responseStr)
    # {"status":200,"email":"huguangjing211@gmail.com","domain":"gmail.com","mx":true,"disposable":false,"alias":false,"did_you_mean":null,"remaining_requests":99}
    return jsondata


def readMongo():
    while True:
        collection.update({"status": "verified"}, {"$set": {"isRight": True}}, upsert=True, multi=True)
        # 把没有邮箱的更新为
        resultList = list(
            collection.find({"emailStr": {"$ne": ""}, "isRight": {"$exists": 0}, "whiteNum": {"$gte": 3},
                             "fhBlackWordCount": 0, "blackNum": 0, "$or": [{"ismms": False, "part": {"$ne": "clothes"}},
                                                                           {"iscmms": False, "part": "clothes"}],
                             "viewCount": {"$gte": 10000}}).limit(100).sort(
                [("insertTime", pymongo.DESCENDING)]))
        if not resultList:
            logging.error("没有需要验证的邮箱")
            time.sleep(60)
            continue
        emails = []
        for result in resultList:
            email = result["emailStr"]
            if email.endswith("svg"):
                logging.error("以SVG结尾{}".format(email))
                collection.update({"emailStr": email}, {"$set": {"isRight": True}}, upsert=True, multi=True)
                continue
            if email in emails:
                continue
            emails.append(email)

            whatRun = result.get("whatRun")
            if whatRun:
                for word in cmsListErro:
                    if str(whatRun).lower().find(word.lower()) >= 0:
                        logging.error('whatRun存在电商框架:{}'.format(word))
                        collection.update({"url": result["url"]}, {"$set": {"isRight": False}}, upsert=True, multi=True)
                        break

            verifyMail(email)


if __name__ == '__main__':
    readMongo()
