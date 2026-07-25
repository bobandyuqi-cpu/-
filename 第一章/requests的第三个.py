import requests
url="https://movie.douban.com/j/chart/top_list"#后面一大串是数据
#url链接过长需要重新封装
param={
"type": "20",
"interval_id":"100:90",
"action":"",
"start": 0,
"limit": 2
}
headers={
"user-agent":
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0"
}
resp=requests.get(url,params=param,headers=headers)
print(resp.json())