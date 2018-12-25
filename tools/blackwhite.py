import csv
import sys
import time

sys.path.append('./../')
from db.mongodb import connectMongo

mongodb = connectMongo(True)
collection = mongodb["blackWhite"]

if __name__ == '__main__':
    datalist = []
    with open("blackwhite.csv", encoding="gbk", newline='', ) as csvfile:
        dataList = []
        csv_reader = csv.reader(csvfile)
        birth_header = next(csv_reader)
        for row in csv_reader:
            print(row)
            dataList.append(row)
        for row in dataList:
            if row[0].strip() == "黑名单":
                isWhite = False
                isBlack = True
            elif row[0].strip() == "白名单":
                isBlack = False
                isWhite = True
            elif row[0].strip() == "白名单2":
                datalist.append(row[1].strip())

            if row[3].strip().lower() == "gearbest":
                part = "GB"
                station = "GearBest"
            elif row[3].strip().lower() == "zaful":
                part = "clothes"
                station = "Zaful"

            elif row[3].strip().lower() == "rosegal":
                part = "clothes"
                station = "Rosegal"

            elif row[3].strip().lower() == "dresslily":
                part = "clothes"
                station = "Dresslily"
            else:
                continue

            if row[5].strip() == "web":
                platId = 3
            elif row[5].strip() == "youtube":
                platId = 1
            elif row[5].strip() == "FB":
                platId = 2
            else:
                continue

            item = {
                "_id": str(platId) + "_" + part + "_" + station + "_" + row[1].strip(),
                "isWhite": isWhite,
                "platId": platId,
                "isBlack": isBlack,
                "word": row[1].strip(),
                "part": part,
                "station": station,
                "person": row[2].strip(),
                "date": row[4].strip(),
                "insertTime": int(time.time())
            }
            try:
                collection.insert(item)
                print(item)
            except Exception as e:
                print(e)
