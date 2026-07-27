import re

from mplfinance import figure

#findall: 匹配字符串中所有的符合正则的内容
lit=re.findall(r"\d+","我的电话号是:10086,我女朋友的电话是10010")
print("findall:")
print(lit)

#finditer:匹配字符串中所有的内容(返回的是迭代器),从迭代器中拿到内容需要.group()
it=re.finditer(r"\d+","我的电话号码是:10086,我女朋友的电话号码是:10010")
print("finditer:")
print(it)
for i in it:
    print(i.group())

#search,找到一个结果就返回,返回的结果是match对象,拿数据需要.group()
s=re.search(r"\d+","我的电话号码是10086,我女朋友的电话号码是:10010")
print("search:")
print(s)
print(s.group())

#match是从头开始匹配,相当于正则前面加个^
s=re.match(r"\d+","10086,我女朋友的电话号码是:10010")
print("match:")
print(s)
print(s.group())

#预加载正则表达式,在compile里面最后加上re.S可以让.匹配换行符避免断开
obj=re.compile(r"\d+")
ret=obj.finditer("我的电话号码是:10086,我女朋友的电话是:10010")
print("complile:")
for i in ret:
    print(i.group())
#案例1(?P<name>正则),可以单独从正则匹配的内容中进一步提取内容
html="""<div class='jay'><span id='1'>郭麒麟</span></div>
<div class='jj'><span id='2'>宋铁</span></div>
<div class='jolin'><span id='3'>大聪明</span></div>
<div class='sylar'><span id='4'>范思哲</span></div>
<div class='tory'><span id='5'>胡说八道</span></div>"""

obk=re.compile(r"<div class='.*?'><span id='(?P<ID>\d)'>(?P<figure>.*?)</span></div>")
ret=obk.finditer(html)
for i in ret:
    print(i.group("ID"))
    print(i.group("figure"))