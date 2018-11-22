import json
import os

import re
import traceback
import jsonpath
import requests
from multiprocessing.pool import ThreadPool

import sys
import time

sys.path.append("./../../")
from logs.loggerDefine import loggerDefine

youtubeDir = "./../../logs/youtube/"
if not os.path.exists(youtubeDir):
    os.makedirs(youtubeDir)
loggerFile = youtubeDir + "mailaddr.log"
logging = loggerDefine(loggerFile)
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# 禁用安全请求警告
from db.mongodb import connectMongo

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from python_anticaptcha import AnticaptchaClient, NoCaptchaTaskProxylessTask
from fake_useragent import UserAgent
import threading

debug_flag = True if sys.argv[1] == "debug" else False
mongodb = connectMongo(debug_flag)
userCollection = mongodb["resources"]

api_key = "2c4f703bb6cd0fa62bedec432feca2de"
site_key_pattern = 'data-sitekey="(.+?)"'
url = 'https://www.google.com/recaptcha/api2/demo'
client = AnticaptchaClient(api_key)


def get_token_channel(url, session):
    url_about = url + "/about?pbj=1"
    headers = {
        "accept-language": "zh-CN,zh;q=0.9",
        "referer": url,
        "user-agent": UserAgent().random,
        "x-client-data": "CIu2yQEIpLbJAQjBtskBCKmdygEIqKPKARj5pcoB",
        "x-spf-previous": url,
        "x-spf-referer": url,
        "x-youtube-client-name": "1",
        "x-youtube-client-version": "2.20181030",
        "x-youtube-page-cl": "218622685",
        "x-youtube-page-label": "youtube.ytfe.desktop_20181024_8_RC0",
        "x-youtube-sts": "17829",
        "x-youtube-utc-offset": "480",
        "x-youtube-variants-checksum": "92a32082074d908eccfd9ce4e205165f"
    }
    token = ""
    channel_id = ""
    for i in range(3):
        try:
            response = session.get(url=url_about, headers=headers, verify=False)
            responseBody = json.loads(response.text)
            token = jsonpath.jsonpath(responseBody, "$..xsrf_token")[0]
            serviceTrackingParams = jsonpath.jsonpath(responseBody, "$..serviceTrackingParams")[0]
            for item in serviceTrackingParams:
                if item["service"] == "GFEEDBACK":
                    params = item["params"]
                    for i in params:
                        if i["key"] == "browse_id":
                            value = i["value"]
                            channel_id = value
            break
        except Exception as e:
            print(traceback.format_exc())

    return token, channel_id


def get_token(form_html):
    site_key = re.search(site_key_pattern, form_html).group(1)
    print(site_key)
    task = NoCaptchaTaskProxylessTask(website_url=url,
                                      website_key=site_key)
    job = client.createTask(task)
    job.join()
    print("获取token中")
    token = job.get_solution_response()
    print("token:{}".format(token))
    return token


def getdata_sitekey(token, url, session):
    url_sitekey = "https://www.youtube.com/channels_profile_ajax?action_get_business_email_captcha=1"
    headers = {
        "accept-language": "zh-CN,zh;q=0.9",
        "referer": url + "/about",
        "user-agent": UserAgent().random,
        "x-client-data": "CIu2yQEIpLbJAQjBtskBCKmdygEIqKPKARj5pcoB",
        "x-spf-previous": url + "/about",
        "x-spf-referer": url + "/about",
        "x-youtube-client-name": "1",
        "x-youtube-client-version": "2.20181030",
        "x-youtube-page-cl": "218622685",
        "x-youtube-page-label": "youtube.ytfe.desktop_20181024_8_RC0",
        "x-youtube-sts": "17829",
        "x-youtube-utc-offset": "480",
        "x-youtube-variants-checksum": "92a32082074d908eccfd9ce4e205165f"
    }
    formdata = {
        "session_token": token
    }
    data_sitekey = ""
    for i in range(3):
        try:
            response = session.post(url=url_sitekey, data=formdata, headers=headers, verify=False)
            responseBody = json.loads(response.text)["html_content"]
            data_sitekey = re.search(r'data-sitekey="(.*?)"', responseBody).group(1)
            break
        except Exception as e:
            print(e)

    return data_sitekey


