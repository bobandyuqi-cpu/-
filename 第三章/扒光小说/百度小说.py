#https://dushu.baidu.com/api/pc/getCatalog?data={"book_id":"4306063500"}目录
#https://dushu.baidu.com/api/pc/getChapterContent?data={"book_id":"4306063500","cid":"4306063500|1569782244","need_bookinfo":1}内容
#https://dushu.baidu.com/pc/detail?gid=4306063500
import re
import requests
import aiohttp
import asyncio


session = None
sem = None
"""
1.同步拿章节cid
2.异步拿所有cid内容
"""
def getcid(url):
    # 从 url 里用正则抠出 book_id
    obj = re.compile(r'data=\{"book_id":"(?P<ID>.*?)"\}')
    b_id = obj.search(url).group('ID')

    dic = requests.get(url).json()
    chapters = []                              # 把 (cid, title) 收集起来，return 给 main 用
    for item in dic['data']['novel']['items']:
        cid = item['cid']
        title = item['title']
        chapters.append((cid, title))
    return b_id, chapters


async def initsession():
    global session, sem
    session = aiohttp.ClientSession()
    sem = asyncio.Semaphore(10)                # 限流：最多同时 10 个请求，别把接口打挂


async def aiocontent(cid, b_id, title):
    url = ('https://dushu.baidu.com/api/pc/getChapterContent?data='
           '{"book_id":"' + b_id + '","cid":"' + b_id + '|' + cid + '","need_bookinfo":1}')
    async with sem:                            # 每个协程进门前先拿信号量
        async with session.get(url) as response:
            resp = await response.json()
            content = resp['data']['novel']['content']
    print(title)                               # 下完一章打印一章
    return title, content


async def main(url1,book_name):
    await initsession()
    # 1.同步拿章节cid
    b_id, chapters = getcid(url1)
    print(f'共 {len(chapters)} 章，开始异步下载{book_name}...')

    # 2.异步拿所有cid内容
    tasks = [aiocontent(cid, b_id, title) for cid, title in chapters]
    results = await asyncio.gather(*tasks)     # gather 按 tasks 顺序返回，章节不乱序

    # 3.按顺序写进同一个文件
    with open(f"{book_name}.txt", 'w', encoding='utf-8') as f:
        for title, content in results:
            f.write(title+'\n\n' +content + '\n\n')

    await session.close()
    print(f'完成，共下载 {len(results)} 章')


if __name__ == '__main__':
    url=input('请输入要爬取的百度小说的网址:')
    obj=re.compile(r'detail\?gid=(?P<b_id>\d+)')#此处若为.*?只能匹配空
    ret=obj.finditer(url)
    for item in ret:
        b_id=item.group('b_id')
    url1 = 'https://dushu.baidu.com/api/pc/getCatalog?data={"book_id":"' + b_id + '"}'
    url2=url1.replace('getCatalog','getDetail')
    resp = requests.get(url2)
    book_name = resp.json()['data']['novel']['book_name']
    asyncio.run(main(url1,book_name))
