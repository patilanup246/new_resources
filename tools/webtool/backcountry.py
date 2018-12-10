import threading
from spider.getspider import getViewInfo
from urllib.request import urlparse
import logging


class backCountry(threading.Thread):
    def __init__(self, collection):
        threading.Thread.__init__(self)
        self.collection = collection

    def run(self):
        while True:
            resultList = list(self.collection.find({"country": ""}))
            urls = []
            for result in resultList:
                url = result["url"]
                if url in urls:
                    continue
                urls.append(url)
                self.dealResult(result)

    def dealResult(self, result):
        url = result["url"]
        domain = urlparse(url).netloc
        viewCountSimilarweb, countrySimilarweb, percentSimilarweb, relateLinkSimilarSites = getViewInfo(domain)
        if countrySimilarweb:
            self.collection.update({"url": url}, {"$set": {
                "country": countrySimilarweb,
                "viewCount": viewCountSimilarweb,
                "percent": percentSimilarweb,
                "relateLinkSimilarSites": relateLinkSimilarSites
            }}, multi=True)
            logging.info("回补国家信息成功:{}".format(url))
