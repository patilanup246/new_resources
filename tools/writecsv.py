import pymongo
import csv
import traceback
import os

# 初始化数据库
from db.mongodb import connectMongo
from datetime import datetime
import logging

from db.mongoquery import mongoQuery

db = connectMongo(True)
database = "globalegrow"
table = "userInfo"
db_des_table = db[table]

# yesterady
yesterady = 0
today = 0


# 将数据写入到CSV文件中
# 如果直接从mongod booster导出, 一旦有部分出现字段缺失，那么会出现结果错位的问题

# newline='' 的作用是防止结果数据中出现空行，专属于python3
def writeCsv():
    try:
        file = os.path.abspath(os.path.join(os.getcwd(), "../..")) + "/file/{}{}.csv".format(table,
                                                                                             str(datetime.now())[:10])
        with open(file, "w", newline='', encoding="utf_8_sig") as csvfileWriter:
            writer = csv.writer(csvfileWriter)
            # 先写列名
            # 写第一行，字段名
            fieldList = ["upTitle", "keyWord", "country", "isMail", "emailAddress", "Facebook", "description", "url",
                         "name", "VideoTitleCount",
                         "subscriberCount", "viewCountAvg", "titleLastUpdateTime", "viewCountFirst", "whiteWord"]
            # print(list(fieldList[0].keys()))
            writer.writerow(fieldList)

            # allRecordRes = list(db_des_table.find({"csvLoad": False}))
            allRecordRes = mongoQuery(db_des_table, {"csvLoad": False, "VideoTitleCount": {"$gte": 2}})
            logging.info("总共数据量:{}".format(len(allRecordRes)))
            # 写入多行数据
            for record in allRecordRes:
                if record["VideoTitleCount"] >= 3:
                    if not record["isRecaptcha"]:
                        continue
                # print(record)
                recordValueLst = []
                try:
                    for field in list(fieldList):
                        if field not in record.keys():
                            recordValueLst.append("None")
                        else:
                            recordValueLst.append(record[field])
                    try:
                        writer.writerow(recordValueLst)
                    except Exception as e:
                        print(e)
                    try:
                        db_des_table.update_one({"_id": record["_id"]}, {"$set": {"csvLoad": True}})
                    except Exception as e:
                        return None
                except Exception as e:
                    print(traceback.format_exc())
        return file
    except Exception as e:
        logging.error(traceback.format_exc())


def getName():
    nameList = db_des_table.distinct("name")
    for name in nameList:
        pass


if __name__ == '__main__':
    getName()
