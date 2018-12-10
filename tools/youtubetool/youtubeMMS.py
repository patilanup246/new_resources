import sys

sys.path.append('./../')

from db.mongodb import connectMongo
import time
from tools.checkurl import checkUrl, checkWebUrl, checkMail
import logging

db = connectMongo(True)
collection = db["resources"]
cmmsDomain = "http://cmms.gloapi.com/"
mmsDomain = "http://mms.gloapi.com/"


def readMongo():
    while True:
        resultList = list(collection.find(
            {"$or": [{"ismms": {"$exists": 0}, "part": {"$ne": "clothes"}},
                     {"iscmms": {"$exists": 0}, "part": "clothes"}]}).limit(5))

        if not resultList:
            logging.error("没有需要验证的数据")
            time.sleep(100)
            continue
        for result in resultList:
            url = result["url"]
            part = result["part"]
            if part == "clothes":
                isExists = checkUrl(url, cmmsDomain)
                if isExists:
                    collection.update_one({"url": url, "part": part}, {"$set": {"iscmms": True}}, upsert=True)
                    logging.info("存在cmms中{}".format(url))
                else:
                    collection.update_one({"url": url, "part": part}, {"$set": {"iscmms": False}}, upsert=True)
                    logging.info("不存在cmms中{}".format(url))
            else:
                isExists = checkUrl(url, mmsDomain)
                if isExists:
                    collection.update_one({"url": url, "part": part}, {"$set": {"ismms": True}}, upsert=True)
                    logging.info("存在mms中{}".format(url))
                else:
                    collection.update_one({"url": url, "part": part}, {"$set": {"ismms": False}}, upsert=True)
                    logging.info("不存在mms中{}".format(url))


if __name__ == '__main__':
    readMongo()
