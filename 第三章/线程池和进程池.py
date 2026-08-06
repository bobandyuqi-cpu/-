#线程池:一次性1开辟一些线程,我们用户直接给线程池提交任务,线程任务的调度交给11线程池来完成1
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

def func1(name):
    for i in range(1000):
        print(name,i)

if __name__ == '__main__':
    with ThreadPoolExecutor(50) as executor:
        for i in range(100):
            executor.submit(func1,name=f'线程{i}')
    print('over')
