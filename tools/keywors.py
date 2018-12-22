# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import sys

sys.path.append('./../')
import time
import traceback

from db.mongodb import connectMongo

"""This example retrieves keywords that are related to a given keyword.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""

import csv
from googleads import adwords
import random

PAGE_SIZE = 500

AD_GROUP_ID = ''
db = connectMongo(True)
collection = db["keyWords"]

<<<<<<< HEAD
langueDict = {"阿拉伯": "1019",
              "孟加拉": "1056",
              "保加利亚": "1020",
              "加泰罗尼亚": "1038",
              "中文": "1017",
              "中文繁体": "1018",
              "克罗地亚": "1039",
              "捷克": "1021",
              "丹麦": "1009",
              "荷兰": "1010",
              "英语": "1000",
              "爱沙尼亚": "1043",
              "菲律宾": "1042",
              "芬兰": "1011",
              "法国": "1002",
              "德国": "1001",
              "希腊": "1022",
              "希伯来": "1027",
              "印地": "1023",
              "匈牙利": "1024",
              "冰岛": "1026",
              "印度尼西亚": "1025",
              "意大利": "1004",
              "日本": "1005",
              "朝鲜": "1012",
              "拉脱维亚": "1028",
              "立陶宛": "1029",
              "马来": "1102",
              "挪威": "1013",
              "波斯": "1064",
              "波兰": "1030",
              "葡萄牙": "1014",
              "罗马尼亚": "1032",
              "俄罗斯": "1031",
              "塞尔维亚": "1035",
              "斯洛伐克": "1033",
              "斯洛文尼亚": "1034",
              "西班牙": "1003",
              "瑞典": "1015",
              "泰米尔": "1130",
              "泰卢固": "1131",
              "泰国": "1044",
              "土耳其": "1037",
              "乌克兰": "1036",
              "乌尔都": "1041",
              "越南": "1040"}
=======
langueDict = {
    "波兰":"1030",
    "葡萄牙":"1014",
    "西班牙":"1003",
    "英语":"1000",
    "德国":"1001",
    "意大利":"1004",
    "土耳其":"1037",
    "法国":"1002",
    "匈牙利":"1024",
    "斯洛文尼亚":"1034",
    "保加利亚":"1020",
    "俄罗斯":"1031"

}
>>>>>>> 00b8661052c6b093b516ce99809036f3f4163d85
holewd = []


# 主函数
def main(part, station, client, keyword, ad_group_id=None):
    data = []
    # 初始化适当的服务。
    targeting_idea_service = client.GetService(
        'TargetingIdeaService', version='v201809')

    # 构造选择器对象并检索相关的关键字。
    selector = {
        "ideaType": "KEYWORD",
        "requestType": "IDEAS"
    }

    selector['requestedAttributeTypes'] = [
        'KEYWORD_TEXT', 'SEARCH_VOLUME', 'CATEGORY_PRODUCTS_AND_SERVICES']

    offset = 0
    selector['paging'] = {
        'startIndex': str(offset),
        'numberResults': str(PAGE_SIZE)
    }

    selector['searchParameters'] = [{
        'xsi_type': 'RelatedToQuerySearchParameter',
        'queries': [keyword[0]]
    }]

    # 语种限定
    # Language setting (optional).
    word = keyword[2]
    if word == "希伯来语":
        word = "希伯来"
    id = langueDict.get(word)
    print(id)
    if not id:
        return
    selector['searchParameters'].append({
        'xsi_type': 'LanguageSearchParameter',
        'languages': [{'id': id}]
    })

    # 网络搜索参数（可选）
    selector['searchParameters'].append({
        'xsi_type': 'NetworkSearchParameter',
        'networkSetting': {
            'targetGoogleSearch': True,
            'targetSearchNetwork': False,
            'targetContentNetwork': False,
            'targetPartnerSearchNetwork': False
        }
    })

    # 使用现有广告组生成创意（可选）
    if ad_group_id is not None:
        selector['searchParameters'].append({
            'xsi_type': 'SeedAdGroupIdSearchParameter',
            'adGroupId': ad_group_id
        })

    more_pages = True
    while more_pages:
        page = targeting_idea_service.get(selector)

        # 显示结果。
        if 'entries' in page:
            for result in page['entries']:
                attributes = {}
                for attribute in result['data']:
                    attributes[attribute['key']] = getattr(
                        attribute['value'], 'value', '0')
                if (int(attributes['SEARCH_VOLUME']) > 200) and (attributes['KEYWORD_TEXT'] not in holewd):
                    holewd.append(attributes['KEYWORD_TEXT'])
                    data.append(
                        (attributes['KEYWORD_TEXT'], attributes['SEARCH_VOLUME'], keyword[1], keyword[2], keyword[3]))
        else:
            print('No related keywords were found.')
        try:
            for result in data:
<<<<<<< HEAD
                platId = 1
                item = {
                    "_id": str(platId) + "_" + part + "_" + station + "_" + result[0],
=======
                # item = {
                #     "_id": result[0],
                #     "originKey": keyword[0],
                #     "language": result[3],
                #     "resPeople": y[4],
                #     "isGet": False,
                #     "category": result[2],
                #     "keyWord": result[0],
                #     "hots": result[1],
                #     "getData": False,
                # }
                platId = 1
                item = {
                    "_id": str(platId) + "_GB_" + result[0],
>>>>>>> 00b8661052c6b093b516ce99809036f3f4163d85
                    "originKey": keyword[0],
                    "language": keyword[2],
                    "resPeople": keyword[4],
                    "isGet": False,
                    "category": keyword[1],
                    "keyWord": result[0],
                    "hots": result[1],
                    "getData": False,
                    "platId": platId,
<<<<<<< HEAD
                    "part": part,
                    "date": keyword[-2],
                    "station": station,
                    "insertTime": int(time.time())
=======
                    "part": "GB"
>>>>>>> 00b8661052c6b093b516ce99809036f3f4163d85
                }
                try:
                    collection.insert(item)
                    print(item)
                except Exception as e:
                    pass
        except:
            for orr in range(0, 10):
                print('orr')
        offset += PAGE_SIZE
        selector['paging']['startIndex'] = str(offset)
        more_pages = offset < int(page['totalNumEntries'])


if __name__ == '__main__':
    with open("keyword.csv", encoding="UTF-8", newline='',errors="ignore" ) as csvfile:
        dataList = []
        csv_reader = csv.reader(csvfile)  # 使用csv.reader读取csvfile中的文件
        birth_header = next(csv_reader)  # 读取第一行每一列的标题
        for row in csv_reader:  # 将csv 文件中的数据保存到birth_data中
<<<<<<< HEAD
            dataList.append(row)
        adwords_client = adwords.AdWordsClient.LoadFromStorage()  # 启动线程
        num = 1
        for row in dataList:
            if not row[0].strip():
                continue
            if row[6].strip().lower() == "gearbest" or row[6].strip().lower() == "gb":
                part = "GB"
                station = "GearBest"
            elif row[6].strip().lower() == "zaful":
                part = "clothes"
                station = "Zaful"

            elif row[6].strip().lower() == "rosegal":
                part = "clothes"
                station = "Rosegal"

            elif row[6].strip().lower() == "dresslily":
                part = "clothes"
                station = "Dresslily"
            else:
                continue
            if "facebook" in row[3].lower() or "fb" in row[3].lower():
                platId = 2
                item = {
                    "_id": str(platId) + "_" + part + "_" + station + "_" + row[0],
=======
            if "Facebook" in row[3]:
                platId = 2
                item = {
                    "_id": str(platId) + "_GB_" + row[0],
>>>>>>> 00b8661052c6b093b516ce99809036f3f4163d85
                    "originKey": row[0],
                    "language": row[2],
                    "resPeople": row[4],
                    "isGet": False,
                    "category": row[1],
                    "keyWord": row[0],
                    "hots": 0,
                    "getData": False,
                    "platId": platId,
<<<<<<< HEAD
                    "part": part,
                    "date": row[-2],
                    "station": station,
                    "insertTime": int(time.time())
=======
                    "part": "GB"
>>>>>>> 00b8661052c6b093b516ce99809036f3f4163d85
                }
                try:
                    collection.insert(item)
                    print(item)
<<<<<<< HEAD
                    num += 1
                except Exception as e:
                    pass
            elif "web" in row[3].lower() or "fb" in row[3].lower():
                platId = 3
                item = {
                    "_id": str(platId) + "_" + part + "_" + station + "_" + row[0],
                    "originKey": row[0],
                    "language": row[2],
                    "resPeople": row[4],
                    "isGet": False,
                    "category": row[1],
                    "keyWord": row[0],
                    "hots": 0,
                    "getData": False,
                    "platId": platId,
                    "part": part,
                    "date": row[-2],
                    "station": station,
                    "insertTime": int(time.time())
                }
                try:
                    collection.insert(item)
                    print(item)
                    num += 1
                except Exception as e:
                    pass
            elif "youtube" in row[3].lower():
                platId = 1
                item = {
                    "_id": str(platId) + "_" + part + "_" + station + "_" + row[0],
                    "originKey": row[0],
                    "language": row[2],
                    "resPeople": row[4],
                    "isGet": False,
                    "category": row[1],
                    "keyWord": row[0],
                    "hots": 0,
                    "getData": False,
                    "platId": platId,
                    "part": part,
                    "date": row[-2],
                    "station": station,
                    "insertTime": int(time.time())
                }

                try:
                    collection.insert(item)
                    print(item)
                    num += 1
                except Exception as e:
                    pass

                # try:
                #     main(part, station, adwords_client, row,
                #          int(AD_GROUP_ID) if AD_GROUP_ID.isdigit() else None)  # 开始联想
                # except:
                #     print(traceback.format_exc())
                #     dataList.append(row)
                #     continue
        print(num)
=======
                except Exception as e:
                    pass
            elif "Youtube" in row[3]:
                print(row)
                adwords_client = adwords.AdWordsClient.LoadFromStorage()  # 启动线程
                try:
                    main(adwords_client, row, int(AD_GROUP_ID) if AD_GROUP_ID.isdigit() else None)  # 开始联想
                except:
                    print(traceback.format_exc())
                    print('no')
                    continue
>>>>>>> 00b8661052c6b093b516ce99809036f3f4163d85
