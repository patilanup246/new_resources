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
}
#

bullshit = {
    'Host': 'builtwith.com',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    # 'Cookie': '__cfduid=dc6a15345be2832c0004eed53056e470f1532659221; _ga=GA1.2.999942773.1532659223; intercom-id-dvzew6nm=21f152a5-82e2-444e-a3fa-1f62373b66fa'
}

pinters = {
    "Host": "www.pinterest.de",
    "Connection": "keep-alive",
    "X-Pinterest-AppState": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "cookie": 'G_ENABLED_IDPS=google; _auth=1; csrftoken=XqfEDei23hmz0XPFHSSqfoRGeG42thN6; _pinterest_sess="TWc9PSZ4bURLR3JEdVVBNW9GQVBqNjV2ZkhIN0R3bGtBNmZ5MXRMSnZDZ01rQ3V0eWY4Z3FKaGt6dFptVytzeTdOdEpTSHBkY0NmeVlSRjFpOFRKNm1WdDVqajZnZkRjYUZTRXRISnR6Nkt3c2d4N2s1SzVNS2hVaVY4Nnk0ejdWdWVUa01BcjNiWEE3aFBkanVLek5pV0NMMnN5ZW03OXpvZDM0NnBSOGc5bXE2UTRKRW5wVW94MlRMNHJxQ2hVNnJ6VVVLR2Y2MEhsN29TeEVBTkhSVFBwTWExRlNFcVBNVzQ5MUF1dTJTZ0ZFc08wdk1td2UzYkY5WEhFTHlGWmdMQncwWFBBSTFtTVcvWHpKMDE0L04wYUdJd2tyaVJGQWFqY1Zid2lSVUQxT3RTVGZiWklZNEp2bUk3b2M2bTQwbzVKU1laQktJS3lVVWNWV3F6M3F0enNqU0pJa2xsc2VIRWhCaTBJeldHaFJxdGQ3RXB1MjNLU2FGdEFSRTFQSDQ1Z0VNajI3SGNua1FidmRDN3FXd25OMVNLc2JXNUkzWERpdjcyay9XYVNUMFJEQUFScTJNNTNETEsvTHYvYS9FTHBJbWYyTGRFTVR0NHUwVm01MUw3SGdjQ3VEaE42SGNpcUNTRGxVRVBmckw5bFZDeG1GTlFhb2V2TDZMNVJEQ2FYNFRxdmpFK3pVLy9qdTdONm83alUrekxoVllWTTByWUQyTzVpYlZVMEh4WFgwTTRVU0hqeG1UVzJiaWZ2TFNWQXNjMVgycFpZK2cwOGJTdk1QYko2UFRVY3FHRnVnUlZkSmxjMi9IaWd2ODRrMG56VXY1NHZpZ1h2VXVhbXMyOUVtSW9uU2cwQ0tCUjVEQ2o5R3NleUExZ2tJa1VudExlaS8wUHloaGYwU3JRd1NkTmttSDdaVHV2WVBmR1FSV2UyTDY4eXRMbGh3QU1FMXpDWlR0aC9ZOEMyditBQWN0bndtK0NyYzJST3ZaWEFvWWVIaFJJemd1N1ppNjhiVkhBZFYyMDNiYkNIb3BYNlduZHhyMlpBTHRCT25VcVZkVUVxQjlhSzNSTlhGckRjL3Vock5IdUNaVDRtRkdBa3pIWHkrJkNtSFJOVVRaQm1WbWo1eW9Fa0xrU3VNMVRCND0="; cm_sub=none; sessionFunnelEventLogged=1; bei=false'
}

pinterest = {
    "Host": "www.pinterest.de",
    "Connection": "keep-alive",
    "Origin": "https://www.pinterest.de",
    "X-APP-VERSION": "78eaeea",
    "X-Pinterest-AppState": "active",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json, text/javascript, */*, q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "X-CSRFToken": "XqfEDei23hmz0XPFHSSqfoRGeG42thN6",
    "Referer": "https://www.pinterest.de/",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "cookie": 'G_ENABLED_IDPS=google; _auth=1; csrftoken=XqfEDei23hmz0XPFHSSqfoRGeG42thN6; _pinterest_sess="TWc9PSZ4bURLR3JEdVVBNW9GQVBqNjV2ZkhIN0R3bGtBNmZ5MXRMSnZDZ01rQ3V0eWY4Z3FKaGt6dFptVytzeTdOdEpTSHBkY0NmeVlSRjFpOFRKNm1WdDVqajZnZkRjYUZTRXRISnR6Nkt3c2d4N2s1SzVNS2hVaVY4Nnk0ejdWdWVUa01BcjNiWEE3aFBkanVLek5pV0NMMnN5ZW03OXpvZDM0NnBSOGc5bXE2UTRKRW5wVW94MlRMNHJxQ2hVNnJ6VVVLR2Y2MEhsN29TeEVBTkhSVFBwTWExRlNFcVBNVzQ5MUF1dTJTZ0ZFc08wdk1td2UzYkY5WEhFTHlGWmdMQncwWFBBSTFtTVcvWHpKMDE0L04wYUdJd2tyaVJGQWFqY1Zid2lSVUQxT3RTVGZiWklZNEp2bUk3b2M2bTQwbzVKU1laQktJS3lVVWNWV3F6M3F0enNqU0pJa2xsc2VIRWhCaTBJeldHaFJxdGQ3RXB1MjNLU2FGdEFSRTFQSDQ1Z0VNajI3SGNua1FidmRDN3FXd25OMVNLc2JXNUkzWERpdjcyay9XYVNUMFJEQUFScTJNNTNETEsvTHYvYS9FTHBJbWYyTGRFTVR0NHUwVm01MUw3SGdjQ3VEaE42SGNpcUNTRGxVRVBmckw5bFZDeG1GTlFhb2V2TDZMNVJEQ2FYNFRxdmpFK3pVLy9qdTdONm83alUrekxoVllWTTByWUQyTzVpYlZVMEh4WFgwTTRVU0hqeG1UVzJiaWZ2TFNWQXNjMVgycFpZK2cwOGJTdk1QYko2UFRVY3FHRnVnUlZkSmxjMi9IaWd2ODRrMG56VXY1NHZpZ1h2VXVhbXMyOUVtSW9uU2cwQ0tCUjVEQ2o5R3NleUExZ2tJa1VudExlaS8wUHloaGYwU3JRd1NkTmttSDdaVHV2WVBmR1FSV2UyTDY4eXRMbGh3QU1FMXpDWlR0aC9ZOEMyditBQWN0bndtK0NyYzJST3ZaWEFvWWVIaFJJemd1N1ppNjhiVkhBZFYyMDNiYkNIb3BYNlduZHhyMlpBTHRCT25VcVZkVUVxQjlhSzNSTlhGckRjL3Vock5IdUNaVDRtRkdBa3pIWHkrJkNtSFJOVVRaQm1WbWo1eW9Fa0xrU3VNMVRCND0="; cm_sub=none; sessionFunnelEventLogged=1; bei=false'
}

snov = {
    'Host': 'app.snov.io',
    'Connection': 'keep-alive',
    'Origin': 'chrome-extension://einnffiilpmgldkapbikhkeicohlaapj',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
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
