# -*- coding: utf-8 -*-
import os
import requests
import time
import calendar
import math
import random
import json
import hashlib
import datetime
import shelve

from typing import List

from weida import get_rule_list_from_weida
from sms import send_sms_for_news

# 读取指定环境变量的值
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
SIGN_KEY = os.environ.get("SIGN_KEY")

PROXY_TEXT = os.environ.get("PROXY")

DSH_COURT_NAME_INFOS = {100003: '1号场地',
                        100004: '2号场地',
                        100005: '3号场地',
                        100006: '4号场地',
                        100007: '5号场地',
                        100008: '6号场地',
                        100009: '7号场地',
                        100010: '8号场地'}
# 场地代号
SALES_ITEM_ID = "100000"
SALES_ID = "100220"
ITEM_NAME = "大沙河"


def gen_nonce(timestamp: int):
    """
    生成 nonce, 该方法解析自前端 js 代码, 大概率不会变化
    """
    e = int(timestamp)
    y = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"
    nonce = ''
    for c in y:
        n = math.trunc((e + 16 * random.random()) % 16)
        e = math.floor(e / 16)
        if 'x' == c:
            nonce += hex(n)[2]
        elif 'y' == c:
            nonce += hex(3 & n | 8)[2]
        else:
            nonce += c
    return nonce


def signature_for_post(timestamp: str, nonce: str, param: str = '', data: dict = None):
    """
    生成post请求的签名
    """
    prefix = '&'.join(
        [f'_key={SIGN_KEY}', '_timestamp=' + timestamp, '_nonce=' + nonce])
    prefix += ',,' + param + ',,'
    if data is not None:
        raw = prefix + json.dumps(data, separators=(',', ':'))
    else:
        raw = prefix
    return hashlib.md5(raw.encode()).hexdigest().upper()


def signature_for_get(timestamp: str, nonce: str, param_str: str = ''):
    """
    生成get请求的签名
    """
    prefix = ','.join([
         f'_key={SIGN_KEY}&_timestamp={timestamp}&_nonce={nonce}',
         param_str,
         "",
         "",
         ""
    ])
    print(prefix)
    return hashlib.md5(prefix.encode()).hexdigest().upper()


def clock_to_timestamp(hour: str):
    """
    福田体育的时间戳比较特殊 (奇葩), 它其实是以 2013-01-01 {hour}:00 为基准, 计算出新的时间戳
    其中 hour 为预订时间
    """
    return int(
        datetime.datetime.strptime(f'2013-01-01 {hour}:00', '%Y-%m-%d %H:%M:%S').timestamp() * 1000)


def timestamp_to_clock(timestamp: int) -> str:
    """
    timestamp 为 Unix 时间戳（毫秒）
    返回值为时钟格式（小时:分钟）
    """
    date = datetime.datetime.fromtimestamp(timestamp / 1000)  # 将毫秒转换为秒
    return date.strftime('%H:%M')


def str_to_timestamp(date_str: str):
    return int(datetime.datetime.strptime(date_str, '%Y-%m-%d').timestamp() * 1000)


def find_available_slots(booked_slots, start_time="07:00", end_time="22:30"):
    """
    根据已预定的时间段，查询可预定的时间段
    """
    booked_slots = sorted(booked_slots, key=lambda x: x[0])  # 按开始时间排序
    available_slots = []

    current_time = datetime.datetime.strptime(start_time, "%H:%M")
    end_time = datetime.datetime.strptime(end_time, "%H:%M")

    for slot in booked_slots:
        slot_start = datetime.datetime.strptime(slot[0], "%H:%M")
        slot_end = datetime.datetime.strptime(slot[1], "%H:%M")

        if current_time < slot_start:
            available_slots.append([current_time.strftime("%H:%M"), slot_start.strftime("%H:%M")])

        current_time = slot_end

    if current_time < end_time:
        available_slots.append([current_time.strftime("%H:%M"), end_time.strftime("%H:%M")])
    return available_slots


