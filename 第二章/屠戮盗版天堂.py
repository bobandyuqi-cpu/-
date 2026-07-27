import requests
import re
import csv
a=0
url='https://www.dygod.vip/'
req=requests.get(url)#有时候会要vertify=False才可以过https验证
req.encoding="gb2312"
obj=re.compile(r'2026新片精品.*?<ul>(?P<title>.*?)</ul>',re.S)
i=obj.finditer(req.text)
child_href_list=[]
for item in i:
    urll=item.group('title')
#提取超链接
# html中a标签表示超链接如:<a href="url">宋雨琦</a>
obj2=re.compile(r"<a href='(?P<name>.*?)'",re.S)
j=obj2.finditer(urll)
for item in j:
    child_href=url+item.group('name').strip("/")
    child_href_list.append(child_href)
#提取子页面信息
obj3=re.compile(r'<head>.*?<title>.*?《(?P<ap>.*?)》.*?</title>.*?专治迅雷无法下载.*?<li><a href="jianpian://pathtype=url&path=(?P<ur>.*?)title=.*?"',re.S)
with open("2026新电影链接.csv","w",encoding="utf-8",newline='') as f:
    writer=csv.writer(f)
    for item in child_href_list:
        child_req=requests.get(item)
        child_req.encoding="gb2312"
        k = obj3.search(child_req.text)
        dic=k.groupdict()
        writer.writerow(dic.values())
        a=a+1
        print(f"成功爬取{a}部")
req.close()
print("over")



