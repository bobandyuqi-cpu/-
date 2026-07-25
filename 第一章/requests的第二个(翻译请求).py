import requests

url = "https://fanyi.baidu.com/sug"
s = input("请输入你要查询的单词: ")

resp = requests.post(url, data={"kw": s})
result = resp.json()

# 核心修改：用 result["data"] 替代之前的 result["g"]
if result.get("data"):
    for item in result["data"]:
        print(f"{item['k']} → {item['v']}")
else:
    print("未找到相关翻译")
