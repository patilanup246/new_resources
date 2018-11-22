# coding:utf-8
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


def get_access_token(website):  # 获取邮箱数据
    connect = []
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
