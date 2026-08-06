import requests
import time
urls = [
    "https://c.ujpg.cc/2026/03/1264iicgu3ph3kh.jpg",
    "https://c.ujpg.cc/2026/03/1104onxeh0cgb4k.jpg",
    "https://c.ujpg.cc/2026/03/1103w5qx3kstzvr.jpg"
]
session = None
def init_session():
    global session
    session = requests.Session()

def download(url):
    name=url.split("/")[-1]
    with session.get(url) as response:
        with open(name, 'wb') as f:
            f.write(response.content)#同步不需要read一块一块的读取
    print(name,'下载完成')

def main():
    init_session()
    for url in urls:
        download(url)

if __name__ == '__main__':
    t1=time.time()
    main()
    t2=time.time()
    print(t2-t1)