import csv
import traceback
import os
from datetime import datetime
# 初始化数据库
from db.mongodb import connectMongo
from datetime import datetime
import logging

from db.mongoquery import mongoQuery
import logging

db = connectMongo(True)
database = "globalegrow"
table = "resources"
db_des_table = db[table]


# 将数据写入到CSV文件中
# 如果直接从mongod booster导出, 一旦有部分出现字段缺失，那么会出现结果错位的问题

# newline='' 的作用是防止结果数据中出现空行，专属于python3
def writeCsv(file, name):
    try:
        with open(file, "w", newline='', encoding="utf_8_sig") as csvfileWriter:
            writer = csv.writer(csvfileWriter)
            # 先写列名
            # 写第一行，字段名
            fieldList = ["upTitle", "keyWord", "country", "isMail", "emailAddress", "Facebook", "description", "url",
                         "name", "VideoTitleCount",
                         "subscriberCount", "viewCountAvg", "titleLastUpdateTime", "viewCountFirst", "whiteWord"]
            writer.writerow(fieldList)
            if name == "袁平":
                allRecordRes = mongoQuery(db_des_table,
                                          {"csvLoad": False, "name": name, "VideoTitleCount": {"$gte": 2}})
            else:
                allRecordRes = mongoQuery(db_des_table,
                                          {"csvLoad": False, "name": name, "VideoTitleCount": {"$gte": 6}})
            logging.info("总共数据量:{}".format(len(allRecordRes)))
            if len(allRecordRes) == 0:
                os.remove(file)
                return

            # 写入多行数据
            for record in allRecordRes:
                if record["name"] == "袁平":
                    if record["VideoTitleCount"] >= 2 and record["isMail"] and record["emailAddress"] == "":
                        if not record["isRecaptcha"]:
                            continue
                else:
                    if record["VideoTitleCount"] >= 6 and record["isMail"] and record["emailAddress"] == "":
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
    except Exception as e:
        logging.error(traceback.format_exc())


def getName():
    today = datetime.now()
    filepath = os.path.abspath(os.path.join(os.getcwd(), "../..")) + "/file/{}_{}_{}/".format(today.year, today.month,
                                                                                              today.day)
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    nameList = db_des_table.distinct("name")
    for name in nameList:
        if not name:
            continue
        fileName = filepath + name + "_{}_{}_{}.csv".format(today.year, today.month, today.day)
        logging.info(fileName)
        writeCsv(fileName, name)
    return filepath


if __name__ == '__main__':
    getName()
