# -*- coding: utf-8 -*-
import scrapy
import logging
import json


class YoutubeSpider(scrapy.Spider):
    name = 'youtube'
    allowed_domains = ['youtube.com']
    start_urls = ['https://www.youtube.com']
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
        "x-client-data": "CIu2yQEIpLbJAQjBtskBCKmdygEIqKPKARj5pcoB",
        "x-spf-previous": "https://www.youtube.com/results?search_query=xiaomi",
        "x-spf-referer": "https://www.youtube.com/results?search_query=xiaomi",
        "x-youtube-client-name": "1",
        "x-youtube-client-version": "2.20181018",
        "x-youtube-page-cl": "217669354",
        "x-youtube-page-label": "youtube.ytfe.desktop_20181017_4_RC1",
        "x-youtube-variants-checksum": "2a9e447e98546a2334b69f8c02eb6c51"
    }

    def parse(self, response):
        url = "https://www.youtube.com/results?search_query=xiaomi&pbj=1"
        yield scrapy.Request(url=url,headers=self.headers,callback=self.parsePage)

    def parsePage(self,response):
        response = json.loads(response.text)[1]
        contents = \
        response["response"]["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]["sectionListRenderer"][
            "contents"][0]["itemSectionRenderer"]["contents"]
        # xsrf_token
        token = response["xsrf_token"]
        # print(token)

        # continuation
        continuations = \
        response["response"]["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]["sectionListRenderer"][
            "contents"][0]["itemSectionRenderer"]["continuations"]
        continuation = continuations[0]["nextContinuationData"]["continuation"]

        # itct
        itct = continuations[0]["nextContinuationData"]["clickTrackingParams"]
        # print(itct)

        # nextPageUrl
        nextPageUrl = response["endpoint"]["urlEndpoint"]["url"]
        nextPageUrl = "https://www.youtube.com" + nextPageUrl + "&pbj=1" + "&ctoken=" + continuation + "&itct=" + continuation

        formData = {
            "session_token": token
        }

        # sendRequestPost(nextPageUrl, headers, formData)
        yield scrapy.FormRequest(
            url=nextPageUrl,
            headers=self.headers,
            formdata=formData,
            method="POST",
            callback=self.parseNextPage
        )

        for content in contents:
            videoRenderer = content.get("videoRenderer")
            if not videoRenderer:
                continue
            userUrl = "https://www.youtube.com" + \
                      videoRenderer["shortBylineText"]["runs"][0]["navigationEndpoint"]["commandMetadata"][
                          "webCommandMetadata"]["url"]
            # print(userUrl)

    def parseNextPage(self,response):
        # logging.info(response.text)
        response = json.loads(response.text)
        if not response:
            logging.error("no response")
            return
        response = response[1]
        contents = \
            response["response"]["continuationContents"]["itemSectionContinuation"]["contents"]
        # xsrf_token
        token = response["xsrf_token"]
        # print(token)

        # continuation
        continuations = \
            response["response"]["continuationContents"]["itemSectionContinuation"]["continuations"]
        continuation = continuations[0]["nextContinuationData"]["continuation"]

        # itct
        itct = continuations[0]["nextContinuationData"]["clickTrackingParams"]
        # print(itct)

        # nextPageUrl
        nextPageUrl = response["endpoint"]["urlEndpoint"]["url"]
        nextPageUrl = "https://www.youtube.com" + nextPageUrl + "&pbj=1" + "&ctoken=" + continuation + "&itct=" + continuation

        formData = {
            "session_token": token
        }

        # sendRequestPost(nextPageUrl, headers, formData)
        yield scrapy.FormRequest(
            url=nextPageUrl,
            headers=self.headers,
            formdata=formData,
            method="POST",
            callback=self.parseNextPage
        )

        for content in contents:
            videoRenderer = content.get("videoRenderer")
            if not videoRenderer:
                continue
            userUrl = "https://www.youtube.com" + \
                      videoRenderer["shortBylineText"]["runs"][0]["navigationEndpoint"]["commandMetadata"][
                          "webCommandMetadata"]["url"]
            logging.info(userUrl)