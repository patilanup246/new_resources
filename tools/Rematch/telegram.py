import sys

sys.path.append('./../../')
import threading
from db.mongodb import connectMongo
import logging
import time

mongodb = connectMongo(True)
collection = mongodb["telegramResource"]
# 黑白名单
blackWhiteCollection = mongodb["blackWhite"]

# 黑名单列表
blackList = list(blackWhiteCollection.distinct("word", {"isBlack": True, "platId": 2, "part": "GB"}))
# 白名单列表
whiteList = list(blackWhiteCollection.distinct("word", {"isWhite": True, "platId": 2, "part": "GB"}))


class whiteReview(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        # while True:
        resultList = list(collection.find({}))
        if not resultList:
            logging.error("没有数据")
            time.sleep(120)
        for result in resultList:
            try:
                url = result["url"]
                descriptionChinese = result["descInfoCN"]
                description = result.get("descInfo")
                if not description:
                    description = ""
                part = result["part"]
                VideoTitleCount = 0
                whiteWord = ""
                for word in whiteList:
                    if word.lower() in description.lower() or word.lower() in descriptionChinese.lower():
                        VideoTitleCount += 1
                        # logging.info(word)
                        word_new = word + " "
                        whiteWord += word_new
                whiteWord = whiteWord.strip()

                blackWord = ""
                blackWordCount = 0
                for word in blackList:
                    if word in description or word in descriptionChinese:
                        blackWord += word + " "
                        blackWordCount += 1
                blackWord = blackWord.strip()
                try:
                    collection.update({"url": url, "part": part},
                                      {"$set": {"whiteWord": whiteWord,
                                                "VideoTitleCount": VideoTitleCount,
                                                "blackWord": blackWord,
                                                "blackWordCount": blackWordCount,
                                                }}, upsert=True, multi=True)
                    print("url:{},现在和黑名单:{},现在的白名单:{}".format(url, blackWord, whiteWord))
                except Exception as e:
                    pass
            except Exception as e:
                logging.error(e)


if __name__ == '__main__':
    youtubeObj = whiteReview()
    youtubeObj.start()
