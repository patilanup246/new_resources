# coding=gbk
import re

string = "小组简介小组说明HTC LG SAMSUNG 小米 ASUS、ROOT、S OFF、POKEMON GO、手機系統維修、刷機、破解、內購、改機社團------------------------------------------奇摩專業刷機賣場https://tw.bid.yahoo.com/tw/booth/Y1001734322露天專業刷機賣場...查看更多小组类型电子游戏成员 · 998管理员Wei Cheng和Paul Huang是管理员。动态0今日新帖数量过去 30 天内有 4 篇998成员人数过去 30 天内有超过 0 位约 3 年前由 Paul Huang 创建"
PATTERN = '小组说明(.+?)查看更多'
pattern = re.compile(PATTERN)
m = pattern.search(string)
print(m.group(1))
print(re.search(r"小组说明(.+?)查看更多",string).group(1))
