import os
import sys

sys.path.append("./..")
from logs.loggerDefine import loggerDefine
from tools.getip import getIp
from tools.checkurl import checkUrl, checkMail

youtubeDir = "./../logs/youtube/"
if not os.path.exists(youtubeDir):
    os.makedirs(youtubeDir)
loggerFile = youtubeDir + "youtubedeep.log"
logging = loggerDefine(loggerFile)
import traceback
import re
from tools.translate.translate_google import mainTranslate
from db.mongodb import connectMongo
from db.mongoquery import mongoQuery
from tools.translate.translateYoudao import *
from fake_useragent import UserAgent
import threading

platId = 1
debug_flag = True if sys.argv[1] == "debug" else False
# mongodb
mongodb = connectMongo(debug_flag)

# 用户信息
collection = mongodb["resources"]

mmsDomain = "http://mms.gloapi.com/"
cmmsDomain = "http://cmms.gloapi.com/"

# 关键字信息
keyWordCollection = mongodb["keyWords"]

# 黑白名单
blackWhiteCollection = mongodb["blackWhite"]

# 黑名单列表
blackList = list(blackWhiteCollection.distinct("word", {"isBlack": True, "platId": 1, "part": "GB"}))
clothesblackList = list(blackWhiteCollection.distinct("word", {"isBlack": True, "platId": 1, "part": "clothes"}))
# 白名单列表
whiteList = list(blackWhiteCollection.distinct("word", {"isWhite": True, "platId": 1, "part": "GB"}))
clotheswhiteList = list(blackWhiteCollection.distinct("word", {"isWhite": True, "platId": 1, "part": "clothes"}))
zafulWhiltList = list(
    blackWhiteCollection.distinct("word", {"isWhite": True, "platId": 1, "part": "clothes", "station": "Zaful"}))

# 已存在的url

whiteCount = 4

invisibleUrl = mongodb["invisibleUrl"]


