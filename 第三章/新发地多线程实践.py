import requests
import csv
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import time
Max_try=3


#=========名称转换区===========
def get_province_map():
    """构造 全称<->简称 映射字典"""
    province_data = [
        ("北京市", "京"),
        ("天津市", "津"),
        ("上海市", "沪"),
        ("重庆市", "渝"),
        ("河北省", "冀"),
        ("山西省", "晋"),
        ("辽宁省", "辽"),
        ("吉林省", "吉"),
        ("黑龙江省", "黑"),
        ("江苏省", "苏"),
        ("浙江省", "浙"),
        ("安徽省", "皖"),
        ("福建省", "闽"),
        ("江西省", "赣"),
        ("山东省", "鲁"),
        ("河南省", "豫"),
        ("湖北省", "鄂"),
        ("湖南省", "湘"),
        ("广东省", "粤"),
        ("海南省", "琼"),
        ("四川省", "川"),
        ("贵州省", "贵"),
        ("云南省", "云"),
        ("陕西省", "陕"),
        ("甘肃省", "甘"),
        ("青海省", "青"),
        ("台湾省", "台"),
        ("内蒙古自治区", "蒙"),
        ("广西壮族自治区", "桂"),
        ("西藏自治区", "藏"),
        ("宁夏回族自治区", "宁"),
        ("新疆维吾尔自治区", "新"),
        ("香港特别行政区", "港"),
        ("澳门特别行政区", "澳")
    ]
    full2short = {full: short for full, short in province_data}#相当于拿short
    short2full = {short: full for full, short in province_data}
    return full2short, short2full


# 获取两个映射表
full_to_short, short_to_full = get_province_map()


def short_to_name(short_str: str):#避免出现连在一起的名称
    """
    简称转省份全称
    支持多产地例如 "冀京蒙" 拆分返回列表
    """
    res = []
    for s in short_str:
        if s in short_to_full:
            res.append(short_to_full[s])
    return res


def name_to_short(name_list: list):
    """省份全称列表转为简称"""
    return [full_to_short[name] for name in name_list if name in full_to_short]


f=open("新发地.csv",mode="a",encoding="utf-8",newline="")
csvwriter=csv.writer(f)
#===============创建多线程池===============
def download_one(number):
    for attempt in range(1,Max_try+1):
        try:
            url = "http://www.xinfadi.com.cn/getPriceData.html"
            headers = {
        "user-agent": "",
        "Mozilla/5.0": "(Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0"
    }
            data = {
                "limit":
                    20,
                "current":
                    number,
                "pubDateStartTime":
                    "2024/01/01"
            }
            response = requests.post(url, data=data,headers=headers)
            res = response.json()
            tetx=response.text.strip()
            if not tetx:
                # print(f"第{number}页失败,第{attempt}次尝试")
                time.sleep(1)
                continue#空白响应不会触发代码异常，所以不会掉进 except，自然不会被错误捕获到
            for food in res['list']:
                spename = food['prodName']
                name = food['prodCat']
                price = food['avgPrice']
                place = food['place']
                zhuan = short_to_name(place)
                speplace = ','.join(zhuan)
                datadata=food['pubDate']
                datadata=datadata.replace("00:00:00",'')
                # print(f'{spename},种类:{name},价格:{price},产地:{speplace},发布时间:{datadata}')
                csvwriter.writerow([spename, name, price, speplace,datadata])
            print(f"第{number}页完成")
            break  # [改] 成功后立即退出重试循环,否则同一页会因每次成功的尝试而重复打印/重复写入CSV
        except Exception as err:
            # print(f"第{number}页 请求失败，报错:{err}")
            time.sleep(1)
    else:  # [改] for...else:仅当上面的循环从未被break(即3次尝试全部失败/空白响应)才打印失败,成功页不会再误报
        print(f"第{number}页已经尝试最大次数,失败获取")
        return number  # [改] 把失败的页号返回给主程序,让主程序收集起来稍后补抓,保证数据完整

def run_batch(page_list):
    """[改] 提交一批页号,返回没成功的页号列表,主程序据此补抓失败页"""
    with ThreadPoolExecutor(3) as t:
        futures = [t.submit(download_one, n) for n in page_list]
    failed = []
    for f in futures:
        r = f.result()
        if r is not None:
            failed.append(r)
    return failed


if __name__ == '__main__':
    # for number in range(1, 100):
    #     download_one(number)效率极低
    failed = run_batch(range(1, 100))
    print("========================done===========================")
    # [改] 实测接口 count=432905,1~99页全有数据,"失败获取"只是临时被限流/网络抖动。
    #     把失败页隔几秒补抓几轮,直到补齐为止,这才是真正的完整数据
    for round_num in range(1, 4):
        if not failed:
            break
        print(f"第{round_num}轮重试,剩余失败页:{failed}")
        time.sleep(3)  # [改] 隔几秒再试,给服务器缓冲,降低被限流概率
        failed = run_batch(failed)
    if failed:
        print(f"多次重试后仍有失败页:{failed},建议稍后再跑或检查网络")
    else:
        print("所有页面都已完整获取")