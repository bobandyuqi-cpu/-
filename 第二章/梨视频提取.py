import requests
import os
import re
#拿到id
#拿到json,time以及视频加密url
#替换id和time
#得到真实视频url
#下载视频
def safe_filename(name):
    """将标题转为安全的文件夹/文件名"""
    # 去掉非法字符
    name = re.sub(r'[\\/:*?"<>|]', '', name)
    # 空格转下划线，压缩连续下划线
    name = re.sub(r'\s+', '_', name).strip('_')
    return name[:80]  # 限制长度
SAVE_DIR = r"D:\Users\bobandyuqi\Desktop\爬虫视频\梨视频"
url =input("请输入要提取的梨视频文章链接:")
headers = {
"referer":
url,
"user-agent":
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0"
}#referer防盗链,意思是该页面进入的源头链接,反爬措施之一

resp=requests.get(url,headers=headers)
obj=re.compile(r"<title>(?P<titel>.*?)-梨视频官网-Pear Video-梨网站</title>")
for i in obj.finditer(resp.text):
    titel = i.group("titel")
titel = safe_filename(titel)

contid=url.split("_")[1]

videpstatus=f"https://www.pearvideo.com/videoStatus.jsp?contId={contid}&mrd=0.1745515378849336"#mrd是随机数无效信息

js=requests.get(videpstatus,headers=headers).json()
# print(js)
encrypt_=js["systemTime"]

encrypt_url=js["videoInfo"]["videos"]["srcUrl"]
# print(encrypt_url)
# print(encrypt_)
#https://video.pearvideo.com/mp4/short/20260630/1785344234783-16078753-hd.mp4
#https://video.pearvideo.com/mp4/short/20260630/cont-1806681-16078753-hd.mp4
real_="cont-"+contid
real_url=encrypt_url.replace(encrypt_,real_)
print(real_url)

if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)#检查创建目录
save_path = os.path.join(SAVE_DIR,f"{titel}.mp4")#拼接绝对路径
with open(save_path,"wb") as f:#写入绝对路径
    f.write(requests.get(real_url,timeout=15).content)#以content二进制的形式写入

print("视频已经下载")
