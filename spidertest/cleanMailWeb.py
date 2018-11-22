import sys

sys.path.append("./..")
from db.mongoquery import mongoQuery

from db.mongodb import connectMongo
import threading
import time

db = connectMongo(True)
resourcesCollection = db["webResources"]


def readMongo():
    resultList = list(resourcesCollection.find({"emailStr": {"$ne": ""}}))
    for result in resultList:
        emailStr = result["emailStr"]
        dealItem(emailStr, result)


def dealItem(emailStr, result):
    emailList = emailStr.split("\n")
    newEmailStr = ""
    newEmailList = []
    for i in emailList:
        if i.endswith("png"):
            # print("存在png结尾的:{}".format(result["url"]))
            continue

        if i.endswith("PNG"):
            # print("存在png结尾的:{}".format(result["url"]))
            continue

        if i.endswith("jpg"):
            # print("存在jpg结尾的:{}".format(result["url"]))
            continue

        if i.endswith("gif"):
            # print("存在jpg结尾的:{}".format(result["url"]))
            continue

        if i.endswith("jif"):
            # print("存在jpg结尾的:{}".format(result["url"]))
            continue

        if i.endswith("JPG"):
            # print("存在jpg结尾的:{}".format(result["url"]))
            continue

        if i.endswith("jpeg"):
            # print("存在jpg结尾的:{}".format(result["url"]))
            continue

        if i.endswith("JPEG"):
            # print("存在jpg结尾的:{}".format(result["url"]))
            continue

        if "@domain." in i:
            # print("存在@domain:{}".format(result["url"]))
            continue

        if "@example." in i:
            # print("存在@domain:{}".format(result["url"]))
            continue

        if "your@" in i:
            # print("存在@domain:{}".format(result["url"]))
            continue
        newEmailList.append(i)
    newEmailStr = "\n".join(newEmailList).strip()
    resourcesCollection.update_one({"_id": result["_id"]}, {"$set": {"emailStr": newEmailStr}})
    print(newEmailList)


if __name__ == '__main__':
    readMongo()
