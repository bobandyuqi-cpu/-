#因为根据检查发现数据是存在于页面源代码的所以可以直接
#1.拿到页面源代码
#2.通过re来提取想要的数据
#3.通过csv存储数据
import re
import csv
import requests
url="https://movie.douban.com/top250"
b=0
for a in range(0,250,25):
    params = {
        "start":a,
        "filter":"",
              }
    headers = {"user-agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0"}
    req=requests.get(url,headers=headers,params=params)
    page_content=req.text
    #准备文件
    f=open("top250.csv","a",newline='',encoding="utf-8")#必须加 newline=''，否则在 Windows 上写入时会出现多余的空行,window一定要encoding,utf-8
    csvwriter=csv.writer(f)
    #解析数据
    obj=re.compile(r'<li>.*?<span class="title">(?P<name>.*?)</span>.*?<div class="bd">.*?<br>(?P<year>.*?)&nbsp;/&nbsp.*?v:average">(?P<grade>.*?)</span>',re.S)
    date=obj.finditer(page_content)
    if b==0:
            csvwriter.writerow(["电影名","年份","评分"])
    for i in date:
        dic =i.groupdict()
        dic['year']=dic['year'].strip()
        csvwriter.writerow(dic.values())
    f.close()
    print(f"over{a//25}")
    b=b+1
req.close()