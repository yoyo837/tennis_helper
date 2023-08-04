#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/7/10 21:38
@Author  : claude89757
@File    : config.py.py
@Software: PyCharm
"""

COURT_NAME_INFOS = {
    # z香蜜
    102925: '1号场地',
    102926: '2号场地',
    102927: '3号场地',
    102928: '4号场地',
    102929: '5号场地',
    104446: '7号场地',
    102930: '6号场地，当日7点后电话（83771352）预定',
    # 黄木岗
    104447: '1号风雨场',
    104448: '2号风雨场',
    104449: '3号风雨场',
    104450: '4号风雨场',
    104451: '5号风雨场',
    102972: '6号风雨场',
    102961: '7号室外场',
    102962: '8号室外场',
    102963: '9号室外场',
    102964: '10号室外场',
    102965: '11号室外场',
    102966: '12号室外场',
    104300: '1号训练墙',
    104301: '2号训练墙',
    104302: '3号训练墙',
    104475: '4号训练墙',
    # 深云
    115554: '1号网球场',
    115555: '2号网球场',
    115546: '3号网球场',
    115547: '4号网球场',
    115548: '5号网球场',
    115549: '6号网球场',
    115550: '7号网球场',
    115551: '8号网球场',
    115552: '9号网球场',
    115553: '10号网球场',
    # 大沙河
    100003: '1号场地',
    100004: '2号场地',
    100005: '3号场地',
    100006: '4号场地',
    100007: '5号场地',
    100008: '6号场地',
    100009: '7号场地',
    100010: '8号场地',
    # 简上
    109895: '1号场',
    109896: '2号场',
    109897: '3号场',
    109898: '4号场',
    109899: '5号场',
    109900: '6号场',
    109901: '7号场',
    109902: '8号场',
}

CD_INDEX_INFOS = {
    "大沙河": 1,
    "深云文体": 2,
    "深圳湾": 3,
    "香蜜体育": 4,
    "莲花体育": 5,
    "简上": 6,
    "黄木岗": 7,
    "华侨城": 8,
    "福田中心": 9,
    "黄冈公园": 10,
    "北站公园": 11,
    # 弘金地
    "金地威新": 12,
    # 泰尼斯
    "泰尼斯香蜜": 13,
    # 酷尚网球
    "总裁俱乐部": 14,
    # 郑洁俱乐部
    "郑洁俱乐部": 15,
    "梅林文体": 16,
    # 大生体育
    "莲花二村": 17,
    "山花馆": 18,
}

CD_ACTIVE_DAY_INFOS = {
    "大沙河": 7,
    "深云文体": 2,
    "深圳湾": 4,
    "香蜜体育": 2,
    "莲花体育": 2,
    "简上": 3,
    "黄木岗": 2,
    "华侨城": 3,
    "福田中心": 7,
    "黄冈公园": 7,
    "北站公园": 7,
    # 弘金地
    "金地威新": 1,
    # 泰尼斯
    "泰尼斯香蜜": 3,
    # 酷尚网球
    "总裁俱乐部": 7,
    # 郑洁俱乐部
    "郑洁俱乐部": 2,
    # 梅林文体
    "梅林文体": 7,
    # 大生体育
    "莲花二村": 7,
    "山花馆": 5,
}


CD_TIME_RANGE_INFOS = {
    "大沙河": {"start_time": "07:00", "end_time": "22:30"},
    "深云文体": {"start_time": "09:00", "end_time": "22:30"},
    "深圳湾": {"start_time": "09:30", "end_time": "22:30"},
    "香蜜体育": {"start_time": "07:00", "end_time": "22:30"},
    "莲花体育": {"start_time": "07:00", "end_time": "22:30"},
    "简上": {"start_time": "08:00", "end_time": "22:00"},
    "黄木岗": {"start_time": "07:00", "end_time": "22:30"},
    "华侨城": {"start_time": "07:00", "end_time": "22:00"},
    "福田中心": {"start_time": "06:00", "end_time": "22:30"},
    "黄冈公园": {"start_time": "06:00", "end_time": "22:30"},
    "北站公园": {"start_time": "00:00", "end_time": "23:59"},
    "金地威新": {"start_time": "08:00", "end_time": "22:00"},
    "泰尼斯香蜜": {"start_time": "07:00", "end_time": "23:59"},
    "总裁俱乐部": {"start_time": "06:00", "end_time": "23:00"},
    "郑洁俱乐部": {"start_time": "08:00", "end_time": "22:00"},
    "梅林文体": {"start_time": "07:00", "end_time": "23:00"},
    "莲花二村": {"start_time": "07:00", "end_time": "23:00"},
    "山花馆": {"start_time": "09:00", "end_time": "22:00"},
}


WEDA_ENV = "prod"
WEDA_USER_DATASOURCE = "vip_jz6a5g3"
ALL_RULE_FILENAME = "all_rule_list.txt"
