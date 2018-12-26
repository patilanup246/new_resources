import sys

sys.path.append('./../')
from datetime import datetime
import csv
import os
import traceback
import os
from datetime import datetime

from db.mongodb import connectMongo
from db.mongoquery import mongoQuery

db = connectMongo(True)


def writeCSV(file, fieldList, collection, query):
    try:
        with open(file, "w", newline='', encoding="utf_8_sig") as csvfileWriter:
            writer = csv.writer(csvfileWriter)
            writer.writerow([
                "语言",
                "描述信息",
                "描述信息中文"
                "站点",
                "人员信息",
                "标题",
                "关键字",
                "url",
                "站点",
                "白名单",
                "黑名单",
                "黑名单数量",
                "白名单数量"])

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
                        # try:
                        #     collection.update_one({"_id": record["_id"]}, {"$set": {"csvLoad": True}})
                        # except Exception as e:
                        #     pass
                except Exception as e:
                    print(traceback.format_exc())
    except Exception as e:
        print(traceback.format_exc())


if __name__ == '__main__':
    today = datetime.now()
    file = "./file/tlelgram{}.{}.{}.{}.csv".format(today.year, today.month, today.day, today.hour)
    fieldList = [
        "language",
        "descInfo",
        "descInfoCN",
        "station",
        "memberInfo",
        "pageTitle",
        "keyWord",
        "url",
        "part",
        "whiteWord",
        "blackWord",
        "blackWordCount",
        "VideoTitleCount"]
    collection = db["telegramResource"]
    query = {"VideoTitleCount": {"$exists": 1}}
    writeCSV(file, fieldList, collection, query)
