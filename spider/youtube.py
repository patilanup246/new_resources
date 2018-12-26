import os
import sys
from multiprocessing.pool import ThreadPool

import pymongo

sys.path.append("./..")
from tools.getip import getIp
from logs.loggerDefine import loggerDefine
from tools.youtubetool.youtubeMMS import readMongo as mmsreadMongo
from tools.youtubetool.backcountry import readMongo as backCountry
from multiprocessing.pool import ThreadPool
import threading

youtubeDir = "./../logs/youtube/"
if not os.path.exists(youtubeDir):
    os.makedirs(youtubeDir)
loggerFile = youtubeDir + "youtube.log"
logging = loggerDefine(loggerFile)
import traceback
import re
from tools.checkurl import checkUrl, checkMail
from tools.translate.translate_google import mainTranslate
import sys

sys.setrecursionlimit(1000000)  # 例如这里设置为一百万
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

# 关键字信息
keyWordCollection = mongodb["keyWords"]
formeryoutubecollection = mongodb["formeryoutube"]
youtubeUrl = mongodb["youtubeUrl"]
platId = 1

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

collection = mongodb["resources"]

invisibleUrl = mongodb["invisibleUrl"]

urlsGB = []
urlsCL = []


class YouTuBe(object):
    def __init__(self):
        self.pageNum = 10
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
                    "x-youtube-client-name": "1",
                    "x-youtube-client-version": "2.20181204",
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
                    logging.error("请求超时{}次,url:{}".format(i + 1, url))
                else:
                    logging.error(e)
        if not responseBody:
            logging.warn("requests url:{} fail for 3 times".format(url))

        return responseBody

    # 获取下一页信息
    def sendRequestPost(self, keyWord, name, part, station, nextPageUrl, formData, language):
        nextPageUrlnew, formDatanew = "", ""
        for i in range(3):
            try:
                headers = {
                    "accept-language": "zh-CN,zh;q=0.9",
                    "x-youtube-client-name": "1",
                    "x-youtube-client-version": "2.20181204",
                }
                response = requests.post(url=nextPageUrl, timeout=5, headers=headers, data=formData,
                                         proxies=getIp(), verify=False)
                response.encoding = "utf-8"
                if response.status_code == 200:
                    nextPageUrlnew, formDatanew = self.parseNextPage(response.text, keyWord, name, part, station,
                                                                     language)
                    break
                else:
                    logging.warn("nextPageUrl:{} 请求失败.statusCode:{}".format(nextPageUrl, response.status_code))
            except Exception as e:
                if repr(e).find("timed out") > 0:
                    logging.error("请求超时{}次,url:{}".format(i + 1, nextPageUrl))
                else:
                    logging.error(traceback.format_exc())
        return nextPageUrlnew, formDatanew

    # 获取用户信息
    def sendRequestUser(self, url, keyWord, name, part, station, language):
        url = "https://www.youtube.com/channel/UCd_PoZmhsco2fQmSsVXJz_g"
        try:
            userUrl = url + "/about?pbj=1"
            headers = {
                "accept-language": "zh-CN,zh;q=0.9",
                "user-agent": UserAgent().random,
                "x-youtube-client-name": "1",
                "x-youtube-client-version": "2.20181204",
            }
            userItem = {}
            logging.info("获取用户about页面part:{},url:{},name:{},language:{}".format(part, url + "/about", name, language))
            for i in range(3):
                try:
                    response = requests.get(url=userUrl, headers=headers, timeout=5, proxies=getIp(), verify=False)
                    response.encoding = "utf-8"
                    if response.status_code == 200:
                        userItem = self.parsePageUser(response.text, userUrl, part, name)
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
                logging.info(
                    "获取用户videos页面part:{},url:{},name:{},language:{}".format(part, url + '/videos', name, language))
                for i in range(3):
                    try:
                        response = requests.get(url=videoUrl, headers=headers, timeout=5, proxies=getIp(),
                                                verify=False)
                        response.encoding = "utf-8"
                        if response.status_code == 200:
                            videoItem = self.parsePageVideo(response.text, videoUrl, part, station, userItem["url"])
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
                    item["language"] = language
                    mailExists = False  # 不存在
                    emailAddress = item["emailAddress"]
                    if emailAddress:
                        if part == "clothes":
                            if item["VideoTitleCount"] >= 4:
                                cmmsDomain = "http://cmms.gloapi.com/"
                                isExists = checkMail(emailAddress, cmmsDomain)
                                if isExists:
                                    logging.warn("邮箱存在cmms中,{}".format(emailAddress))
                                    # 代表存在数据库中
                                    mailExists = True

                    item["_id"] = "1_" + part + "_" + item["url"]
                    item["part"] = part
                    if not emailAddress:
                        try:
                            collection.insert(dict(item))
                        except Exception as e:
                            logging.error(e)

                    relateChannel = item["relateChannel"]
                    if relateChannel:
                        for url in relateChannel.split("\n"):
                            try:
                                result = youtubeUrl.find_one({"url": url})
                                if result:
                                    continue
                                # # keyWord, name, part, station
                                youtubeUrl.insert({
                                    "_id": url,
                                    "url": url,
                                    "getData": False,
                                    "keyWord": item["keyWord"],
                                    "name": name,
                                    "part": part,
                                    "station": station,
                                    "language": language
                                })
                            except Exception as e:
                                pass
        except Exception as e:
            logging.exception(e)

    # 视频信息
    def parsePageVideo(self, response, videoUrl, part, station, userUrl):
        try:
            response = json.loads(response)
            titleList = jsonpath.jsonpath(response, "$..gridRenderer.items..title..simpleText")
            # 取8个
            titleList = titleList[:self.videoNum]
            lastUpdateTimeList = jsonpath.jsonpath(response, "$..gridRenderer.items..publishedTimeText.simpleText")
            lastUpdateTimeList = lastUpdateTimeList[:self.videoNum]

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
                    continue
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
        except Exception as e:
            item = {}
        return item

    def parsePageUser(self, response, url, part, name):
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
                urlList = [url]
            userurl = ""
            for i in urlList:
                if "www.youtube.com" not in i:
                    continue
                userurl = "https://" + i.split("://")[-1]
            if not userurl:
                return None

            # 判断是否在数据库中
            result = collection.find_one({"part": part, "url": userurl, "platId": platId})
            if result:
                logging.warn("存在库中part:{},name:{},url:{}".format(part, name, userurl))
                return None
            result = formeryoutubecollection.find_one({"part": part, "url": url, "platId": platId})
            if result:
                logging.warn("存在库中part:{},name:{},url:{}".format(part, name, url))
                return None

            if part == "clothes":
                # 判断是否在cmms中
                domain = "http://cmms.gloapi.com/"
                isExists = checkUrl(userurl, domain)
                if isExists:
                    # 代表存在接口中
                    return None
            elif part == "GB":
                # 判断是否在mms中
                domain = "http://mms.gloapi.com/"
                isExists = checkUrl(userurl, domain)
                if isExists:
                    # 代表存在接口中
                    return None

            # 订阅者数量
            subscriberCount = self.dealSubscriberCount(responseText)

            # 观看人数
            viewCount = self.dealViewCont(responseText)

            # 评论:内容
            description, descriptionLong = self.dealDescription(responseText)
            isBlack = False
            blackWord = ""
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
                "url": userurl,  # blackWord = ""  blackWordCount = 0
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

    # 首页信息解析
    def parsePage(self, response, keyWord, name, part, station, language):
        global urlsGB
        global urlsCL
        global debug_flag
        try:
            logging.info("获取下一页链接,keyWord:{}  name:{}".format(keyWord, name))
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
            nextPageUrl = "https://www.youtube.com" + nextPageUrl + "&pbj=1" + "&ctoken=" + continuation + "&itct=" + continuation
            logging.info("获取下一页链接成功,keyWord:{}".format(keyWord))
            formData = {
                "session_token": token
            }

            urlList = []
            for content in contents:
                videoRenderer = content.get("videoRenderer")
                if not videoRenderer:
                    videoRenderer = content.get("channelRenderer")
                    if not videoRenderer:
                        continue
                try:
                    userUrl = "https://www.youtube.com" + \
                              videoRenderer["shortBylineText"]["runs"][0]["navigationEndpoint"]["commandMetadata"][
                                  "webCommandMetadata"]["url"]
                except Exception as e:
                    continue
                if userUrl not in urlList:
                    urlList.append(userUrl)

            gList = []
            for url in urlList:
                if part == "GB":
                    if url in urlsGB:
                        continue
                    if url not in urlsGB:
                        urlsGB.append(url)
                else:
                    if url in urlsCL:
                        continue
                    if url not in urlsCL:
                        urlsCL.append(url)

                # 判断是否在数据库中
                result = collection.find_one({"part": part, "url": url, "platId": platId})
                if result:
                    logging.warn("存在库中part:{},name:{},url:{}".format(part, name, url))
                    continue

                result = formeryoutubecollection.find_one({"part": part, "url": url, "platId": platId})
                if result:
                    logging.warn("存在库中part:{},name:{},url:{}".format(part, name, url))
                    continue

                if part == "clothes":
                    # 判断是否在cmms中
                    domain = "http://cmms.gloapi.com/"
                    isExists = checkUrl(url, domain)
                    if isExists:
                        # 代表存在接口中
                        continue
                elif part == "GB":
                    # 判断是否在mms中
                    domain = "http://mms.gloapi.com/"
                    isExists = checkUrl(url, domain)
                    if isExists:
                        # 代表存在接口中
                        continue
                self.sendRequestUser(url, keyWord, name, part, station, language)
            self.GetNextWhile(keyWord, name, part, station, nextPageUrl, formData, language)
        except Exception as e:
            logging.error(traceback.format_exc())
            self.changeWordStatus(keyWord, part, station)

    # 循环获取下一页信息
    def GetNextWhile(self, keyWord, name, part, station, nextPageUrl, formData, language):
        nextPageUrlnew, formDatanew = self.sendRequestPost(keyWord, name, part, station, nextPageUrl, formData,
                                                           language)
        i = 0
        while i < self.pageNum:
            # while True:
            i += 1
            nextPageUrlnew, formDatanew = self.sendRequestPost(keyWord, name, part, station, nextPageUrl, formData,
                                                               language)
            if not nextPageUrlnew or not formDatanew:
                logging.error("没有下一页")
                break

        self.changeWordStatus(keyWord, part, station)

    def changeWordStatus(self, keyWord, part, station):
        try:
            keyWordCollection.update_one({"keyWord": keyWord, "platId": platId, "part": part, "station": station},
                                         {"$set": {"getData": True}})
            logging.info("关键字:{} 状态改为已经抓取状态".format(keyWord))
        except Exception as e:
            logging.error(e)

    # 解析下一页信息
    def parseNextPage(self, response, keyWord, name, part, station, language):
        global urlsGB
        global urlsCL
        nextPageUrl, formData = "", ""
        global debug_flag
        try:
            response = json.loads(response)
            if not response:
                return nextPageUrl, formData
            try:
                response = response[1]
            except Exception as e:
                return nextPageUrl, formData
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
                return nextPageUrl, formData

            # nextPageUrl
            # logging.info(response["endpoint"]["urlEndpoint"])
            nextPageUrl = response["endpoint"]["urlEndpoint"]["url"].split("&")[0]

            nextPageUrl = "https://www.youtube.com" + nextPageUrl + "&pbj=1" + "&ctoken=" + continuation + "&itct=" + continuation
            logging.info("获取下一页链接成功,keyWord:{}".format(keyWord))
            formData = {
                "session_token": token
            }

            urlList = []
            for content in contents:
                videoRenderer = content.get("videoRenderer")
                if not videoRenderer:
                    continue
                try:
                    userUrl = "https://www.youtube.com" + \
                              videoRenderer["shortBylineText"]["runs"][0]["navigationEndpoint"]["commandMetadata"][
                                  "webCommandMetadata"]["url"]
                except Exception as e:
                    continue

                if userUrl not in urlList:
                    urlList.append(userUrl)

            gList = []
            for url in urlList:
                if part == "GB":
                    if url in urlsGB:
                        continue
                    if url not in urlsGB:
                        urlsGB.append(url)
                else:
                    if url in urlsCL:
                        continue
                    if url not in urlsCL:
                        urlsCL.append(url)

                # 判断是否在数据库中
                result = collection.find_one({"part": part, "url": url, "platId": platId})
                if result:
                    logging.warn("存在库中part:{},name:{},url:{}".format(part, name, url))
                    continue
                result = formeryoutubecollection.find_one({"part": part, "url": url, "platId": platId})
                if result:
                    logging.warn("存在库中part:{},name:{},url:{}".format(part, name, url))
                    continue

                if part == "clothes":
                    # 判断是否在cmms中
                    domain = "http://cmms.gloapi.com/"
                    isExists = checkUrl(url, domain)
                    if isExists:
                        # 代表存在接口中
                        continue
                else:
                    # 判断是否在mms中
                    domain = "http://mms.gloapi.com/"
                    isExists = checkUrl(url, domain)
                    if isExists:
                        # 代表存在接口中
                        continue
                self.sendRequestUser(url, keyWord, name, part, station, language)
        except Exception as e:
            logging.error(traceback.format_exc())

        return nextPageUrl, formData


