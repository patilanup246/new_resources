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

header = {
    #     "Connection": "keep-alive",
    #     "Accept-encoding": "gzip,deflate,br",
    #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
    # "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    # "Accept-Encoding": "gzip, deflate, br",
    # "Upgrade-Insecure-Requests": "1",
    # "Cookie": "PHPSESSID=kttboga3lp0k4fof0ctne7g4b3; tools_using=%5B%5D; __utma=196994606.1874289139.1536228312.1536228312.1536228312.1; __utmc=196994606; __utmz=196994606.1536228312.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __unam=cdad7b-165ae57c330-5dbb6632-4; __utmb=196994606.4.9.1536229341294"
}
#

bullshit = {
    'Host': 'builtwith.com',
    'Connection': 'keep-alive',
    'User-Agent': UserAgent().random,
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    "User-Agent": random.choice(USER_AGENTS),
    # 'Cookie': '__cfduid=dc6a15345be2832c0004eed53056e470f1532659221; _ga=GA1.2.999942773.1532659223; intercom-id-dvzew6nm=21f152a5-82e2-444e-a3fa-1f62373b66fa'
}

pinters = {
    "Host": "www.pinterest.de",
    "Connection": "keep-alive",
    "X-Pinterest-AppState": "1",
    "User-Agent": UserAgent().random,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    # "cookie": 'G_ENABLED_IDPS=google; _auth=1; csrftoken=XqfEDei23hmz0XPFHSSqfoRGeG42thN6; _pinterest_sess="TWc9PSZ4bURLR3JEdVVBNW9GQVBqNjV2ZkhIN0R3bGtBNmZ5MXRMSnZDZ01rQ3V0eWY4Z3FKaGt6dFptVytzeTdOdEpTSHBkY0NmeVlSRjFpOFRKNm1WdDVqajZnZkRjYUZTRXRISnR6Nkt3c2d4N2s1SzVNS2hVaVY4Nnk0ejdWdWVUa01BcjNiWEE3aFBkanVLek5pV0NMMnN5ZW03OXpvZDM0NnBSOGc5bXE2UTRKRW5wVW94MlRMNHJxQ2hVNnJ6VVVLR2Y2MEhsN29TeEVBTkhSVFBwTWExRlNFcVBNVzQ5MUF1dTJTZ0ZFc08wdk1td2UzYkY5WEhFTHlGWmdMQncwWFBBSTFtTVcvWHpKMDE0L04wYUdJd2tyaVJGQWFqY1Zid2lSVUQxT3RTVGZiWklZNEp2bUk3b2M2bTQwbzVKU1laQktJS3lVVWNWV3F6M3F0enNqU0pJa2xsc2VIRWhCaTBJeldHaFJxdGQ3RXB1MjNLU2FGdEFSRTFQSDQ1Z0VNajI3SGNua1FidmRDN3FXd25OMVNLc2JXNUkzWERpdjcyay9XYVNUMFJEQUFScTJNNTNETEsvTHYvYS9FTHBJbWYyTGRFTVR0NHUwVm01MUw3SGdjQ3VEaE42SGNpcUNTRGxVRVBmckw5bFZDeG1GTlFhb2V2TDZMNVJEQ2FYNFRxdmpFK3pVLy9qdTdONm83alUrekxoVllWTTByWUQyTzVpYlZVMEh4WFgwTTRVU0hqeG1UVzJiaWZ2TFNWQXNjMVgycFpZK2cwOGJTdk1QYko2UFRVY3FHRnVnUlZkSmxjMi9IaWd2ODRrMG56VXY1NHZpZ1h2VXVhbXMyOUVtSW9uU2cwQ0tCUjVEQ2o5R3NleUExZ2tJa1VudExlaS8wUHloaGYwU3JRd1NkTmttSDdaVHV2WVBmR1FSV2UyTDY4eXRMbGh3QU1FMXpDWlR0aC9ZOEMyditBQWN0bndtK0NyYzJST3ZaWEFvWWVIaFJJemd1N1ppNjhiVkhBZFYyMDNiYkNIb3BYNlduZHhyMlpBTHRCT25VcVZkVUVxQjlhSzNSTlhGckRjL3Vock5IdUNaVDRtRkdBa3pIWHkrJkNtSFJOVVRaQm1WbWo1eW9Fa0xrU3VNMVRCND0="; cm_sub=none; sessionFunnelEventLogged=1; bei=false'
}

