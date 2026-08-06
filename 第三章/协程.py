#我对协程的理解就是单线程实现多任务并发达到类似多线程的实现
import asyncio
import time


async def download(url):
    print('开始下载')
    await asyncio.sleep(1)
    print('下载完成')

async def main():
    urls={
        1,
        2,
        3,
    }
    tasks=[]
    for url in urls:
        d=asyncio.create_task(download(url))
        tasks.append(d)
    await asyncio.wait(tasks)

if __name__ == '__main__':
    t0=time.time()
    asyncio.run(main())
    t1=time.time()
    total=t1-t0
    print(total)
