import requests
import json
from lxml import etree

url = "https://www.amazon.com/hz/reviews-render/ajax/medley-filtered-reviews/get/ref=cm_cr_dp_d_fltr"

data = {
    "asin": "B07FVX7Y5J",
    "sortBy": "helpful",
    "scope": "reviewsAjax5"
}
response = requests.post(url=url, data=data)

reslist = response.text.replace("&&&", "").split("\n")
responseStr = ""
for i in reslist:
    if not i:
        continue
    # print(i.strip())
    responseStr += json.loads(i.strip())[-1]

# print(responseStr)

selector = etree.HTML(responseStr)
nodeList = selector.xpath('//div[@data-hook="review"]')
for node in nodeList:
    # 用户
    print(node.xpath('.//a[@data-hook="review-author"]/text()')[0])
    # 评分
    print(node.xpath('.//div[@class="a-row"]/a[1]/@title')[0])
    # 评论标题
    print(node.xpath('.//div[@class="a-row"]/a[2]/text()')[0])
    # 评论时间
    print(node.xpath('.//span[@data-hook="review-date"]/text()')[0])
    #  Verified Purchase
    print(node.xpath('.//span[@data-hook="avp-badge-linkless"]/text()')[0])
    # 评论内容
    print(node.xpath('.//span[@data-hook="review-body-truncated"]/text()')[0])
    # 图片链接
    print(node.xpath('.//div[@class="review-image-tile-section "]//img/@src'))
    # 视频
    print(node.xpath('.//input/@value'))

