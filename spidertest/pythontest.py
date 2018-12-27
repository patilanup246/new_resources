from db.mongodb import connectMongo

db = connectMongo(True)

collection = db["webResources"]
googleUrl = db["googleUrl"]

urlList = collection.distinct("url",{"insertTime":{"$gte":1545902821}})
for url in urlList:
    googleUrl.update_one({"url": url}, {"$set": {"isData": False}})
