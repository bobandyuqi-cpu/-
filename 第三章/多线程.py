# #如果要导入多线程要导入一个包
from threading import Thread
# def func():
#     for i in range(100):
#         print("func",i)
#
# if __name__ == '__main__':
#     t = Thread(target=func)#带括号就不会乱,不带括号就会乱,func() 代表马上执行 func，等到函数跑完、循环打印完 0‑99，才会去创建线程对象。
#     t.start()
#     for i in range(100):
#         print("func",i)


#继承写法
class MyThread(Thread):
    def run(self):#更改run 方法相当于写入target
        for i in range(100):
            print('子线程',i)
if __name__ == '__main__':
    t = MyThread()
    t.start()
    for i in range(100):
        print('主线程',i)
