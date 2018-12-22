# coding:utf-8
<<<<<<< HEAD
import os
import sys

import requests

sys.path.append("./../")
from logs.loggerDefine import loggerDefine
import traceback
from tools.option import getOption
from selenium import webdriver

webspiderDir = "./../logs/web/"
if not os.path.exists(webspiderDir):
    os.makedirs(webspiderDir)
loggerFile = webspiderDir + "webspider.log"
logging = loggerDefine(loggerFile)
from tools.webtool.verifyMail import readMongo as readMongoVerifyMail

from tools.webtool.webMMStrip import readMongo as readMongowebMMStrip
from tools.checkurl import checkWebUrl
from tools.translate.translate_google import mainTranslate
from db.mongodb import connectMongo
from tools.request_headers import *
import re
import time
import jsonpath
from spider.getspider import getSimilarwebInfo, getHtml, sendRequestWhatrun, sendRequestalexa, getViewInfo
from lxml import etree
from urllib.request import urlparse
from googletrans import Translator
import json
import threading
import pymongo
import csv

platId = 3

blackWordList = [
    "买家",
    "交付",
    "交货",
    "付款",
    "优惠",
    "卖家",
    "大车",
    "尺码",
    "我最喜爱的",
    "折扣",
    "换货",
    "清单",
    "物品",
    "结账",
    "订单",
    "订购",
    "购物箱",
    "购物袋",
    "购物车",
    "运往",
    "运费",
    "运输",
    "运送",
    "退货",
    "送货",
    "钱包",
    "ship",
    "cart",
    "payment",
    "paypal",
    "配送",
    "愿望录"
]

translator = Translator()
countrycode = {
    '376': '以色列',
    '674': '圣马力诺',
    '798': '图瓦卢', '8': '阿尔巴尼亚', '320': '危地马拉', '20': '安道尔', '492': '摩纳哥',
    '570': '纽埃', '530': '荷属安的列斯', '732': '西撒哈拉', '833': '英国属地曼岛', '312': '瓜德罗普', '324': '几内亚', '214': '多米尼加',
    '170': '哥伦比亚', '760': '叙利亚', '360': '印度尼西亚', '136': '开曼群岛', '296': '基里巴斯', '500': '蒙特塞拉特', '174': '科摩罗',
    '262': '吉布提', '598': '巴布亚新几内亚', '203': '捷克', '238': '福克兰群岛（马尔维纳斯）', '144': '斯里兰卡', '660': '安圭拉',
    '630': '波多黎各', '233': '爱沙尼亚', '64': '不丹', '772': '托克劳', '388': '牙买加', '862': '委内瑞拉', '807': '前南马其顿',
    '854': '布基纳法索', '462': '马尔代夫', '752': '瑞典', '51': '亚美尼亚', '784': '阿联酋', '840': '美国', '600': '巴拉圭',
    '584': '马绍尔群岛', '208': '丹麦', '352': '冰岛', '428': '拉脱维亚', '634': '卡塔尔', '736': '苏丹', '764': '泰国',
    '654': '圣赫勒拿', '438': '列支敦士登', '268': '格鲁吉亚', '222': '萨尔瓦多', '204': '贝宁', '100': '保加利亚',
    '666': '圣皮埃尔和密克隆', '860': '乌兹别克斯坦', '40': '奥地利', '858': '乌拉圭', '140': '中非', '748': '斯威士兰', '32': '阿根廷',
    '270': '冈比亚', '108': '布隆迪', '704': '越南', '70': '波黑', '528': '荷兰', '334': '赫德岛和麦克唐纳岛', '434': '利比亚',
    '703': '斯洛伐克', '348': '匈牙利', '470': '马耳他', '624': '几内亚比绍', '72': '博茨瓦纳', '768': '多哥', '392': '日本',
    '484': '墨西哥', '332': '海地', '44': '巴哈马', '795': '土库曼斯坦', '92': '英属维尔京群岛', '24': '安哥拉', '28': '安提瓜和巴布达',
    '180': '刚果（金）', '688': '塞尔维亚', '508': '莫桑比克', '156': '中国', '454': '马拉维', '364': '伊朗', '804': '乌克兰',
    '612': '皮特凯恩', '380': '意大利', '48': '巴林', '422': '黎巴嫩', '591': '巴拿马', '744': '斯瓦尔巴岛和扬马延岛', '232': '厄立特里亚',
    '724': '西班牙', '266': '加蓬', '226': '赤道几内亚', '887': '也门', '192': '古巴', '248': '奥兰群岛', '418': '老挝',
    '548': '瓦努阿图', '706': '索马里', '662': '圣卢西亚', '694': '塞拉利昂', '246': '芬兰', '218': '厄瓜多尔', '356': '印度',
    '410': '韩国', '254': '法属圭亚那', '562': '尼日尔', '112': '白俄罗斯', '212': '多米尼克', '440': '立陶宛', '686': '塞内加尔',
    '478': '毛利塔尼亚', '450': '马达加斯加', '678': '圣多美和普林西比', '762': '塔吉克斯坦', '426': '莱索托', '554': '新西兰',
    '780': '特立尼达和多巴哥', '430': '利比里亚', '524': '尼泊尔', '608': '菲律宾', '581': '美国本土外小岛屿', '788': '突尼斯',
    '566': '尼日利亚', '60': '百慕大', '372': '爱尔兰', '516': '纳米比亚', '604': '秘鲁', '408': '朝鲜', '50': '孟加拉国',
    '800': '乌干达', '499': '黑山', '716': '津巴布韦', '84': '伯利兹', '275': '巴勒斯坦', '344': '香港', '304': '格陵兰',
    '398': '哈萨克斯坦', '16': '美属萨摩亚', '583': '密克罗尼西亚联邦', '832': '泽西岛', '90': '所罗门群岛', '292': '直布罗陀',
    '158': '台湾', '643': '俄罗斯联邦', '682': '沙特阿拉伯', '234': '法罗群岛', '184': '库克群岛', '74': '布维岛',
    '166': '科科斯（基林）群岛', '188': '哥斯达黎加', '384': '科特迪瓦', '124': '加拿大', '520': '瑙鲁', '242': '斐济', '400': '约旦',
    '96': '文莱', '533': '阿鲁巴', '850': '美属维尔京群岛', '620': '葡萄牙', '231': '埃塞俄比亚', '580': '北马里亚纳', '116': '柬埔寨',
    '474': '马提尼克', '690': '塞舌尔', '328': '圭亚那', '540': '新喀里多尼亚', '152': '智利', '417': '吉尔吉斯斯坦', '56': '比利时',
    '504': '摩洛哥', '10': '南极洲', '120': '喀麦隆', '276': '德国', '4': '阿富汗', '642': '罗马尼亚', '818': '埃及',
    '756': '瑞士', '466': '马里', '894': '赞比亚', '340': '洪都拉斯', '638': '留尼汪', '586': '巴基斯坦', '616': '波兰',
    '626': '东帝汶', '162': '圣诞岛', '308': '格林纳达', '368': '伊拉克', '404': '肯尼亚', '480': '毛里求斯', '31': '阿塞拜疆',
    '12': '阿尔及利亚', '776': '汤加', '36': '澳大利亚', '260': '法属南部领地', '414': '科威特', '882': '萨摩亚', '52': '巴巴多斯',
    '442': '卢森堡', '702': '新加坡', '705': '斯洛文尼亚', '740': '苏里南', '792': '土耳其', '512': '阿曼',
    '239': '南乔治亚岛和南桑德韦奇岛', '132': '佛得角', '796': '特克斯和凯科斯群岛', '646': '卢旺达', '831': '格恩西岛', '250': '法国',
    '148': '乍得', '76': '巴西', '834': '坦桑尼亚', '178': '刚果（布）', '670': '圣文森特和格林纳丁斯', '458': '马来西亚', '710': '南非',
    '826': '英国', '446': '澳门', '316': '关岛', '68': '玻利维亚', '300': '希腊', '191': '克罗地亚', '104': '缅甸',
    '288': '加纳', '86': '英属印度洋领地', '196': '塞浦路斯', '336': '梵蒂冈', '496': '蒙古', '585': '帕劳', '574': '诺福克岛',
    '876': '瓦利斯和富图纳', '175': '马约特', '498': '摩尔多瓦', '258': '法属波利尼西亚', '659': '圣基茨和尼维斯', '558': '尼加拉瓜',
    '578': '挪威'}

