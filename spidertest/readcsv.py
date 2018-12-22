import csv

fieldList = ["upTitle", "keyWord", "country", "isMail", "emailAddress", "Facebook", "description", "url",
                 "name", "VideoTitleCount",
                 "subscriberCount", "viewCountAvg", "titleLastUpdateTime", "viewCountFirst", "whiteWord",
                 "whiteWord2", "VideoTitleCount2"]
csvfileWriter = open("./newdata.csv", "w", newline='', encoding="utf_8_sig")
writer = csv.writer(csvfileWriter)
writer.writerow(fieldList)