def get_free_tennis_court_infos(date: str, access_token: str, proxy_list: list) -> dict:
    """
    获取可预订的场地信息
    """
    got_response = False
    response = None
    index_list = list(range(len(proxy_list)))
    # 打乱列表的顺序
    random.shuffle(index_list)
    print(index_list)
    for index in index_list:
        check_data = str_to_timestamp(date)
        timestamp = math.trunc(time.time() * 1000)
        nonce = gen_nonce(timestamp)
        params = {
            "salesItemId": SALES_ITEM_ID,
            "curDate": str(check_data),
            "venueGroupId": "",
            "_time": str(timestamp)
        }
        param_str = f"salesItemId={SALES_ITEM_ID}&curDate={check_data}&venueGroupId=&_time={str(timestamp)}"  # 仅用于签名
        signature = signature_for_get(str(timestamp), nonce.replace('-', ''), param_str=param_str)
        headers = {
            "Host": "isz.ydmap.cn",
            "accept": "application/json, text/plain, */*",
            "openid-token": "",
            "nonce": nonce.replace('-', ''),
            "timestamp": str(timestamp),
            "sec-fetch-site": "same-origin",
            "x-requested-with": "XMLHttpRequest",
            "accept-language": "zh-CN,zh-Hans;q=0.9",
            "entry-tag": "",
            "signature": signature,
            "sec-fetch-mode": "cors",
            "access-token": access_token,
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5_1 like Mac OS X) AppleWebKit/605.1.15 "
                          "(KHTML, like Gecko) "
                          "Mobile/15E148/openweb=paschybrid/SZSMT_IOS,VERSION:4.5.0",
            "referer": F"https://isz.ydmap.cn/booking/schedule/{SALES_ID}?salesItemId={SALES_ITEM_ID}",
            "sec-fetch-dest": "empty"
        }
        url = "https://isz.ydmap.cn/srv100352/api/pub/sport/venue/getVenueOrderList"
        print(url)
        print(params)
        print(headers)
        proxy = proxy_list[index]
        print(f"trying for {index} time for {proxy}")
        try:
            proxies = {"https": proxy}
            response = requests.get(url, headers=headers, params=params, proxies=proxies, timeout=30)
            if response.status_code == 200:
                print(f"success for {proxy}")
                got_response = True
                time.sleep(1)
                break
            else:
                print(f"failed for {proxy}: {response}")
                continue
        except Exception as error:  # pylint: disable=broad-except
            print(f"failed for {proxy}: {error}")
            continue
    print(f"response: {response}")
    print(f"response: {response.text}")
    if got_response:
        if response.status_code == 200:
            if response.json()['code'] == 0:
                booked_court_infos = {}
                for data in response.json()['data']:
                    start_time = timestamp_to_clock(data['startTime'])
                    end_time = timestamp_to_clock(data['endTime'])
                    if booked_court_infos.get(data['venueId']):
                        booked_court_infos[data['venueId']].append([start_time, end_time])
                    else:
                        booked_court_infos[data['venueId']] = [[start_time, end_time]]
                available_slots_infos = {}
                for venue_id, booked_slots in booked_court_infos.items():
                    available_slots = find_available_slots(booked_slots)
                    available_slots_infos[venue_id] = available_slots
                return available_slots_infos
            else:
                raise Exception(response.text)
        else:
            raise Exception(response.text)
    else:
        raise Exception(f"all proxies failed")


def merge_time_ranges(data: List[List[str]]) -> List[List[str]]:
    """
    将时间段合并

    Args:
        data: 包含多个时间段的列表，每个时间段由开始时间和结束时间组成，格式为[['07:00', '08:00'], ['07:00', '09:00'], ...]

    Returns:
        合并后的时间段列表，每个时间段由开始时间和结束时间组成，格式为[['07:00', '09:00'], ['09:00', '16:00'], ...]
    """
    # 将时间段转换为分钟数，并按照开始时间排序
    data_in_minutes = sorted([(int(start[:2]) * 60 + int(start[3:]), int(end[:2]) * 60 + int(end[3:]))
                              for start, end in data])

    # 合并重叠的时间段
    merged_data = []
    start, end = data_in_minutes[0]
    for i in range(1, len(data_in_minutes)):
        next_start, next_end = data_in_minutes[i]
        if next_start <= end:
            end = max(end, next_end)
        else:
            merged_data.append((start, end))
            start, end = next_start, next_end
    merged_data.append((start, end))

    # 将分钟数转换为时间段
    result = [[f'{start // 60:02d}:{start % 60:02d}', f'{end // 60:02d}:{end % 60:02d}'] for start, end in merged_data]

    return result


