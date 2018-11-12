import json
import random
import urllib.request
import requests
import time

from tools.HandleJs import Py4Js
from tools.useragent import USER_AGENTS
import logging
import requests
import re


def getCookie():
    NID = ""
    try:
        headers = {
            "User-Agent":random.choice(USER_AGENTS)
        }
        response = requests.get("https://translate.google.cn")
        response.encoding = "utf-8"
        if response.status_code == 200:
            setCookie = response.headers["Set-Cookie"]
            # print(setCookie)
            NID = re.search(r"(NID.*?;)",setCookie).group(1)
    except Exception as e:
        pass
    return NID
cookies = ""
for i in range(3):
    cookies = getCookie()
    if cookies:
        break


def open_url(url):
    global cookies
    print(cookies)
    data = ""
    for i in range(3):
        try:
            headers = {
                'User-Agent': random.choice(USER_AGENTS),
                # "referer": "https://translate.google.cn/",
                "x-client-data": "CIu2yQEIpLbJAQjBtskBCKmdygEIqKPKARj5pcoB",
                "accept-language": "zh-CN,zh;q=0.9",
                "cookie": cookies
            }
            response = requests.get(url=url, headers=headers, timeout=5)
            response.encoding = "utf-8"
            if response.status_code == 200:
                data = response.text
                break
            else:
                print(response.status_code)
        except Exception as e:
            data = ""
    return data


def translate(content, tk):
    word = ''
    if len(content) > 4891:
        print("翻译的长度超过限制！！！")
        return

    content = urllib.parse.quote(content)

    url = "http://translate.google.cn/translate_a/single?client=t&sl=auto&tl=zh-CN&hl=zh-CN&dt=at&dt=bd&dt=ex&dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss&dt=t&ie=UTF-8&oe=UTF-8&source=btn&ssel=0&tsel=0&kc=0&tk=%s&q=%s" % (
        tk, content)
    result = open_url(url)
    if result:
        result_json = json.loads(result)
        # print(result_json)
        # print(type(result_json))
        # print(len(result_json[0]))
        for i in range(len(result_json[0]) - 1):
            word = word + result_json[0][i][0]
            # end = result.find("\",")
            # if end > 4:
            #     print(result[4:end])
    else:
        word = content
    return word


def main(text):
    js = Py4Js()
    content = text
    tk = js.getTk(content)
    text = translate(content, tk)
    return text


if __name__ == "__main__":
    print(main("""
    
    Канал для детей: летсплеи, развивающие мультики, сказки и обзоры детских игр и приложений на iOS и Android!

Подписывайтесь на канал, ставьте лайки, комментируйте, рекомендуйте нас и смотрите новые интересные видео.

Контакты / Промо-коды:  tehnodetki@gmail.com

A channel for children . kids: letsplays, educational & learning cartoons, fairy tales and reviews of children's games and applications on iOS and Android! 

Subscribe to the channel, place the thumbs up, comment, recommend us and see the new interest video.

Contacts / Promo-Codes:  tehnodetki@gmail.com
    
    """))