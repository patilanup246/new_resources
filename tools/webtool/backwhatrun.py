import sys

sys.path.append('./../')
from spider.webspider import getFrameData
from urllib.request import urlparse
from db.mongodb import connectMongo
import time

db = connectMongo(True)
collection = db["webResources"]


def mainR():
    while True:
        urlList = list(collection.find({"whatRun": {"$exists": 0}}).limit(100))
        if not urlList:
            time.sleep(30)
        urls = []
        for result in urlList:
            mongoUrl = result["url"]
            if mongoUrl in urls:
                continue
            urls.append(mongoUrl)
            scheme = urlparse(mongoUrl).scheme
            domain = urlparse(mongoUrl).netloc
            item = getFrameData(scheme, domain, mongoUrl)
            if item:
                collection.update({"url": mongoUrl}, {"$set": {"whatRun": item}}, upsert=True, multi=True)
                logging.info("{}新增whatRun信息{}".format(mongoUrl, item))


if __name__ == '__main__':
    mainR()
