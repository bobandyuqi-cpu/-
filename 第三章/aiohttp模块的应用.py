import asyncio
import time

import aiohttp
import aiofiles

session = None

urls = [
    "https://c.ujpg.cc/2026/03/1264iicgu3ph3kh.jpg",
    "https://c.ujpg.cc/2026/03/1104onxeh0cgb4k.jpg",
    "https://c.ujpg.cc/2026/03/1103w5qx3kstzvr.jpg"
]


async def initsession():
    global session
    session = aiohttp.ClientSession()


async def aiodownload(url):
    name = url.split("/")[-1]
    async with session.get(url) as response:
        # aiofiles.open 才是异步文件打开，支持async with
        async with aiofiles.open(name, "wb") as f:
            await f.write(await response.content.read())
    print(f"{name} 下载完成")


async def main():
    # 初始化会话（同一个事件循环内）
    await initsession()

    # 构建任务列表，实现并发下载
    tasks = [aiodownload(u) for u in urls]
    await asyncio.gather(*tasks)

    # 关闭会话释放TCP连接
    await session.close()


if __name__ == '__main__':
    t1 = time.time()
    asyncio.run(main())
    t2 = time.time()
    t=t2-t1
    print(t)
