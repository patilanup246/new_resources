import time

from db.mongodb import connectMongo
from multiprocessing.pool import ThreadPool
import threading

from db.mongoquery import mongoQuery

db = connectMongo(True)
collection = db["blackWhite"]
file = open("./pbc.txt", "r", encoding="utf-8", errors="ignore")


def writeMongo(words):
    try:
        collection.insert({
            "_id": words,
            "isBlack": True,
            "word": words,
            "isWhite": False
        })
    except Exception as e:
        print(e)


while True:
    text = file.readline()
    if not text:
        break
    words = text.strip()
    print(words)
    time.sleep(0.005)
    th = threading.Thread(target=writeMongo, args=(words,))
    th.start()
