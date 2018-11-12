import json
from urllib import request, parse
import hashlib
import time, random
import jsonpath
import requests


def get_salt():
    salt = int(time.time() * 1000) + random.randint(0, 10)
    return salt


def get_md5(v):
    # Message Digest Algorithm MD5（中文名为消息摘要算法第五版）为计算机安全领域广泛使用的一种散列函数，用以提供消息的完整性保护
    md5 = hashlib.md5()  # md5对象，md5不能反解，但是加密是固定的，就是关系是一一对应，所以有缺陷，可以被对撞出来

    ## update需要一个bytes格式参数
    md5.update(v.encode('utf-8'))  # 要对哪个字符串进行加密，就放这里
    value = md5.hexdigest()  # 拿到加密字符串
    return value


def get_sign(key, salt):
    sign = 'fanyideskweb' + key + str(salt) + 'ebSeFb%=XZ%T[KZ)c(sy!'
    sign = get_md5(sign)
    return sign

def youdao(key):
    # 请求地址
    url = 'http://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule'
    salt = get_salt()
    print(get_sign(key, salt))
    # 请求体
    data = {
        "i": key,
        "from": "AUTO",
        "to": "AUTO",
        "smartresult": "dict",
        "client": "fanyideskweb",
        "salt": str(salt),  ### 盐：很长的随机串，防止用字典反推
        "sign": get_sign(key, salt),  ## 签名：js加密
        "doctype": "json",
        "version": "2.1",
        "keyfrom": "fanyi.web",
        "action": "FY_BY_REALTIME",
        "typoResult": "false"
    }

    # 数据编码
    data = parse.urlencode(data).encode()

    headers = {
        "Accept": "application/json,text/javascript,*/*;q = 0.01",
        # "Accept-Encoding": "gzip,deflate",      #### 啥意思。。查。。有它就会错误
        "Accept-Language": "zh-CN,zh;q = 0.8",
        "Connection": "keep-alive",
        "Content-Length": str(len(data)),
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Cookie": "YOUDAO_EAD_UUID=c7c1d171-272e-443f-9d07-d9f8c779342e; _ntes_nnid=f691c54e993915b7e783b9985d6cc6aa,1490533835544; __guid=204659719.1198573978453254000.1502548625976.454; OUTFOX_SEARCH_USER_ID_NCOO=937151153.4321815; P_INFO=userlvkaokao@163.com|1523271382|0|other|00&99|bej&1523189875&hzhr#bej&null#10#0#0|157818&0|hzhr|userlvkaokao@163.com; OUTFOX_SEARCH_USER_ID=-2077552359@180.201.180.165; _ga=GA1.2.667209885.1524559124; JSESSIONID=aaaTQDWkaB_7QbzNHL4nw; monitor_count=1; fanyi-ad-id=44547; fanyi-ad-closed=1; ___rl__test__cookies=1526736521106",
        "Host": "fanyi.youdao.com",
        "Origin": "http://fanyi.youdao.com",
        "Referer": "http://fanyi.youdao.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
    }

    response = requests.post(url=url, data=data, headers=headers)
    # print(response.text)

    response.encoding = "utf-8"
    if response.status_code == 200:

        print(response.text)
        html = json.loads(response.text)

        result = jsonpath.jsonpath(html,"$..tgt")
        textZh = ""
        for i in result:
            i = i + "\n"
            textZh += i
    else:
        print(response.status_code)
        textZh = ''
    return textZh


if __name__ == '__main__':
    print(len("ac6f4569e90a3dd0914420368f453f56"))
    youdao("""Making videos on Technology,Telecom,Science and other relevant topics.There will be Vlogs and Live streams also.You will also find mobile app reviews, tips and tricks.I also intend to do product reviews in future and want manufacturers to send me free products to me for review. Please subscribe to  AmlanTalks and keep getting updates.
Channel History:
2008- Created a Youtube channel for uploading private videos.The Channel name was my own name-"Amlan Sarma".
2017- March- First Video uploaded for new channel
26.06.2017- 100 subscribers.

Please share my videos on whatsapp,facebook ,twitter or any other social network,so that more and more people gets associated with my channel. Thanks.

For business inquiries: amlansarma@gmail.com

Our Channel:
youtube.com/amlantalks
Follow Us Facebook:
https://www.facebook.com/amlantalks
Follow Us Twitter:
https://twitter.com/amlantalks""")