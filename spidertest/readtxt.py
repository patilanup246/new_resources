import sys

sys.path.append("./..")

import logging
import requests
from fake_useragent import UserAgent

from tools.getip import getIp

from db.mongodb import connectMongo
from urllib.request import urlparse

from spider.webspider import getViewInfo, getalexaInfo

db = connectMongo(True)
collection = db["webResources"]
import time
import threading

file = open("./web.txt")
while True:
    url = file.readline().strip()
    if not url:
        break
    collection.update({"url": url}, {"$set": {"csvLoad": True}}, multi=True)
    print(url)

if __name__ == '__main__':
    pass
