# sitemap-url-spider
抓取网站源码并分析链接URL，用于生成sitemap，可开多个线程，速度非常快

# 安装说明
pip install BeautifulSoup requests threading queue

# 运行说明
python s.py --domain https://www.xxxxx.com --thread 18

### 参数说明
--domain  必填 网站域名 如 https://wwww.xxxxx.com

--thread 可选 线程数 默认18 数字越大越快