class YouTuBe(object):
    def __init__(self):
        self.nextPageUrl = ""
        self.userUrlList = []
        self.formData = {}
        self.thList = []
        self.pageNum = 9
        self.videoNum = 8
        self.VideoTitleCount = 1

    def sendRequestExcavate(self, url, keyWord, name, part, stationName):
        relateChannel = None
        try:
            userUrl = url + "/about?pbj=1"
            headers = {
                "accept-language": "zh-CN,zh;q=0.9",
                "referer": url,
                "user-agent": UserAgent().random,
                "x-client-data": "CIu2yQEIpLbJAQjBtskBCKmdygEIqKPKARj5pcoB",
                "x-spf-previous": url,
                "x-spf-referer": url,
                "x-youtube-client-name": "1",
                "x-youtube-client-version": "2.20181025",
                "x-youtube-page-cl": "218622685",
                "x-youtube-page-label": "youtube.ytfe.desktop_20181024_8_RC0",
                "x-youtube-sts": "17829",
                "x-youtube-utc-offset": "480",
                "x-youtube-variants-checksum": "80cb024c85d222102f525ddbcc2d0915"
            }
            userItem = {}
            logging.info("获取用户about页面,url:{}".format(url + "/about"))
            for i in range(3):
                try:
                    response = requests.get(url=userUrl, headers=headers, timeout=5, proxies={})
                    response.encoding = "utf-8"
                    if response.status_code == 200:
                        userItem = self.parsePageUser(response.text, userUrl, part)
                        break
                except Exception as e:
                    if repr(e).find("timed out") > 0:
                        logging.error("请求超时,url:{}".format(userUrl))
                    else:
                        logging.error(e)

            if userItem:
                url = userItem["url"]
                videoUrl = url + "/videos?pbj=1"
                videoItem = {}
                logging.info("获取用户videos页面,url:{}".format(url + '/videos'))
                for i in range(3):
                    try:
                        response = requests.get(url=videoUrl, headers=headers, timeout=5, proxies={})
                        response.encoding = "utf-8"
                        if response.status_code == 200:
                            videoItem = self.parsePageVideo(response.text, videoUrl, part, stationName, userItem["url"])
                            break
                    except Exception as e:
                        if repr(e).find("timed out") > 0:
                            logging.error("请求超时,url:{}".format(videoUrl))
                        else:
                            logging.error(e)
                if videoItem:
                    item = {}
                    for key, value in userItem.items():
                        item[key] = value
                    for key, value in videoItem.items():
                        item[key] = value
                    # item["_id"] = "1_" + userItem["upTitle"]
                    # item["url"] = url
                    item["keyWord"] = keyWord
                    item["platId"] = 1
                    item["csvLoad"] = False
                    item["isDeep"] = True
                    item["isRecaptcha"] = False
                    item["lastUpdate"] = int(time.time())
                    item["name"] = name
                    item["part"] = part
                    item["station"] = stationName
                    item["_id"] = str(platId) + "_" + part + "_" + item["url"]
                    emailAddress = item["emailAddress"]
                    mailExists = False  # 不存在
                    if emailAddress:
                        if part == "clothes":
                            if item["VideoTitleCount"] >= 4:
                                cmmsDomain = "http://cmms.gloapi.com/"
                                isExists = checkMail(emailAddress, cmmsDomain)
                                if isExists:
                                    logging.warn("邮箱存在cmms中,{}".format(emailAddress))
                                    # 代表存在数据库中
                                    mailExists = True
                    if not mailExists:
                        try:
                            collection.insert(item)
                        except Exception as e:
                            logging.error(e)
                    if videoItem["VideoTitleCount"] >= whiteCount:
                        relateChannel = item["relateChannel"].strip().split("\n")
        except Exception as e:
            logging.exception(e)

        return relateChannel, keyWord

    def deepExcavate(self, _id, relateChannel, keyWord, name, part, station):
        if not relateChannel:
            return
        relateChannelurlList = relateChannel.split("\n")
        urlList = relateChannelurlList
        if not urlList:
            return
        ExistUrl = []
        num = 0
        while True:
            num += 1
            if not urlList:
                break
            for url in urlList:
                if not urlList:
                    break
                urlList.remove(url)
                url = url.strip()
                if not url:
                    continue
                if url in self.userUrlList:
                    continue
                if url in self.thList:
                    continue
                if url in ExistUrl:
                    continue

                result = invisibleUrl.find_one({"url": url})
                if result:
                    logging.warn("观看量或者订阅量不达标,name:{},url:{}".format(name, url))
                    continue

                    # 判断是否在数据库中
                result = collection.find_one({"part": part, "url": url, "platId": 1})
                if result:
                    logging.warn("存在库中part:{},name:{},url:{}".format(part, name, url))
                    continue

                if part == "clothes":
                    # 判断是否在cmms中
                    domain = "http://cmms.gloapi.com/"
                    isExists = checkUrl(url, domain)
                    if isExists:
                        try:
                            collection.insert({
                                "_id": str(platId) + "_" + part + "_" + url,
                                "url": url,
                                "platId": platId,
                                "part": part,
                                "lastUpdate": int(time.time())
                            })
                            logging.warn("存在cmms中part:{},name:{},url:{}".format(part, name, url))
                        except Exception as e:
                            logging.error(e)
                        # 代表存在接口中
                        continue
                elif part == "GB":
                    # 判断是否在mms中
                    domain = "http://mms.gloapi.com/"
                    isExists = checkUrl(url, domain)
                    if isExists:
                        try:
                            collection.insert({
                                "_id": str(platId) + "_" + part + "_" + url,
                                "url": url,
                                "platId": platId,
                                "part": part,
                                "lastUpdate": int(time.time())
                            })
                            logging.warn("存在mms中part:{},name:{},url:{}".format(part, name, url))
                        except Exception as e:
                            logging.error(e)
                        # 代表存在接口中
                        continue

                self.userUrlList.append(url)
                ExistUrl.append(url)

                try:
                    channelList, keyWord = self.sendRequestExcavate(url, keyWord, name, part, station)
                except Exception as e:
                    logging.error(traceback.format_exc())
                    continue
                if channelList:
                    for urlChanel in channelList:
                        if urlChanel not in ExistUrl:
                            if urlChanel in urlList:
                                urlList.append(urlChanel)

            if num > 100:
                break
            logging.info("第{}圈,keyWord:{}".format(num, keyWord))

        try:
            collection.update_one({"_id": _id}, {"$set": {"isDeep": True}})
        except Exception as e:
            logging.error(e)

            # 视频信息

    def parsePageVideo(self, response, videoUrl, part, station, userUrl):
        response = json.loads(response)
        titleList = jsonpath.jsonpath(response, "$..gridRenderer.items..title..simpleText")
        # 取8个
        titleList = titleList[:self.videoNum]
        lastUpdateTimeList = jsonpath.jsonpath(response, "$..gridRenderer.items..publishedTimeText.simpleText")
        lastUpdateTimeList = lastUpdateTimeList[:self.videoNum]
        if "年" in lastUpdateTimeList[0]:
            try:
                invisibleUrl.insert({
                    "_id": str(platId) + "_" + userUrl,
                    "url": userUrl,
                    "platId": platId,
                    "insertTime": int(time.time()),
                    "titleLastUpdateTime": lastUpdateTimeList[0]
                })
            except Exception as e:
                pass
            return None
        if "月" in lastUpdateTimeList[0]:
            if int(re.search(r"(\d+)", lastUpdateTimeList[0]).group(1)) > 6:
                try:
                    invisibleUrl.insert({
                        "_id": str(platId) + "_" + userUrl,
                        "url": userUrl,
                        "platId": platId,
                        "insertTime": int(time.time()),
                        "titleLastUpdateTime": lastUpdateTimeList[0]
                    })
                except Exception as e:
                    logging.error(traceback.format_exc())
                return None

        viewCountTextList = jsonpath.jsonpath(response, "$..gridRenderer.items..viewCountText.simpleText")
        viewCountTextList = viewCountTextList[:self.videoNum]

        totalViewCount = 0
        viewCountList = []
        for viewCountText in viewCountTextList:
            try:
                viewCount = int(
                    viewCountText.replace("次观看", "").replace("人正在观看", "").replace(",", "").strip())
                viewCountList.append(viewCount)
                totalViewCount += viewCount
            except Exception as e:
                # logging.info(viewCountText)
                continue
        if int(totalViewCount / len(titleList)) < 4000:
            logging.error("播放量低于4000,url:{}".format(videoUrl))
            try:
                invisibleUrl.insert({
                    "_id": str(platId) + "_" + userUrl,
                    "url": userUrl,
                    "platId": platId,
                    "insertTime": int(time.time()),
                    "viewCountAvg": int(totalViewCount / len(titleList))
                })
            except Exception as e:
                logging.error(traceback.format_exc())
            return None
        videoTittle = ""
        for title, lastUpdateTime, viewCount in zip(titleList, lastUpdateTimeList, viewCountList):
            videoTittle += title + "\n"
        # videoTittle = youdao(videoTittle)
        if not videoTittle.strip():
            videoTittleChinese = ""
        else:
            videoTittleChinese = mainTranslate(videoTittle)
        VideoTitleCount = 0
        whiteWord = ""
        if part == "GB":
            whiteListall = whiteList
        else:
            whiteListall = clotheswhiteList
            if station == "Zaful":
                whiteListall = zafulWhiltList
        for word in whiteListall:
            if word.lower() in videoTittle.lower() or word.lower() in videoTittleChinese.lower():
                VideoTitleCount += 1
                # logging.info(word)
                word_new = word + " "
                whiteWord += word_new

        logging.error("part:{},匹配度等于{}分,videoUrl:{},匹配单词:{}".format(part, VideoTitleCount, userUrl,
                                                                    whiteWord.strip()))
        try:
            titleFirst = videoTittleChinese.split("\n")[0]
        except Exception as e:
            titleFirst = ""

        try:
            viewCountFirst = int(
                viewCountTextList[0].replace("次观看", "").replace("人正在观看", "").replace(",", "").strip())
        except Exception as e:
            viewCountFirst = 0

        item = {
            "videoTittle": videoTittleChinese,
            "videotitleUn": videoTittle,
            "viewCountAvg": int(totalViewCount / len(titleList)),
            "titleLastUpdateTime": lastUpdateTimeList[0],
            "whiteWord": whiteWord.strip(),
            "VideoTitleCount": VideoTitleCount,
            "titleFirst": titleFirst,
            "viewCountFirst": viewCountFirst
        }
        return item

    def parsePageUser(self, response, url, part):
        try:
            responseBody = json.loads(response)
            try:
                responseText = responseBody[1]
            except Exception as e:
                return None

            # 获取url
            try:
                urlList = jsonpath.jsonpath(responseBody, "$..ownerUrls")[0]
            except Exception as e:
                logging.error(e)
                return None
            userurl = ""
            for i in urlList:
                if "www.youtube.com" not in i:
                    continue
                userurl = "https://" + i.split("://")[-1]
            if not userurl:
                return None

            result = invisibleUrl.find_one({"url": userurl})
            if result:
                logging.warn("观看量或者订阅量不达标,name:{},url:{}".format(name, userurl))
                return None

                # 判断是否在数据库中
            result = collection.find_one({"part": part, "url": userurl, "platId": 1})
            if result:
                logging.warn("存在库中part:{},name:{},url:{}".format(part, name, userurl))
                return None

            if part == "clothes":
                # 判断是否在cmms中
                domain = "http://cmms.gloapi.com/"
                isExists = checkUrl(userurl, domain)
                if isExists:
                    try:
                        collection.insert({
                            "_id": str(platId) + "_" + part + "_" + userurl,
                            "url": userurl,
                            "platId": platId,
                            "part": part,
                            "lastUpdate": int(time.time())
                        })
                        logging.warn("存在cmms中part:{},name:{},url:{}".format(part, name, userurl))
                    except Exception as e:
                        logging.error(e)
                    # 代表存在接口中
                    return None
            elif part == "GB":
                # 判断是否在mms中
                domain = "http://mms.gloapi.com/"
                isExists = checkUrl(userurl, domain)
                if isExists:
                    try:
                        collection.insert({
                            "_id": str(platId) + "_" + part + "_" + userurl,
                            "url": userurl,
                            "platId": platId,
                            "part": part,
                            "lastUpdate": int(time.time())
                        })
                        logging.warn("存在mms中part:{},name:{},url:{}".format(part, name, userurl))
                    except Exception as e:
                        logging.error(e)
                    # 代表存在接口中
                    return None
            # 订阅者数量
            subscriberCount = self.dealSubscriberCount(responseText)
            if subscriberCount < 5000:
                logging.error("订阅者数量不超过5000,userUrl:{},订阅人数:{}".format(url.split("?")[0], subscriberCount))
                try:
                    invisibleUrl.insert({
                        "_id": str(platId) + "_" + userurl,
                        "url": userurl,
                        "platId": platId,
                        "insertTime": int(time.time()),
                        "subscriberCount": subscriberCount
                    })
                except Exception as e:
                    logging.error(traceback.format_exc())
                return None

                # 观看人数
            viewCount = self.dealViewCont(responseText)

            # 评论:内容
            description, descriptionLong = self.dealDescription(responseText)
            if part == "GB":
                blackListall = blackList
            else:
                blackListall = clothesblackList
            # 翻译成中文
            if not description.strip():
                descriptionChinese = ""
            else:
                descriptionChinese = mainTranslate(description)
            # descriptionChinese = youdao(description)

            blackWord = ""
            blackWordCount = 0
            for word in blackListall:
                if word in description or word in descriptionChinese:
                    blackWord += word + ""
                    blackWordCount += 1
            blackWord = blackWord.strip()

            # emailAddress = re.findall("(\w+@\S+.\w+)", descriptionLong)
            pattern = re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}\b')
            try:
                emailAddress = re.search(pattern, descriptionLong).group()
            except Exception as e:
                emailAddress = ""

            if emailAddress:
                if part == "clothes":
                    cmmsDomain = "http://cmms.gloapi.com/"
                    isExists = checkMail(emailAddress, cmmsDomain)
                    if isExists:
                        logging.warn("邮箱存在cmms中,{}".format(emailAddress))
                        # 代表存在数据库中
                        return None

            # 国家
            country = self.dealCountry(responseText)

            # 标题title
            upTitle = self.dealTitle(responseText)

            # 链接
            Facebook, Youtube, Instagram = self.dealLinks(responseText)

            # 商务邮箱
            businessEmail = self.dealMail(responseText)

            # 相关频道
            relateChannel = self.relateChannel(responseText)

            UserItem = {
                "subscriberCount": subscriberCount,
                "description": descriptionChinese,
                "descriptionUn": descriptionLong,
                "country": country,
                "viewCount": viewCount,
                "upTitle": upTitle,
                "Facebook": Facebook,
                "Youtube": Youtube,
                "Instagram": Instagram,
                "emailAddress": emailAddress,
                "isMail": businessEmail,
                "relateChannel": relateChannel.strip(),
                "url": userurl,
                "blackWord": blackWord,
                "blackWordCount": blackWordCount
            }
        except Exception as e:
            logging.error(traceback.format_exc())
            UserItem = {}
        return UserItem

    def relateChannel(self, response):
        link = ""
        links = jsonpath.jsonpath(response, "$..verticalChannelSectionRenderer..title..webCommandMetadata.url")
        # print(links)
        if links:
            for i in links:
                link += "https://www.youtube.com" + i + "\n"
        return link

    def dealMail(self, response):
        businessEmail = jsonpath.jsonpath(response, "$..businessEmailLabel.simpleText")
        if businessEmail:
            isMail = True
        else:
            isMail = False
        return isMail

    def dealLinks(self, response):
        channelHeaderLinksRenderer = jsonpath.jsonpath(response, "$..channelHeaderLinksRenderer")
        Facebook = ""
        Youtube = ""
        Instagram = ""
        if channelHeaderLinksRenderer:
            channelHeaderLinksRenderer = channelHeaderLinksRenderer[0]
            primaryLinks = channelHeaderLinksRenderer.get("primaryLinks")
            if primaryLinks:
                for primaryLink in primaryLinks:
                    link = primaryLink["navigationEndpoint"]["commandMetadata"]["webCommandMetadata"]["url"]
                    if 'facebook.com' in link:
                        Facebook += link + "\n"
                    elif "twitter.com" in link:
                        Youtube += link + "\n"
                    elif "instagram.com" in link:
                        Instagram += link + "\n"
            secondaryLinks = channelHeaderLinksRenderer.get("secondaryLinks")
            if secondaryLinks:
                for secondaryLink in secondaryLinks:
                    try:
                        link = secondaryLink["navigationEndpoint"]["commandMetadata"]["webCommandMetadata"]["url"]
                    except Exception as e:
                        continue
                    if 'facebook.com' in link:
                        Facebook += link + "\n"
                    elif "twitter.com" in link:
                        Youtube += link + "\n"
                    elif "instagram.com" in link:
                        Instagram += link + "\n"
        return Facebook.strip(), Youtube.strip(), Instagram.strip()

    def dealTitle(self, response):
        title = ""
        try:
            title = jsonpath.jsonpath(response, "$..channelMetadataRenderer.title")[0]
        except Exception as e:
            logging.error(e)
        return title

    def dealViewCont(self, response):
        viewCount = 0
        try:
            viewCountText = jsonpath.jsonpath(response, "$..viewCountText.runs")[0][0]["text"]
            viewCount = int(viewCountText.replace(",", ""))
        except Exception as e:
            logging.error(e)
        return viewCount

    def dealCountry(self, response):
        country = ""
        try:
            country = jsonpath.jsonpath(response, "$..country.simpleText")
            if not country:
                country = ""
            else:
                country = country[0]
                # country = country[0]
        except Exception as e:
            logging.error(e)
        return country

    def dealDescription(self, response):
        try:
            description = jsonpath.jsonpath(response, "$..microformatDataRenderer.description")[0]
            descriptionLong = response["response"]["metadata"]["channelMetadataRenderer"]["description"]
        except Exception as e:
            logging.exception(e)
            description = ""
            descriptionLong = ""

        return description, descriptionLong

    def dealSubscriberCount(self, response):
        try:
            subscriberCountText = response["response"]["header"]["c4TabbedHeaderRenderer"]["subscriberCountText"][
                "simpleText"]
        except Exception as e:
            subscriberCountText = ""

        if subscriberCountText:
            subscriberCount = int(subscriberCountText.split(" ")[0].replace(",", ""))
        else:
            subscriberCount = 0

        return subscriberCount


