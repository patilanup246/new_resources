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
formeryoutube = mongodb["formeryoutube"]
youtubeUrl = mongodb["youtubeUrl"]
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

GBwhiteList2 = ['初学者', '区别', '包装', '实惠', '对比', '预算', '顶级', '钥匙', '超值', '赠品', '评价', '评测', '评论', '搭配', '最好', '最火', '比价',
                '自拍', '低价', '便宜', '指南', '拆除', 'Best', 'top', '风格', '难以置信', '购买', '运动', '不同', '想法', '产品', '优点', '体会',
                '体验', '值得', '使用', '区别', '参数', '博客', '观点', '最好', '最佳', '发布', '全部', '品味', '圈子', '奇特', '对比', '尝试', '差异',
                '建议', '想法', '感受', '感想', '指南', '排名', '排行', '搭配', '推测', '方式', '方法', '最好', '最具', '材料', '比较', '测试', '汇总',
                '火热', '火爆', '点评', '爆红', '点评', '玩家', '独特', '礼品', '礼物', '缺点', '见解', '见地', '观点', '规格', '评论', '评价', '购买',
                '超值', '集合', '顶部', '预估', '预想', '预料', '预测', '预言', 'Best', '多好', '惊奇', '惊喜', '难以置信', '惊人', '怪异', '样式',
                '谈论', '细数', '发现', '论点', '评分', '评比', '见解', '优点']

# 已存在的url
whiteCount = 4
invisibleUrl = mongodb["invisibleUrl"]
ExistUrl = []


class YouTuBe(object):
    def __init__(self):
        self.nextPageUrl = ""
        self.userUrlList = []
        self.formData = {}
        self.thList = []
        self.pageNum = 9
        self.videoNum = 8
        self.VideoTitleCount = 1

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
                    # logging.info(viewCountText)
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
        except Exception as e:
            logging.error(e)
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
                urlList = [url.replace("/about?pbj=1", "")]
            userurl = ""
            for i in urlList:
                if "www.youtube.com" not in i:
                    continue
                userurl = "https://" + i.split("://")[-1]
            if not userurl:
                return None
            if url.replace("/about?pbj=1", "") != userurl:
                logging.info("开始url:{},目前url:{}".format(url.replace("/about?pbj=1", ""), userurl))
            # result = invisibleUrl.find_one({"url": userurl})
            # if result:
            #     logging.warn("观看量或者订阅量不达标,name:{},url:{}".format(name, userurl))
            #     return None

            # 判断是否在数据库中
            result = collection.find_one({"part": part, "url": userurl, "platId": 1})
            if result:
                # youtubeUrl.update_one({"url": userurl}, {"$set": {"getData": True}})
                logging.warn("存在库中part:{},name:{},url:{}".format(part, name, userurl))
                return None

            result = formeryoutube.find_one({"part": part, "url": userurl, "platId": 1})
            if result:
                # youtubeUrl.update_one({"url": userurl}, {"$set": {"getData": True}})
                logging.warn("存在库中part:{},name:{},url:{}".format(part, name, userurl))
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


if __name__ == '__main__':
    # whiteObj = whiteReview()
    # whiteObj.start()
    mainR()
