import multiprocessing
import os
import sys

import pymongo

sys.path.append("./..")
from tools.getip import getIp
from logs.loggerDefine import loggerDefine

youtubeDir = "./../logs/youtube/"
if not os.path.exists(youtubeDir):
    os.makedirs(youtubeDir)
loggerFile = youtubeDir + "youtube.log"
logging = loggerDefine(loggerFile)
import traceback
import re
from tools.checkurl import checkUrl
from tools.translate.translate_google import mainTranslate

from db.mongodb import connectMongo

import threading
import multiprocessing
from tools.translate.translateYoudao import *
from fake_useragent import UserAgent

mmsDomain = "http://mms.gloapi.com/"
cmmsDomain = "http://cmms.gloapi.com/"

debug_flag = True if sys.argv[1] == "debug" else False
# mongodb
mongodb = connectMongo(debug_flag)

# 用户信息
userInfoCollection = mongodb["userInfo"]

# 关键字信息
keyWordCollection = mongodb["keyWords"]

# 黑白名单
blackWhiteCollection = mongodb["blackWhite"]

blackUrlCollection = mongodb["blackUrl"]

# 黑名单列表
blackList = list(blackWhiteCollection.distinct("word", {"isBlack": True}))
# 白名单列表
whiteList = list(blackWhiteCollection.distinct("word", {"isWhite": True}))

# 已存在的url
formerUrlCollection = mongodb["formerUrl"]


