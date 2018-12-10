import sys

sys.path.append('./../')

import csv
import os
import traceback
import os

print(os.getcwd())

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
    "vtex enterprise"
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
                url = record["url"]

                isRight = record.get("isRight")
                if isRight == None:
                    # 代表还没有验证邮箱状态
                    pass
                else:
                    if not isRight:
                        # 代表邮箱不可用  只导出一条数据
                        pass
                    else:
                        # 代表邮箱可用
                        pass

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
                        if url not in urlList:
                            urlList.append(url)
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
    countryList = collection.distinct("country", {"ismms": False})

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
        query = {"country": country, "whiteNum": {"$gte": 3}, "fhBlackWordCount": {"$lte": 1}, "blackNum": {"$lte": 1},
                 "ismms": False, "header": {"$ne": ""}, "footer": {"$ne": ""}, "csvLoad": False}
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
    file = "./web菲律宾.csv"
    fieldList = ["url",
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
                 "status",
                 "firstName",
                 "lastName",
                 "position",
                 "isRight",
                 "blackNum",
                 "fhBlackWordCount"
                 ]
    collection = db["webResources"]
    query = {"country": "菲律宾", "csvLoad": False, "whiteNum": {"$gte": 1}, "ismms": False, "part": 'GB',
             "fhBlackWordCount": 0, "blackNum": 0}
    writeCSV(file, fieldList, collection, query)