def sort_key(item):
    return int(item.split("号")[0])


if __name__ == '__main__':
    run_start_time = time.time()
    # 每天0点-7点不巡检， 其他时间巡检
    now = datetime.datetime.now().time()
    if datetime.time(0, 0) <= now < datetime.time(7, 0):
        print('Skipping task execution between 0am and 7am')
        exit()
    else:
        print('Executing task at {}'.format(datetime.datetime.now()))

    # 获取公网HTTPS代理
    url = "https://raw.githubusercontent.com/claude89757/free_https_proxies/main/free_https_proxies.txt"
    response = requests.get(url)
    # 将文本内容按行分割，并去除每行两端的空格
    text = response.text.strip()
    print(text)
    proxy_list = [line.strip() for line in text.split()]
    print(proxy_list)

    # 查询空闲的球场信息
    available_tennis_court_slice_infos = {}
    for index in range(0, 7):
        check_date = (datetime.datetime.now() + datetime.timedelta(days=index)).strftime('%Y-%m-%d')
        print(f"checking {check_date}")
        available_tennis_court_slice_infos[check_date] = []
        free_tennis_court_infos = get_free_tennis_court_infos(check_date, ACCESS_TOKEN, proxy_list)
        available_tennis_court_slice_infos[check_date] = free_tennis_court_infos
        time.sleep(5)
    print(f"available_tennis_court_slice_infos: {available_tennis_court_slice_infos}")

    # 获取推送规则
    rule_list = get_rule_list_from_weida(ITEM_NAME)
    print(f"rule_list: {len(rule_list)}")
    for rule in rule_list:
        print(rule)
    print("-----------------------------------------")

    # 推送可预定时间段的消息列表，并特别标注晚上时间段的场地
    msg_list = [f"{ITEM_NAME}网球场可预定时间段"]
    found_court_infos = []
    for date, free_slot_infos in available_tennis_court_slice_infos.items():
        # 检查是否有符合日期的推送规则
        filter_rule_list = []
        for rule in rule_list:
            check_date = datetime.datetime.strptime(date, "%Y-%m-%d")
            rule_start_date = datetime.datetime.strptime(rule['start_date'], "%Y-%m-%d")
            rule_end_date = datetime.datetime.strptime(rule['end_date'], "%Y-%m-%d")
            if rule_start_date <= check_date <= rule_end_date:
                print(f"{date}在{rule['start_date']}和{rule['end_date']}之间")
                filter_rule_list.append(rule)
            else:
                print(f"{date}不在{rule['start_date']}和{rule['end_date']}之间")

        weekday = calendar.day_name[datetime.datetime.strptime(date, '%Y-%m-%d').date().weekday()]
        weekday_cn = {'Monday': '星期一', 'Tuesday': '星期二', 'Wednesday': '星期三', 'Thursday': '星期四',
                      'Friday': '星期五', 'Saturday': '星期六', 'Sunday': '星期日'}[weekday]
        date_and_weekday = f'{date}（{weekday_cn}）'
        msg_list.append(f"{date_and_weekday}")
        check_date_slot_list = []
        # 对每个时间段的场地进行检查，看看是否有符合条件的时间段
        for court_name, slots in free_slot_infos.items():
            print(f"slots: {slots}")
            # 将列表转换为元组，并将元组转换为集合，实现去重
            unique_data = set(tuple(item) for item in slots)
            # 将元组转换为列表，并按照第一个元素和第二个元素进行排序
            sorted_slot_list = sorted([list(item) for item in unique_data], key=lambda x: (x[0], x[1]))
            print(f"sorted_slot_list: {sorted_slot_list}")
            tag_slot_list = []
            for slot in sorted_slot_list:
                if not filter_rule_list:
                    # 无推送规则，无需进一步检查时间段
                    tag_slot_list.append(f"{slot[0]}-{slot[1]}")
                else:
                    # 有推送规则，详细继续检查时间段
                    cur_start_time = slot[0]
                    cur_end_time = slot[1]

                    hit_rule_list = []
                    for rule in filter_rule_list:
                        watch_start_time = rule['start_time']
                        watch_end_time = rule['end_time']
                        cur_start_time_obj = datetime.datetime.strptime(cur_start_time, "%H:%M")
                        cur_end_time_obj = datetime.datetime.strptime(cur_end_time, "%H:%M")
                        watch_start_time_obj = datetime.datetime.strptime(watch_start_time, "%H:%M")
                        watch_end_time_obj = datetime.datetime.strptime(watch_end_time, "%H:%M")
                        # 计算两个时间范围的交集
                        start_time = max(cur_start_time_obj, watch_start_time_obj)
                        end_time = min(cur_end_time_obj, watch_end_time_obj)
                        # 计算交集的时间长度
                        duration = end_time - start_time
                        if duration >= datetime.timedelta(minutes=60):
                            print("两个时间范围有交集，且交集的时间大于等于60分钟")
                            # 检查场地的结束时间比当前时间晚2小时以上
                            time_str = f"{date} {cur_end_time}"
                            time_obj = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M")
                            if time_obj > datetime.datetime.now() + datetime.timedelta(hours=2):
                                print(f"{time_str}比当前时间大于2小时, 来得及去打球")
                                hit_rule_list.append(rule)
                            else:
                                # print(f"{time_str}比当前时间小于等于2小时， 来不及去打球")
                                pass
                        else:
                            # print("两个时间范围没有交集，或者交集的时间小于60分钟")
                            pass
                    if hit_rule_list:
                        # 添加到待推送短信的列表中
                        for rule in hit_rule_list:
                            date_obj = datetime.datetime.strptime(date, '%Y-%m-%d')
                            formatted_date = date_obj.strftime('%m-%d')
                            found_court_infos.append({"phone": rule['phone'],
                                                      "date": f"{formatted_date} {weekday_cn}",
                                                      "court_index": court_name,
                                                      "start_time": slot[0],
                                                      "end_time": slot[1]})

                        tag_slot_list.append(f"`{slot[0]}`-`{slot[1]}`")
                    else:
                        tag_slot_list.append(f"{slot[0]}-{slot[1]}")
            if tag_slot_list:
                check_date_slot_list.append(f"{court_name}: {'|'.join(tag_slot_list)}")
            else:
                pass
        if check_date_slot_list:
            sorted_check_date_slot_list = sorted(check_date_slot_list)
            check_date_slot_msg = "\n".join(sorted_check_date_slot_list)
            msg_list.append(f"{check_date_slot_msg}")
        else:
            msg_list.append(f"> 无场")
        msg_list.append("")
    msg = "\n".join(msg_list)
    print("打印场地的可预订信息============================================")
    print(msg)
    print("============================================")

    # 汇总信息，并发送短信
    print(f"found_court_infos: {found_court_infos}")
    phone_slot_infos = {}
    for court_info in found_court_infos:
        if court_info['court_index'] == 102930:
            # 香蜜的6号场只能电话预定，这里先剔除
            continue
        else:
            pass
        print(court_info)
        key = f"{court_info['phone']}_{court_info['date']}"
        if phone_slot_infos.get(key):
            phone_slot_infos[key].append([court_info['start_time'], court_info['end_time']])
        else:
            phone_slot_infos[key] = [[court_info['start_time'], court_info['end_time']]]
    if not phone_slot_infos:
        print(F"无需要通知的场地信息")
    else:
        # 打开本地文件缓存
        script_name = os.path.splitext(os.path.basename(__file__))[0]  # 获取当前脚本的文件名
        cache = shelve.open(f'{script_name}_cache.db')
        print(f"phone_slot_infos: {phone_slot_infos}")
        for phone_date, slot_list in phone_slot_infos.items():
            print(f"sending {phone_date} sms of {slot_list}")
            merge_slot_list = merge_time_ranges(slot_list)
            print(f"merge_slot_list: {merge_slot_list}")
            cache_key = f"{phone_date}_{merge_slot_list[0][0]}_{merge_slot_list[0][0]}"
            if phone_date in cache:
                print(f"{cache_key} has already been sent, skipping...")
                continue
            else:
                # 执行任务
                phone = phone_date.split('_')[0]
                date = phone_date.split('_')[1]
                send_sms_for_news([phone], [date, ITEM_NAME, merge_slot_list[0][0], merge_slot_list[0][1]])
            # 更新本地文件缓存
            cache[phone_date] = 1
        # 关闭本地文件缓存
        cache.close()

    # 计算执行时间
    run_end_time = time.time()
    execution_time = run_end_time - run_start_time
    print(f"执行时间：{execution_time}秒")
