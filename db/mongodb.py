import pymongo


def connectMongo(debug_flag):
    if debug_flag:
        mongoClient = pymongo.MongoClient(
            host='52.203.246.147',
            port=27017,
        )
    else:
        mongoClient = pymongo.MongoClient(
            host='172.31.16.68',
            port=27017,
        )
    db_auth = mongoClient.globalegrow
    db_auth.authenticate("gb_rw", "vHC3xdG")
    db = mongoClient["globalegrow"]

    return db

