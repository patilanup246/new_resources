import sys
from urllib.parse import urlparse

sys.path.append("./..")
from db.mongodb import connectMongo

db = connectMongo(True)
webResourcesCollection = db["webResources"]
googleCollection = db["googleUrl"]
# blackUrl = db["blackUrl"]
urlList = googleCollection.distinct("url", {"isData": False})
import time
import threading


def updateItem(url):
    # 查询是否在web库中
    result = webResourcesCollection.find_one({"url": url})
    if result:
        print(url)
        googleCollection.update_one({"url": url}, {"$set": {"isData": True}})


for url in urlList:
    time.sleep(0.0001)
    th = threading.Thread(target=updateItem, args=(url,))
    th.start()