db = connectMongo(True)
urlCollection = db["googleUrl"]
keyCollection = db["keyWords"]
blackWhiteCollection = db["blackWhite"]
blackUrlCollection = db["blackUrl"]
webResourcesCollection = db["webResources"]

black = blackWhiteCollection.distinct("word", {"isBlack": True, "platId": 3, "part": "GB"})
white = blackWhiteCollection.distinct("word", {"isWhite": True, "platId": 3, "part": "GB"})

cmsListErro = [
    "bigcommerce",
    "shopper approved",
    "shopify",
    "prestashop",
    "oscommerce",
    "openCart",
    "magento",
    "demandware",
    "craft cms",
    "qubit opentag",
    "3dcart",
    "vtex enterprise",
    "prestashop",
    "demandware",
]


# 请求whatrun  API 获取框架信息
def getFrameData(scheme, domain, mongoUrl):
    runItem = {}
    try:
        domain = domain.replace('www.', '')  # 域名 去除www
        whatrunUrl = 'https://www.whatruns.com/api/v1/get_site_apps'
        formData = {
            "data": json.dumps({"rawhostname": domain, "hostname": domain,
                                "url": mongoUrl, "type": "ajax"})
        }
        logging.info("构建whatrun请求信息,开始请求whatrun  API,mongoUrl:[{}],data:[{}]".format(mongoUrl, formData))
        # whatrunHeaders["Content-Length"] = str(len(formData))
        whatRunApps = sendRequestWhatrun(whatrunUrl, formData, whatrunHeaders)
        if whatRunApps == "":
            return
        try:
            whatRunAppsDict = json.loads(whatRunApps)
        except Exception as e:
            logging.error(whatRunApps)
            return

        for key, value in whatRunAppsDict.items():
            for key, value in value.items():
                detailList = []
                for item in value:
                    name = item["name"]
                    version = item.get("version")
                    if not version:
                        version = ""
                    detailName = name + " " + version
                    detailList.append(detailName.strip())
                runItem[key] = detailList
            return runItem
    except Exception as e:
        logging.error(traceback.format_exc())
    return runItem


def getMailPage(responseBody, selector):
    try:
        emailStr = ""
        pattern = re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}\b')
        try:
            response = responseBody
        except Exception as e:
            response = responseBody

        email_lists = []
        for xin in maid:
            footr = selector.xpath(xin)
            foots = " ".join(footr)
            email_list = pattern.findall(foots)
            if len(email_list) > 0:
                email_lists += email_list

        # 去重
        email_lists = list(set(email_lists))
        if email_lists:
            for i in email_lists:
                if i.endswith("png"):
                    continue

                if i.endswith("PNG"):
                    continue

                if i.endswith("jpg"):
                    continue

                if i.endswith("gif"):
                    continue

                if i.endswith("jif"):
                    continue

                if i.endswith("JPG"):
                    continue

                if i.endswith("jpeg"):
                    continue

                if i.endswith("JPEG"):
                    continue

                if "@domain." in i:
                    continue

                if "@example." in i:
                    continue

                if "your@" in i:
                    continue

                emailStr += i + "\n"
    except Exception as e:
        logging.error(traceback.format_exc())
        logging.error("邮箱获取失败")
        emailStr = ""
    return emailStr.strip()


def getDetail(mongoUrl, part):
    whiteNum = 0
    blackNum = 0
    blackStr = ""
    whiteStr = ""
    headerStr, footerStr = "", ""
    headerZH, footerZH = "", ""
    fhBlackWord, fhBlackWordCount = "", 0
    facebook, instagram, youtube, twitter, title, desc, titleChinese, emailStr = "", "", "", "", "", "", "", ""
    try:
        # 获取url的源码信息
        responseBody = getHtml(mongoUrl, webResourcesCollection)
        if not responseBody:
            logging.error("访问mongoUrl:{}没有获取到任何相关信息".format(mongoUrl))
            return fhBlackWord, fhBlackWordCount, blackStr, headerZH, footerZH, headerStr, footerStr, blackNum, whiteNum, whiteStr, title, desc, titleChinese, emailStr, facebook, instagram, youtube, twitter, blackStr
        else:
            fhBlackWord, fhBlackWordCount, blackStr, headerZH, footerZH, headerStr, footerStr, blackNum, whiteNum, whiteStr, title, desc, titleChinese, emailStr, facebook, instagram, youtube, twitter, blackStr = dealResponse(
                responseBody, mongoUrl)
            return fhBlackWord, fhBlackWordCount, blackStr, headerZH, footerZH, headerStr, footerStr, blackNum, whiteNum, whiteStr, title, desc, titleChinese, emailStr, facebook, instagram, youtube, twitter, blackStr
    except Exception as e:
        logging.error(traceback.format_exc())
        return fhBlackWord, fhBlackWordCount, blackStr, headerZH, footerZH, headerStr, footerStr, blackNum, whiteNum, whiteStr, title, desc, titleChinese, emailStr, facebook, instagram, youtube, twitter, blackStr


