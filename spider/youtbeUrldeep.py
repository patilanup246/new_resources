import sys

urlList = [
    "https://www.youtube.com/channel/UCG8YbvNZiZ7VotHwWJD4Nbw",
    "https://www.youtube.com/channel/UCTiACSuWlwxw0WMCYr2n41g",
    "https://www.youtube.com/user/BenchTV",
    "https://www.youtube.com/channel/UCavyuuc-vW5XurigfRqhriw",
    "https://www.youtube.com/channel/UCSMlOhvjAn7jvFRIX0oHTMw",
    "https://www.youtube.com/user/rrraych",
    "https://www.youtube.com/channel/UCjVZkDTxofi37a3IHPaBLeg",
    "https://www.youtube.com/channel/UCcUlWLH4Qr2XI8n_1Yrtx1g",
    "https://www.youtube.com/channel/UCcTFMqWgKbEL-p_CLmbT0Dw",
    "https://www.youtube.com/channel/UC-d1mPNvjjuIaFFAwdQ6bsQ",
    "https://www.youtube.com/channel/UCA6dmsIq-u4i-4X9ErOzA7Q",
    "https://www.youtube.com/channel/UCHFsgSxmjWP_DRnzO9ac5bw",
    "https://www.youtube.com/channel/UCKwqMylQgZIV2Oqq7C7ku1Q",
    "https://www.youtube.com/channel/UCieuwqJy9JROM9bt5oMypOw",
    "https://www.youtube.com/channel/UCTSXDQRpJcGjLubm8CaCPWA",
    "https://www.youtube.com/channel/UCrum5zljMbqR_8HPuM74z4A",
    "https://www.youtube.com/channel/UCe1wck8XdyX6zjF4jIeTiYQ",
    "https://www.youtube.com/channel/UCvG2HYD8_mIcOeSCXBqeCMQ",
    "https://www.youtube.com/channel/UCGAOiyBBov9SBzHYI14m2oQ",
    "https://www.youtube.com/user/ChannelOfMiakaStar",
    "https://www.youtube.com/channel/UCGk87EgdZ7A61WIPEvoMGnw",
    "https://www.youtube.com/channel/UC4uF23SfGe1Mu-jMfd_mmRQ",
    "https://www.youtube.com/channel/UCUfSt4SOmHr2h-sJrjh3jNw",
    "https://www.youtube.com/channel/UCwR1lLNctdqD9NwySF_t-TQ",
    "https://www.youtube.com/channel/UC_czN3dOCvMrqKpNUo-f4IA",
    "https://www.youtube.com/channel/UC-mKTrG8jrc6wTKkxx7w-yg",
    "https://www.youtube.com/channel/UCp2Fm1fzjSAMmlnZ8F-C1nA",
    "https://www.youtube.com/channel/UCK_a_kGsvmKct-6b3TcUzmA",
    "https://www.youtube.com/channel/UCFMubAzy5RcTrLigSRA5jQg",
    "https://www.youtube.com/channel/UCyoLstvUOn_0D646NWwomdA",
    "https://www.youtube.com/channel/UCrPo31V8wpuuCMseyzEDZMQ"
]
sys.path.append("./..")
from db.mongodb import connectMongo
from spider.youtubedeep import YouTuBe
import time
from fake_useragent import UserAgent
import logging
from multiprocessing.pool import ThreadPool

mongoDB = connectMongo(True)
youtubeUrl = mongoDB["youtubeUrl"]
resource = mongoDB["resources"]
collection = mongoDB["resources"]
youtubeObj = YouTuBe()
import requests

platId = 1


def readMongoUrl():
    while True:
        resultList = list(youtubeUrl.find({"getData": False}).limit(4))
        if not resultList:
            print("没有需要相关挖掘的url")
            time.sleep(60)
            continue
        for result in resultList:
            dealResult(result)


