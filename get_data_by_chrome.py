#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024-09-13
@Author  : claude
@File    : get_data_by_chrome.py
@Software: PyCharm
"""

import os
import re
import time
import random
import requests
import json
import base64
import datetime

import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup


FILENAME = "isz_data_infos.json"


def generate_proxies():
    """
    获取待检查的代理列表
    """
    urls = [
        "https://raw.githubusercontent.com/claude89757/free_https_proxies/main/isz_https_proxies.txt"
    ]
    proxies = []

    for url in urls:
        print(f"getting proxy list for {url}")
        response = requests.get(url)
        # 将文本内容按行分割，并去除每行两端的空格
        text = response.text.strip()
        lines = text.split("\n")
        lines = [line.strip() for line in lines]
        proxies.extend(lines)
        print(f"Loaded {len(lines)} proxies from {url}")
    print(f"Total {len(proxies)} proxies loaded")
    random.shuffle(proxies)
    return proxies


# 上传文件（相当于推送）
def upload_file_to_github(input_data):
    token = os.environ['GIT_TOKEN']
    repo = 'claude89757/tennis_helper'
    url = f'https://api.github.com/repos/{repo}/contents/{FILENAME}'

    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # 把data_list转换成content
    content = json.dumps(input_data)
    encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')

    data = {
        'message': f'Update proxy list by scf',
        'content': encoded_content,
        'sha': get_file_sha(url, headers)  # You need to get the SHA if you're updating an existing file
    }
    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 200:
        print(F"File uploaded successfully, total {len(input_data)} data")
    else:
        print("Failed to upload file:", response.status_code, response.text)


def get_file_sha(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['sha']
    return None


class TwitterWatcher:
    def __init__(self, timeout=10, headless: bool = True):
        self.driver_path = "/usr/local/bin/chromedriver"
        self.timeout = timeout
        self.interaction_timeout = 10
        self.driver = None
        self.headless = headless

    def setup_driver(self, proxy=None):
        chrome_options = Options()
        chrome_options.add_argument("--lang=cn")
        if self.headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        # 定义多个 User-Agent 字符串
        user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/128.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/128.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/14.1.1 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/14.1.1 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]

        # 随机选择一个 User-Agent
        random_user_agent = random.choice(user_agents)
        chrome_options.add_argument(f"user-agent={random_user_agent}")

        if proxy:
            chrome_options.add_argument(f'--proxy-server={proxy}')

        # Check Selenium version
        selenium_version = selenium.__version__

        if selenium_version.startswith('3'):
            self.driver = webdriver.Chrome(executable_path=self.driver_path, options=chrome_options)
        else:
            service = Service(self.driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def teardown_driver(self):
        if self.driver:
            self.driver.quit()

    def random_delay(self, min_delay=1, max_delay=3):
        time.sleep(random.uniform(min_delay, max_delay))

    def wait_for_element(self, by, value, timeout=None):
        timeout = timeout or self.timeout
        return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, value)))

    def wait_for_url_change(self, current_url, timeout=None):
        timeout = timeout or self.timeout
        WebDriverWait(self.driver, timeout).until(EC.url_changes(current_url))

    def solve_slider_captcha(self):
        slider = self.wait_for_element(By.CLASS_NAME, "btn_slide")
        action_chains = ActionChains(self.driver)

        # 点击并按住滑块
        action_chains.click_and_hold(slider).perform()
        time.sleep(random.uniform(0.5, 1.0))  # 模拟人类按住滑块的时间

        # 模拟人类滑动的过程
        total_offset = 300  # 滑动的总距离
        current_offset = 0
        while current_offset < total_offset:
            move_by = random.randint(10, 30)  # 每次滑动的距离
            action_chains.move_by_offset(move_by, 0).perform()
            current_offset += move_by
            time.sleep(random.uniform(0.01, 0.03))  # 每次滑动后的短暂延迟

        # 释放滑块
        action_chains.release().perform()
        time.sleep(random.uniform(0.5, 1.0))  # 模拟人类释放后的时间

    def transfer_cookies(self):
        cookies = self.driver.get_cookies()
        session = requests.Session()
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])
        return session

    def transfer_headers(self):
        headers = {
            'User-Agent': self.driver.execute_script("return navigator.userAgent;")
        }
        return headers


COOKIES_FILE = 'cookies.json'
HEADERS_FILE = 'headers.json'


def load_cookies_and_headers():
    if os.path.exists(COOKIES_FILE) and os.path.exists(HEADERS_FILE):
        with open(COOKIES_FILE, 'r') as f:
            cookies = json.load(f)
        with open(HEADERS_FILE, 'r') as f:
            headers = json.load(f)
        return cookies, headers
    return None, None


def save_cookies_and_headers(cookies, headers):
    with open(COOKIES_FILE, 'w') as f:
        json.dump(cookies, f)
    with open(HEADERS_FILE, 'w') as f:
        json.dump(headers, f)


def print_with_timestamp(*args, **kwargs):
    """
    打印函数带上当前时间戳
    """
    timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime())
    print(timestamp, *args, **kwargs)


if __name__ == '__main__':
    """
    遍历查询多个网球场的信息，并缓存到github上
    """
    # 每天0点-8点不巡检
    now = datetime.datetime.now().time()
    if datetime.time(0, 0) <= now < datetime.time(8, 0):
        print_with_timestamp('Skipping task execution between 0am and 8am')
        exit()
    else:
        print_with_timestamp('Executing task at {}'.format(datetime.datetime.now()))

    start_time = time.time()
    watcher = TwitterWatcher(headless=False)
    watcher.setup_driver()

    # 先正常登录网站
    url = "https://wxsports.ydmap.cn/booking/schedule/100220?salesItemId=100000"

    # 随机延迟模拟人类行为
    watcher.random_delay()
    watcher.random_delay()
    watcher.wait_for_element(By.TAG_NAME, "body", timeout=10)
    # 加载缓存的 cookies 和 headers
    cookies, headers = load_cookies_and_headers()
    if cookies and headers:
        watcher.driver.get(url)
        # 应用 cookies
        for cookie in cookies:
            watcher.driver.add_cookie(cookie)
        watcher.driver.get(url)  # 使用 cookies 重新加载页面
        watcher.driver.refresh()
        watcher.random_delay()
        print(f"使用缓存的 cookies 和 headers 访问页面。")
    else:
        watcher.driver.get(url)
        print(f"没有找到缓存，直接访问页面。")
    # 随机延迟模拟人类行为
    watcher.random_delay()
    watcher.random_delay()
    # 等待页面加载完成
    watcher.wait_for_element(By.TAG_NAME, "body", timeout=5)
    if "网球" in str(watcher.driver.page_source):
        print(f"[1] processing directly...")
        current_url = watcher.driver.current_url
        print(f"Current URL: {current_url}")
    elif "验证" in str(watcher.driver.page_source):
        print(f"[2] processing by slider...")
        watcher.random_delay()
        watcher.solve_slider_captcha()
        WebDriverWait(watcher.driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        # 获取当前的 URL 和新的 cookies、headers
        current_url = watcher.driver.current_url
        print(f"Current URL: {current_url}")
        cookies = watcher.driver.get_cookies()
        headers = {
            'User-Agent': watcher.driver.execute_script("return navigator.userAgent;")
        }
        print(f"cookies: {cookies}")
        print(f"headers: {headers}")
        # 重新缓存 cookies 和 headers
        save_cookies_and_headers(cookies, headers)
        # 应用 cookies
        for cookie in cookies:
            watcher.driver.add_cookie(cookie)
        watcher.driver.get(url)  # 使用 cookies 重新加载页面
    else:
        raise Exception(f"未知错误?")
    print(f"=====Success=====")

    url_infos = {
        "香蜜体育": "https://wxsports.ydmap.cn/booking/schedule/101332?salesItemId=100341",
        "莲花体育": "https://wxsports.ydmap.cn/booking/schedule/101335?salesItemId=100347",
        "大沙河": "https://wxsports.ydmap.cn/booking/schedule/100220?salesItemId=100000",
        "黄木岗": "https://wxsports.ydmap.cn/booking/schedule/101333?salesItemId=100344",
        "华侨城": "https://wxsports.ydmap.cn/booking/schedule/105143?salesItemId=105347",
    }
    try:
        output_data = {}
        for place_name, url in url_infos.items():
            print(f"Checking {place_name} {url}")
            try:
                watcher.driver.get(url)  # 重新加载页面

                # 随机延迟模拟人类行为
                watcher.random_delay()
                watcher.random_delay()
                watcher.random_delay()

                # 等待页面加载完成
                watcher.wait_for_element(By.TAG_NAME, "body", timeout=5)
                print(f"Current URL: {watcher.driver.current_url}")

                if "网球" in str(watcher.driver.page_source):
                    print(f"[1] processing directly...")
                    current_url = watcher.driver.current_url
                    print(f"Current URL: {current_url}")
                    # Get the page source
                    page_source = watcher.driver.page_source

                    # 等待日期滑动条加载
                    date_slider = WebDriverWait(watcher.driver, 10).\
                        until(EC.presence_of_element_located((By.CLASS_NAME, 'slider-box-datetime')))
                    # 获取所有日期元素
                    date_elements = date_slider.find_elements(By.CLASS_NAME, 'new-datetime')
                    # 遍历每个日期元素
                    index = 0
                    for date_element in date_elements:
                        # 获取日期文本
                        date_text = date_element.find_element(By.CLASS_NAME, 'datetime').text
                        week_text = date_element.find_element(By.CLASS_NAME, 'week').text
                        print(f"Processing date: {date_text}")
                        print(f"Processing week: {week_text}")

                        # 点击日期
                        if index == 0:
                            print("跳过点击今天的日期")
                            pass
                        else:
                            date_element.click()
                            watcher.random_delay()
                            watcher.random_delay()

                        # 使用BeautifulSoup解析页面
                        soup = BeautifulSoup(page_source, 'html.parser')

                        # 提取场馆名称
                        header_table = soup.find('table', class_='schedule-table__header')
                        venue_names = []
                        if header_table:
                            header_row = header_table.find('thead').find('tr')
                            header_cells = header_row.find_all('th')
                            for cell in header_cells:
                                venue_name = cell.get_text(strip=True)
                                if venue_name:  # 排除空单元格
                                    venue_names.append(venue_name)

                        # 初始化数据结构
                        venue_times = {venue: [] for venue in venue_names}

                        # 处理rowspan和colspan的函数
                        def expand_cell(row_index, col_index, rowspan, colspan):
                            for i in range(rowspan):
                                for j in range(colspan):
                                    key = (row_index + i, col_index + j)
                                    occupied_cells.add(key)


                        # 正则表达式匹配时间间隔
                        time_pattern = re.compile(r'\d{2}:\d{2}-\d{2}:\d{2}')

                        # 处理body表格
                        body_table = soup.find('table', class_='schedule-table__body')
                        if body_table:
                            body_rows = body_table.find_all('tr')
                            num_cols = len(venue_names)
                            # 记录因rowspan和colspan占用的单元格
                            occupied_cells = set()
                            for row_index, row in enumerate(body_rows):
                                col_index = 0
                                cells = row.find_all(['td', 'th'])
                                for cell in cells:
                                    # 跳过被占用的单元格
                                    while (row_index, col_index) in occupied_cells:
                                        col_index += 1
                                    # 获取rowspan和colspan
                                    rowspan = int(cell.get('rowspan', 1))
                                    colspan = int(cell.get('colspan', 1))
                                    # 获取当前列对应的场馆
                                    if col_index < num_cols:
                                        venue = venue_names[col_index]
                                        # 提取时间段和状态
                                        cell_text = cell.get_text(strip=True)
                                        # 使用正则表达式提取时间和状态
                                        if cell_text:
                                            time_matches = time_pattern.findall(cell_text)
                                            if time_matches:
                                                time_slot = '-'.join(time_matches)
                                                # 从单元格文本中移除时间以获取状态
                                                status = time_pattern.sub('', cell_text).strip()
                                                # 添加到场馆的列表中
                                                venue_times[venue].append({
                                                    'time': time_slot,
                                                    'status': status
                                                })
                                    # 标记因rowspan和colspan占用的单元格
                                    expand_cell(row_index, col_index, rowspan, colspan)
                                    col_index += colspan  # 移动到下一个列

                        # 将数据输出为JSON格式
                        # json_output = json.dumps(venue_times, ensure_ascii=False, indent=4)
                        if output_data.get(place_name):
                            output_data[place_name][f"{date_text}({week_text})"] = venue_times
                        else:
                            output_data[place_name] = {f"{date_text}({week_text})": venue_times}
                        print(output_data)
                        index += 1
                elif "验证" in str(watcher.driver.page_source):
                    print(f"[2] processing by slider...")
                    watcher.random_delay()
                    watcher.solve_slider_captcha()
                    WebDriverWait(watcher.driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

                    # 获取当前的 URL 和新的 cookies、headers
                    current_url = watcher.driver.current_url
                    print(f"Current URL: {current_url}")
                    cookies = watcher.driver.get_cookies()
                    headers = {
                        'User-Agent': watcher.driver.execute_script("return navigator.userAgent;")
                    }
                    print(f"cookies: {cookies}")
                    print(f"headers: {headers}")

                    # 重新缓存 cookies 和 headers
                    save_cookies_and_headers(cookies, headers)
                else:
                    print("[3] ？？？？？")
            except Exception as error:
                print(f"{place_name} failed: {str(error).splitlines()[0]}")
        upload_file_to_github(output_data)
    finally:
        watcher.teardown_driver()

    # 记录耗时
    cost_time = time.time() - start_time
    print(f"Total cost time：{cost_time} s")
