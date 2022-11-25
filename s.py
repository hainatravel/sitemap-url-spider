import os
import argparse
from urllib import parse
from bs4 import BeautifulSoup
import threading
import queue
import requests

HOST = 'https://wwww.asiahighligts.com'
WORKER_NUM = 18  # 工作线程

PREPARE_URL_QUEUE = queue.Queue()  # 待抓取的URL队列
RESULT_URL_LIST = []  # 结果URL队列
THREAD_LOCK = threading.Lock()  # 线程锁


def save_result(auto_save=False):
    line_str = '\n'
    filename = HOST.replace('https://', '')
    if auto_save:
        filename += '_autosave.txt'
    else:
        filename += '.txt'
    with open(filename, 'w+', encoding='UTF-8') as file:
        file.write(line_str.join(RESULT_URL_LIST))


def do_threading():
    while True:
        URL = PREPARE_URL_QUEUE.get()  # 阻塞等待
        get_urls(URL)
        PREPARE_URL_QUEUE.task_done()


def get_urls(url):
    print(PREPARE_URL_QUEUE.qsize(), len(RESULT_URL_LIST), url)
    try:
        with requests.get(url=url) as response:
            soup = BeautifulSoup(response.text, "html.parser")  # 解析源码
            for link in soup.find_all('a'):  # 获取A元素
                temp_url = link.get('href')
                if temp_url:
                    temp_url = temp_url.lower().strip()  # 提取URL
                else:
                    continue
                # URL格式判断
                if temp_url == '':
                    continue
                # 或含有?或者#的不抓 带有https://前缀的网址需要先做替换
                elif temp_url.find('?') != -1 or temp_url.find('#') != -1 or temp_url.find(';') != -1 or temp_url.find('./') != -1 or temp_url.replace('://', '').find(':') != -1:
                    continue

                # 如果是以https开头的，取判断含有host，否则就是外网链接
                if (temp_url.find('http://', 0, 7) != -1 or temp_url.find('https://', 0, 8) != -1) and temp_url.find(HOST, 0, len(HOST)) == -1:
                    continue

                # 判断url开头，如果是/结尾，则需要补齐域名 是相对目录，需要补齐域名和/
                if temp_url.find(HOST, 0, len(HOST)) == -1:
                    if temp_url.find('/', 0, 1) == -1:
                        temp_url = HOST+'/'+temp_url
                    else:
                        temp_url = HOST+temp_url

                (url_path, url_ext) = os.path.splitext(temp_url)
                if url_ext != '':
                    if url_ext != '.htm' and url_ext != '.html':  # 有后缀且是.html .htm则抓
                        continue

                try:  # 添加线程锁
                    THREAD_LOCK.acquire(True)
                    if RESULT_URL_LIST.count(temp_url) == 0:
                        RESULT_URL_LIST.append(temp_url)
                        PREPARE_URL_QUEUE.put(temp_url)
                finally:
                    THREAD_LOCK.release()

    except Exception as e:
        print(e)


parser = argparse.ArgumentParser(description='一个sitemap抓取程序 -ycc')
parser.add_argument("--domain", type=str, default="",
                    required=True, help="网站域名 如 https://wwww.asiahighligts.com")
parser.add_argument("--thread", type=int, default=18,
                    required=False, help="线程数 默认18 数字越大越快")
args = parser.parse_args()

if args.domain == "":
    print("必须输入网站域名")
    exit()
else:
    if args.domain.find('/', len(args.domain)-1) == -1:
        HOST = args.domain
    else:
        HOST = args.domain[:-1]

if args.thread:
    WORKER_NUM = args.thread

if __name__ == '__main__':
    print('开始')
    PREPARE_URL_QUEUE.put(HOST)
    REFRESH_TOKEN_TIMER = threading.Timer(
        600, save_result, args=[True, ])  # 每10分钟存一次文件
    REFRESH_TOKEN_TIMER.daemon = True
    REFRESH_TOKEN_TIMER.start()
    for i in range(WORKER_NUM):
        threading.Thread(target=do_threading, daemon=True).start()
    PREPARE_URL_QUEUE.join()
    save_result()
    print('完成')
