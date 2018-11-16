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


# 主函数
def main(client, keyword, ad_group_id=None):
    data = []
    # 初始化适当的服务。
    targeting_idea_service = client.GetService(
        'TargetingIdeaService', version='v201802')

    # 构造选择器对象并检索相关的关键字。
    selector = {
        'ideaType': 'KEYWORD',
        'requestType': 'IDEAS'
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
    id = langueDict.get(keyword[2])
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
                    print(attributes['KEYWORD_TEXT'], attributes['SEARCH_VOLUME'])
                    data.append(
                        (attributes['KEYWORD_TEXT'], attributes['SEARCH_VOLUME'], keyword[1], keyword[2], keyword[3]))
        else:
            print('No related keywords were found.')
        try:
            for result in data:
                item = {
                    "_id": result[0],
                    "originKey": keyword[0],
                    "language": result[3],
                    "resPeople": y[4],
                    "isGet": False,
                    "category": result[2],
                    "keyWord": result[0],
                    "hots": result[1],
                    "getData": False,
                }
                try:
                    collection.insert(item)
                except Exception as e:
                    collection.update_one({"_id": result[0]}, {"$set": {"hots": result[1], "originKey": keyword[0]}})
        except:
            for orr in range(0, 10):
                print('orr')
        offset += PAGE_SIZE
        selector['paging']['startIndex'] = str(offset)
        more_pages = offset < int(page['totalNumEntries'])


if __name__ == '__main__':
    ops = open('error.txt', 'a')
    lines = [lin for lin in csv.reader(open('start.csv', 'r',encoding="gbk"))]
    # for y in lines:
    #     item = {
    #         "_id": y[0],
    #         "originKey": y[0],
    #         "language": y[2],
    #         "resPeople": y[4],
    #         "isGet": False,
    #         "category": y[1],
    #         "keyWord": y[0],
    #         "hots": 99999,
    #         "getData": False,
    #     }
    #     try:
    #         collection.insert(item)
    #     except Exception as e:
    #         print(e)

    holewd = []

    adwords_client = adwords.AdWordsClient.LoadFromStorage()  # 启动线程
    for y in lines:
        print(y)
        try:
            main(adwords_client, y, int(AD_GROUP_ID) if AD_GROUP_ID.isdigit() else None)  # 开始联想
        except:
            ops.writelines(y)
            print(traceback.format_exc())
            print('no')
            continue
    # time.sleep(random.randint(40, 60))
