import pymongo
import pymysql
import threading

from db.mongodb import connectMongo
from multiprocessing.pool import ThreadPool
import traceback


class Detail(object):
    def __init__(self):
        self.mysql_connection = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='',
            db='youtube',
            charset='utf8'
        )
        self.mysql_connection.ping(reconnect=True)
        self.cur = self.mysql_connection.cursor()

        # 链接mongodb
        self.db = connectMongo(True)

        self.collection = self.db["keyWords"]
        self.wordList = list(self.collection.distinct("keyWord"))

    def readMysql(self):
        sql_fetch = "select * from %s" % ("startwords")
        self.cur.execute(sql_fetch)
        mysql_result = self.cur.fetchall()
        item_list = []
        for result in mysql_result:
            # print(result)
            keyWord = result[0]
            if keyWord in self.wordList:
                continue
            resPeople = result[1]
            category = result[2]
            language = result[3]
            getData = result[4]
            hots = result[5]
            ggsh = result[6]
            fbSearch = result[7]
            item = {
                "_id": keyWord,
                "keyWord": keyWord,
                "resPeople": resPeople,
                "category": category,
                "language": language,
                "getData": True if getData else False,
                "hots": int(hots),
                "ggsh": True if ggsh else False,
                "fbSearch": True if fbSearch else False,
                "isGet": False
            }
            th = threading.Thread(target=self.writeMongo,args=(item,))
            th.start()
        #     item_list.append(item)
        #
        # self.dealThread(item_list)
        # # self.writeMongo(item)

    def dealThread(self, item_list):
        pool = ThreadPool(20)
        pool.map_async(self.writeMongo, item_list)
        pool.close()
        pool.join()

    def writeMongo(self, item):
        try:
            self.collection.insert(item)
            print(item)
        except Exception as e:
            print(traceback.format_exc())


if __name__ == '__main__':
    detail = Detail()
    detail.readMysql()
