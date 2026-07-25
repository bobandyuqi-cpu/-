import requests

url="https://fanyi.baidu.com/sug"

req=requests.post(url)
s=input("请输入你要查询的单词:")
dat={
    "kw":f"{s}"
}
resp=requests.post(url,data=dat)
print(resp.json())#这里直接将要处理的数据变为json

