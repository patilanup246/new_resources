import pymongo
import pymysql
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
        self.mongoClient = pymongo.MongoClient(
            host='52.203.246.147',
            port=27017,
        )
        db_auth = self.mongoClient.globalegrow
        db_auth.authenticate("gb_rw", "vHC3xdG")
        self.db = self.mongoClient["globalegrow"]

        self.collection = self.db["blackWhite"]

    def readMysql(self):
        sql_fetch = "select * from %s" % ("ytbbwords")
        self.cur.execute(sql_fetch)
        mysql_result = self.cur.fetchall()
        for result in mysql_result:
            word = result[0]
            black = result[1]
            white = result[2]
            item = {
                "_id": word,
                "word": word,
                "isBlack": True if black else False,
                "isWhite": True if white else False
            }
            self.writeMongo(item)

    def writeMongo(self, item):
        try:
            self.collection.insert(item)
            print(item)
        except Exception as e:
            print(traceback.format_exc())


if __name__ == '__main__':
    detail = Detail()
    detail.readMysql()
