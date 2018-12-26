import sys

sys.path.append('./../')

import csv
import os
import traceback
import os
from datetime import datetime

from db.mongodb import connectMongo
from db.mongoquery import mongoQuery

db = connectMongo(True)
from tools.mail.sendmail import send_email

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
]


def write(file, fieldList, collection, query):
    try:
        with open(file, "w", newline='', encoding="utf_8_sig") as csvfileWriter:
            writer = csv.writer(csvfileWriter)
            writer.writerow(fieldList)
            # urlList = collection.distinct("url", query)
            allRecordRes = mongoQuery(collection, query)
            print("总共数据量:{}".format(len(allRecordRes)))
            if len(allRecordRes) == 0:
                os.remove(file)
                return

            # 写入多行数据
            urlList = []
            for record in allRecordRes:
                # blackWord = record.get("blackWord")
                # if blackWord:
                #     continue
                # if record["VideoTitleCount"] >= 2:
                #     pass
                # elif record["VideoTitleCount"] == 1:
                #     if record["VideoTitleCount2"] >= 1:
                #         pass
                #     else:
                #         continue
                # else:
                #     continue
                recordValueLst = []
                try:
                    for field in list(fieldList):
                        if field not in record.keys():
                            recordValueLst.append("None")
                        else:
                            recordValueLst.append(record[field])
                    try:
                        print(recordValueLst)
                        writer.writerow(recordValueLst)
                    except Exception as e:
                        print(e)
                        # try:
                        #     collection.update_one({"_id": record["_id"]}, {"$set": {"csvLoad": True}})
                        # except Exception as e:
                        #     pass
                except Exception as e:
                    print(traceback.format_exc())
    except Exception as e:
        print(traceback.format_exc())


def writeweb(file, fieldList, collection, query):
    try:
        with open(file, "w", newline='', encoding="utf_8_sig") as csvfileWriter:
            writer = csv.writer(csvfileWriter)
            writer.writerow(fieldList)

            # urlList = collection.distinct("url", query)
            allRecordRes = mongoQuery(collection, query)
            print("总共数据量:{}".format(len(allRecordRes)))
            if len(allRecordRes) == 0:
                os.remove(file)
                return

            # 写入多行数据
            urlList = []
            for record in allRecordRes:
                whatRun = record.get("whatRun")
                if whatRun:
                    for word in cmsListErro:
                        if str(whatRun).lower().find(word.lower()) >= 0:
                            continue
                recordValueLst = []
                try:
                    for field in list(fieldList):
                        if field not in record.keys():
                            recordValueLst.append("None")
                        else:
                            recordValueLst.append(record[field])
                    try:
                        print(recordValueLst)
                        writer.writerow(recordValueLst)
                    except Exception as e:
                        print(e)
                        # try:
                        #     collection.update_one({"_id": record["_id"]}, {"$set": {"csvLoad": True}})
                        # except Exception as e:
                        #     pass
                except Exception as e:
                    print(traceback.format_exc())
    except Exception as e:
        print(traceback.format_exc())


def youtube():
    today = datetime.now()
    filepath = os.getcwd() + "/youtube/{}{}{}/".format(today.year, today.month, today.day)
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    collection = db["resources"]
    countryList = collection.distinct("country", {"ismms": False})

    for country in countryList:
        # file = filepath +
        fieldList = ["upTitle", "keyWord", "country", "isMail", "emailAddress", "Facebook", "description", "url",
                     "name", "VideoTitleCount",
                     "subscriberCount", "viewCountAvg", "titleLastUpdateTime", "viewCountFirst", "whiteWord",
                     "whiteWord2", "VideoTitleCount2"]
        query = {"country": country, "ismms": False, "VideoTitleCount": {"$gte": 1}}
        if not country:
            country = "all"
        # 查询
        file = filepath + "youtube" + country + ".csv"
        print(file)
        write(file, fieldList, collection, query)


def web():
    today = datetime.now()
    filepath = os.getcwd() + "/web/{}{}{}/".format(today.year, today.month, today.day)
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    collection = db["webResources"]
    countryList = collection.distinct("country", {"ismms": False, "part": "GB"})

    for country in countryList:
        # file = filepath +
        fieldList = ["url",
                     "part",
                     "whiteNum",
                     "whiteStr",
                     "titleChinese",
                     "emailStr",
                     "facebook",
                     "instagram",
                     "youtube",
                     "twitter",
                     "viewCount",
                     "country",
                     "percent",
                     "globalRankAlexa",
                     "countryAlexa",
                     "countryRankAlexa",
                     "status",
                     "firstName",
                     "lastName",
                     "sourcePage",
                     "position",
                     "isRight",
                     "blackNum",
                     "fhBlackWordCount"
                     ]
        query = {"country": country, "whiteNum": {"$gte": 3}, "fhBlackWordCount": 0, "blackNum": 0,
                 "ismms": False, "header": {"$ne": ""}, "footer": {"$ne": ""}, "part": "GB"}
        if not country:
            country = "all"
        # 查询
        file = filepath + "web" + country + ".csv"
        print(file)
        writeweb(file, fieldList, collection, query)


def writeCSV(file, fieldList, collection, query):
    try:
        with open(file, "w", newline='', encoding="utf_8_sig") as csvfileWriter:
            writer = csv.writer(csvfileWriter)
            writer.writerow(["url",
                             "事业部",
                             "白名单数量",
                             "白名单",
                             "标题描述",
                             "邮箱",
                             "facebook",
                             "instagram",
                             "youtube",
                             "twitter",
                             "流量",
                             "国家",
                             "百分比",
                             "邮箱是否可用",
                             ])

            # urlList = collection.distinct("url", query)
            allRecordRes = mongoQuery(collection, query)
            print("总共数据量:{}".format(len(allRecordRes)))
            if len(allRecordRes) == 0:
                os.remove(file)
                return

            # 写入多行数据
            urlList = []
            for record in allRecordRes:
                whatRun = record.get("whatRun")
                if whatRun:
                    for word in cmsListErro:
                        if str(whatRun).lower().find(word.lower()) >= 0:
                            continue

                blackNum = record.get("blackNum")
                if blackNum:
                    if blackNum != 0:
                        continue
                recordValueLst = []
                try:
                    for field in list(fieldList):
                        if field not in record.keys():
                            recordValueLst.append("None")
                        else:
                            recordValueLst.append(record[field])
                    try:
                        print(recordValueLst)
                        writer.writerow(recordValueLst)
                    except Exception as e:
                        print(e)
                    try:
                        collection.update_one({"_id": record["_id"]}, {"$set": {"csvLoad": True}})
                    except Exception as e:
                        pass
                except Exception as e:
                    print(traceback.format_exc())
    except Exception as e:
        print(traceback.format_exc())


if __name__ == '__main__':
    file = "./web以色列.csv"
    fieldList = ["url",
                 "part",
                 "whiteNum",
                 "whiteStr",
                 "titleChinese",
                 "emailStr",
                 "facebook",
                 "instagram",
                 "youtube",
                 "twitter",
                 "viewCount",
                 "country",
                 "percent",
                 "isRight",
                 ]
    collection = db["webResources"]
    query = {"country": "以色列", "whiteNum": {"$gte": 2}, "part": "GB", "ismms": False, "blackNum": 0,
             "fhBlackWordCount": 0}
    writeCSV(file, fieldList, collection, query)
