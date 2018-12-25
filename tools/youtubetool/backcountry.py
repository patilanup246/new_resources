import sys

sys.path.append('./../../')
from googletrans import Translator
from db.mongodb import connectMongo
import time
import logging
import traceback

countrys = {
    'af': '南非',
    'sq': '阿尔巴尼亚',
    'am': '阿姆哈拉',
    'ar': '阿拉伯',
    'hy': '亚美尼亚',
    'az': '阿塞拜疆',
    'eu': '巴斯克',
    'be': '白俄罗斯',
    'bn': '孟加拉',
    'bs': '波斯尼亚',
    'bg': '保加利亚',
    'ca': '加泰罗尼亚',
    'ceb': '宿务',
    'zh-CN': '中国',
    'zh-TW': '台湾',
    'co': '科西嘉',
    'hr': '克罗地亚',
    'cs': '捷克',
    'da': '丹麦',
    'nl': '荷兰',
    'en': '英国',
    'eo': '世界',
    'et': '爱沙尼亚',
    'fi': '芬兰',
    'fr': '法国',
    'fy': '弗里斯兰',
    'gl': '加利西亚',
    'ka': '格鲁吉亚',
    'de': '德国',
    'el': '希腊',
    'gu': '古吉拉特',
    'ht': '海地克里奥尔',
    'ha': '豪萨',
    'haw': '夏威夷',
    'iw': '希伯来',
    'hi': '印地',
    'hmn': '苗国',
    'hu': '匈牙利',
    'is': '冰岛',
    'ig': '伊博',
    'id': '印度尼西亚',
    'ga': '爱尔兰',
    'it': '意大利',
    'ja': '日本',
    'jw': '爪哇',
    'kn': '卡纳达',
    'kk': '哈萨克',
    'km': '高棉',
    'ko': '韩国',
    'ku': '库尔德',
    'ky': '吉尔吉斯',
    'lo': '老挝',
    'la': '拉丁',
    'lv': '拉脱维亚',
    'lt': '立陶宛',
    'lb': '卢森堡',
    'mk': '马其顿',
    'mg': '马尔加什',
    'ms': '马来',
    'ml': '马拉雅拉姆',
    'mt': '马耳他',
    'mi': '毛利',
    'mr': '马拉地',
    'mn': '蒙古',
    'my': '缅甸',
    'ne': '尼泊尔',
    'no': '挪威',
    'ny': '尼杨扎',
    'ps': '普什图',
    'fa': '波斯',
    'pl': '波兰',
    'pt': '葡萄牙',
    'pa': '旁遮普',
    'ro': '罗马尼亚',
    'ru': '俄罗斯',
    'sm': '萨摩亚',
    'gd': '苏格兰盖尔',
    'sr': '塞尔维亚',
    'st': '塞索托',
    'sn': '修纳',
    'sd': '信德',
    'si': '僧伽罗',
    'sk': '斯洛伐克',
    'sl': '斯洛文尼亚',
    'so': '索马里',
    'es': '西班牙',
    'su': '巽他',
    'sw': '斯瓦希里',
    'sv': '瑞典',
    'tl': '菲律宾',
    'tg': '塔吉克',
    'ta': '泰米尔',
    'te': '泰卢固',
    'th': '泰国',
    'tr': '土耳其',
    'uk': '乌克兰',
    'ur': '乌尔都',
    'uz': '乌兹别克',
    'vi': '越南',
    'cy': '威尔士',
    'xh': '班图',
    'yi': '意第绪',
    'yo': '约鲁巴',
    'zu': '祖鲁',
}
transd = Translator()


def checkcountry(describtion, upname, url):
    country = ""
    if describtion:
        try:
            rez = transd.detect(describtion).lang
        except Exception as e:
            rez = "error"
        country = countrys.get(rez)
        if not country:
            try:
                rez = transd.detect(upname).lang
            except Exception as e:
                rez = "error"
            country = countrys.get(rez)
    else:
        try:
            rez = transd.detect(upname).lang
        except Exception as e:
            rez = "error"
        country = countrys.get(rez)
    print("国家:{}".format(country))
    if not country:
        logging.error("依旧没有获取到国家信息{}".format(url))
        # 一个一个搜索
        descUpStr = describtion + " " + upname
        for word in descUpStr.split(" "):
            try:
                rez = transd.detect(word).lang
            except Exception as e:
                rez = "error"
            country = countrys.get(rez)
            if country:
                logging.info("终于获取国家信息成功:{}".format(url))
                return country
    else:
        return country


def sendReq(describtion, upname, url):
    try:
        country = checkcountry(describtion, upname, url)
        return country
    except Exception as e:
        print(e)
        logging.error("国家信息获取失败,describtion:{},upname:{}".format(describtion, upname))
        logging.error(traceback.format_exc())
        # country = "美国"


def readMongo(collection):
    while True:
        resultList = list(collection.find({"country": ""}))
        if not resultList:
            logging.warn("没有需要回补的国家信息,collection:{}".format(collection.full_name))
            time.sleep(100)
            continue
        for result in resultList:
            time.sleep(1)
            url = result["url"]
            desc = result["descriptionUn"]
            uptitle = result["upTitle"]
            country = sendReq(desc, uptitle, url)
            if not country:
                logging.error("没有正确返回国家信息:{}".format(url))
                continue
            updateCountry(collection, country, url)


def updateCountry(collection, country, url):
    try:
        collection.update({"url": url}, {"$set": {"country": country}}, multi=True)
        logging.info("回补国家成功,url:{},country:{}".format(url, country))
    except Exception as e:
        logging.info("回补国家失败,url:{},country:{}".format(url, country))
        logging.error(e)


if __name__ == '__main__':
    db = connectMongo(True)
    collection = db["resources"]
    readMongo(collection)
