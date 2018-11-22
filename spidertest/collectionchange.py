import sys

import time

sys.path.append("./..")

from db.mongodb import connectMongo
from db.mongoquery import mongoQuery
from urllib.request import urlparse

db = connectMongo(True)
collection = db["keyWords_url"]
newCollection = db["googleUrl"]


def readCollection():
    resultList = mongoQuery(newCollection, {"language":""})
    # resultList = newCollection.find({}).limit(1)
    for result in resultList:
        sourceUrl = result["sourceUrl"]
        if sourceUrl:
            resultU = collection.find_one({"url_detail": sourceUrl})
            if resultU:
                language = resultU.get("language")
                if language:
                    print(language)
                    newCollection.update_one({"_id": result["_id"]}, {"$set": {"language": language}})
                else:
                    print("没有找到语言:{}".format(sourceUrl))
            else:
                print("没有搜索到{}".format(sourceUrl))
        else:
            print("不存在:{}".format(sourceUrl))


def insertItem(item):
    try:
        newCollection.insert(item)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    readCollection()