def dealResponse(responseBody, mongoUrl):
    whiteNum = 0
    blackNum = 0
    blackStr = ""
    whiteStr = ""
    headerStr, footerStr = "", ""
    headerZH, footerZH = "", ""
    fhBlackWord, fhBlackWordCount = "", 0
    facebook, instagram, youtube, twitter, title, desc, titleChinese, emailStr = "", "", "", "", "", "", "", ""
    try:
        selector = etree.HTML(responseBody)
    except Exception as e:
        logging.error(e)
        selector = etree.HTML(responseBody.decode())

    # 获取邮箱信息
    emailStr = getMailPage(responseBody, selector)
    # 获取标题
    try:
        title = selector.xpath('//title/text()')[0].replace('\n', '').replace('  ', ' ').strip()
    except:
        logging.error("url:{},标题为空".format(mongoUrl))
        title = ""

    # 获取描述信息
    try:
        desc = selector.xpath('//meta[@name="description"]/@content')[0].replace('\n', '').replace('  ', ' ')
    except:
        try:
            desc = selector.xpath('//meta[@name="Description"]/@content')[0].replace('\n', '').replace('  ', ' ')
        except Exception as e:
            desc = ""

    # 标题和描述信息拼接
    titkeDesc = title + "\n" + desc
    try:
        if titkeDesc:
            titleChinese = mainTranslate(titkeDesc)
            for bd in black:
                if bd in titleChinese:
                    blackword = bd
                    blackNum += 1
                    blackStr += blackword + " "
                    logging.error("存在黑名单,word:{},url:{}".format(blackword, mongoUrl))
                    # return blackNum, whiteNum, whiteStr, title, desc, titleChinese, emailStr, facebook, instagram, youtube, twitter
            blackStr = blackStr.strip()
            for td in white:
                if td in titleChinese:
                    whiteNum += 1
                    whiteStr += td + " "
            whiteStr = whiteStr.strip()
        else:
            titleChinese = ""
    except:
        titleChinese = ""
    for lid in li:
        urlds = selector.xpath(lid[0])
        if len(urlds) > 0:
            for keys in urlds:
                if ('facebook' in str(keys)) and (facebook == ''):
                    facebook = lid[1] + str(keys)
                elif ('instagram' in str(keys)) and (instagram == ''):
                    instagram = lid[1] + str(keys)
                elif ('twitter' in str(keys)) and (twitter == ''):
                    twitter = lid[1] + str(keys)
                elif ('youtube' in str(keys)) and (youtube == ''):
                    youtube = lid[1] + str(keys)

    headerStr, footerStr, headerZH, footerZH, fhBlackWord, fhBlackWordCount = dealHeaderFooterInfo(selector)
    return fhBlackWord, fhBlackWordCount, blackStr, headerZH, footerZH, headerStr, footerStr, blackNum, whiteNum, whiteStr, title.strip(), desc.strip(), titleChinese.strip(), emailStr, facebook.strip(), instagram.strip(), youtube.strip(), twitter.strip(), blackStr.strip()


def dealHeaderFooterInfo(selector):
    headerStr, footerStr, headerZH, footerZH, fhBlackWord, fhBlackWordCount = "", "", "", "", "", 0
    try:
        textList = selector.xpath("//header//text()")
        node = selector.xpath("//*[contains(@class,'header')]") + selector.xpath(
            "//*[contains(@id,'header')]") + selector.xpath("//*[contains(@class,'Header')]") + selector.xpath(
            "//*[contains(@id,'Header')]")
        if node:
            for i in node:
                textList += i.xpath(".//text()")
        else:
            textList += selector.xpath("//head//text()")

        if not textList:
            headerStr = ""
        else:
            textStr = ""
            for text in list(set(textList)):
                text = text.replace("\n", "").strip()
                if not text:
                    continue
                text = text + ","
                textStr += text
            headerStr = textStr.strip()[:-1]
        textList = selector.xpath("//footer//text()")
        node = selector.xpath("//*[contains(@class,'footer')]") + selector.xpath(
            "//*[contains(@id,'footer')]") + selector.xpath("//*[contains(@class,'Footer')]") + selector.xpath(
            "//*[contains(@id,'Footer')]")
        if node:
            for i in node:
                textList += i.xpath(".//text()")
        else:
            textList = []

        if not textList:
            footerStr = ""
        else:
            textStr = ""
            for text in list(set(textList)):
                text = text.replace("\n", "").strip()
                if not text:
                    continue
                text = text + ","
                textStr += text
            footerStr = textStr.strip()[:-1]
        if not footerStr and not headerStr:
            headerZH = ""
            footerZH = ""
        else:  # 两者至少有一个
            if not footerStr:
                headerZH = mainTranslate(headerStr[:4000])
                footerZH = ""
            elif not headerStr:
                footerZH = mainTranslate(footerStr[:4000])
                headerZH = ""
            else:
                # 合并翻译
                headerZH = mainTranslate(headerStr[:4000])
                footerZH = mainTranslate(footerStr[:4000])
        fhBlackWord = ""
        fhBlackWordCount = 0
        for word in blackWordList:
            if word in footerStr or word in headerZH or word in footerZH or word in headerStr:
                fhBlackWord += word + " "
                fhBlackWordCount += 1
        fhBlackWord = fhBlackWord.strip()
    except Exception as e:
        logging.error(traceback.format_exc())

    return headerStr, footerStr, headerZH, footerZH, fhBlackWord, fhBlackWordCount
=======
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import pymongo
import collections, re
import time
import jsonpath
from getspider import spida, spidno, allspider, getcmsd
from lxml import etree
import random
from urlparse import urlparse
from googletrans import Translator
import codecs
import csv
import sys
import json
import logging


import threading

debugFlg = sys.argv[1]
countryco = open('country.txt', 'r').read()
countrycode = eval(countryco)

bullshit = {
    'Host': 'www.whatruns.com',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
    'Content-type': 'application/x-www-form-urlencoded',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cookie': '__cfduid=dc6a15345be2832c0004eed53056e470f1532659221; _ga=GA1.2.999942773.1532659223; intercom-id-dvzew6nm=21f152a5-82e2-444e-a3fa-1f62373b66fa'
}

adasd = {
    'Host': 'w3techs.com',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
    'Content-type': 'application/x-www-form-urlencoded',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    # 'Accept-Language': 'zh-CN,zh;q=0.9',
}

baidu = {
    'Host': 'translate.google.cn',
    'Upgrade-Insecure-Requests': '1',
    'Connection': 'keep-alive',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'cookies': '_ga=GA1.3.1147932913.1532412771; 1P_JAR=2018-8-3-10; NID=135=l-tjMuDl2WviixSLeXKVxYJBimmDDqXAHQjdP-q6fYVhwBwJmVsReuWJJuFxgp15T6j-LheIoapHzJH0UnSD0WVCv3yfSBQPOEDO-zz-nmd_CzSK7GrLYmAjQZvnVI1IU1TJ0bLHf9uxwOJzWw',
}

similarweb = {
    "Host": "api.similarweb.com",
    "Connection": "keep-alive",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9"
}

li = [['//footer/descendant::a/@href', ''],
      ['//header/descendant::a/@href', ''],
      ['//a/@href', '  ']]

maid = ['//footer/descendant::*/text()', '//header/descendant::*/text()']

client = pymongo.MongoClient('52.203.246.147', 27017)
db = client.globalegrow
db.authenticate('gb_rw', 'vHC3xdG')
table = db.keyWord_url
table_1 = db.keyWords


