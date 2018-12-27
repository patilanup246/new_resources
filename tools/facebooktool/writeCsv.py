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
            writer.writerow(["描述信息",
                             "成员数量",
                             "url",
                             "群名称",
                             "群类型",
                             "30天内发帖数",
                             "群主链接",
                             "事业部",
                             "关键词",
                             "关键词语言",
                             "白名单",
                             "表名单数量",
                             ])
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
    today = datetime.now()
    file = "./file/facebook{}.{}.{}.{}.csv".format(today.year, today.month, today.day, today.hour)
    fieldList = ["description",
                 "groupNum",
                 "url",
                 "groupName",
                 "groupType",
                 "postNum",
                 "manager",
                 "part",
                 "keyWord",
                 "language",
                 "whiteWord",
                 "whiteNum",
                 ]
    collection = db["fbresources"]
    query = {"language": {"$regex": "希伯来"}, "blackNum": 0, "whiteNum": {"$gte": 1}, "groupType": {"$ne": "二手交易"},
             "groupNum": {"$gte": 100}}
    writeCSV(file, fieldList, collection, query)
