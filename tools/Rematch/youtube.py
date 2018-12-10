import sys

sys.path.append('./../../')
import threading
from db.mongodb import connectMongo
import logging

mongodb = connectMongo(True)
collection = mongodb["resources"]
# 黑白名单
blackWhiteCollection = mongodb["blackWhite"]

# 黑名单列表
blackList = list(blackWhiteCollection.distinct("word", {"isBlack": True, "platId": 1, "part": "GB"}))
clothesblackList = list(blackWhiteCollection.distinct("word", {"isBlack": True, "platId": 1, "part": "clothes"}))
# 白名单列表
whiteList = list(blackWhiteCollection.distinct("word", {"isWhite": True, "platId": 1, "part": "GB"}))
clotheswhiteList = list(blackWhiteCollection.distinct("word", {"isWhite": True, "platId": 1, "part": "clothes"}))
zafulWhiltList = list(
    blackWhiteCollection.distinct("word", {"isWhite": True, "platId": 1, "part": "clothes", "station": "Zaful"}))

GBwhiteList2 = ['初学者', '区别', '包装', '实惠', '对比', '预算', '顶级', '钥匙', '超值', '赠品', '评价', '评测', '评论', '搭配', '最好', '最火', '比价',
                '自拍', '低价', '便宜', '指南', '拆除', 'Best', 'top', '风格', '难以置信', '购买', '运动', '不同', '想法', '产品', '优点', '体会',
                '体验', '值得', '使用', '区别', '参数', '博客', '观点', '最好', '最佳', '发布', '全部', '品味', '圈子', '奇特', '对比', '尝试', '差异',
                '建议', '想法', '感受', '感想', '指南', '排名', '排行', '搭配', '推测', '方式', '方法', '最好', '最具', '材料', '比较', '测试', '汇总',
                '火热', '火爆', '点评', '爆红', '点评', '玩家', '独特', '礼品', '礼物', '缺点', '见解', '见地', '观点', '规格', '评论', '评价', '购买',
                '超值', '集合', '顶部', '预估', '预想', '预料', '预测', '预言', 'Best', '多好', '惊奇', '惊喜', '难以置信', '惊人', '怪异', '样式',
                '谈论', '细数', '发现', '论点', '评分', '评比', '见解', '优点']


class whiteReview(threading.Thread):
    def __init__(self, part):
        threading.Thread.__init__(self)
        self.part = part

    def run(self):
        resultList = list(collection.find({"part": self.part}))
        if not resultList:
            logging.error("没有数据")
            time.sleep(24 * 3600 * 7)
        for result in resultList:
            try:
                url = result["url"]
                videoTittle = result["videotitleUn"]
                videoTittleChinese = result["videoTittle"]
                descriptionChinese = result["description"]
                description = result.get("descriptionUn")
                if not description:
                    description = ""
                part = result["part"]
                VideoTitleCount = 0
                whiteWord = ""
                if part == "GB":
                    whiteListall = whiteList
                else:
                    whiteListall = clotheswhiteList
                    station = result.get("station")
                    if station == "Zaful":
                        whiteListall = zafulWhiltList
                for word in whiteListall:
                    if word.lower() in videoTittle.lower() or word.lower() in videoTittleChinese.lower():
                        VideoTitleCount += 1
                        # logging.info(word)
                        word_new = word + " "
                        whiteWord += word_new
                whiteWord = whiteWord.strip()

                VideoTitleCount2 = 0
                whiteWord2 = ""
                if part == "GB":
                    for word in GBwhiteList2:
                        if word.lower() in videoTittle.lower() or word.lower() in videoTittleChinese.lower():
                            VideoTitleCount2 += 1
                            # logging.info(word)
                            word_new = word + " "
                            whiteWord2 += word_new
                    whiteWord2 = whiteWord2.strip()
                else:
                    pass
                blackWord = ""
                blackWordCount = 0
                if part == "GB":
                    blackListall = blackList
                else:
                    blackListall = clothesblackList
                for word in blackListall:
                    if word in description or word in descriptionChinese:
                        blackWord += word + ""
                        blackWordCount += 1
                blackWord = blackWord.strip()
                try:
                    collection.update({"url": url, "part": part},
                                      {"$set": {"whiteWord": whiteWord,
                                                "VideoTitleCount": VideoTitleCount,
                                                "blackWord": blackWord,
                                                "blackWordCount": blackWordCount,
                                                "whiteWord2": whiteWord2,
                                                "VideoTitleCount2": VideoTitleCount2
                                                }}, upsert=True, multi=True)
                    print("url:{},现在和黑名单:{},现在的白名单:{}".format(url, blackWord, whiteWord))
                except Exception as e:
                    pass
            except Exception as e:
                logging.error(e)


if __name__ == '__main__':
    youtubeObj = whiteReview(part="GB")
    youtubeObj.start()
