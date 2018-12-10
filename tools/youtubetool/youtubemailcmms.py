import sys

sys.path.append('./../../')

from db.mongodb import connectMongo
import time
from tools.checkurl import checkUrl, checkWebUrl, checkMail

db = connectMongo(True)
collection = db["resources"]
cmmsDomain = "http://cmms.gloapi.com/"
mmsDomain = "http://mms.gloapi.com/"

part = "clothes"


def readMongo():
    resultList = list(collection.find(
        {"part": part, "iscmmsmail": {"$exists": 0}, "emailAddress": {"$ne": ""},
         "VideoTitleCount": {"$gte": 0}}))
    emails = []
    for result in resultList:
        emailAddress = result["emailAddress"]
        if emailAddress in emails:
            continue
            emails.append(emailAddress)
        if part == "GB":
            isExists = checkMail(emailAddress, mmsDomain)
        else:
            isExists = checkMail(emailAddress, cmmsDomain)
        if isExists:
            collection.update({"emailAddress": emailAddress, "part": part}, {"$set": {"iscmmsmail": True}}, upsert=True)
            print("存在cmms中{}".format(emailAddress))
        else:
            collection.update({"emailAddress": emailAddress, "part": part}, {"$set": {"iscmmsmail": False}},
                              upsert=True)
            print("不存在cmms中{}".format(emailAddress))


if __name__ == '__main__':
    readMongo()