def getviews(urls):  # 获取网站流量相关数据
    # print str(urls).replace('www.','')
    # lidd = [ldo.strip() for ldo in open('C:\\Python27\\Lib\\ipport.txt', 'r').readlines()]
    url = 'https://api.similarweb.com/v1/SimilarWebAddon/' + str(urls).replace('www.', '') + '/all'
    data = spida(url, similarweb)
    logging.info("")
    print 'fanhuilaide:..'.data
    html = json.loads(data)
    try:
        viees = jsonpath.jsonpath(html, "$..Visits")[0]
    except:
        viees = ''
    try:
        count = jsonpath.jsonpath(html, "$..TopCountryShares")[0][0]
        counts = countrycode[str(count['Country'])]
    except:
        count = {}
        counts = ''
    try:
        percent = count['Value']
    except:
        percent = ''
    return [viees, counts, percent]


def getcms(urll, domain):  # 获取建站框架数据
    url = domain.replace('www.', '')
    cms, cmss, pay = '', '', ''
    urls = 'https://www.whatruns.com/api/v1/get_site_apps'
    text = 'data=%7B%22rawhostname%22%3A%22' + url + '%22%2C%22hostname%22%3A%22' + url + '%22%2C%22url%22%3A%22' + str(
        urll) + '%3A%2F%2F' + url + '%2F%22%2C%22type%22%3A%22ajax%22%7D'

    html = allspider(urls, text, bullshit)

    datas = json.loads(html)
    cmsd = jsonpath.jsonpath(datas, "$..apps")

    try:
        daoz = jsonpath.jsonpath(json.loads(cmsd[0]), "$..CMS")

        almost = json.dumps(daoz)
        rzd = json.loads(almost)
        CMD = jsonpath.jsonpath(rzd, "$..name")[0:3]
        # name = jsonpath.jsonpath(rzdq,'$..parentElement')[0:3]
        cms = '.'.join(CMD)

        # names = ','.join(name)

    except:
        cms = 'N'

        # names = 'N'
    try:
        daozz = jsonpath.jsonpath(json.loads(cmsd[0]), "$..CMS")

        rzds = json.loads(almost)
        verson = jsonpath.jsonpath(rzds, "$..version")[0:3]

        cmss = ','.join(verson)

    except:
        cmss = 'N'

    return ["Plugins:" + str(cms), "wordPress:" + str(cmss)]


def getmails(htmld, datasd):
    email_lists = []
    pattern = re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}\b')
    for xin in maid:
        footr = datasd.xpath(xin)
        foots = " ".join(footr)
        email_list = re.findall(pattern, str(foots))
        if len(email_list) > 0:
            email_lists += email_list
    if len(email_lists) == 0:
        email_lis = re.findall(pattern, htmld)
        for xind in email_lis:
            email_lists.append('  ' + str(xind))
    if len(email_lists) > 0:
        emails = ','.join(email_lists)
    else:
        emails = 'O'
    return str(emails)


def getit(url):
    titleloge = 0
    blackwhite = 0
    print url
    html = spidno(url)
    datas = etree.HTML(html)
    email = getmails(html, datas)
    facebook, instagram, youtube, twitter = '0', '0', '0', '0'
    try:
        title = datas.xpath('//title/text()')[0].replace('\n', '').replace('  ', ' ')
    except:
        title = 'n'
    try:
        descr = datas.xpath('//meta[@name="Description"]/@content')[0].replace('\n', '').replace('  ', ' ')
    except:
        descr = 'n'
    tield = title + descr
    try:
        titles = translator.translate(tield, dest='zh-cn').text
        for bd in black:
            if bd in titles:
                blackwhite += 1
        for td in whites:
            if td in titles:
                titleloge += 1
    except:
        titles = 'n'
    for lid in li:
        urlds = datas.xpath(lid[0])
        if len(urlds) > 0:
            for keys in urlds:
                if ('facebook' in str(keys)) and (facebook == '0'):
                    facebook = lid[1] + str(keys)
                elif ('instagram' in str(keys)) and (instagram == '0'):
                    instagram = lid[1] + str(keys)
                elif ('twitter' in str(keys)) and (twitter == '0'):
                    twitter = lid[1] + str(keys)
                elif ('youtube' in str(keys)) and (youtube == '0'):
                    youtube = lid[1] + str(keys)
    print 'heibaimingdan----', (blackwhite, titleloge)
    return [blackwhite, titleloge, title, titles, email, facebook, instagram, youtube, twitter]
>>>>>>> 00b8661052c6b093b516ce99809036f3f4163d85


def get_access_token(website):  # 获取邮箱数据
    connect = []
<<<<<<< HEAD
    try:
        url = 'https://app.snov.io/oauth/access_token'
        params = {
            'grant_type': 'client_credentials',
            'client_id': '4807dc4e3735fbe657bfcaffbce0d418',
            'client_secret': '631b2b69947b0db37f27dde1bfbe6a08'
        }
        res = requests.post(url=url, data=params, verify=False, timeout=30)
        resText = res.text
        # logging.info(resText)
        token = json.loads(resText)['access_token']
        logging.info(token)
        params = {'access_token': token,
                  'domain': website,
                  'type': 'all',
                  'limit': 100
                  }
        url = 'https://app.snov.io/restapi/get-domain-emails-with-info'
        res = requests.post(url=url, data=params, verify=False, timeout=30)
        # logging.info(res.text)
        emails = []
        responseBody = json.loads(res.text)
        errType = jsonpath.jsonpath(responseBody, "$..error_description")
        if errType:
            if errType[0] == "Domain is invalid":
                return connect
        for x in responseBody['emails']:
            try:
                status = x['status']
                email = x['email']
                if not email:
                    continue
                if email in emails:
                    continue
                if email:
                    emails.append(email)
            except:
                status, email = '', ''
            try:
                firstName = x['firstName']
                lastName = x['lastName']
            except:
                firstName, lastName = '', ''
            try:
                sourcePage = x['sourcePage']
                position = x['position']
            except:
                sourcePage, position = '', ''
            connect.append([status, email, firstName, lastName, sourcePage, position])
    except Exception as e:
        logging.error(traceback.format_exc())
        logging.info(responseBody)
        return None
    return connect


def getalexaInfo(url):
    globalRankAlexa, countryAlexa, countryRankAlexa, relateLinksAlexa = 0, "", "", ""
    try:
        responseBody = sendRequestalexa(url)
        if responseBody:
            selector = etree.HTML(responseBody)
            globalRank = selector.xpath('//*[@id="siteStats"]/tbody/tr[1]/td[1]/div[1]/a/text()')
            if globalRank:
                try:
                    globalRankAlexa = int(globalRank[0].strip().replace(",", ""))
                except Exception as e:
                    logging.error(e)
            else:
                globalRankAlexa = 0

            countryAlexa = selector.xpath('//*[@id="siteStats"]/tbody/tr[1]/td[2]/div[1]/a/@title')
            if countryAlexa:
                try:
                    countryAlexa = countryAlexa[0].strip()
                except Exception as e:
                    logging.error(e)
            else:
                countryAlexa = ""

            countryRankAlexa = selector.xpath('//*[@id="siteStats"]/tbody/tr[1]/td[2]/div[1]/a/text()')
            if countryRankAlexa:
                try:
                    countryRankAlexa = int(countryRankAlexa[0].strip().replace(",", ""))
                except Exception as e:
                    logging.error(e)
            else:
                countryRankAlexa = 0

            relateLinksAlexa = selector.xpath('//*[@id="siteStats"]/tbody/tr[4]/td[1]/div[2]/ul/li/a/@href')
            if relateLinksAlexa:
                try:
                    relateLinksAlexa = "\n".join(relateLinksAlexa).strip()
                except Exception as e:
                    logging.error(e)
            else:
                relateLinksAlexa = ""
    except Exception as e:
        logging.error(traceback.format_exc())
    return globalRankAlexa, countryAlexa, countryRankAlexa, relateLinksAlexa