def runThreadlanguage(language):
    youtube = YouTuBe()
    while True:
        resultList = list(keyWordCollection.find({"language": language, "getData": False, "platId": 1}).limit(1000))
        if not resultList:
            logging.error("没有相关关键字,language:{}".format(language))
            time.sleep(600)
            continue
        for result in resultList:
            keyWord = result["keyWord"]
            name = result["resPeople"]
            part = result["part"]
            try:
                logging.info("beggin to deal with keyWord:{},name:{},part:{}".format(keyWord, name, part))
                url = "https://www.youtube.com/results?search_query=" + parse.quote(keyWord) + "&pbj=1"
                responseBody = youtube.sendRequest(url, keyWord)
                if responseBody:
                    youtube.parsePage(responseBody, keyWord, name, part)
            except Exception as e:
                logging.error(e)


def runThreadEnglish(language):
    while True:
        resultList = list(
            keyWordCollection.find({"getData": False, "platId": 1, "language": language}).limit(100).sort(
                [('insertTime', pymongo.DESCENDING)]))
        if not resultList:
            logging.error("没有相关关键字")
            time.sleep(600)
            continue
        # for result in resultList:
        #     dealkeyWord(result)
        pool = ThreadPool(1)
        pool.map_async(dealkeyWord, resultList)
        pool.close()
        pool.join()


def dealkeyWord(result):
    youtube = YouTuBe()
    keyWord = result["keyWord"]
    name = result["resPeople"]
    part = result["part"]
    station = result["station"]
    language = result["language"]
    try:
        logging.info("beggin to deal with keyWord:{},name:{},part:{},station:{}".format(keyWord, name, part, station))
        url = "https://www.youtube.com/results?search_query=" + parse.quote(keyWord) + "&pbj=1"
        responseBody = youtube.sendRequest(url, keyWord)
        if responseBody:
            youtube.parsePage(responseBody, keyWord, name, part, station, language)
    except Exception as e:
        logging.error(e)


if __name__ == '__main__':
    # 验证 mms 和cmms
    # mmsreadMongoth = threading.Thread(target=mmsreadMongo, args=())
    # mmsreadMongoth.start()

    # 回补国家
    backcountryth = threading.Thread(target=backCountry, args=(collection,))
    backcountryth.start()

    # # runThreadEnglish("立陶宛", "孙海龙")
    # languageList = keyWordCollection.distinct("language", {"getData": False, "platId": 1})
    # for language in languageList:
    #     pro = multiprocessing.Process(target=runThreadEnglish, args=(language,))
    #     pro.start()