pinterest = {
    "Host": "www.pinterest.de",
    "Connection": "keep-alive",
    "Origin": "https://www.pinterest.de",
    "X-APP-VERSION": "78eaeea",
    "X-Pinterest-AppState": "active",
    "User-Agent": UserAgent().random,
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json, text/javascript, */*, q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "X-CSRFToken": "XqfEDei23hmz0XPFHSSqfoRGeG42thN6",
    "Referer": "https://www.pinterest.de/",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    # "cookie": 'G_ENABLED_IDPS=google; _auth=1; csrftoken=XqfEDei23hmz0XPFHSSqfoRGeG42thN6; _pinterest_sess="TWc9PSZ4bURLR3JEdVVBNW9GQVBqNjV2ZkhIN0R3bGtBNmZ5MXRMSnZDZ01rQ3V0eWY4Z3FKaGt6dFptVytzeTdOdEpTSHBkY0NmeVlSRjFpOFRKNm1WdDVqajZnZkRjYUZTRXRISnR6Nkt3c2d4N2s1SzVNS2hVaVY4Nnk0ejdWdWVUa01BcjNiWEE3aFBkanVLek5pV0NMMnN5ZW03OXpvZDM0NnBSOGc5bXE2UTRKRW5wVW94MlRMNHJxQ2hVNnJ6VVVLR2Y2MEhsN29TeEVBTkhSVFBwTWExRlNFcVBNVzQ5MUF1dTJTZ0ZFc08wdk1td2UzYkY5WEhFTHlGWmdMQncwWFBBSTFtTVcvWHpKMDE0L04wYUdJd2tyaVJGQWFqY1Zid2lSVUQxT3RTVGZiWklZNEp2bUk3b2M2bTQwbzVKU1laQktJS3lVVWNWV3F6M3F0enNqU0pJa2xsc2VIRWhCaTBJeldHaFJxdGQ3RXB1MjNLU2FGdEFSRTFQSDQ1Z0VNajI3SGNua1FidmRDN3FXd25OMVNLc2JXNUkzWERpdjcyay9XYVNUMFJEQUFScTJNNTNETEsvTHYvYS9FTHBJbWYyTGRFTVR0NHUwVm01MUw3SGdjQ3VEaE42SGNpcUNTRGxVRVBmckw5bFZDeG1GTlFhb2V2TDZMNVJEQ2FYNFRxdmpFK3pVLy9qdTdONm83alUrekxoVllWTTByWUQyTzVpYlZVMEh4WFgwTTRVU0hqeG1UVzJiaWZ2TFNWQXNjMVgycFpZK2cwOGJTdk1QYko2UFRVY3FHRnVnUlZkSmxjMi9IaWd2ODRrMG56VXY1NHZpZ1h2VXVhbXMyOUVtSW9uU2cwQ0tCUjVEQ2o5R3NleUExZ2tJa1VudExlaS8wUHloaGYwU3JRd1NkTmttSDdaVHV2WVBmR1FSV2UyTDY4eXRMbGh3QU1FMXpDWlR0aC9ZOEMyditBQWN0bndtK0NyYzJST3ZaWEFvWWVIaFJJemd1N1ppNjhiVkhBZFYyMDNiYkNIb3BYNlduZHhyMlpBTHRCT25VcVZkVUVxQjlhSzNSTlhGckRjL3Vock5IdUNaVDRtRkdBa3pIWHkrJkNtSFJOVVRaQm1WbWo1eW9Fa0xrU3VNMVRCND0="; cm_sub=none; sessionFunnelEventLogged=1; bei=false'
}

snov = {
    'Host': 'app.snov.io',
    'Connection': 'keep-alive',
    'Origin': 'chrome-extension://einnffiilpmgldkapbikhkeicohlaapj',
    "User-Agent": UserAgent().random,
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
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


def getHtml(url, webResourcesCollection):
    url = url + "/"
    html = ""
    for i in range(3):
        try:
            response = requests.get(url=url, headers=header, timeout=15, verify=False)
            if response.status_code == 200:
                # if response.headers["Content-Encoding"] == "br":
                #     html = brotli.decompress(response.content)
                #     # logging.info("br")
                # elif response.headers["Content-Encoding"] == "gzip":
                #     # logging.info("gzip")
                #     html = gzip.decompress(response.content)
                # else:
                # logging.info("text")
                html = response.content
                # html = response.content
                break
            else:
                if str(response.status_code).startswith("4") or str(response.status_code).startswith("5"):
                    try:
                        webResourcesCollection.remove({"url": url})
                        logging.info("删除成功:{}".format(url))
                    except Exception as e:
                        pass
                    logging.error("访问页面详情的状态码是:{},url:{}".format(response.status_code, url))
                    break
                logging.error("访问页面详情的状态码是:{},url:{}".format(response.status_code, url))
        except Exception as e:
            if repr(e).find("timed out") > 0:
                logging.error("请求超时{}次,url:{}".format(i + 1, url))
            else:
                try:
                    webResourcesCollection.remove({"url": url})
                    logging.info("删除成功:{}".format(url))
                except Exception as e:
                    pass
                break
            html = ""
    return html


def sendRequestWhatrun(url, data, headers):
    apps = ""
    for i in range(3):
        responseStr = ""
        try:
            response = requests.post(url=url, data=data, headers=headers, verify=False, timeout=8,
                                     # proxies=getIp()
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
            apps = responseDict["apps"]
        except Exception as e:
            apps = ""
        if apps:
            break
    return apps


if __name__ == '__main__':
    pass