def updateStatusGoogleUrl(mongoUrl):
    try:
        urlCollection.update({"url": mongoUrl}, {"$set": {"isData": True}}, multi=True)
    except Exception as e:
        logging.error("googleUrl更新为已经抓取状态失败")


# 主调度器
def mainRun(result):
    mongoUrl = result["url"]

    resPeople = result.get("name")
    if not resPeople:
        resPeople = ""

    language = result.get("language")
    if not language:
        language = ""

    part = result.get("part")
    if not part:
        part = "GB"

    station = result.get("station")
    if not station:
        station = "Gearbest"

    keyWord = result.get("keyWord")
    if not keyWord:
        keyWord = ""

    try:
        # 获取mongoUrl中的协议和域名
        scheme = urlparse(mongoUrl).scheme  # https 和 http
        domain = urlparse(mongoUrl).netloc  # www.amazon.com
        logging.info("mongoUrl:[{}],协议:[{}],域名:[{}]".format(mongoUrl, scheme, domain))

        # 获取白名单数量  标题  邮箱  facebook数据 instagram数据  youtube数据  Twitter数据
        logging.info("通过{}页面获取相关信息".format(mongoUrl))
        fhBlackWord, fhBlackWordCount, blackStr, headerZH, footerZH, headerStr, footerStr, blackNum, whiteNum, whiteStr, title, desc, titleChinese, emailStr, facebook, instagram, youtube, twitter, blackStr = getDetail(
            mongoUrl, part)

        cms, cmss = "", ""

        # 获取网站流量信息 包括访问量  国家  百分比
        viewCountSimilarweb, countrySimilarweb, percentSimilarweb, relateLinkSimilarSites = getViewInfo(domain)

        # https://www.apple.com
        url = "https://www.alexa.com/minisiteinfo/{}?offset=5&version=alxg_20100607".format(domain)
        globalRankAlexa, countryAlexa, countryRankAlexa, relateLinksAlexa = getalexaInfo(url)

        connect = ""

        item = {
            "url": mongoUrl,
            "whiteNum": whiteNum,
            "whiteStr": whiteStr,
            "title": title,
            "desc": desc,
            "titleChinese": titleChinese,
            "facebook": facebook,
            "instagram": instagram,
            "youtube": youtube,
            "twitter": twitter,
            "viewCount": viewCountSimilarweb,
            "country": countrySimilarweb,
            "percent": percentSimilarweb,
            "cms": cms,
            "cmms": cmss,
            "relateLinkSimilarSites": relateLinkSimilarSites,
            "globalRankAlexa": globalRankAlexa,
            "countryAlexa": countryAlexa,
            "countryRankAlexa": countryRankAlexa,
            "relateLinksAlexa": relateLinksAlexa,
            "connect": connect,
            "csvLoad": False,
            "insertTime": int(time.time()),
            "isGetLink": False,
            "language": language,
            "resPeople": resPeople,
            "station": station,
            "part": part,
            "header": headerStr,
            "footer": footerStr,
            "headerZH": headerZH,
            "footerZH": footerZH,
            "fhBlackWord": fhBlackWord,
            "fhBlackWordCount": fhBlackWordCount,
            "blackStr": blackStr,
            "blackNum": blackNum
        }
        if emailStr:
            emailList = list(set(emailStr.split("\n")))
            for num, email in enumerate(emailList):
                if not email:
                    continue
                item["_id"] = "3_" + part + "_" + mongoUrl + "_" + str(num + 1)
                item["emailStr"] = email
                try:
                    webResourcesCollection.insert(item)
                except Exception as e:
                    pass
                updateStatusGoogleUrl(mongoUrl)
                logging.info("插入成功,url:{}".format(mongoUrl))
        else:
            item["_id"] = "3_" + part + "_" + mongoUrl
            item["emailStr"] = emailStr
            try:
                webResourcesCollection.insert(item)
            except Exception as e:
                pass
            updateStatusGoogleUrl(mongoUrl)
            logging.info("插入成功,url:{}".format(mongoUrl))
        try:
            if whiteNum >= 6:
                dealRelateLink(relateLinkSimilarSites, relateLinksAlexa, part, station, mongoUrl)
        except Exception as e:
            logging.error(e)
    except Exception as e:
        logging.error(traceback.format_exc())


def dealRelateLink(relateLinkSimilarSites, relateLinksAlexa, part, station, sourceUrl):
    urlList = []
    if relateLinkSimilarSites:
        urlList = urlList + relateLinkSimilarSites.split("\n")

    if relateLinksAlexa:
        urlList = urlList + relateLinksAlexa.split("\n")

    urlList = list(set(urlList))
    for url in urlList:
        if not url:
            continue
        if "http" not in url:
            url = "https://" + url
        scheme = urlparse(url).scheme
        domain = urlparse(url).netloc
        _id = domain
        item = {
            "_id": _id,
            "url": url,
            "sourceUrl": sourceUrl,
            "domain": domain,
            "scheme": scheme,
            "keyWord": "",
            "language": "",
            "name": "",
            "title": "",
            "desc": "",
            "isData": False,
            "word": "",
            "insertTime": int(time.time()),
            "station": station,
            "part": part
        }
        try:
            resultMongo = urlCollection.find_one({"domain": domain})
            if not resultMongo:
                urlCollection.insert(item)
                logging.info("新增url:{}成功".format(url))
            else:
                logging.warn("存在数据库中:{}".format(domain))
        except Exception as e:
            pass


def getMongoUrl():
    while True:
        resultList = list(
            urlCollection.find({"isData": False}).limit(5).sort([('insertTime', pymongo.DESCENDING)]))
        if not resultList:
            logging.error("数据库中没有需求url,时间:{}".format(int(time.time())))
            time.sleep(60)
            continue
        # resultList = []
        # file = ""
        # csv_reader = csv.reader(open(file, errors="ignore"))
        # for row in csv_reader:
        #     result["url"] = row[0]
        #     result["language"] = row[1]
        #     resultList.append(result)
        for result in resultList:
            mainRun(result)


