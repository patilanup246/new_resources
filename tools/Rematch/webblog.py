import threading
import sys

sys.path.append('./../../')
from db.mongodb import connectMongo

db = connectMongo(True)
blackWhiteCollection = db["blackWhite"]
collection = db["webResources"]

black = blackWhiteCollection.distinct("word", {"isBlack": True, "platId": 3, "part": "GB"})
white = blackWhiteCollection.distinct("word", {"isWhite": True, "platId": 3, "part": "GB"})
blackWordList = [
    "买家",
    "交付",
    "交货",
    "付款",
    "优惠",
    "卖家",
    "大车",
    "尺码",
    "我最喜爱的",
    "折扣",
    "换货",
    "清单",
    "物品",
    "结账",
    "订单",
    "订购",
    "购物箱",
    "购物袋",
    "购物车",
    "运往",
    "运费",
    "运输",
    "运送",
    "退货",
    "送货",
    "钱包",
    "ship",
    "cart",
    "payment",
    "paypal",
    "配送",
    "愿望录"
]


class whiteReview(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        resultList = list(collection.find({}))
        if not resultList:
            logging.error("没有数据")
            return
        urls = []
        for result in resultList:
            url = result["url"]
            if url in urls:
                continue
            urls.append(url)
            self.dealResult(result)

    def dealResult(self, result):
        url = result["url"]
        title = result["title"]
        desc = result["desc"]
        titleChinese = result["titleChinese"]
        # 标题简介黑白名单
        whiteNum = 0
        whiteStr = ""
        for word in white:
            if word in title or word in desc or word in titleChinese:
                whiteNum += 1
                whiteStr += word + " "
        whiteStr = whiteStr.strip()

        blackNum = 0
        blackStr = ""
        for word in black:
            if word in title or word in desc or word in titleChinese:
                blackNum += 1
                blackStr += word + " "
        blackStr = blackStr.strip()

        # header和footer黑白名单
        header = result["header"]
        footer = result["footer"]
        headerZH = result["headerZH"]
        footerZH = result["footerZH"]
        fhBlackWord = ""
        fhBlackWordCount = 0
        for word in blackWordList:
            if word in header or word in footer or word in headerZH or word in footerZH:
                fhBlackWord += word + " "
                fhBlackWordCount += 1
        fhBlackWord = fhBlackWord.strip()

        collection.update({"url": url}, {
            "$set": {"whiteNum": whiteNum, "whiteStr": whiteStr, "blackNum": blackNum, "blackStr": blackStr}},
                          multi=True)
        print(url)


if __name__ == '__main__':
    webblogObj = whiteReview()
    webblogObj.start()
