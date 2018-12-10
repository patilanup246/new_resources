from db.mongodb import connectMongo
import time
from tools.checkurl import checkUrl, checkWebUrl
import logging

db = connectMongo(True)
collection = db["webResources"]
cmmsDomain = "http://cmms.gloapi.com/"
mmsDomain = "http://mms.gloapi.com/"


def readMongo():
    while True:
        resultList = list(collection.find({"$or": [{"ismms": {"$exists": 0}, "part": {"$ne": "clothes"}},
                                                   {"iscmms": {"$exists": 0}, "part": "clothes"}]}).limit(100))
        if not resultList:
            logging.error("没有需要验证数据")
            time.sleep(60)
            continue
        urlGBs = []
        urlclothess = []
        for result in resultList:
            url = result["url"]
            part = result["part"]
            if part == "clothes":
                if url in urlclothess:
                    continue
                urlclothess.append(url)
                isExists = checkWebUrl(url, cmmsDomain)
                if isExists:
                    collection.update({"url": url, "part": part}, {"$set": {"iscmms": True}}, upsert=True, multi=True)
                    logging.info("存在cmms中{}".format(url))
                else:
                    collection.update({"url": url, "part": part}, {"$set": {"iscmms": False}}, upsert=True, multi=True)
                    logging.info("不存在cmms中{}".format(url))
            else:
                if url in urlGBs:
                    continue
                urlGBs.append(url)
                isExists = checkWebUrl(url, mmsDomain)
                if isExists:
                    collection.update({"url": url, "part": part}, {"$set": {"ismms": True}}, upsert=True, multi=True)
                    logging.info("存在mms中{}".format(url))
                else:
                    collection.update({"url": url, "part": part}, {"$set": {"ismms": False}}, upsert=True, multi=True)
                    logging.info("不存在mms中{}".format(url))


if __name__ == '__main__':
    readMongo()
