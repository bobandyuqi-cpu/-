#防止自己的ip被永久封锁导致自身利益受损可以使用他人的ip来进行爬取
#网上一般有所谓的免费ip代理,透明是可用的
#假如一个代理IP以及端口为:8.134.140.146:8081
from jsonpointer import resolve_pointer
import requests
ip="8.134.140.146:8081"
proxies={
    "http":f"http://{ip}",
    "https":f"http://{ip}",
}
resp=requests.get("https://www.baidu.com/",proxies=proxies)
resp.encoding="utf-8"
print(resp.text)