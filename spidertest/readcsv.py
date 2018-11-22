# _*_ coding:utf-8 _*_
import csv

import sys
from urllib.parse import urlparse

sys.path.append("./..")
import time

from db.mongodb import connectMongo
import threading

db = connectMongo(True)
collection = db["googleUrl"]
import traceback


def readCsvFile():
    with open("hole.csv", encoding="gbk") as csvfile:
        dataList = []
        csv_reader = csv.reader(csvfile)  # 使用csv.reader读取csvfile中的文件
        birth_header = next(csv_reader)  # 读取第一行每一列的标题
        try:
            for row in csv_reader:  # 将csv 文件中的数据保存到birth_data中
                url = row[0]
                scheme = urlparse(url).scheme
                domain = urlparse(url).netloc
                url = scheme + "://" + domain
                print(url)
                item = {
                    "_id": domain,
                    "url": url,
                    "sourceUrl": url,
                    "domain": domain,
                    "scheme": scheme,
                    "keyWord": "",
                    "language": "",
                    "name": "服装吴泽荣",
                    "title": "",
                    "desc": "",
                    "isData": False,
                    "word": "",
                    "insertTime": int(time.time()),
                    "part": "clothes",
                    "station": "Zaful"
                }
                print(item)
                try:
                    collection.insert(item)
                except Exception as e:
                    pass

        except Exception as e:
            print(traceback.format_exc())


if __name__ == '__main__':
    readCsvFile()
