import csv
import os
import traceback

from datetime import datetime

from db.mongodb import connectMongo
from db.mongoquery import mongoQuery


def write(file, fieldList, collection, query):
    try:
        with open(file, "w", newline='', encoding="utf_8_sig") as csvfileWriter:
            writer = csv.writer(csvfileWriter)
            writer.writerow(fieldList)
            allRecordRes = mongoQuery(collection, query)
            print("总共数据量:{}".format(len(allRecordRes)))
            if len(allRecordRes) == 0:
                os.remove(file)
                return

            # 写入多行数据
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
    file = "./youtube菲律宾{}_{}_{}.csv".format(today.year, today.month, today.day)
    fieldList = ["upTitle", "keyWord", "country", "isMail", "emailAddress", "Facebook", "description", "url",
                 "name", "VideoTitleCount",
                 "subscriberCount", "viewCountAvg", "titleLastUpdateTime", "viewCountFirst", "whiteWord", "videoTittle"]
    db = connectMongo(True)
    collection = db["resources"]
    query = {"country": "菲律宾", "part": "clothes"}
    write(file, fieldList, collection, query)
