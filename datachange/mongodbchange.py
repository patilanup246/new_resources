import sys

sys.path.append("./../")

from db.mongodb import connectMongo
from db.mongoquery import mongoQuery
import threading
import time

db = connectMongo(True)
collection = db["resources"]

resourcesCollection = db["resources"]


def insertCollection(item):
    if "clothes" in item["_id"]:
        part = "clothes"
    else:
        part = "GB"
    try:
        resourcesCollection.update_one({"_id": item["_id"]}, {"$set": {"part": part}}, upsert=True)
    except Exception as e:
        print(e)


def main():
    resultList = mongoQuery(collection, {})
    for result in resultList:
        time.sleep(0.0001)
        print(result)
        th = threading.Thread(target=insertCollection, args=(result,))
        th.start()


if __name__ == '__main__':
    main()
