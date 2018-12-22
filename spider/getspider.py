<<<<<<< HEAD
# coding:utf-8
import collections, re
import gzip
import time
from lxml import etree
import jsonpath
import random
import ssl
import json
import traceback
import requests
from tools.getip import getIp
import logging
import random
from fake_useragent import UserAgent

from tools.useragent import USER_AGENTS
import brotli

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
from tools.request_headers import *

header = {
    #     "Connection": "keep-alive",
    #     "Accept-encoding": "gzip,deflate,br",
    #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
    # "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    # "Accept-Encoding": "gzip, deflate, br",
    # "Upgrade-Insecure-Requests": "1",
    # "Cookie": "PHPSESSID=kttboga3lp0k4fof0ctne7g4b3; tools_using=%5B%5D; __utma=196994606.1874289139.1536228312.1536228312.1536228312.1; __utmc=196994606; __utmz=196994606.1536228312.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __unam=cdad7b-165ae57c330-5dbb6632-4; __utmb=196994606.4.9.1536229341294"
=======
#!/usr/bin/env python
# coding:utf-8
import collections, re
import time
import brotli
from lxml import etree
import jsonpath
import random
import urllib, urllib2
import gzip, StringIO
import ssl
import json

ssl._create_default_https_context = ssl._create_unverified_context
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
# chrome_executable_path = r"/home/123456/web//chromedriver.exe"
# socket.setdefaulttimeout(seconds)
# users = [dazz.strip() for dazz in open('/home/123456/web/user-agent.txt', 'r').readlines()]
header = {
    "Connection": "keep-alive",
    "Accept-encoding": "gzip,deflate,br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "User-Agent": 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Accept-Encoding": "gzip, deflate",
    "upgrade-insecure-requests": "1",
    "Cookie": "PHPSESSID=kttboga3lp0k4fof0ctne7g4b3; tools_using=%5B%5D; __utma=196994606.1874289139.1536228312.1536228312.1536228312.1; __utmc=196994606; __utmz=196994606.1536228312.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __unam=cdad7b-165ae57c330-5dbb6632-4; __utmb=196994606.4.9.1536229341294"
    # "Accept-Language":"zh-CN,zh;q=0.9",
    # "Host":"noahlee.co.il",
    # "If-None-Match": "8ea519effa91a04be6280aaea8a5b1d9"
>>>>>>> 00b8661052c6b093b516ce99809036f3f4163d85
}
#

bullshit = {
    'Host': 'builtwith.com',
    'Connection': 'keep-alive',
<<<<<<< HEAD
    'User-Agent': UserAgent().random,
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    "User-Agent": random.choice(USER_AGENTS),
=======
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
>>>>>>> 00b8661052c6b093b516ce99809036f3f4163d85
    # 'Cookie': '__cfduid=dc6a15345be2832c0004eed53056e470f1532659221; _ga=GA1.2.999942773.1532659223; intercom-id-dvzew6nm=21f152a5-82e2-444e-a3fa-1f62373b66fa'
}

pinters = {
    "Host": "www.pinterest.de",
    "Connection": "keep-alive",
    "X-Pinterest-AppState": "1",
<<<<<<< HEAD
    "User-Agent": UserAgent().random,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    # "cookie": 'G_ENABLED_IDPS=google; _auth=1; csrftoken=XqfEDei23hmz0XPFHSSqfoRGeG42thN6; _pinterest_sess="TWc9PSZ4bURLR3JEdVVBNW9GQVBqNjV2ZkhIN0R3bGtBNmZ5MXRMSnZDZ01rQ3V0eWY4Z3FKaGt6dFptVytzeTdOdEpTSHBkY0NmeVlSRjFpOFRKNm1WdDVqajZnZkRjYUZTRXRISnR6Nkt3c2d4N2s1SzVNS2hVaVY4Nnk0ejdWdWVUa01BcjNiWEE3aFBkanVLek5pV0NMMnN5ZW03OXpvZDM0NnBSOGc5bXE2UTRKRW5wVW94MlRMNHJxQ2hVNnJ6VVVLR2Y2MEhsN29TeEVBTkhSVFBwTWExRlNFcVBNVzQ5MUF1dTJTZ0ZFc08wdk1td2UzYkY5WEhFTHlGWmdMQncwWFBBSTFtTVcvWHpKMDE0L04wYUdJd2tyaVJGQWFqY1Zid2lSVUQxT3RTVGZiWklZNEp2bUk3b2M2bTQwbzVKU1laQktJS3lVVWNWV3F6M3F0enNqU0pJa2xsc2VIRWhCaTBJeldHaFJxdGQ3RXB1MjNLU2FGdEFSRTFQSDQ1Z0VNajI3SGNua1FidmRDN3FXd25OMVNLc2JXNUkzWERpdjcyay9XYVNUMFJEQUFScTJNNTNETEsvTHYvYS9FTHBJbWYyTGRFTVR0NHUwVm01MUw3SGdjQ3VEaE42SGNpcUNTRGxVRVBmckw5bFZDeG1GTlFhb2V2TDZMNVJEQ2FYNFRxdmpFK3pVLy9qdTdONm83alUrekxoVllWTTByWUQyTzVpYlZVMEh4WFgwTTRVU0hqeG1UVzJiaWZ2TFNWQXNjMVgycFpZK2cwOGJTdk1QYko2UFRVY3FHRnVnUlZkSmxjMi9IaWd2ODRrMG56VXY1NHZpZ1h2VXVhbXMyOUVtSW9uU2cwQ0tCUjVEQ2o5R3NleUExZ2tJa1VudExlaS8wUHloaGYwU3JRd1NkTmttSDdaVHV2WVBmR1FSV2UyTDY4eXRMbGh3QU1FMXpDWlR0aC9ZOEMyditBQWN0bndtK0NyYzJST3ZaWEFvWWVIaFJJemd1N1ppNjhiVkhBZFYyMDNiYkNIb3BYNlduZHhyMlpBTHRCT25VcVZkVUVxQjlhSzNSTlhGckRjL3Vock5IdUNaVDRtRkdBa3pIWHkrJkNtSFJOVVRaQm1WbWo1eW9Fa0xrU3VNMVRCND0="; cm_sub=none; sessionFunnelEventLogged=1; bei=false'
=======
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "cookie": 'G_ENABLED_IDPS=google; _auth=1; csrftoken=XqfEDei23hmz0XPFHSSqfoRGeG42thN6; _pinterest_sess="TWc9PSZ4bURLR3JEdVVBNW9GQVBqNjV2ZkhIN0R3bGtBNmZ5MXRMSnZDZ01rQ3V0eWY4Z3FKaGt6dFptVytzeTdOdEpTSHBkY0NmeVlSRjFpOFRKNm1WdDVqajZnZkRjYUZTRXRISnR6Nkt3c2d4N2s1SzVNS2hVaVY4Nnk0ejdWdWVUa01BcjNiWEE3aFBkanVLek5pV0NMMnN5ZW03OXpvZDM0NnBSOGc5bXE2UTRKRW5wVW94MlRMNHJxQ2hVNnJ6VVVLR2Y2MEhsN29TeEVBTkhSVFBwTWExRlNFcVBNVzQ5MUF1dTJTZ0ZFc08wdk1td2UzYkY5WEhFTHlGWmdMQncwWFBBSTFtTVcvWHpKMDE0L04wYUdJd2tyaVJGQWFqY1Zid2lSVUQxT3RTVGZiWklZNEp2bUk3b2M2bTQwbzVKU1laQktJS3lVVWNWV3F6M3F0enNqU0pJa2xsc2VIRWhCaTBJeldHaFJxdGQ3RXB1MjNLU2FGdEFSRTFQSDQ1Z0VNajI3SGNua1FidmRDN3FXd25OMVNLc2JXNUkzWERpdjcyay9XYVNUMFJEQUFScTJNNTNETEsvTHYvYS9FTHBJbWYyTGRFTVR0NHUwVm01MUw3SGdjQ3VEaE42SGNpcUNTRGxVRVBmckw5bFZDeG1GTlFhb2V2TDZMNVJEQ2FYNFRxdmpFK3pVLy9qdTdONm83alUrekxoVllWTTByWUQyTzVpYlZVMEh4WFgwTTRVU0hqeG1UVzJiaWZ2TFNWQXNjMVgycFpZK2cwOGJTdk1QYko2UFRVY3FHRnVnUlZkSmxjMi9IaWd2ODRrMG56VXY1NHZpZ1h2VXVhbXMyOUVtSW9uU2cwQ0tCUjVEQ2o5R3NleUExZ2tJa1VudExlaS8wUHloaGYwU3JRd1NkTmttSDdaVHV2WVBmR1FSV2UyTDY4eXRMbGh3QU1FMXpDWlR0aC9ZOEMyditBQWN0bndtK0NyYzJST3ZaWEFvWWVIaFJJemd1N1ppNjhiVkhBZFYyMDNiYkNIb3BYNlduZHhyMlpBTHRCT25VcVZkVUVxQjlhSzNSTlhGckRjL3Vock5IdUNaVDRtRkdBa3pIWHkrJkNtSFJOVVRaQm1WbWo1eW9Fa0xrU3VNMVRCND0="; cm_sub=none; sessionFunnelEventLogged=1; bei=false'
>>>>>>> 00b8661052c6b093b516ce99809036f3f4163d85
}

pinterest = {
    "Host": "www.pinterest.de",
    "Connection": "keep-alive",
    "Origin": "https://www.pinterest.de",
    "X-APP-VERSION": "78eaeea",
    "X-Pinterest-AppState": "active",
<<<<<<< HEAD
    "User-Agent": UserAgent().random,
=======
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36",
>>>>>>> 00b8661052c6b093b516ce99809036f3f4163d85
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json, text/javascript, */*, q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "X-CSRFToken": "XqfEDei23hmz0XPFHSSqfoRGeG42thN6",
    "Referer": "https://www.pinterest.de/",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
<<<<<<< HEAD
    # "cookie": 'G_ENABLED_IDPS=google; _auth=1; csrftoken=XqfEDei23hmz0XPFHSSqfoRGeG42thN6; _pinterest_sess="TWc9PSZ4bURLR3JEdVVBNW9GQVBqNjV2ZkhIN0R3bGtBNmZ5MXRMSnZDZ01rQ3V0eWY4Z3FKaGt6dFptVytzeTdOdEpTSHBkY0NmeVlSRjFpOFRKNm1WdDVqajZnZkRjYUZTRXRISnR6Nkt3c2d4N2s1SzVNS2hVaVY4Nnk0ejdWdWVUa01BcjNiWEE3aFBkanVLek5pV0NMMnN5ZW03OXpvZDM0NnBSOGc5bXE2UTRKRW5wVW94MlRMNHJxQ2hVNnJ6VVVLR2Y2MEhsN29TeEVBTkhSVFBwTWExRlNFcVBNVzQ5MUF1dTJTZ0ZFc08wdk1td2UzYkY5WEhFTHlGWmdMQncwWFBBSTFtTVcvWHpKMDE0L04wYUdJd2tyaVJGQWFqY1Zid2lSVUQxT3RTVGZiWklZNEp2bUk3b2M2bTQwbzVKU1laQktJS3lVVWNWV3F6M3F0enNqU0pJa2xsc2VIRWhCaTBJeldHaFJxdGQ3RXB1MjNLU2FGdEFSRTFQSDQ1Z0VNajI3SGNua1FidmRDN3FXd25OMVNLc2JXNUkzWERpdjcyay9XYVNUMFJEQUFScTJNNTNETEsvTHYvYS9FTHBJbWYyTGRFTVR0NHUwVm01MUw3SGdjQ3VEaE42SGNpcUNTRGxVRVBmckw5bFZDeG1GTlFhb2V2TDZMNVJEQ2FYNFRxdmpFK3pVLy9qdTdONm83alUrekxoVllWTTByWUQyTzVpYlZVMEh4WFgwTTRVU0hqeG1UVzJiaWZ2TFNWQXNjMVgycFpZK2cwOGJTdk1QYko2UFRVY3FHRnVnUlZkSmxjMi9IaWd2ODRrMG56VXY1NHZpZ1h2VXVhbXMyOUVtSW9uU2cwQ0tCUjVEQ2o5R3NleUExZ2tJa1VudExlaS8wUHloaGYwU3JRd1NkTmttSDdaVHV2WVBmR1FSV2UyTDY4eXRMbGh3QU1FMXpDWlR0aC9ZOEMyditBQWN0bndtK0NyYzJST3ZaWEFvWWVIaFJJemd1N1ppNjhiVkhBZFYyMDNiYkNIb3BYNlduZHhyMlpBTHRCT25VcVZkVUVxQjlhSzNSTlhGckRjL3Vock5IdUNaVDRtRkdBa3pIWHkrJkNtSFJOVVRaQm1WbWo1eW9Fa0xrU3VNMVRCND0="; cm_sub=none; sessionFunnelEventLogged=1; bei=false'
=======
    "cookie": 'G_ENABLED_IDPS=google; _auth=1; csrftoken=XqfEDei23hmz0XPFHSSqfoRGeG42thN6; _pinterest_sess="TWc9PSZ4bURLR3JEdVVBNW9GQVBqNjV2ZkhIN0R3bGtBNmZ5MXRMSnZDZ01rQ3V0eWY4Z3FKaGt6dFptVytzeTdOdEpTSHBkY0NmeVlSRjFpOFRKNm1WdDVqajZnZkRjYUZTRXRISnR6Nkt3c2d4N2s1SzVNS2hVaVY4Nnk0ejdWdWVUa01BcjNiWEE3aFBkanVLek5pV0NMMnN5ZW03OXpvZDM0NnBSOGc5bXE2UTRKRW5wVW94MlRMNHJxQ2hVNnJ6VVVLR2Y2MEhsN29TeEVBTkhSVFBwTWExRlNFcVBNVzQ5MUF1dTJTZ0ZFc08wdk1td2UzYkY5WEhFTHlGWmdMQncwWFBBSTFtTVcvWHpKMDE0L04wYUdJd2tyaVJGQWFqY1Zid2lSVUQxT3RTVGZiWklZNEp2bUk3b2M2bTQwbzVKU1laQktJS3lVVWNWV3F6M3F0enNqU0pJa2xsc2VIRWhCaTBJeldHaFJxdGQ3RXB1MjNLU2FGdEFSRTFQSDQ1Z0VNajI3SGNua1FidmRDN3FXd25OMVNLc2JXNUkzWERpdjcyay9XYVNUMFJEQUFScTJNNTNETEsvTHYvYS9FTHBJbWYyTGRFTVR0NHUwVm01MUw3SGdjQ3VEaE42SGNpcUNTRGxVRVBmckw5bFZDeG1GTlFhb2V2TDZMNVJEQ2FYNFRxdmpFK3pVLy9qdTdONm83alUrekxoVllWTTByWUQyTzVpYlZVMEh4WFgwTTRVU0hqeG1UVzJiaWZ2TFNWQXNjMVgycFpZK2cwOGJTdk1QYko2UFRVY3FHRnVnUlZkSmxjMi9IaWd2ODRrMG56VXY1NHZpZ1h2VXVhbXMyOUVtSW9uU2cwQ0tCUjVEQ2o5R3NleUExZ2tJa1VudExlaS8wUHloaGYwU3JRd1NkTmttSDdaVHV2WVBmR1FSV2UyTDY4eXRMbGh3QU1FMXpDWlR0aC9ZOEMyditBQWN0bndtK0NyYzJST3ZaWEFvWWVIaFJJemd1N1ppNjhiVkhBZFYyMDNiYkNIb3BYNlduZHhyMlpBTHRCT25VcVZkVUVxQjlhSzNSTlhGckRjL3Vock5IdUNaVDRtRkdBa3pIWHkrJkNtSFJOVVRaQm1WbWo1eW9Fa0xrU3VNMVRCND0="; cm_sub=none; sessionFunnelEventLogged=1; bei=false'
>>>>>>> 00b8661052c6b093b516ce99809036f3f4163d85
}

snov = {
    'Host': 'app.snov.io',
    'Connection': 'keep-alive',
    'Origin': 'chrome-extension://einnffiilpmgldkapbikhkeicohlaapj',
<<<<<<< HEAD
    "User-Agent": UserAgent().random,
=======
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
>>>>>>> 00b8661052c6b093b516ce99809036f3f4163d85
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
<<<<<<< HEAD
    # 'Cookie': 'lang=eyJpdiI6IlwvcFBBYzduZW1KUHRoRDNvMFIrbU1nPT0iLCJ2YWx1ZSI6IlZ0UXRGbzllUG40Y3Vhc0d6WGpGMHc9PSIsIm1hYyI6IjZmMzkwNzExMGFiYWFkNDRjNDViYTU3ZDYyYzcyZWY1OWJjYmM4YmE2MWQ1OGUxYjE0YjQ5MjdlMzNmNDgzMjYifQ%3D%3D; _ga=GA1.3.1065387345.1533257221; _gid=GA1.3.1943155483.1533257221; _ga=GA1.2.1065387345.1533257221; _gid=GA1.2.1943155483.1533257221; all_visits=24db7a08-6531-45c5-8327-c5d36a5ab194; device-source=https://app.snov.io/prospects#; device-referrer=https://accounts.google.com/signin/oauth/oauthchooseaccount?client_id=225538090989-s9vlbc05cblpq6j9abps7v2ic5nl4vd1.apps.googleusercontent.com&as=9PaWiyzE0OLIaalA2VeXfA&destination=https%3A%2F%2Fapp.snov.io&approval_state=!ChRvUG5qQTNKSFpkR1lZeWU4cFZsMRIfODFfZ0d1WWVvRllSY01pNW5wOWhjSFRQc0JmVVR4WQ%E2%88%99ANKMe1QAAAAAW2T3xOnH2FbAR9b9Lv1wynIfZl-MMmrq&oauthgdpr=1&xsrfsig=AHgIfE8fh0T7VP5j3BcNdS3fd9BMfVr-7w&flowName=GeneralOAuthFlow; cookiePolicyPolitics=1; helpcrunch-device={"id":4485093,"secret":"4rbBM09maFTkgDX12LrDsZxVHjxpkZItCS+efM6bNWkXU/oipgxzYXXFjHhlivvuU87OAy3hB2A+HqrxpTDuMA==","sessions":9}; userId=6ca73491766f5475be2f6b8ada520a22f397ee9ea7f625cd85764ea45579b15b; token=4c83d1c8b5c670c39fde80dfa5948af1; selector=da43d12295a6cdcdc23b69c6b6284454; XSRF-TOKEN=eyJpdiI6ImNneEYyTERYOHpJdGJzc3JUcWdhdGc9PSIsInZhbHVlIjoidGF1ekVSVjNCek1PbEJlWU5EY3FkNDNBUFhOXC9uSDdFb2NMb0hES00rWEdNXC9QcVZaTXFrMzFQekRzU3JremJlUFwvaTNPbm1FaGNvMlEwZkdzaUp5MEE9PSIsIm1hYyI6IjBmMTIyNmZjYmRiMGNlM2I4NWY2ZmQ5ZDZhNTFmNDQyNTRjOGVjZjY2NjUzYWFiNTJjYjYyZjFlMGMxOGVkNWQifQ%3D%3D; snov_io=eyJpdiI6IkJsanpmNStsYk5zNFBIZ0ZsUlUzTWc9PSIsInZhbHVlIjoiblNuZ2dkNmJBYU5oYWV6eHh2MDNNMURXdUNEOGlBb2JxXC8rc1VkeTdvYmFYRDhcL2wyQUNKOEtCYTVOajR4SWZqZmtyMkFpODFLXC9IZHN0cldaZXErdmc9PSIsIm1hYyI6IjIwZWRjMTZhMWU1NDBkMjI0M2IxZTJlMjQ1OTMyZWM0NGYzZThlMzc1MGEzZWIwY2E3NWU3NTFhM2RkZTQwMTgifQ%3D%3D'
}
alexaheader = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "AlexaToolbar-ALX_NS_PH": "AlexaToolbar/alx-4.0.3",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    # "Cookie": "rpt=%21; _ga=GA1.2.1749063631.1543198289; _gid=GA1.2.1035753863.1543198289; lv=1543211196",
    "Host": "www.alexa.com",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": UserAgent().random
}


def getSimilarwebInfo(url, header):
    html = ""
    for i in range(3):
        try:
            response = requests.get(url=url, headers=header, timeout=8, verify=False, proxies=getIp())
            if response.status_code == 200:
                html = response.text
                break
        except Exception as e:
            if repr(e).find("timed out") > 0:
                logging.error("请求超时{}次,url:{}".format(i + 1, url))
            else:
                logging.error(e)
            html = ""
        if html:
            break
    return html


def sendRequestalexa(url):
    html = ""
    for i in range(3):
        try:
            response = requests.get(url=url, headers=alexaheader, timeout=8, verify=False, proxies=getIp())
            if response.status_code == 200:
                html = response.text
                break
        except Exception as e:
            if repr(e).find("timed out") > 0:
                logging.error("请求超时{}次,url:{}".format(i + 1, url))
            else:
                logging.error(e)
            html = ""
    return html


def getHtml(url, collection):
    formerUrl = url
    url = url + "/"
    html = ""
    for i in range(3):
        try:
            response = requests.get(url=url, headers=header, timeout=20, verify=False)
            response.encoding = "utf-8"
            if response.status_code == 200:
                html = response.content
                break
            else:
                if str(response.status_code).startswith("4") or str(response.status_code).startswith("5"):
                    logging.error("访问页面详情的状态码是:{},url:{}".format(response.status_code, url))
                    result = collection.find_one({"url": formerUrl})
                    if result:
                        collection.remove({"url": formerUrl})
                    break
                logging.error("访问页面详情的状态码是:{},url:{}".format(response.status_code, url))
        except Exception as e:
            if repr(e).find("timed out") > 0:
                logging.error("请求超时{}次,url:{}".format(i + 1, url))
            else:
                result = collection.find_one({"url": formerUrl})
                if result:
                    collection.remove({"url": formerUrl})
                break
            html = ""
    return html


def sendRequestWhatrun(url, data, headers):
    apps = ""
    for i in range(2):
        responseStr = ""
        try:
            response = requests.post(url=url, data=data, headers=headers, verify=False, timeout=30,
                                     proxies=getIp()
                                     )
            if response.status_code == 200:
                if response.headers["Content-Encoding"] == "br":
                    responseStr = brotli.decompress(response.content).decode()
                elif response.headers["Content-Encoding"] == "gzip":
                    responseStr = gzip.decompress(response.content).decode()
                else:
                    responseStr = response.text
            else:
                logging.info("状态码为:{}".format(response.status_code))
        except Exception as e:
            if repr(e).find("timed out") > 0:
                logging.error("请求超时{}次,url:{}".format(i + 1, url))
            else:
                logging.error(e)
            responseStr = ""
        try:
            responseDict = json.loads(responseStr)
            if responseDict["status"]:
                return responseDict["apps"]
            else:
                # 代表返回的数据状态为false
                apps = responseDict.get("apps")
                if apps:
                    return apps
                else:
                    logging.error("返回状态false,{}".format(responseDict))
        except Exception as e:
            logging.error(e)
    return apps


def getViewInfo(domain):  # 获取网站流量相关数据
    viewCount, country, percent, relateLinkSimilarSites = 0, "", "", ""
    try:
        url = 'https://api.similarweb.com/v1/SimilarWebAddon/' + str(domain).replace('www.', '') + '/all'
        data = getSimilarwebInfo(url, similarweb)
        html = json.loads(data)
        try:
            viewCount = int(jsonpath.jsonpath(html, "$..Visits")[0])
        except:
            viewCount = 0
        try:
            count = jsonpath.jsonpath(html, "$..TopCountryShares")[0][0]
            country = countrycode[str(count['Country'])]
        except Exception as e:
            count = {}
            country = ''
        try:
            percent = count['Value']
            percent = '%.2f%%' % (percent * 100)
        except:
            percent = 0
        relateLinkSimilarSitesList = jsonpath.jsonpath(html, "$..SimilarSites..Site")
        if relateLinkSimilarSitesList:
            relateLinkSimilarSites = "\n".join(relateLinkSimilarSitesList).strip()
        else:
            relateLinkSimilarSites = ""
    except Exception as e:
        logging.error(e)
    logging.info("国家:[{}],观看量:[{}],百分比:[{}],域名:{}".format(country, viewCount, percent, domain))
    return viewCount, country, percent, relateLinkSimilarSites


if __name__ == '__main__':
    pass
=======
    'Cookie': 'lang=eyJpdiI6IlwvcFBBYzduZW1KUHRoRDNvMFIrbU1nPT0iLCJ2YWx1ZSI6IlZ0UXRGbzllUG40Y3Vhc0d6WGpGMHc9PSIsIm1hYyI6IjZmMzkwNzExMGFiYWFkNDRjNDViYTU3ZDYyYzcyZWY1OWJjYmM4YmE2MWQ1OGUxYjE0YjQ5MjdlMzNmNDgzMjYifQ%3D%3D; _ga=GA1.3.1065387345.1533257221; _gid=GA1.3.1943155483.1533257221; _ga=GA1.2.1065387345.1533257221; _gid=GA1.2.1943155483.1533257221; all_visits=24db7a08-6531-45c5-8327-c5d36a5ab194; device-source=https://app.snov.io/prospects#; device-referrer=https://accounts.google.com/signin/oauth/oauthchooseaccount?client_id=225538090989-s9vlbc05cblpq6j9abps7v2ic5nl4vd1.apps.googleusercontent.com&as=9PaWiyzE0OLIaalA2VeXfA&destination=https%3A%2F%2Fapp.snov.io&approval_state=!ChRvUG5qQTNKSFpkR1lZeWU4cFZsMRIfODFfZ0d1WWVvRllSY01pNW5wOWhjSFRQc0JmVVR4WQ%E2%88%99ANKMe1QAAAAAW2T3xOnH2FbAR9b9Lv1wynIfZl-MMmrq&oauthgdpr=1&xsrfsig=AHgIfE8fh0T7VP5j3BcNdS3fd9BMfVr-7w&flowName=GeneralOAuthFlow; cookiePolicyPolitics=1; helpcrunch-device={"id":4485093,"secret":"4rbBM09maFTkgDX12LrDsZxVHjxpkZItCS+efM6bNWkXU/oipgxzYXXFjHhlivvuU87OAy3hB2A+HqrxpTDuMA==","sessions":9}; userId=6ca73491766f5475be2f6b8ada520a22f397ee9ea7f625cd85764ea45579b15b; token=4c83d1c8b5c670c39fde80dfa5948af1; selector=da43d12295a6cdcdc23b69c6b6284454; XSRF-TOKEN=eyJpdiI6ImNneEYyTERYOHpJdGJzc3JUcWdhdGc9PSIsInZhbHVlIjoidGF1ekVSVjNCek1PbEJlWU5EY3FkNDNBUFhOXC9uSDdFb2NMb0hES00rWEdNXC9QcVZaTXFrMzFQekRzU3JremJlUFwvaTNPbm1FaGNvMlEwZkdzaUp5MEE9PSIsIm1hYyI6IjBmMTIyNmZjYmRiMGNlM2I4NWY2ZmQ5ZDZhNTFmNDQyNTRjOGVjZjY2NjUzYWFiNTJjYjYyZjFlMGMxOGVkNWQifQ%3D%3D; snov_io=eyJpdiI6IkJsanpmNStsYk5zNFBIZ0ZsUlUzTWc9PSIsInZhbHVlIjoiblNuZ2dkNmJBYU5oYWV6eHh2MDNNMURXdUNEOGlBb2JxXC8rc1VkeTdvYmFYRDhcL2wyQUNKOEtCYTVOajR4SWZqZmtyMkFpODFLXC9IZHN0cldaZXErdmc9PSIsIm1hYyI6IjIwZWRjMTZhMWU1NDBkMjI0M2IxZTJlMjQ1OTMyZWM0NGYzZThlMzc1MGEzZWIwY2E3NWU3NTFhM2RkZTQwMTgifQ%3D%3D'
}


def spider(url, ip):
    httpproxy_handler = urllib2.ProxyHandler({'http': ip})
    nullproxy_handler = urllib2.ProxyHandler({})
    proxySwitch = True
    if proxySwitch:
        opener = urllib2.build_opener(httpproxy_handler)
    else:
        opener = urllib2.build_opener(nullproxy_handler)
    pdas = urllib2.Request(url, headers=header)
    time.sleep(random.randint(3, 7))
    sd = opener.open(pdas, timeout=5)
    time.sleep(random.randint(3, 7))
    if sd.info().get('Content-Encoding') == 'gzip':
        html = gzip.GzipFile(fileobj=StringIO.StringIO(sd.read()), mode="r").read()
    elif sd.info().get('Content-Encoding') == 'br':
        html = brotli.decompress(sd.read())
    else:
        html = sd.read()
    opener.close()
    return html


def spiderd(url, data):
    try:
        sd = urllib2.urlopen(urllib2.Request(url, data=data, headers=pinterest), timeout=5)
        time.sleep(random.randint(3, 6))
        if sd.info().get('Content-Encoding') == 'gzip':
            html = gzip.GzipFile(fileobj=StringIO.StringIO(sd.read()), mode="r").read()
        elif sd.info().get('Content-Encoding') == 'br':
            html = brotli.decompress(sd.read())
        else:
            html = sd.read()
    except urllib2.HTTPError, e:
        if e.info().get('Content-Encoding') == 'gzip':
            html = gzip.GzipFile(fileobj=StringIO.StringIO(e.read()), mode="r").read()
        elif e.info().get('Content-Encoding') == 'br':
            html = brotli.decompress(e.read())
        else:
            html = e.read()
    return html


def spida(url, header):
    try:
        htmla = urllib2.Request(url, headers=header)
        time.sleep(random.randint(2, 4))
        sd = urllib2.urlopen(htmla)
        time.sleep(random.randint(2, 4))
        if sd.info().get('Content-Encoding') == 'gzip':
            html = gzip.GzipFile(fileobj=StringIO.StringIO(sd.read()), mode="r").read()
        elif sd.info().get('Content-Encoding') == 'br':
            html = brotli.decompress(sd.read())
        else:
            html = sd.read()
    except urllib2.HTTPError, e:
        if e.info().get('Content-Encoding') == 'gzip':
            html = gzip.GzipFile(fileobj=StringIO.StringIO(e.read()), mode="r").read()
        elif e.info().get('Content-Encoding') == 'br':
            html = brotli.decompress(e.read())
        else:
            html = e.read()
    return html


def spidno(url):
    try:
        htmla = urllib2.Request(url, headers=header)
        print htmla
        time.sleep(random.randint(2, 3))
        sd = urllib2.urlopen(htmla)
        time.sleep(random.randint(2, 3))
        if sd.info().get('Content-Encoding') == 'gzip':
            html = gzip.GzipFile(fileobj=StringIO.StringIO(sd.read()), mode="r").read()
        elif sd.info().get('Content-Encoding') == 'br':
            html = brotli.decompress(sd.read())
        else:
            html = sd.read()
    except urllib2.HTTPError, e:
        if e.info().get('Content-Encoding') == 'gzip':
            html = gzip.GzipFile(fileobj=StringIO.StringIO(e.read()), mode="r").read()
        elif e.info().get('Content-Encoding') == 'br':
            html = brotli.decompress(e.read())
        else:
            html = e.read()
    return html


def getip():
    try:
        # psd = selesp('http://www.data5u.com/free/index.shtml')
        psd = selesp('http://www.data5u.com/free/gwpt/index.shtml')
        # print psd
        dats = etree.HTML(psd)
        ips = dats.xpath('//html/body/div[5]/ul/li[2]/ul/span[1]/li/text()')
        oust = dats.xpath('//html/body/div[5]/ul/li[2]/ul/span[2]/li/text()')
        pds = open('ipport.txt', 'wb')
        for xin in range(1, len(ips)):
            dat = ips[xin] + ':' + oust[xin]
            pds.writelines(dat + '\n')
        pds.close()
    except:
        print 'errs'


def allspider(url, data, head):
    try:

        sd = urllib2.urlopen(urllib2.Request(url, data=data, headers=head), timeout=8)
        time.sleep(random.randint(5, 9))
        if sd.info().get('Content-Encoding') == 'gzip':
            html = gzip.GzipFile(fileobj=StringIO.StringIO(sd.read()), mode="r").read()
        elif sd.info().get('Content-Encoding') == 'br':
            html = brotli.decompress(sd.read())
        else:
            html = sd.read()
    except urllib2.HTTPError, e:
        if e.info().get('Content-Encoding') == 'gzip':
            html = gzip.GzipFile(fileobj=StringIO.StringIO(e.read()), mode="r").read()
        elif e.info().get('Content-Encoding') == 'br':
            html = brotli.decompress(e.read())
        else:
            html = e.read()
    return html


def spiders(url, header, ip):
    httpproxy_handler = urllib2.ProxyHandler({"http": ip})
    nullproxy_handler = urllib2.ProxyHandler({})
    proxySwitch = True
    if proxySwitch:
        opener = urllib2.build_opener(httpproxy_handler)
    else:
        opener = urllib2.build_opener(nullproxy_handler)
    pdas = urllib2.Request(url, headers=header)
    time.sleep(random.randint(3, 7))
    sd = opener.open(pdas, timeout=7)
    time.sleep(random.randint(3, 7))
    if sd.info().get('Content-Encoding') == 'gzip':
        html = gzip.GzipFile(fileobj=StringIO.StringIO(sd.read()), mode="r").read()
    elif sd.info().get('Content-Encoding') == 'br':
        html = brotli.decompress(sd.read())
    else:
        html = sd.read()
    opener.close()
    return html


def spiderss(url, data, header, ip):
    httpproxy_handler = urllib2.ProxyHandler({"http": ip})
    nullproxy_handler = urllib2.ProxyHandler({})
    proxySwitch = True
    if proxySwitch:
        opener = urllib2.build_opener(httpproxy_handler)
    else:
        opener = urllib2.build_opener(nullproxy_handler)
    pdas = urllib2.Request(url, data=data, headers=header)
    time.sleep(random.randint(3, 7))
    sd = opener.open(pdas, timeout=7)
    time.sleep(random.randint(3, 7))
    if sd.info().get('Content-Encoding') == 'gzip':
        html = gzip.GzipFile(fileobj=StringIO.StringIO(sd.read()), mode="r").read()
    elif sd.info().get('Content-Encoding') == 'br':
        html = brotli.decompress(sd.read())
    else:
        html = sd.read()
    opener.close()
    return html


def getmail(url):
    emails = []
    unemails = []
    text = 'domain=' + url
    html = allspider('https://app.snov.io/api/getContacts', text, snov)
    jsondata = json.loads(html)
    datalist = jsondata['list']
    for x in datalist:
        if x["verify_stat"] == 1:
            emails.append(x['email'])
        if x["verify_stat"] == 0:
            unemails.append(x['email'])
    one = [','.join(emails), ','.join(unemails)]
    return one


def getrullink(url):
    dazz = urllib2.Request(url, headers=header)
    try:
        result = urllib2.urlopen(dazz, timeout=7)
        yrkd = str(result.geturl())
    except:
        yrkd = url
    return yrkd


def getcmsd(url):
    li = ['eCommerce', 'Payment']
    lid = []
    urld = 'https://builtwith.com/mobile.aspx?' + url
    htm = spida(urld, bullshit)
    data = etree.HTML(htm)
    name = data.xpath('//h6/text()')
    for x in li:
        if x in name:
            lid.append(x)
    return lid


if __name__ == '__main__':
    # print getcms('https://www.taobao.com')
    # print spide('https://www.facebook.com/hamka.ryana')
    for x in range(0, 500):
        getip()
        time.sleep(random.randint(50, 80))
        # print header
        # print spider('https://www.google.com/search?safe=active&source=hp&q=תאורת+LED&start=0','139.162.235.163:31028')
        # print selesp('http://noahlee.co.il')
>>>>>>> 00b8661052c6b093b516ce99809036f3f4163d85