class YouTuBe(object):
    def __init__(self):
        self.nextPageUrl = ""
        self.userUrlList = []
        self.formData = {}
        self.thList = []
        self.pageNum = 20
        self.videoNum = 8
        self.VideoTitleCount = 1
        # self.IPlist = getip()

    # 获取首页信息
    def sendRequest(self, url, keyWord):
        logging.info("request first page,keyWord:{}".format(keyWord))
        responseBody = ""
        for i in range(3):
            try:
                headers = {
                    "user-agent": UserAgent().random,
                    # "referer": "https://www.youtube.com/results?search_query=" + parse.quote(keyWord),
                    # "x-client-data": "CIu2yQEIpLbJAQjBtskBCKmdygEIqKPKARj5pcoB",
                    # "x-spf-previous": "https://www.youtube.com/results?search_query=" + parse.quote(keyWord),
                    # "x-spf-referer": "https://www.youtube.com/results?search_query=" + parse.quote(keyWord),
                    "x-youtube-client-name": "1",
                    "x-youtube-client-version": "2.20181025",
                    # "x-youtube-page-cl": "218622685",
                    # "x-youtube-page-label": "youtube.ytfe.desktop_20181024_8_RC0",
                    # "x-youtube-variants-checksum": "80cb024c85d222102f525ddbcc2d0915",
                    "accept-language": "zh-CN,zh;q=0.9"
                }
                response = requests.get(url=url, timeout=5, headers=headers, proxies=getIp(), verify=False)
                response.encoding = "utf-8"
                if response.status_code == 200:
                    responseBody = response.text
                    break
                else:
                    logging.warn("状态码:{},url:{}".format(response.status_code, url))
            except Exception as e:
                if repr(e).find("timed out") > 0:
                    logging.error("请求超时,url:{}".format(url))
                else:
                    logging.error(e)
        if not responseBody:
            logging.warn("requests url:{} fail for 3 times".format(url))

        return responseBody

    # 获取下一页信息
    def sendRequestPost(self, keyWord, name):
        for i in range(3):
            try:
                headers = {
                    "accept-language": "zh-CN,zh;q=0.9",
                    # "origin": "https://www.youtube.com",
                    # "referer": "https://www.youtube.com/results?search_query=" + parse.quote(keyWord),
                    # "user-agent": UserAgent().random,
                    # "x-client-data": "CIu2yQEIpLbJAQjBtskBCKmdygEIqKPKARj5pcoB",
                    # "x-spf-previous": "https://www.youtube.com/results?search_query=" + parse.quote(keyWord),
                    # "x-spf-referer": "https://www.youtube.com/results?search_query=" + parse.quote(keyWord),
                    "x-youtube-client-name": "1",
                    "x-youtube-client-version": "2.20181025",
                    # "x-youtube-page-cl": "218622685",
                    # "x-youtube-page-label": "youtube.ytfe.desktop_20181024_8_RC0",
                    # "x-youtube-utc-offset": "480",
                    # "x-youtube-variants-checksum": "80cb024c85d222102f525ddbcc2d0915"
                }
                # print(headers)
                response = requests.post(url=self.nextPageUrl, timeout=5, headers=headers, data=self.formData,
                                         proxies=getIp(), verify=False)
                response.encoding = "utf-8"
                if response.status_code == 200:
                    self.parseNextPage(response.text, keyWord, name)
                    break
                else:
                    logging.warn("nextPageUrl:{} 请求失败.statusCode:{}".format(self.nextPageUrl, response.status_code))
            except Exception as e:
                if repr(e).find("timed out") > 0:
                    logging.error("请求超时,url:{}".format(self.nextPageUrl))
                else:
                    logging.error(e)

    # 每个用于一个线程
    def tdSendRequestPost(self, url, keyWord, isDeep=False, round=0):
        thd = threading.Thread(target=self.sendRequestUser, args=(url, keyWord))
        thd.start()

    # 获取用户信息
    def sendRequestUser(self, url, keyWord, name, isDeep=False, round=0):
        try:
            userUrl = url + "/about?pbj=1"
            headers = {
                "accept-language": "zh-CN,zh;q=0.9",
                # "referer": url,
                "user-agent": UserAgent().random,
                # "x-client-data": "CIu2yQEIpLbJAQjBtskBCKmdygEIqKPKARj5pcoB",
                # "x-spf-previous": url,
                # "x-spf-referer": url,
                "x-youtube-client-name": "1",
                "x-youtube-client-version": "2.20181025",
                # "x-youtube-page-cl": "218622685",
                # "x-youtube-page-label": "youtube.ytfe.desktop_20181024_8_RC0",
                # "x-youtube-sts": "17829",
                # "x-youtube-utc-offset": "480",
                # "x-youtube-variants-checksum": "80cb024c85d222102f525ddbcc2d0915"
            }
            userItem = {}
            logging.info("获取用户about页面,url:{}".format(url + "/about"))
            for i in range(3):
                try:
                    response = requests.get(url=userUrl, headers=headers, timeout=5, proxies=getIp(), verify=False)
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
                        response = requests.get(url=videoUrl, headers=headers, timeout=5, proxies=getIp(),
                                                verify=False)
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
                    try:
                        formerUrlCollection.insert({
                            "_id": "1_" + item["url"],
                            "url": item["url"],
                            "platId": 1,
                            "lastUpdate": int(time.time())
                        })
                        userInfoCollection.insert(item)
                    except Exception as e:
                        logging.error(e)
        except Exception as e:
            logging.exception(e)

    def sendRequestExcavate(self, url, keyWord, isDeep=True, round=0):
        relateChannel = None
        try:
            userUrl = url + "/about?pbj=1"
            headers = {
                "accept-language": "zh-CN,zh;q=0.9",
                # "referer": url,
                "user-agent": UserAgent().random,
                # "x-client-data": "CIu2yQEIpLbJAQjBtskBCKmdygEIqKPKARj5pcoB",
                # "x-spf-previous": url,
                # "x-spf-referer": url,
                "x-youtube-client-name": "1",
                "x-youtube-client-version": "2.20181025",
                # "x-youtube-page-cl": "218622685",
                # "x-youtube-page-label": "youtube.ytfe.desktop_20181024_8_RC0",
                # "x-youtube-sts": "17829",
                # "x-youtube-utc-offset": "480",
                # "x-youtube-variants-checksum": "80cb024c85d222102f525ddbcc2d0915"
            }
            userItem = {}
            logging.info("获取用户about页面,url:{}".format(url + "/about"))
            for i in range(3):
                try:
                    response = requests.get(url=userUrl, headers=headers, timeout=5, proxies=getIp(), verify=False)
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
                        response = requests.get(url=videoUrl, headers=headers, timeout=5, proxies=getIp(),
                                                verify=False)
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
                    try:
                        formerUrlCollection.insert({
                            "_id": "1_" + item["url"],
                            "url": item["url"],
                            "platId": 1,
                            "lastUpdate": int(time.time())
                        })
                        userInfoCollection.insert(item)
                    except Exception as e:
                        logging.error(e)
                    # 对VideoTitleCount >=3 的进行深挖掘
                    if videoItem["VideoTitleCount"] >= 3:
                        relateChannel = item["relateChannel"].strip().split("\n")
        except Exception as e:
            logging.exception(e)

        return relateChannel, keyWord

    def deepExcavate(self, relateChannel, keyWord, round):
        urlList = relateChannel.split("\n")
        ExistUrl = []
        round = 0
        num = 0
        while True:
            if round >= 7 + len(relateChannel.split("\n")):
                break
            if num > 1000:
                break
            logging.info("第{}圈,keyWord:{}".format(round, keyWord))
            for url in urlList:
                url = url.strip()
                if not url:
                    continue
                if url in self.userUrlList:
                    continue
                if url in self.thList:
                    continue
                if url in ExistUrl:
                    continue

                result = formerUrlCollection.find_one({"url": url})
                if result:
                    # 代表存在
                    logging.warn("存在数据库中:url:{}".format(url))
                    continue

                # 判断是否存在接口中
                isExists = checkUrl(url)
                if isExists:
                    try:
                        formerUrlCollection.insert({
                            "_id": "1_" + url,
                            "url": url,
                            "platId": 1,
                            "lastUpdate": int(time.time())
                        })
                    except Exception as e:
                        logging.error(e)
                    # 代表存在接口中
                    continue
                self.userUrlList.append(url)
                self.thList.append(url)
                ExistUrl.append(url)
                round += 1
                if round >= 7 + len(relateChannel.split("\n")):
                    break
                try:
                    channelList, keyWord = self.sendRequestExcavate(url, keyWord, True, round)
                except Exception as e:
                    logging.error(traceback.format_exc())
                    continue
                if channelList:
                    num += 1
                    for urlChanel in channelList:
                        if urlChanel not in ExistUrl:
                            urlList.append(urlChanel)

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
        videoTittleChinese = mainTranslate(videoTittle)
        VideoTitleCount = 0
        whiteWord = ""
        for word in whiteList:
            if word.lower() in videoTittle.lower() or word.lower() in videoTittleChinese.lower():
                VideoTitleCount += 1
                # logging.info(word)
                word_new = word + " "
                whiteWord += word_new

        if VideoTitleCount < self.VideoTitleCount:
            logging.error("匹配度不超过{}分,videoUrl:{},目前匹配度:{},匹配单词:{}".format(self.VideoTitleCount, videoUrl.split("?")[0],
                                                                          VideoTitleCount, whiteWord.strip()))
            return None
        else:
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

    # 首页信息解析
    def parsePage(self, response, keyWord, name):
        global debug_flag
        try:
            logging.info("获取下一页链接,keyWord:{}".format(keyWord))
            response = json.loads(response)
            itemSectionRenderer = jsonpath.jsonpath(response, "$..itemSectionRenderer")[0]
            contents = itemSectionRenderer["contents"]
            # xsrf_token
            token = jsonpath.jsonpath(response, "$..xsrf_token")[0]
            logging.info("获取下一页链接token成功,keyWord:{},token:{}".format(keyWord, token))
            # print(token)

            # continuation
            try:
                continuations = itemSectionRenderer["continuations"]
                continuation = continuations[0]["nextContinuationData"]["continuation"]
            except Exception as e:
                return

            # nextPageUrl
            nextPageUrl = jsonpath.jsonpath(response, "$..endpoint.urlEndpoint.url")[0]
            # nextPageUrl = response["endpoint"]["urlEndpoint"]["url"]
            self.nextPageUrl = "https://www.youtube.com" + nextPageUrl + "&pbj=1" + "&ctoken=" + continuation + "&itct=" + continuation
            logging.info("获取下一页链接成功,keyWord:{}".format(keyWord))
            self.formData = {
                "session_token": token
            }

            for content in contents:
                videoRenderer = content.get("videoRenderer")
                if not videoRenderer:
                    videoRenderer = content.get("channelRenderer")
                    if not videoRenderer:
                        continue

                userUrl = "https://www.youtube.com" + \
                          videoRenderer["shortBylineText"]["runs"][0]["navigationEndpoint"]["commandMetadata"][
                              "webCommandMetadata"]["url"]

                if userUrl in self.userUrlList:
                    logging.error("url:{}存在列表中".format(userUrl))
                    continue

                if userUrl in self.thList:
                    logging.error("url:{}存在线程列表中".format(userUrl))
                    continue

                # 判断是否在库中
                result = formerUrlCollection.find_one({"url": userUrl})
                if result:
                    # 代表存在
                    logging.warn("存在数据库中:url:{}".format(userUrl))
                    continue

                # 判断是否在黑名单中
                result = blackUrlCollection.find_one({"url": userUrl})
                if result:
                    logging.warn("存在黑名单中:url:{}".format(userUrl))
                    continue

                # 判断是否存在接口中
                isExists = checkUrl(userUrl)
                if isExists:
                    try:
                        formerUrlCollection.insert({
                            "_id": "1_" + userUrl,
                            "url": userUrl,
                            "platId": 1,
                            "lastUpdate": int(time.time())
                        })
                    except Exception as e:
                        logging.error(e)
                    # 代表存在接口中
                    continue

                self.thList.append(userUrl)
                self.userUrlList.append(userUrl)
                if debug_flag:
                    self.sendRequestUser(userUrl, keyWord, name)
                else:
                    self.tdSendRequestPost(userUrl, keyWord, name)
            self.GetNextWhile(keyWord, name)
        except Exception as e:
            logging.error(traceback.format_exc())
            self.changeWordStatus(keyWord)

    # 循环获取下一页信息
    def GetNextWhile(self, keyWord, name):
        i = 0
        while i < self.pageNum:
            # logging.info("time sleep 5s")
            # time.sleep(5)
            self.sendRequestPost(keyWord, name)
            i += 1

        self.changeWordStatus(keyWord)

    def changeWordStatus(self, keyWord):
        try:
            keyWordCollection.update_one({"_id": keyWord}, {"$set": {"getData": True}})
            logging.info("关键字:{} 状态改为已经抓取状态".format(keyWord))
        except Exception as e:
            logging.error(e)

    # 解析下一页信息
    def parseNextPage(self, response, keyWord, name):
        global debug_flag
        try:
            response = json.loads(response)
            if not response:
                return
            try:
                response = response[1]
            except Exception as e:
                return
            contents = \
                response["response"]["continuationContents"]["itemSectionContinuation"]["contents"]
            # xsrf_token
            token = response["xsrf_token"]
            logging.info("获取下一页链接token成功,keyWord:{},token:{}".format(keyWord, token))
            # logging.info(token)

            # continuation
            try:
                continuations = \
                    response["response"]["continuationContents"]["itemSectionContinuation"]["continuations"]
                continuation = continuations[0]["nextContinuationData"]["continuation"]
            except Exception as e:
                return

            # nextPageUrl
            # logging.info(response["endpoint"]["urlEndpoint"])
            nextPageUrl = response["endpoint"]["urlEndpoint"]["url"].split("&")[0]

            self.nextPageUrl = "https://www.youtube.com" + nextPageUrl + "&pbj=1" + "&ctoken=" + continuation + "&itct=" + continuation
            logging.info("获取下一页链接成功,keyWord:{}".format(keyWord))
            self.formData = {
                "session_token": token
            }

            for content in contents:
                videoRenderer = content.get("videoRenderer")
                if not videoRenderer:
                    continue
                userUrl = "https://www.youtube.com" + \
                          videoRenderer["shortBylineText"]["runs"][0]["navigationEndpoint"]["commandMetadata"][
                              "webCommandMetadata"]["url"]

                if userUrl in self.userUrlList:
                    logging.error("url:{}存在列表中".format(userUrl))
                    continue
                if userUrl in self.thList:
                    logging.error("url:{}存在线程列表中".format(userUrl))
                    continue

                result = formerUrlCollection.find_one({"url": userUrl})
                if result:
                    # 代表存在
                    logging.warn("存在数据库中:url:{}".format(userUrl))
                    continue

                # 判断是否在黑名单中
                result = blackUrlCollection.find_one({"url": userUrl})
                if result:
                    logging.warn("存在黑名单中:url:{}".format(userUrl))
                    continue

                # 判断是否存在接口中
                isExists = checkUrl(userUrl)
                if isExists:
                    # 代表存在接口中
                    try:
                        formerUrlCollection.insert({
                            "_id": "1_" + userUrl,
                            "url": userUrl,
                            "platId": 1,
                            "lastUpdate": int(time.time())
                        })
                    except Exception as e:
                        logging.error(e)
                    continue
                self.thList.append(userUrl)
                self.userUrlList.append(userUrl)
                if debug_flag:
                    self.sendRequestUser(userUrl, keyWord, name)
                else:
                    self.tdSendRequestPost(userUrl, keyWord)
        except Exception as e:
            logging.error(traceback.format_exc())


def deal(result, youtube, name):
    keyWord = result["keyWord"]
    try:
        logging.info("beggin to deal with keyWord:{}".format(keyWord))
        url = "https://www.youtube.com/results?search_query=" + parse.quote(keyWord) + "&pbj=1"
        responseBody = youtube.sendRequest(url, keyWord)
        if responseBody:
            youtube.parsePage(responseBody, keyWord, name)
    except Exception as e:
        logging.error(e)


def dealWord(name):
    youtube = YouTuBe()
    while True:
        resultList = list(
            keyWordCollection.find({"resPeople": name, "getData": False}).sort([("hots", pymongo.DESCENDING)]).limit(
                2))
        if not resultList:
            time.sleep(60)
        thList = []
        for result in resultList:
            th = threading.Thread(target=deal, args=(result, youtube, name))
            th.start()
            thList.append(th)
        for th in thList:
            th.join()


def mainR():
    peopleList = list(keyWordCollection.distinct("resPeople"))
    for name in peopleList:
        pro = multiprocessing.Process(target=dealWord, args=(name,))
        pro.start()


if __name__ == '__main__':
    logging.info("runing")
    mainR()