def mainRBackWhatRun():
    while True:
        if sys.argv[1] == "debug":
            urlList = list(webResourcesCollection.find(
                {"whatRun": {"$exists": 0}, "whiteNum": {"$gte": 3}, "fhBlackWordCount": {"$lte": 1},
                 "blackNum": {"$lte": 1}, "$or": [{"ismms": False, "part": {"$ne": "clothes"}},
                                                  {"iscmms": False, "part": "clothes"}]}).limit(5))
        else:
            urlList = list(webResourcesCollection.find(
                {"whatRun": {"$exists": 0}, "whiteNum": {"$gte": 3}, "fhBlackWordCount": {"$lte": 1},
                 "blackNum": {"$lte": 1}, "$or": [{"ismms": False, "part": {"$ne": "clothes"}},
                                                  {"iscmms": False, "part": "clothes"}]}).limit(1000).sort(
                [("insertTime", pymongo.DESCENDING)]))
        if not urlList:
            urlList = list(webResourcesCollection.find(
                {"whatRun": {"$exists": 0}, "$or": [{"ismms": False, "part": {"$ne": "clothes"}},
                                                    {"iscmms": False, "part": "clothes"}]}).limit(1000))
            if not urlList:
                time.sleep(30)
                continue
        urls = []
        for result in urlList:
            time.sleep(30)
            mongoUrl = result["url"]
            if mongoUrl in urls:
                continue
            urls.append(mongoUrl)
            scheme = urlparse(mongoUrl).scheme
            domain = urlparse(mongoUrl).netloc
            item = getFrameData(scheme, domain, mongoUrl)
            if item == None:
                continue
            webResourcesCollection.update({"url": mongoUrl}, {"$set": {"whatRun": item}}, upsert=True, multi=True)
            logging.info("{}新增whatRun信息{}".format(mongoUrl, item))


