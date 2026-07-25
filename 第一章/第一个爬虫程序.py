from urllib.request import urlopen
from urllib.parse import urlparse

url=input("请输入你的要爬取的网站:")

# 解析URL，提取域名部分
hostname = urlparse(url).hostname  # 得到 "www.name.com"

# 去掉 "www." 前缀，再取第一个点之前的部分
name = hostname.replace("www.", "").split(".")[0]


try:
    resp = urlopen(url)
    html_bytes = resp.read()

    # 推荐方式：以二进制模式写入，避免编码问题
    with open(f"{name}.html", mode="wb") as f:
        f.write(html_bytes)

    print("over")

except Exception as e:
    print(f"请求失败: {e}")