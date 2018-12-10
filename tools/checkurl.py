import requests
import json
import traceback
import logging

from db.mongodb import connectMongo

from urllib.request import urlparse


def sendRequest(url, domain):
    try:
        requestUrl = domain + "api/query/url"
        data = {
            "complete": url.encode(),
            # "fuzzy": url.encode()
        }
        response = requests.post(url=requestUrl, data=data)
        return json.loads(response.text)
    except Exception as e:
        print(traceback.format_exc())


def checkUrl(url, domain):
    if url.endswith("/"):
        url = url[:-1]
    urlList = url.split(".com/")
    if "youtube" in url:
        url = "http://www.youtube.com/" + urlList[-1]
    elif "facebook" in url:
        url = "http://www.facebook.com/" + urlList[-1]
    else:
        return
    # domain = "http://mms.gloapi.com/"
    isExist = True  # 代表存在mms中
    responseBody = sendRequest(url, domain)
    if responseBody:
        if responseBody["status"]:
            if responseBody["data"]["complete"]:
                isExist = False  # False代表不存在数据库

    # if isExist:
    #     # 存在直接返回
    #     print("存在mms中,url:{}".format(url))
    #     return isExist
    # else:
    #     isExist = True  # 代表存在cmms中
    #     # 不存在继续看是否存在另外库中
    #     domain = "http://cmms.gloapi.com/"
    #     responseBody = sendRequest(url, domain)
    #     if responseBody:
    #         if responseBody["status"]:
    #             if responseBody["data"]["complete"]:
    #                 isExist = False  # False代表不存在数据库
    #             else:
    #                 isExist = True
    #     if isExist:
    #         print("存在cmms中,url:{}".format(url))

    return isExist


def checkMail(mail, domain):
    isExist = True  # 代表存在mms中
    responseBody = sendRequestMail(mail, domain)
    if responseBody:
        if responseBody["status"]:
            if responseBody["data"]:
                if responseBody["data"]["email"]:
                    isExist = False  # False代表不存在数据库
    return isExist


def sendRequestMail(mail, domain):
    try:
        requestUrl = domain + "api/query/email"
        data = {
            "email": mail.encode(),
            # "fuzzy": url.encode()
        }
        response = requests.post(url=requestUrl, data=data)
        return json.loads(response.text)
    except Exception as e:
        print(traceback.format_exc())


def checkWebUrl(url, domain):
    urlDomain = urlparse(url).netloc
    if "www." not in urlDomain:
        url = "http://www." + urlDomain
    else:
        url = "http://" + urlDomain
    isExist = True  # 代表存在mms中
    responseBody = sendRequestWeb(url, domain)
    if responseBody:
        if responseBody["status"]:
            if responseBody["data"]["complete"]:
                isExist = False  # False代表不存在数据库
    return isExist


def sendRequestWeb(url, domain):
    try:
        requestUrl = domain + "api/query/url"
        data = {
            "complete": url.encode(),
            # "fuzzy": url.encode()
        }
        response = requests.post(url=requestUrl, data=data)
        return json.loads(response.text)
    except Exception as e:
        print(traceback.format_exc())


if __name__ == '__main__':
    mmsDomain = "http://mms.gloapi.com/"
    cmmsDomain = "http://cmms.gloapi.com/"
    print(checkMail("kitkotfirst@gmail.com",cmmsDomain))