class TitleBack(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        if sys.argv[1] == "debug":
            options = getOption(False)
            driver = webdriver.Chrome(chrome_options=options)
        else:
            options = getOption(True)
            driver = webdriver.Chrome(executable_path="./chromedriver", chrome_options=options)
        driver.set_page_load_timeout(10)
        # 打开百度网页
        driver.get("https://www.baidu.com/")
        try:
            while True:
                if sys.argv[1] == "debug":
                    resultList = list(
                        webResourcesCollection.find(
                            {"title": "", "header": "", "footer": "", "desc": "", "viewCount": {"$gte": 10000}}).limit(
                            5))
                else:
                    resultList = list(
                        webResourcesCollection.find(
                            {"title": "", "header": "", "footer": "", "desc": "", "viewCount": {"$gte": 10000},
                             "$or": [{"ismms": False, "part": {"$ne": "clothes"}},
                                     {"iscmms": False, "part": "clothes"}]}).limit(
                            1000).sort(
                            [("insertTime", pymongo.DESCENDING)]))
                if not resultList:
                    time.sleep(60)
                    continue
                for result in resultList:
                    url = result["url"]
                    part = result["part"]
                    self.dealItem(url, part, result, driver)
        except Exception as e:
            logging.error(e)
        finally:
            driver.quit()

    def dealItem(self, url, part, result, driver):
        try:
            try:
                js = 'window.open("{}");'.format(url)
                driver.execute_script(js)
                time.sleep(5)
                driver.switch_to_window(driver.window_handles[1])
                time.sleep(5)
            except:
                driver.close()
                driver.switch_to_window(driver.window_handles[0])
                return

            responseBody = driver.page_source
            if not responseBody:
                driver.close()
                driver.switch_to_window(driver.window_handles[0])
                return
            fhBlackWord, fhBlackWordCount, blackStr, headerZH, footerZH, headerStr, footerStr, blackNum, whiteNum, whiteStr, title, desc, titleChinese, emailStr, facebook, instagram, youtube, twitter, blackStr = dealResponse(
                responseBody, url)
            if title:
                logging.info("重新获取网页信息成功,{}==={}".format(url, title))
                result["fhBlackWord"] = fhBlackWord
                result["fhBlackWordCount"] = fhBlackWordCount
                result["blackStr"] = blackStr
                result["headerZH"] = headerZH
                result["footerZH"] = footerZH
                result["header"] = headerStr
                result["footer"] = footerStr
                result["blackNum"] = blackNum
                result["whiteNum"] = whiteNum
                result["whiteStr"] = whiteStr
                result["title"] = title
                result["desc"] = desc
                result["titleChinese"] = titleChinese
                result["facebook"] = facebook
                result["instagram"] = instagram
                result["youtube"] = youtube
                result["twitter"] = twitter
                result["insertTime"] = int(time.time())
                webResourcesCollection.remove({"url": url})
                if emailStr:
                    # 把最初的数据删除
                    emailList = list(set(emailStr.split("\n")))
                    for num, email in enumerate(emailList):
                        if not email:
                            continue
                        result["_id"] = "3_" + part + "_" + url + "_" + str(num + 1)
                        result["emailStr"] = email
                        try:
                            webResourcesCollection.insert(result)
                        except Exception as e:
                            logging.error(e)
                    logging.info("回补标题信息成功:{}".format(url))
                else:
                    # 没有邮箱  直接更新数据即可
                    result["_id"] = "3_" + part + "_" + url
                    result["emailStr"] = emailStr
                    try:
                        webResourcesCollection.insert(result)
                        logging.info("回补标题成功,url:{}".format(url))
                    except Exception as e:
                        logging.error(e)
                try:
                    if whiteNum >= 6:
                        relateLinkSimilarSites = result["relateLinkSimilarSites"]
                        relateLinksAlexa = result["relateLinksAlexa"]
                        dealRelateLink(relateLinkSimilarSites, relateLinksAlexa, result["part"], result["station"],
                                       result["url"])
                except Exception as e:
                    logging.error(e)

            else:
                logging.error("依旧没有获取到标题{}".format(url))

        except Exception as e:
            logging.error(traceback.format_exc())
        finally:
            driver.close()
            driver.switch_to_window(driver.window_handles[0])


class GetLinMail(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            # 查询数据
            resultList = list(webResourcesCollection.find(
                {"emailStr": "", "connect": "", "title": {"$ne": ""}, "whiteNum": {"$gte": 2},
                 "isGetLink": False,
                 "$or": [{"ismms": False, "part": {"$ne": "clothes"}},
                         {"iscmms": False, "part": "clothes"}], "fhBlackWordCount": 0, "blackNum": 0,
                 "viewCount": {"$gte": 10000},
                 "whatRun": {"$exists": 1}, "csvLoad": False}).limit(100))

            if not resultList:
                time.sleep(600)
                logging.error("目前没有数据需要获取邮箱")
                continue
            urls = []
            for result in resultList:
                url = result["url"]
                if url in urls:
                    continue
                urls.append(url)

                whatRun = result.get("whatRun")
                if whatRun:
                    for word in cmsListErro:
                        if str(whatRun).lower().find(word.lower()) >= 0:
                            logging.error("获取邮箱时,whatrun出现黑名单:{},url:{}".format(word, url))
                            webResourcesCollection.update_one({"url": url}, {"$set": {"isGetLink": True}})
                            continue

                part = result["part"]
                domain = urlparse(url).netloc
                emailList = get_access_token(domain)
                if emailList == None:
                    logging.error("获取邮箱失败:{}".format(url))
                    continue
                if emailList:
                    # 查询是否在其他part
                    for result in list(webResourcesCollection.find({"url": url})):
                        part = result["part"]
                        logging.info("url:{}有搜索到邮箱,邮箱个数:{},part:{}".format(url, len(emailList), part))
                        webResourcesCollection.remove({"url": result["url"], "part": part})
                        for num, email in enumerate(emailList):
                            # 删除以前的数据
                            result["_id"] = "3_" + part + "_" + url + "_" + str(num + 1)
                            # [status, email, firstName, lastName, sourcePage, position]
                            if not email[1].strip():
                                continue
                            result["emailStr"] = email[1].strip()
                            result["status"] = email[0]
                            result["firstName"] = email[2]
                            result["lastName"] = email[3]
                            result["sourcePage"] = email[4]
                            result["position"] = email[5]
                            result["isGetLink"] = True
                            try:
                                webResourcesCollection.insert(result)
                            except Exception as e:
                                logging.error("新增邮箱插入数据失败,原因:{}".format(traceback.format_exc()))
                else:
                    # 更新状态代表已经获取数据
                    logging.error("url:{}没有收到邮箱".format(url))
                    webResourcesCollection.update({"url": url}, {"$set": {"isGetLink": True}}, multi=True)
                time.sleep(30)


class backHeaderFooter(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            # 查询header和footer均为空的数据
            if sys.argv[1] == "debug":
                resultList = list(
                    webResourcesCollection.find(
                        {"header": "", "footer": "", "whiteNum": {"$gte": 3}, "title": {"$ne": ""},
                         "viewCount": {"$gte": 10000}}).limit(5))
            else:
                resultList = list(webResourcesCollection.find(
                    {"header": "", "footer": "", "whiteNum": {"$gte": 3}, "title": {"$ne": ""},
                     "viewCount": {"$gte": 10000}, "$or": [{"ismms": False, "part": {"$ne": "clothes"}},
                                                           {"iscmms": False, "part": "clothes"}]}).limit(1000).sort(
                    [("insertTime", pymongo.DESCENDING)]))
            if not resultList:
                logging.error("没有需要回补headers和footer的数据")
                resultList = list(webResourcesCollection.find(
                    {"header": "", "footer": "", "title": {"$ne": ""}, "viewCount": {"$gte": 10000},
                     "$or": [{"ismms": False, "part": {"$ne": "clothes"}},
                             {"iscmms": False, "part": "clothes"}]}).limit(1000))
                if not resultList:
                    time.sleep(60)
                    continue
            urls = []
            for result in resultList:
                url = result["url"]
                if url in urls:
                    continue
                urls.append(url)
                logging.info("开始处理:{}".format(url))
                self.dealUrl(url)

    def dealUrl(self, url):
        try:
            responseStr = getHtml(url, webResourcesCollection)
            if not responseStr:
                return
            try:
                selector = etree.HTML(responseStr)
            except Exception as e:
                print(e)
                selector = etree.HTML(responseStr.decode("utf-8"))
                return

            headerStr, footerStr, headerZH, footerZH, fhBlackWord, fhBlackWordCount = dealHeaderFooterInfo(selector)
            if headerStr or footerStr:
                webResourcesCollection.update({"url": url}, {"$set": {
                    "header": headerStr,
                    "footer": footerStr,
                    "headerZH": headerZH,
                    "footerZH": footerZH,
                    "fhBlackWord": fhBlackWord,
                    "fhBlackWordCount": fhBlackWordCount
                }}, multi=True)
                logging.info("新增header信息{}".format(url))
            else:
                webResourcesCollection.update({"url": url}, {"$set": {
                    "header": "没有header信息",
                    "footer": "没有footer信息",
                    "headerZH": "",
                    "footerZH": "",
                    "fhBlackWord": "",
                    "fhBlackWordCount": 0
                }}, multi=True)
                logging.error("依旧没有获取到header和footer信息:{}".format(url))
        except Exception as e:
            logging.error(traceback.format_exc())
            return


class backCountry(threading.Thread):
    def __init__(self, collection):
        threading.Thread.__init__(self)
        self.collection = collection

    def run(self):
        while True:
            resultList = list(
                self.collection.find({country: "", "whiteNum": {"$gte": 2}, "blackNum": 0, "fhBlackWordCount": 0,
                                      "$or": [{"ismms": False, "part": {"$ne": "clothes"}},
                                              {"iscmms": False, "part": "clothes"}]}).limit(1000).sort(
                    [("insertTime", pymongo.DESCENDING)]))
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
            logging.info("回补国家信息成功:{},国家:{}".format(url, countrySimilarweb))
        else:
            logging.error("依旧没有回不到国家信息,url:{}".format(url))


if __name__ == '__main__':
    # 获取lin邮箱
    linTh = GetLinMail()
    linTh.start()

    # 回补国家
    countryth = backCountry(webResourcesCollection)
    countryth.start()

    # 验证邮箱
    verifyMailth = threading.Thread(target=readMongoVerifyMail, args=())
    verifyMailth.start()

    # 回补mainRBackWhatRun信息
    WhatRunth = threading.Thread(target=mainRBackWhatRun, args=())
    WhatRunth.start()

    # web端去重mms
    readMongowebMMStripth = threading.Thread(target=readMongowebMMStrip, args=())
    readMongowebMMStripth.start()

    # 回补没有标题的数据
    titleObj = TitleBack()
    titleObj.start()

    # # 抓取web端详细信息
    webth = threading.Thread(target=getMongoUrl, args=())
    webth.start()

    # 回补所有的数据header 和 footer为空的数据
    backHeaderFooterOBJ = backHeaderFooter()
    backHeaderFooterOBJ.start()

    while True:
        if not verifyMailth.is_alive():
            # 验证邮箱
            verifyMailth = threading.Thread(target=readMongoVerifyMail, args=())
            verifyMailth.start()

        if not WhatRunth.is_alive():
            # 回补mainRBackWhatRun信息
            WhatRunth = threading.Thread(target=mainRBackWhatRun, args=())
            WhatRunth.start()

        if not readMongowebMMStripth.is_alive():
            # web端去重mms
            readMongowebMMStripth = threading.Thread(target=readMongowebMMStrip, args=())
            readMongowebMMStripth.start()

        if not titleObj.is_alive():
            # 回补没有标题的数据
            titleObj = TitleBack()
            titleObj.start()

        if not webth.is_alive():
            # 抓取web端详细信息
            webth = threading.Thread(target=getMongoUrl, args=())
            webth.start()

        if not backHeaderFooterOBJ.is_alive():
            # 回补所有的数据header 和 footer为空的数据
            backHeaderFooterOBJ = backHeaderFooter()
            backHeaderFooterOBJ.start()

        time.sleep(10)
=======
    params = {
        'grant_type': 'client_credentials',
        'client_id': '4807dc4e3735fbe657bfcaffbce0d418',
        'client_secret': '631b2b69947b0db37f27dde1bfbe6a08'
    }
    res = requests.post('https://app.snov.io/oauth/access_token', data=params)
    resText = res.text.encode('ascii', 'ignore')
    token = json.loads(resText)['access_token']
    print token
    params = {'access_token': token,
              'domain': website,
              'type': 'all',
              'limit': 100
              }
    res = requests.post('https://app.snov.io/restapi/get-domain-emails-with-info', data=params)
    print json.loads(res.text)['emails']
    for x in json.loads(res.text)['emails']:
        try:
            status = x['status']
            email = x['email']
        except:
            status, email = '', ''
        try:
            firstName = x['firstName']
            lastName = x['lastName']
        except:
            firstName, lastName = '', ''
        try:
            sourcePage = x['sourcePage']
            position = x['position']
        except:
            sourcePage, position = '', ''
        connect.append([status, email, firstName, lastName, sourcePage, position])
    return connect


def getwebsit(url):  # 获取网站信息P
    print "url--", url
    scheme = urlparse(url[0]).scheme
    domain = urlparse(url[0]).netloc

    frame_date = getcms(scheme, domain)
    print 'frame_date-----------', frame_date
    alld = getit(url[0])
    if alld[0] == 0:
        try:
            viewd = getviews(domain)
        except:
            viewd = ['none', 'none', 'none']
        time.sleep(random.randint(2, 13))
        if alld[1] > 2:
            try:
                linkdatas = get_access_token(domain)
            except:
                linkdatas = ['none']
            for linkdata in linkdatas:
                newda.writerow(url + alld + viewd + linkdata + frame_date)
        else:
            print url, alld
            newda.writerow(url + alld + viewd + frame_date)


def keyWord_url():
    list = []
    for tup in table.find({}).limit(5):
        list.append(tup['url'].split())

    return list


def black_white():
    black = []
    white = []
    with open('black_white.csv', 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        birth_header = next(csv_reader)
        for x in csv_reader:

            if x[1] == "1":
                black.append(x[0])
            elif x[1] == "0":
                white.append(x[0])

    return black, white


if __name__ == '__main__':
    translator = Translator()
    dazz = open('css.txt', 'wb')

    black = ['组织', '租赁', '总部', '资产', '资本主义', '资本市场', '注释', '住宿', '周报', '治疗', '制造商', '支票', '支付', '支持', '政府', '诊所', '账单',
             '战争游戏', '战争', '战士游戏', '在线游戏', '在线设计', '在线购物', '在线购买', '运营商', '运费', '预付', '有限公司', '游戏', '游轮', '邮报', '应用设计',
             '应用程序', '营销', '银行', '议院', '议会', '医院', '医学', '医生', '医疗', '页面未找到', '眼科', '研究院', '研究所', '学院', '学校', '信用卡',
             '新店', '协会', '校服', '销售', '下单', '物流', '维修', '维基', '网站设计', '网上购物', '网络游戏', '网店', '投资者', '投资机构', '投资', '投注',
             '听力', '天气', '所有比赛', '诉讼', '送货', '售卖', '食谱', '实验室', '设计', '商业', '商店', '商城', '商场', '色情', '赛车游戏', '赛车', '融资',
             '人道主义', '企业', '旗舰店', '皮肤科', '配送', '培训', '女孩游戏', '模拟器', '免邮', '免费游戏', '门票', '旅馆', '旅店', '铃声', '疗法', '联赛',
             '联邦法院', '理工', '理财', '乐高', '课程', '军事', '俱乐部', '拒绝访问', '酒店', '经销商', '金融邮报', '金融信息', '解剖学', '解决方案', '教育',
             '教学', '集团', '基金会', '机构', '国际', '国会', '官网', '官司', '官方', '顾问', '股市', '股票', '股份', '购物', '供应商', '公司', '工作室',
             '付钱', '付款', '分销商', '费用', '房地产', '翻译', '法院', '法务', '法律', '法典', '赌场', '动物收容所', '动物救援', '订购', '店铺', '电子商务',
             '电影', '电信', '电视台', '电商', '抵押', '待售', '贷款', '代码', '大学', '词典', '储蓄', '出租', '出售', '出版', '程序设计', '程序开发', '城市',
             '餐厅', '财政', '财务', '财产', '博物馆', '博彩', '保险', 'vpn', 'Spotify', 'SIM', 'online course', 'Flash游戏', 'AT&T',
             'apk', '404未找到', '403禁止', '503', '502', '404', '403']

    time.sleep(random.randint(2, 5))

    white = ['最新', '最具', '最佳', '最火', '最好', '最大', '主意', '指引', '指南', '指点', '指导', '值得', '折扣', '找到', '怎样', '怎能', '怎么', '原因',
             '预想', '预料', '预估', '预测', '有趣', '优质', '优惠', '优点', '应该', '寻找', '选择', '幸福', '新闻', '消息', '想象', '想法', '五大', '问答',
             '为什么', '为何', '网红', '玩家', '推荐', '推断', '推测', '体验', '体会', '特别', '讨论', '谈谈', '谈话', '所有', '收集', '收藏', '试用',
             '试穿', '使用', '实验', '时尚', '十大', '社群', '社区', '如何', '如果', '仍然', '热点', '群组', '缺点', '全部', '圈子', '去年', '区别', '奇特',
             '评论', '评价', '评分', '评测', '评比', '品味', '品尝', '盘点', '排名', '排行', '哪些', '哪里', '门户', '媒体', '论调', '论坛', '论点', '流行',
             '理由', '礼物', '礼品', '来自中国', '科技', '今年', '解析', '觉得', '交流', '建议', '见解', '见地', '检测', '技术', '记录', '集合', '火热',
             '火爆', '汇总', '汇集', '怀疑', '红人', '规格', '观点', '沟通', '感想', '感受', '感觉', '分析', '方式', '方法', '发布', '对比', '独特', '顶部',
             '点评', '第一', '等级', '导航', '大全', '答问', '搭配', '从中国', '超值', '超级', '拆箱', '拆解', '差异', '测试', '测评', '参数', '不同',
             '博客', '比较', '比价', '爆红', '包含', '安卓', 'Top', 'Best', 'Baby Gear', '10大', '九大', '9大', '8大', '八大', '七大', '7大',
             '6大', '六大', '5大', '四大', '4大', '三大', '3大', '二大', '2大', '前10', '前十', '前九', '前9', '前8', '前八', '前七', '前7',
             '前6', '前六', '前五', '前5', '前四', '前4', '前三', '前3', '前二', '前2', '10种', '十种', '九种', '9种', '8种', '八种', '七种',
             '7种', '6种', '六种', '五种', '5种', '四种', '4种', '三种', '3种', '二种', '2种', '10个', '十个', '九个', '9个', '8个', '八个',
             '七个', '7个', '6个', '六个', '五个', '5个', '四个', '4个', '三个', '3个', '二个', '2个', '2018', '2017', '2016', '2015']

    time.sleep(random.randint(4, 8))

    # listd = [lin.strip() for lin in open('yuanpings.txt','r').readlines()]

    listd = keyWord_url()

    newda = csv.writer(open('zhenjian.csv', 'ab'))
    if debugFlg == "debug":
        for trsd in listd:
            getwebsit(trsd)
    else:
        threads = [threading.Thread(target=getwebsit, args=(trsd,)) for trsd in listd]
        for t in threads:
            try:
                t.start()
            except:
                print 'error'
                continue
            while True:
                if (len(threading.enumerate()) < 15):
                    break
>>>>>>> 00b8661052c6b093b516ce99809036f3f4163d85