def dealResult(result):
    url = result["url"]
    try:
        youtubeUrl.update_one({"url": url}, {"$set": {"getData": True}})
    except Exception as e:
        print(e)

    resulgMongo = collection.find_one({"url": url})
    if resulgMongo:
        print("存在数据库中:{}".format(url))
        return
    # keyWord, name, part, station
    keyWord = result.get("keyWord")
    if not keyWord:
        keyWord = ""

    name = result.get("name")
    if not name:
        name = ""

    part = result.get("part")
    if not part:
        part = "GB"

    language = result.get("language")
    if not language:
        language = ""

    station = result.get("station")
    if not station:
        station = ""
    sendRequestUser(url, keyWord, name, part, station, language)


def sendRequestUser(url, keyWord, name, part, station, language):
    try:
        userUrl = url + "/about?pbj=1"
        headers = {
            "accept-language": "zh-CN,zh;q=0.9",
            "user-agent": UserAgent().random,
            "x-youtube-client-name": "1",
            "x-youtube-client-version": "2.20181204",
        }
        userItem = {}
        for i in range(3):
            try:
                response = requests.get(url=userUrl, headers=headers, timeout=5, verify=False)
                response.encoding = "utf-8"
                if response.status_code == 200:
                    userItem = youtubeObj.parsePageUser(response.text, userUrl, part, name)
                    break
            except Exception as e:
                if repr(e).find("timed out") > 0:
                    logging.error("请求超时{}次,url:{}".format(i + 1, userUrl))
                else:
                    logging.error(e)

        if userItem:
            url = userItem["url"]
            videoUrl = url + "/videos?pbj=1"
            videoItem = {}
            for i in range(3):
                try:
                    response = requests.get(url=videoUrl, headers=headers, timeout=5, verify=False)
                    response.encoding = "utf-8"
                    if response.status_code == 200:
                        videoItem = youtubeObj.parsePageVideo(response.text, videoUrl, part, station,
                                                              userUrl=userUrl)
                        break
                except Exception as e:
                    if repr(e).find("timed out") > 0:
                        logging.error("请求超时{}次,url:{}".format(i + 1, videoUrl))
                    else:
                        logging.error(e)
            if videoItem:
                item = {}
                for key, value in userItem.items():
                    item[key] = value
                for key, value in videoItem.items():
                    item[key] = value
                # item["url"] = url
                item["keyWord"] = keyWord
                item["platId"] = platId
                item["csvLoad"] = False
                item["isDeep"] = False
                item["isRecaptcha"] = False
                item["lastUpdate"] = int(time.time())
                item["name"] = name
                item["station"] = station
                item["_id"] = "1_" + part + "_" + item["url"]
                item["part"] = part
                item["language"] = language
                try:
                    collection.insert(dict(item))
                except Exception as e:
                    logging.error(e)
                try:
                    relateChannel = item["relateChannel"]
                    if relateChannel:
                        for url in relateChannel.split("\n"):
                            result = youtubeUrl.find_one({"url": url})
                            if result:
                                continue
                            youtubeUrl.insert({
                                "_id": url,
                                "url": url,
                                "getData": False,
                                "keyWord": keyWord,
                                "name": name,
                                "part": part,
                                "station": station,
                                "language": language
                            })
                except Exception as e:
                    print(e)
    except Exception as e:
        logging.exception(e)


def getInfo(url):
    pass


def getRelateUrl():
    urls = []
    for url in urlList:
        urlresult = resource.find_one({"url": url, "name": {"$exists": 1}, "relateChannel": {"$ne": ""}})
        if urlresult:
            relateChannel = urlresult["relateChannel"]
            for url in relateChannel.split("\n"):
                if url not in urls:
                    urls.append(url)
        else:
            pass
    for url in urls:
        try:
            youtubeUrl.insert({
                "_id": url,
                "url": url,
                "getData": False
            })
        except Exception as e:
            print(e)


if __name__ == '__main__':
    # getRelateUrl()
    readMongoUrl()
