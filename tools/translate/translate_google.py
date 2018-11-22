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

    return textChinses


def mainTranslate(text):
    return sendRequest(text)


if __name__ == '__main__':
    text = """Kitchen Knives,Baselayers & Underwear,0,Trousers & Shorts,REFINE,Custom Knives,New Items,Search:,Urban Essentials,Schrade,Tents & Shelters,Headlamps,Navigation,Mats & Pillows,Organisers & Add-ons,Batteries and Chargers,*,Stopwatches,//<![CDATA[    var newsletterSubscriberFormDetail = new VarienForm('newsletter-validate-detail');    new Varien.searchForm('newsletter-validate-detail', 'newsletter', 'Enter your email address');    //]]>            var body = jQuery('body');        jQuery('.newsletter_banner.collapse').click(function(){            jQuery(this).closest('.newsletter-banner_wrapper').addClass('collapsed');            Mage.Cookies.set('hide_newsletter_banner',1);            body.removeClass('showing_newsletter_banner');        });                body.addClass('showing_newsletter_banner');,Carry Accessories,Emergency Repairs,Survival,Knife and Tool Sharpeners,Water Purification,Emergency Power,You have no items in your shopping cart.,Flashlights,Sign up for a chance to win £150,CRKT,Books & Media,Nitecore,Sign up to our mailing list for a chance to win each month.,Fire Starters,Heinnie Haynes,Miniatures & Letter Openers,Saws,Hammocks, Cots & Seating,T&C applies.,Watches,Spinners,Blog,Lighting Accessories,Apparel Accessories,Boker Plus,Bags,Cookware,Apparel,Fallkniven,Clearance,Carving & Knife Making,Triple Aught Design,First Aid,Sheaths & Holsters,Men's Jewellery,Pouches & Pockets,Grooming,Ladders,5.11,Lighting,Hand Warmers,Pens,Hard Cases,Food,Carry,Search,Travel Safety,Axes,Belts,Morale Patches,Machetes,Best Sellers,Folding Blade Knives,Insect Protection,Signalling Devices,Lanterns,Flasks,Close,Eyewear,Shelter,New subscribers only.,Lighters,Knives & Tools,Canine,Optics,More没有资源"""
    print(mainTranslate(text))