import random

from fake_useragent import UserAgent

from tools.useragent import USER_AGENTS

# whatrunHeaders = {
#     'Host': 'www.whatruns.com',
#     'Connection': 'keep-alive',
#     "User-Agent": UserAgent().random,
#     "Content-type": "application/x-www-form-urlencoded",
#     'Accept': '*/*',
#     'Accept-Encoding': 'gzip,deflate,br',
#     'Accept-Language': 'zh-CN,zh;q=0.9',
#     'Cookie': "__cfduid=ddb5f0de40238be38d1553f1b889485381542870547"
# }
whatrunHeaders = {
    "Host": "www.whatruns.com",
    "Connection": "keep-alive",
    "Content-Length": "195",
    "Origin": "chrome-extension://cmkdbmfndkfgebldhnkbfhlneefdaaip",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
    "Content-type": "application/x-www-form-urlencoded",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cookie": "__cfduid=ddb5f0de40238be38d1553f1b889485381542870547"

}

adasd = {
    'Host': 'w3techs.com',
    'Connection': 'keep-alive',
    "User-Agent": UserAgent().random,
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
    "User-Agent": UserAgent().random,
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    # 'cookies': '_ga=GA1.3.1147932913.1532412771; 1P_JAR=2018-8-3-10; NID=135=l-tjMuDl2WviixSLeXKVxYJBimmDDqXAHQjdP-q6fYVhwBwJmVsReuWJJuFxgp15T6j-LheIoapHzJH0UnSD0WVCv3yfSBQPOEDO-zz-nmd_CzSK7GrLYmAjQZvnVI1IU1TJ0bLHf9uxwOJzWw',
}

similarweb = {
    "Host": "api.similarweb.com",
    "Connection": "keep-alive",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "User-Agent": UserAgent().random,
    "Accept-Encoding": "deflate",
    "Accept-Language": "zh-CN,zh;q=0.9"
}

li = [
    ['//footer/descendant::a/@href', ''],
    ['//header/descendant::a/@href', ''],
    ['//a/@href', '  ']
]

maid = ['//footer/descendant::*/text()', '//header/descendant::*/text()']

whatrunsheader = {
    "Connection": "keep-alive",
    "Accept-encoding": "gzip,deflate,br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "User-Agent": UserAgent().random,
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Accept-Encoding": "gzip, deflate",
    "upgrade-insecure-requests": "1",
    "Cookie": "PHPSESSID=kttboga3lp0k4fof0ctne7g4b3; tools_using=%5B%5D; __utma=196994606.1874289139.1536228312.1536228312.1536228312.1; __utmc=196994606; __utmz=196994606.1536228312.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __unam=cdad7b-165ae57c330-5dbb6632-4; __utmb=196994606.4.9.1536229341294"
    # "Accept-Language":"zh-CN,zh;q=0.9",
    # "Host":"noahlee.co.il",
    # "If-None-Match": "8ea519effa91a04be6280aaea8a5b1d9"
}