def get_mail(recaptcha_response, token, url, channel_id, session):
    url = url + "/about"
    url_mail = "https://www.youtube.com/channels_profile_ajax?action_verify_business_email_recaptcha=1"
    formdata = {
        "channel_id": channel_id,
        "g-recaptcha-response": recaptcha_response,
        "session_token": token
    }
    headers = {
        # "accept-language": "zh-CN,zh;q=0.9",
        # "content-length": "630",
        # "content-type": "application/x-www-form-urlencoded",
        # "origin": "https://www.youtube.com",
        # "cookie": cookie,
        # "referer": url,
        "user-agent": UserAgent().random,
        # "x-client-data": "CIu2yQEIpLbJAQjBtskBCKmdygEIqKPKARj5pcoB",
        # "x-spf-previous": url,
        # "x-spf-referer": url,
        # "x-youtube-client-name": "1",
        # "x-youtube-client-version": "2.20181027",
        # "x-youtube-page-cl": "219164749",
        # "x-youtube-page-label": "youtube.ytfe.desktop_20181026_9_RC1",
        # "x-youtube-utc-offset": "480",
        # "x-youtube-variants-checksum": "fc7620c75c4bdbc88a99fc42400686f8"
    }
    mail_addr = ""
    for i in range(5):
        try:
            response = session.post(
                url=url_mail,
                data=formdata,
                headers=headers,
                timeout=5,
                allow_redirects=False,
                # cookies=cookie
            )
            if response.status_code == 200:
                responseBody = json.loads(response.text)
                html_content = responseBody["html_content"]
                mail_addr = re.search(r'"mailto:(.*?)"', html_content).group(1)
                break
            else:
                print(response.status_code)
        except Exception as e:
            print(e)
            print(url)

    return mail_addr


def get_recaptcha_response(channel_url, site_key, session):
    try:
        url = channel_url + "/about"
        task = NoCaptchaTaskProxylessTask(
            website_url=url,
            website_key=site_key,
            website_s_token=None
        )
        job = client.createTask(task)
        job.join()
        return job.get_solution_response()
    except Exception as e:
        print(e)


def take_thread():
    # while True:
    #     if VideoTitleCount == 2 or VideoTitleCount == 3 or VideoTitleCount == 4:
    #         # resultList = userCollection.find_one(
    #         #     {"emailAddress": "", "isRecaptcha": True,"VideoTitleCount": VideoTitleCount})
    #         resultList = userCollection.find_one({"isMail": True, "csvLoad": False, "emailAddress": "", "isRecaptcha": False,"VideoTitleCount": VideoTitleCount})
    #     else:
    #         resultList = userCollection.find_one({"isMail": True, "csvLoad": False, "emailAddress": "", "isRecaptcha": False,"$or": [{"VideoTitleCount": VideoTitleCount}, {"VideoTitleCount": VideoTitleCount + 1}]})
    #         # resultList = userCollection.find_one({"emailAddress": "", "isRecaptcha": True,"$or": [{"VideoTitleCount": VideoTitleCount}, {"VideoTitleCount": VideoTitleCount + 1}]})
    #     if not resultList:
    #         # logging.error("目前没有需要处理的数据")
    #         time.sleep(60)
    #         continue
    #     try:
    #         main_process(resultList["url"])
    #     except Exception as e:
    #         print(e)
    while True:
        threadNum = 10
        resultList = list(
            userCollection.find({"isMail": True, "csvLoad": False, "emailAddress": "", "isRecaptcha": False,
                                 "VideoTitleCount": {"$gte": 4}}).limit(10))
        if not resultList:
            logging.error("没有需要获取邮箱的数据")
            time.sleep(60)
            continue
        channel_url_list = []
        for result in resultList:
            channel_url_list.append(result["url"])
        pool = ThreadPool(threadNum)
        pool.map_async(main_process, channel_url_list)
        pool.close()
        pool.join()


def main_process(channel_url):
    mail_addr = ""
    for i in range(3):
        logging.info("破解邮箱处理中,url:{}".format(channel_url))
        session = requests.Session()
        token, channel_id = get_token_channel(channel_url, session)
        if not token or not channel_id:
            logging.error("token or channel_id 获取失败,url:{}".format(url))
            continue
        else:
            logging.info("token and channel_id 获取成功,url:{},token:{},channel_id:{}".format(url, token, channel_id))
        data_sitekey = getdata_sitekey(token, channel_url, session)
        if not data_sitekey:
            logging.error("data_sitekey 获取失败,url:{}".format(url))
            continue
        else:
            logging.info("data_sitekey 获取成功,url:{},data_sitekey:{}".format(url, data_sitekey))
        recaptcha_response = get_recaptcha_response(channel_url, data_sitekey, session)
        if not recaptcha_response:
            logging.error("recaptcha_response 获取失败,url:{}".format(channel_url))
            continue
        else:
            logging.info("recaptcha_response 获取成功,url:{}".format(channel_url))
        mail_addr = get_mail(recaptcha_response, token, channel_url, channel_id, session)
        if mail_addr:
            logging.info("邮箱获取成功,url:{},addr:{}".format(channel_url, mail_addr))
            break
        else:
            logging.error("邮箱获取失败{}次,url:{}".format(i+1,channel_url))
            continue
    try:
        userCollection.update({"url": channel_url}, {
            "$set": {"emailAddress": mail_addr, "isRecaptcha": True}}, multi=True)
        logging.info("邮箱新增成功:url:{},  mailaddr:{}".format(channel_url, mail_addr))
    except Exception as e:
        logging.error(e)


if __name__ == '__main__':
    take_thread()
    # for VideoTitleCount in range(5, 22, 2):
    #     th = threading.Thread(target=take_thread, args=(VideoTitleCount,))
    #     th.start()
    #
    # for VideoTitleCount in range(2, 5):
    #     th = threading.Thread(target=take_thread, args=(VideoTitleCount,))
    #     th.start()
