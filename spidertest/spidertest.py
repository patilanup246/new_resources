import sys

sys.path.append("./..")
from logs.loggerDefine import loggerDefine
from multiprocessing.pool import ThreadPool
from db.mongodb import connectMongo
import time
import json

loggerFile = "backlog.log"
logging = loggerDefine(loggerFile)
db = connectMongo(True)
webResourcesCollection = db["webResources"]
import re


def main_process(result):
    part = result["part"]
    url = result["url"]
    print(url)
    webResourcesCollection.remove({"url": url})
    try:
        emailList = list(set(result["connect"].split("\n")))
    except Exception as e:
        return
    for num, email in enumerate(emailList):
        result["_id"] = "3_" + part + "_" + url + "_" + str(num + 1)
        # [status, email, firstName, lastName, sourcePage, position]
        # status:notVerified,email:kerry@bikebling.com,firstName: ,lastName: ,sourcePage: ,position:
        status = re.search("status:(.*?),", email).group(1).strip()
        emailStr = re.search("email:(.*?),", email).group(1).strip()
        firstName = re.search("firstName:(.*?),", email).group(1).strip()
        lastName = re.search("lastName:(.*?),", email).group(1).strip()
        sourcePage = re.search("sourcePage:(.*?),", email).group(1).strip()
        position = re.search("position:(.*?)", email).group(1).strip()
        print(
            "status:{},email:{},firstName:{},lastName:{},sourcePage:{},position:{}".format(status, emailStr, firstName,
                                                                                           lastName, sourcePage,
                                                                                           position))

        if not emailStr:
            continue
        result["emailStr"] = emailStr
        result["status"] = status
        result["firstName"] = firstName
        result["lastName"] = lastName
        result["sourcePage"] = sourcePage
        result["position"] = position
        result["isGetLink"] = True
        result["connect"] = ""
        try:
            webResourcesCollection.insert(result)
        except Exception as e:
            logging.error(e)


def readMongo():
    resultList = list(webResourcesCollection.distinct("emailStr",{"emailStr": {"$ne": ""}}))
    for result in resultList:

        mail = result.split("\n")

        if len(mail) != 1:
            print(1)


if __name__ == '__main__':
    readMongo()