def mainR(name):
    youtube = YouTuBe()
    # 查看大于等于5,非深挖的数据
    while True:
        logging.info(name)
        resultList = list(
            collection.find(
                {"name": name, "isDeep": False, "VideoTitleCount": {"$gte": 0}, "relateChannel": {"$ne": ""}}).limit(
                100))
        if not resultList:
            logging.warn("没有合适的数据,[{}]".format(name))
            # 把所有的弄成False
            # try:
            #     collection.update({"name": name, "relateChannel": {"$ne": ""}}, {"$set": {"isDeep": False}}, multi=True)
            # except Exception as e:
            #     pass
            time.sleep(60)
            continue
        for result in resultList:
            _id = result["_id"]
            relateChannel = result["relateChannel"]
            keyWord = result["keyWord"]
            name = result["name"]
            part = result["part"]
            station = result["station"]
            youtube.deepExcavate(_id, relateChannel, keyWord, name, part, station)


class whiteReview(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        # find({csvLoad:false,VideoTitleCount:{$lt:4}})
        resultList = mongoQuery(collection, {"part": "clothes", "whiteWord": {"$exists": 1}})
        # resultList = list(collection.find({"part": "clothes"}).limit(20))
        if not resultList:
            logging.error("没有数据")
            time.sleep(24 * 3600 * 7)
        for result in resultList:
            try:
                url = result["url"]
                beforeWhiteWord = result["whiteWord"]
                videoTittle = result["videoTittle"]
                videoTittleChinese = result["description"]
                part = result["part"]
                VideoTitleCount = 0
                whiteWord = ""
                if part == "GB":
                    whiteListall = whiteList
                else:
                    whiteListall = clotheswhiteList
                    station = result.get("station")
                    if station == "Zaful":
                        whiteListall = zafulWhiltList
                for word in whiteListall:
                    if word.lower() in videoTittle.lower() or word.lower() in videoTittleChinese.lower():
                        VideoTitleCount += 1
                        # logging.info(word)
                        word_new = word + " "
                        whiteWord += word_new
                try:
                    collection.update_one({"url": url, "part": part},
                                          {"$set": {"whiteWord": whiteWord.strip(),
                                                    "VideoTitleCount": VideoTitleCount}})
                    logging.info("url:{},以前的白名单:{},现在的白名单:{}".format(url, beforeWhiteWord, whiteWord))
                except Exception as e:
                    pass
            except Exception as e:
                logging.error(e)


if __name__ == '__main__':
    # whiteObj = whiteReview()
    # whiteObj.start()
    nameList = collection.distinct("name", {"name": {"$exists": 1}})
    names = []
    threads = []
    for name in nameList:
        if not name:
            continue
        th = threading.Thread(target=mainR, args=(name,))
        th.setDaemon(True)
        th.start()
        names.append(name)
        threads.append(th)
    while True:
        for th, name in zip(threads, names):
            if not th.is_alive():
                logging.warn("线程停止{}".format(th.name))
                threads.remove(th)
                names.remove(name)
                th = threading.Thread(target=mainR, args=(name,))
                th.setDaemon(True)
                th.start()
                names.append(name)
                threads.append(th)
        time.sleep(10)
