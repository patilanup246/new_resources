import csv
import sys
import json

import time

sys.path.append('./../')
from db.mongodb import connectMongo

mongodb = connectMongo(True)
collection = mongodb["blackWhite"]

if __name__ == '__main__':
    with open("youtubewhite.csv", encoding="gbk") as csvfile:
        dataList = []
        csv_reader = csv.reader(csvfile)  # 使用csv.reader读取csvfile中的文件
        birth_header = next(csv_reader)  # 读取第一行每一列的标题
        for row in csv_reader:  # 将csv 文件中的数据保存到birth_data中
            word = row[0].strip()
            if not word:
                continue
            item = {
                "_id": "1_GB_" + word,
                "isWhite": True,
                "platId": 1,
                "isBlack": False,
                "word": word,
                "part": "GB"
            }
            try:
                collection.insert(item)
                print(item)
            except Exception as e:
                print(e)
