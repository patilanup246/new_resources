# coding:utf-8
import json

import requests
import logging

import sys


def sendRequest(text):
    url = "http://www.1talking.net:8000/api/v1.0/common/translate"
    formData = {
        "key": "d#*fsd32iofdg0&*fsfjan21374fdshf",  # 固定值key
        "q": text,  # 需要翻译的文本，接受一个数组或者字符串,
        "source": "auto",  # 源语言，不传则自动检测
        "target": "zh-cn"  # 目标语言
    }
    textChinses = ""
    for i in range(3):
        try:
            if sys.version_info[0] == 2:
                import urllib2
                import urllib
                proxy_handler = urllib2.ProxyHandler({})
                opener = urllib2.build_opener(proxy_handler)
                request = urllib2.Request(url=url, data=urllib.urlencode(formData))
                resp = opener.open(request)
                if resp.code == 200:
                    responseBody = json.loads(resp.read())
                    if responseBody["success"]:
                        textChinses = responseBody["data"]["translations"][0]["translatedText"]
                        break
            else:
                response = requests.post(url=url, data=formData)
                response.encoding = "utf-8"
                if response.status_code == 200:
                    responseBody = json.loads(response.text)
                    if responseBody["success"]:
                        textChinses = responseBody["data"]["translations"][0]["translatedText"]
                        break
        except Exception as e:
            print(e)
            logging.error(e)
            logging.warn("****************翻译失败****************")
    if not textChinses:
        textChinses = text
    return textChinses


def mainTranslate(text):
    return sendRequest(text)


if __name__ == '__main__':
    text = """"""
    print(mainTranslate(text[:4000]))
