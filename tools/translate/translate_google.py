import json

import requests
import logging


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
            response = requests.post(url=url, data=formData)
            response.encoding = "utf-8"
            if response.status_code == 200:
                responseBody = json.loads(response.text)
                if responseBody["success"]:
                    textChinses = responseBody["data"]["translations"][0]["translatedText"]
                    break
        except Exception as e:
            logging.error(e)
            logging.warn("****************翻译失败****************")

    return textChinses

def mainTranslate(text):
    return sendRequest(text)


if __name__ == '__main__':
    text = """Мультики про машинки. Ремонтируем Джип. Игры для мальчиков с машинками
Игрушки Сказочный Патруль и Герои в масках в Прямом эфире  🔴 Мультики для детей
Салон красоты - Мультфильм Барби. Штеффи сделала тату?! Видео для девочек
Герои в масках отбирают конфеты! Видео для детей с Pj Masks
Герои в масках делают конфеты! Мультики для детей
Герои в масках: Кристалл силы и ловушки! Мультики для детей
Игры для мальчиков. Соревнования Бен 10 и другие. Видео с игрушками
Герои в масках открыли ресторан! Мультик с ЛОЛ и игрушками
"""
    print(mainTranslate(text))
