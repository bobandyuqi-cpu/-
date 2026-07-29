import requests
from bs4 import BeautifulSoup
import time
import os
url="https://www.xiurenlu.com/"
search="search/?s="
name=input("请输入要查询的图片信息:")
save_dir = rf"D:\Users\bobandyuqi\Desktop\爬虫图片\{name}"#可以自行修改下载路径
# 文件夹不存在自动创建
if not os.path.exists(save_dir):
    os.makedirs(save_dir)
for p in range(1):#自行修改下载的页数
    headers={
    "user-agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0"
    }
    params={
    "page":
    p
    }
    resp=requests.get(url+search+name,headers=headers,params=params)
    resp.encoding="utf-8"
    main_page=BeautifulSoup(resp.text,"lxml")#features是解析器的意思
    flist=main_page.find_all("figure")
    alist=main_page.find_all("a", class_="xr-purchase-card")
    # for item in flist:
    #     src=item.find_all("img")
    #     for img in src:
    #         src=img.get("src")
    #         if src:
    #             print(src)
    #                                  # 拿到预览图


    # for a in alist:
    #     href = a.get("href")
    #     full_url = url + href.strip("/")
    #     title = a.find("h3").get_text(strip=True)
    #     print("作品集标题：", title)
    #     print("详情页链接：", full_url)
                                    #拿到预览子链接


    for item in flist:
        # 1.提取详情链接+标题
        a_tag = item.parent
        if a_tag.name == "a":
            href = a_tag.get("href")
            full_href = url + href.strip("/")
            h3 = a_tag.find("h3")
            if h3:
                title = h3.get_text(strip=True)
                print("标题：", title)
                print("详情页：", full_href)


        # 2.提取预览图片
        safe_title = title.replace('\\', '_').replace('/', '_').replace(':', '_').replace('*', '_').replace('?',
                                                                                                            '_').replace(
            '"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
        img = item.find("img")
        if img:
            pic_src = img.get("src")
            print("预览图：", pic_src)
        file_path = os.path.join(save_dir, safe_title + ".jpg")
        # 下载图片
        img_resp = requests.get(pic_src)
        with open(file_path,"wb") as f:
             f.write(img_resp.content)
        time.sleep(1)
        print("预览图已下载")
        print("-" * 50)                         #拿到三件套
    print("over")
