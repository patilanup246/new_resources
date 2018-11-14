import os
import sys

sys.path.append("./..")
from logs.loggerDefine import loggerDefine

youtubeDir = "./../logs/youtube/"
if not os.path.exists(youtubeDir):
    os.makedirs(youtubeDir)
loggerFile = youtubeDir + "youtubedeep.log"
logging = loggerDefine(loggerFile)
import traceback
import re
from tools.translate.translate_google import mainTranslate
from db.mongodb import connectMongo
from tools.translate.translateYoudao import *
from fake_useragent import UserAgent

debug_flag = True if sys.argv[1] == "debug" else False
# mongodb
mongodb = connectMongo(debug_flag)

# 用户信息
collection = mongodb["resources"]

# 关键字信息
keyWordCollection = mongodb["keyWords"]

# 黑名单url
blackUrlCollection = mongodb["blackUrl"]

# 黑白名单
blackWhiteCollection = mongodb["blackWhite"]

# 黑名单列表
blackList = list(blackWhiteCollection.distinct("word", {"isBlack": True}))
# 白名单列表
whiteList = list(blackWhiteCollection.distinct("word", {"isWhite": True}))

# 已存在的url

whiteCount = 3


class YouTuBe(object):
    def __init__(self):
        self.nextPageUrl = ""
        self.userUrlList = []
        self.formData = {}
        self.thList = []
        self.pageNum = 9
        self.videoNum = 8
        self.VideoTitleCount = 1

    def sendRequestExcavate(self, url, keyWord, name, isDeep=True, round=0):
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
                    response = requests.get(url=userUrl, headers=headers, timeout=5)
                    response.encoding = "utf-8"
                    if response.status_code == 200:
                        userItem = self.parsePageUser(response.text, userUrl)
                        break
                except Exception as e:
                    if repr(e).find("timed out") > 0:
                        logging.error("请求超时,url:{}".format(userUrl))
                    else:
                        logging.error(e)

            if userItem:
                videoUrl = url + "/videos?pbj=1"
                videoItem = {}
                logging.info("获取用户videos页面,url:{}".format(url + '/videos'))
                for i in range(3):
                    try:
                        response = requests.get(url=videoUrl, headers=headers, timeout=5)
                        response.encoding = "utf-8"
                        if response.status_code == 200:
                            videoItem = self.parsePageVideo(response.text, videoUrl)
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
                    item["_id"] = "1_" + userItem["upTitle"]
                    item["url"] = url
                    item["keyWord"] = keyWord
                    item["platId"] = 1
                    item["csvLoad"] = False
                    item["isDeep"] = isDeep
                    item["isRecaptcha"] = False
                    item["lastUpdate"] = int(time.time())
                    item["name"] = name
                    # 对VideoTitleCount >=3 的进行深挖掘
                    if videoItem["VideoTitleCount"] >= whiteCount:
                        try:
                            collection.insert(item)
                        except Exception as e:
                            logging.error(e)
                        relateChannel = item["relateChannel"].strip().split("\n")
        except Exception as e:
            logging.exception(e)

        return relateChannel, keyWord

    def deepExcavate(self, _id, relateChannel, keyWord, name):
        if not relateChannel:
            return
        relateChannelurlList = relateChannel.split("\n")
        urlList = relateChannelurlList
        if not urlList:
            return
        ExistUrl = []
        round = 0
        num = 0
        while True:
            if not urlList:
                continue
            num += 1
            for url in urlList:
                if url in relateChannelurlList:
                    continue
                url = url.strip()
                if not url:
                    continue
                if url in self.userUrlList:
                    continue
                if url in self.thList:
                    continue
                if url in ExistUrl:
                    continue

                # 判断是否在黑名单中
                result = blackUrlCollection.find_one({"url": url})
                if result:
                    logging.warn("存在黑名单中,name:{},url:{}".format(name, url))
                    continue

                if name == "服装事业部":
                    # 判断是否在数据库中
                    result = collection.find_one({"part": "clothes", "url": url})
                    if result:
                        logging.warn("存在库中,name:{},url:{}".format(name, url))
                        continue

                else:
                    # 判断是否在数据库中
                    result = collection.find_one({"part": "GB", "url": url})
                    if result:
                        logging.warn("存在库中,name:{},url:{}".format(name, url))
                        continue
                self.userUrlList.append(url)
                ExistUrl.append(url)

                try:
                    channelList, keyWord = self.sendRequestExcavate(url, keyWord, name, True, round)
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
            logging.info("第{}圈,keyWord:{}".format(round, keyWord))

        try:
            collection.update_one({"_id": _id}, {"$set": {"isDeep": True}})
        except Exception as e:
            logging.error(e)

    # 视频信息
    def parsePageVideo(self, response, videoUrl):
        response = json.loads(response)
        titleList = jsonpath.jsonpath(response, "$..gridRenderer.items..title..simpleText")
        # 取8个
        titleList = titleList[:self.videoNum]
        lastUpdateTimeList = jsonpath.jsonpath(response, "$..gridRenderer.items..publishedTimeText.simpleText")
        lastUpdateTimeList = lastUpdateTimeList[:self.videoNum]
        if "年" in lastUpdateTimeList[0]:
            return None
        if "月" in lastUpdateTimeList[0]:
            if int(re.search(r"(\d+)", lastUpdateTimeList[0]).group(1)) > 6:
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
        if int(totalViewCount / len(titleList)) < 2000:
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
        for word in whiteList:
            if word.lower() in videoTittle.lower() or word.lower() in videoTittleChinese.lower():
                VideoTitleCount += 1
                # logging.info(word)
                word_new = word + " "
                whiteWord += word_new


        logging.error("匹配度大于等于{}分,videoUrl:{},匹配单词:{}".format(self.VideoTitleCount, videoUrl.split("?")[0],
                                                              whiteWord.strip()))
        try:
            titleFirst = videoTittleChinese.split("\n")[0]
        except Exception as e:
            titleFirst = ""

        try:
            viewCountFirst = int(viewCountTextList[0].replace("次观看", "").replace("人正在观看", "").replace(",", "").strip())
        except Exception as e:
            viewCountFirst = 0

        item = {
            "videoTittle": videoTittleChinese,
            "viewCountAvg": int(totalViewCount / len(titleList)),
            "titleLastUpdateTime": lastUpdateTimeList[0],
            "whiteWord": whiteWord.strip(),
            "VideoTitleCount": VideoTitleCount,
            "titleFirst": titleFirst,
            "viewCountFirst": viewCountFirst
        }
        return item

    def parsePageUser(self, response, url):
        try:
            # print(response)
            responseBody = json.loads(response)
            try:
                responseText = responseBody[1]
            except Exception as e:
                return None
            # 订阅者数量
            subscriberCount = self.dealSubscriberCount(responseText)
            if subscriberCount < 5000:
                logging.error("订阅者数量不超过5000,userUrl:{},订阅人数:{}".format(url.split("?")[0], subscriberCount))
                return None

                # 观看人数
            viewCount = self.dealViewCont(responseText)
            if viewCount < 5000:
                logging.error("观看人数不超过5000,userUrl:{},观看人数:{}".format(url.split("?")[0], viewCount))
                return None

            # 评论:内容
            description, descriptionLong = self.dealDescription(responseText)
            isBlack = False
            blackWord = ""
            for word in blackList:
                if word in description:
                    blackWord = word
                    isBlack = True
                    break
            if isBlack:
                try:
                    blackUrlCollection.insert({
                        "_id": url.split("?")[0].replace("/about", ""),
                        "url": url.split("?")[0].replace("/about", ""),
                        "blackword": blackWord
                    })
                except Exception as e:
                    pass
                logging.error("处于非中文黑名单中,名词:{},userUrl:{}".format(blackWord, url.split("?")[0]))
                return None
            # 翻译成中文
            if not description.strip():
                descriptionChinese = ""
            else:
                descriptionChinese = mainTranslate(description)
            # descriptionChinese = youdao(description)

            isBlack = False
            blackWord = ""
            for word in blackList:
                if word in descriptionChinese:
                    blackWord = word
                    isBlack = True
                    break
            if isBlack:
                try:
                    blackUrlCollection.insert({
                        "_id": url.split("?")[0].replace("/about", ""),
                        "url": url.split("?")[0].replace("/about", ""),
                        "blackword": blackWord
                    })
                except Exception as e:
                    pass
                logging.error("处于中文黑名单中,名词:{},userUrl:{}".format(blackWord, url.split("?")[0]))
                return None

            # logging.info(description)

            emailAddress = re.findall("(\w+@\S+.\w+)", descriptionLong)
            if not emailAddress:
                # print(description)
                emailAddress = ""
            else:
                emailAddress = emailAddress[0]
                if emailAddress.endswith("."):
                    emailAddress = emailAddress.strip()

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
                "country": country,
                "viewCount": viewCount,
                "upTitle": upTitle,
                "Facebook": Facebook,
                "Youtube": Youtube,
                "Instagram": Instagram,
                "emailAddress": emailAddress,
                "isMail": businessEmail,
                "relateChannel": relateChannel.strip(),
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


def mainR():
    youtube = YouTuBe()
    # 查看大于等于5,非深挖的数据
    while True:
        resultList = list(
            collection.find(
                {"isDeep": False, "VideoTitleCount": {"$gte": whiteCount}, "relateChannel": {"$ne": ""}}).limit(100))
        if not resultList:
            logging.warn("没有合适的数据")
            time.sleep(60)
            continue
        for result in resultList:
            _id = result["_id"]
            relateChannel = result["relateChannel"]
            keyWord = result["keyWord"]
            name = result["name"]
            youtube.deepExcavate(_id, relateChannel, keyWord, name)


if __name__ == '__main__':
    logging.info("runing")
    mainR()
