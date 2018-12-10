import sys

sys.path.append("./..")
from tools.checkurl import checkUrl
from db.mongodb import connectMongo

db = connectMongo(True)
collection = db["resources"]


def readMongo():
    resultList = list(collection.find({"part": "GB", "whiteWord": {"$exists": 1}}))
    for result in resultList:
        url = result["url"]
        mmsDomain = "http://mms.gloapi.com/"
        isExists = checkUrl(url, mmsDomain)
        if isExists:
            collection.update_one({"url": url, "part": "GB"}, {"$set": {"ismms": True}}, upsert=True)
        else:
            collection.update_one({"url": url, "part": "GB"}, {"$set": {"ismms": False}}, upsert=True)


if __name__ == '__main__':
    readMongo()
