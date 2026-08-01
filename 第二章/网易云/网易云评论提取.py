import requests
from Crypto.Cipher import AES#爬虫加密模块
from base64 import b64encode#导入解码
import json
#加密过程:
# # var bVk4e = window.asrsea(JSON.stringify(i6y), bxo4q(["流泪", "强"]), bxo4q(BF0a.md), bxo4q(["爱心", "女孩", "惊恐", "大笑"]));
#             e8m.data = j2G.cq6e({
#                 params: bVk4e.encText,
#                 encSecKey: bVk4e.encSecKey
#             })

# 处理加密
d="data0"#此处的data0指提交的表单数据
e='01001'
f='00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
g='0CoJUm6Qyw8W8jud'
i='VD6vNUm7u8Wt9Pou'#由以下分析可知此处i可以随机,只要与enscrkey可以互相解密即可

                        #通过浏览器开发者控制台得到所有密钥
"""
    function a(a=16) {总之就是返回随机16位字符串
        var d, e, b = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", c = "";
        for (d = 0; a > d; d += 1)#循环16ci
            e = Math.random() * b.length,#随机数
            e = Math.floor(e),#取整
            c += b.charAt(e);#取字符串b里的e位置
        return c
    }
    function b(a, b) {
        var c = CryptoJS.enc.Utf8.parse(b)
          , d = CryptoJS.enc.Utf8.parse("0102030405060708")
          , e = CryptoJS.enc.Utf8.parse(a)
          , f = CryptoJS.AES.encrypt(e, c, {#aes加密,c是密钥
            iv: d,#偏移量
            mode: CryptoJS.mode.CBC #模式cbc
        });
        return f.toString()
    }
    function c(a, b, c) {#c不做随机加密
        var d, e;
        return setMaxDigits(131),
        d = new RSAKeyPair(b,"",c),
        e = encryptedString(d, a)
    }
    function d(d, e, f, g) {d:i6y数据    e:'010001'  f:在上面很长 g:'0CoJUm6Qyw8W8jud',i='g50hrVWCyeBMfu45'#我固定了
        var h = {} #声明空对象
          , i = a(16);#随机值,我在浏览器的控制台把他固定了,得到第二次加密的密钥
        return h.encText = b(d, g),#g密钥,d第一次加密
        h.encText = b(h.encText, i),#i是密钥,d第二次加密
        h.encSecKey = c(i, e, f),#从传入数据看以及程序内部没有随机方法,则若i定死结果必然定死
        h
    }
"""
#复现前端加密过程,分析可得可以省去i加密过程
def to_16(data0):#aes加密机制16的倍数
    cha=16-len(data0)%16
    data0+=chr(cha)*cha
    return data0

def get_encSecKey(): #当i='VD6vNUm7u8Wt9Pou'此时加密数据为这个
    return "70fe7631a28b4ea4dafc44b40025c99bbb115b60e08e5969a7ccb10c2c05d6573add701c74c0d0a7349bce452116670bd61b1888d208e81753a05bb275f789f51e54f6971ab86a78384713cdaae776268239415514783d35d8ed66eda008852f07d25d2d1c4a5cb04e0e619a721bed1b8130a031772c8ee641dbda71c38522e9"

def get_params(data0):#默认收到的是字符串
    first=enc_params(data0,g)
    second=enc_params(first,i)
    return second
def enc_params(data0,key):#复现加密过程
    IV="0102030405060708"
    data0= to_16(data0)
    aes=AES.new(key=key.encode("utf-8"),IV=IV.encode("utf-8"),mode=AES.MODE_CBC)#加密器
    bs=aes.encrypt(data0.encode('utf-8'))#得到加密数据但是不是utf-8形式需要解码成计算机看的懂的形式,还有加密一定要是16的倍数
    return str(b64encode(bs),"utf-8")

#解密data完成,可以正常修改data0的数据来爬取任意的评论区数据,发送请求得到评论结果
url = "https://music.163.com/weapi/comment/resource/comments/get"#评论区获取接口
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0",
    "Referer": "",            # ⬅️ 建议添加防盗链验证(可以不要只要token在data0里)
    "Cookie": ""}#⬅️ 建议添加防盗链验证(可以不要这里只要那个token在data0里)

#data就是表单 通过开发者工具知道需要包含 params 和 encSecKey 两个字段的字典
#定义传入数据data0为未加密,data1为data0通过网易加密,data为开发者工具拿到的data1
data0={
#================= 下面这些字段决定了你要爬"哪个界面"的评论,改完直接运行即可 =================
# 只有这个字典是"明文",上面的加密函数会自动帮你处理,所以只管放心改

# 登录令牌:登录网页后生成的凭证。可以 F12 → Network → 随便一个 weapi 请求的
# Form Data 里抄过来,或者从 Cookie 的 __csrf 字段取;不登录留空有时也能用
"csrf_token"
:"bc1b5a938f79d65b175ba0a26ec310a3",

# 游标:评论区翻页的"唯一开关"。第一页固定填 "-1"
# 之后把上一页响应里 data.cursor 的值填回来接力(实测单独改 pageNo 没用,见下方翻页循环)
"cursor"
:"-1",

# 偏移量:从第几条开始取(offset = 已取的条数)。简单理解:第一页0、第二页20、第三页40...
# 这个接口翻页以 cursor 为主,offset 保持 0 一般也行
"offset"
:"0",

# 排序方式(实测结论):0 = 倒序(从旧到新,会先翻出最早那批评论)   1 = 正序(从新到旧,当前值)
# 注意:这和"热度"无关!想爬最早的高赞评论,把 1 改成 0 即可
"orderType"
:"1",

# 页码:实测翻页不靠它(cursor 才是),保持 "1" 即可
"pageNo"
:"1",

# 每页条数:一次请求取多少条,网易对单次条数有限制,一般填 20
"pageSize"
:"20",

# ★★★★★ 最关键:rid + threadId 决定"爬哪个内容"的评论 ★★★★★
# 格式 = 前缀 + 内容类型 + 内容ID,其中 内容ID 就是网页地址栏里 id= 后面的数字
# 规律(实测 2026-08):只有歌单用 A_PL_0_,其余类型都是 R_ 开头
#     歌曲页  music.163.com/#/song?id=1329907658     →  R_SO_4_1329907658
#     歌单页  music.163.com/#/playlist?id=5127071989 →  A_PL_0_5127071989  (当前这行,唯一特例)
#     专辑页  music.163.com/#/album?id=xxxx          →  R_AL_3_xxxx
#     歌手页  music.163.com/#/artist?id=xxxx         →  R_AR_5_xxxx
#     视频页  music.163.com/#/video?id=xxxx          →  R_VI_62_xxxx
# 最保险的做法:打开目标页面 → F12 → Network → 刷新,找 weapi/comment 开头的请求,
# 直接把它 Form Data 里的 rid / threadId 原样复制过来,保证不会错
"rid"
:"A_PL_0_5127071989",

# 线程ID:和 rid 配套,用来标识"这一串评论",填和 rid 一样的内容即可
"threadId"
:"A_PL_0_5127071989"
}
data1={
    "params":get_params(json.dumps(data0)),#用json库把字典变为字符串
    "encSecKey":get_encSecKey()#网易拿到这个后反解i,只有得到正确的i,然后才可以用它来得到params,而我们提前固定i,得到encseckey相当于直接省略这一步了也就是不用再次复现加密过程了,也就是节省了解密时间
}
# (以下 data 是我早先从开发者工具复制的加密结果,仅作对照参考;实际请求用的是上面算出来的 data1,这段可以删掉)
data = {
    "params": "1JvTggr0djpiUvRxxui6PYqnARXwV/yGSCmknKd37Wy0s2EAh2jJw9gvJHql/NDgsru6zTRD+POO7xt1KUdKPCjW4GQlhJ6BtBR7rbrg9E33kP2Ej0fuNhwJ4/YzdZQOSlBlNnu4lIGyPEsIG6KyJc+25UJ0RIVSWzLDV4iW4FnPPoqTRvdC+eZJGU4dWWQwSlY2XV9JjyGMX8gjCFGVNLZ/h6jRbliGnACFmN8nYAVxzoEvYNlnPzMzpucNwnDSV9s6yfC5yWTWIXBN0t3Jrm6b24fUOtfVionjGIhrZpfDfJzqzUdnfgpsuq6Koa/NJdGpV5y5VgKvbND3p8EqcffEKtZZDhlvYZbNNY9TT4s=",
    "encSecKey": "1c38432ad8f1d0c0c9091f9d9cf6c2e52412c77867bd7b0654bf2f3693bf047091ce74062cab17c4d71df6df1fb9a6cb9e5e28bdbf8fcd4983bc777f79534789ef8625bc2258775d86cd291073680edd0aadde83d038fd26fb91ccb51dbfb004f2ae13e9bf94f609162682563acad9ad3776c81ffe5190842b28541147c25c74"  # ⬅️ 取消注释并放入字典
}

# ==================== 链接解析(把网页链接变成评论接口要的 rid) ====================
from urllib.parse import urlparse, parse_qs   # Python 内置库,用来拆解 URL

def parse_netease_url(url):
    """输入网易云网页链接,返回 (rid, 内容类型),如 ("R_SO_4_5257138", "song")。"""
    # 常见链接格式(要兼容好几种):
    #   https://music.163.com/#/playlist?id=5127071989   ← 路由藏在 # 后面
    #   https://music.163.com/playlist?id=5127071989     ← 路由就在路径里
    #   https://m.music.163.com/m/song?id=1329907658     ← 移动端,路径多一层 /m/
    # 思路:取出"内容类型 + id",再查前缀表拼成 rid
    u = urlparse(url)
    # 真实路由可能在 fragment(# 后)也可能在 path 里,取有值的那一个
    route = u.fragment.lstrip("/") if u.fragment else u.path.lstrip("/")
    # 内容类型 = 路由最后一段(兼容 /m/song 这种);id 从查询串里取
    type_part = route.split("?")[0].split("/")[-1]       # 如 playlist / song
    params = parse_qs(route.split("?", 1)[1]) if "?" in route else {}
    if not params:                                       # 兜底:id 在 path 后面的 ? 里
        params = parse_qs(u.query)
    id_val = (params.get("id") or [None])[0]
    if not id_val:
        raise ValueError("链接里没找到 id 参数,请确认链接格式")

    if type_part not in PREFIX_MAP:
        raise ValueError(f"暂不支持这种链接类型: {type_part}")
    return (PREFIX_MAP[type_part] + id_val, type_part)   # 返回 (rid, 内容类型)

import re   # 正则库,用来抠 <title> 标签

# 内容类型 → rid 前缀(实测 2026-08 验证):只有歌单用 A_PL_0_,其余都是 R_ 开头
PREFIX_MAP = {
    "song": "R_SO_4_",       # 歌曲
    "playlist": "A_PL_0_",   # 歌单(唯一特例)
    "album": "R_AL_3_",      # 专辑
    "artist": "R_AR_5_",     # 歌手
    "video": "R_VI_62_",     # 视频
    "mv": "R_MV_8_",         # MV
    "program": "R_DJ_1_",    # 电台
}

def type_from_rid(rid):
    """根据 rid 前缀反推内容类型(直接贴 rid 时用它,如 R_SO_4_xxx → song)"""
    for t, pre in PREFIX_MAP.items():
        if rid.startswith(pre):
            return t
    return ""

def build_name(title, content_type):
    """把页面标题转成安全的文件名。
    歌曲:歌名_歌手名(标题第二段就是歌手,如"屋顶 - 周杰伦/温岚/吴宗宪")
    其他:只取第一段(歌单名/专辑名等)"""
    title = re.sub(r'[\\/:*?"<>|]', "_", title)       # 非法字符 → _
    parts = [p.strip() for p in title.split(" - ")]  # 按 " - " 拆段
    name = parts[0]
    if content_type == "song" and len(parts) > 1:
        name = f"{name}_{parts[1]}"                   # 歌曲:歌名_歌手
    return name.rstrip(" .")[:40]

def get_page_title(raw_url):
    """请求页面 HTML,抓 <title> 当保存文件的命名依据。"""
    # 注意:#/ 只是前端路由,真正请求要拼回 music.163.com/song?id=xxx 这样的地址
    u = urlparse(raw_url)
    page_url = f"{u.scheme}://{u.netloc}/" + u.fragment.lstrip("/") if u.fragment else raw_url
    r = requests.get(page_url, headers={"User-Agent": headers["User-Agent"],
                                        "Referer": "https://music.163.com/"}, timeout=10)
    m = re.search(r"<title>(.*?)</title>", r.text, re.S)
    return m.group(1).strip() if m else ""   # 返回原始标题,build_name 负责加工

# ==================== 交互输入(程序跑起来后会停下来问你) ====================
# input("提示语") 会暂停运行,等你在终端里打字、回车,输入的内容以字符串返回
# 想恢复"写死数值"的话,把下面 input 都删掉,直接给变量赋值即可

# 1) 问:要爬哪个内容?贴网页链接,或直接贴 rid(如 A_PL_0_5127071989)
#    while True 循环:解析失败就提示重新输入,直到成功为止
while True:
    raw = input("粘贴网易云链接(歌单/歌曲/专辑/歌手/视频/MV/电台),或直接贴 rid:\n> ").strip()
    if raw.startswith(("A_", "R_")):      # 直接给的就是 rid 格式,跳过解析
        rid = raw
        content_type = type_from_rid(rid)  # 从前缀反推类型(可能为空)
        break
    try:
        rid, content_type = parse_netease_url(raw)   # 返回 (rid, 内容类型)
        print(f"  ✓ 解析成功: rid = {rid}")
        break
    except ValueError as e:
        print(f"  ⚠ {e},请重新粘贴。")

# 1.5) 顺便抓一下页面标题,给保存的文件起名
#      (贴的是链接才抓;贴的是 rid 或抓取失败,就退回用 rid 命名)
source_url = raw                 # 记录来源链接(存文件时写在最前面)
page_name = rid                  # 文件名兜底先用 rid
if not raw.startswith(("A_", "R_")):
    try:
        page_title = get_page_title(raw)
        page_name = build_name(page_title, content_type) or rid
        print(f"  ✓ 页面标题: {page_title}")
        print(f"  ✓ 命名: {page_name}")
    except Exception:
        page_name = rid           # 抓不到就用 rid 命名,不影响爬取

# 2) 问:爬几页?int() 把输入转成整数;0 = 一直爬到没有评论为止
try:
    page_limit = int(input("想爬几页?(0 = 一直爬到底): "))
except ValueError:   # 输入的不是数字(比如空回车)时 int() 会报错,这里兜底成 0
    print("  ⚠ 输入的不是数字,按 0(爬到底)处理。")
    page_limit = 0

# 3) 问:排序方式?这就是 data0 里的 orderType 字段,在这里运行时改它
#    直接回车 = 用默认值 "1"(从新到旧);"0" = 从旧到新
order_type = input("排序?0=从旧到新(倒序) 1=从新到旧(正序) [默认1]: ") or "1"

# 4) 问:打印详情?输入 y 或直接回车 = 打印每条评论;输入 n = 只打印进度和统计
print_detail = input("打印每条评论? y=是(默认) n=否: ").lower() != "n"

# 5) 问:要不要存文件?y = 存 CSV;x = 存 Excel;直接回车 = 不保存
save_choice = input("保存结果? y=csv  x=excel  回车=不保存: ").strip().lower()
# ======================================================================

# ==================== 翻页抓取 + 解析输出 ====================
# 写代码前先记住几条实测结论(2026-08 验证):
#   1) 翻页唯一靠 cursor(游标接力),单独改 pageNo 没用,保持 "1" 即可
#   2) hasMore 一直返回 False,不可靠;判断"还有没有下一页"= 本页是否取到评论
#   3) 精彩评论 hotComments 只在第一页(cursor=-1)稳定返回,之后是 null,只取第一次
#   4) orderType: 0=从旧到新(倒序)  1=从新到旧(正序)
#   5) totalCount 只是近似值(实测宣称 1873,实际翻完是 1994 条),不能拿它当停止条件,
#      必须翻到"空页"才停——下方 if not comments: break 就是在做这件事
from datetime import datetime  # 时间戳转可读时间(局部导入,不碰顶部解密代码)

# 复制一份 data0 作为"每页都要改"的请求数据,不动上面那个模板
req_data = dict(data0)
req_data["orderType"] = order_type   # 排序选择(加密会自动跟着变)
req_data["rid"] = rid                # 爬哪个内容
req_data["threadId"] = rid           # 和 rid 配套,保持一致

max_pages = 1000    # 安全上限:防止接口异常时死循环(一般不用动,想爬超长歌单再改大)
cursor = "-1"       # 游标:第一页固定 -1
page_no = 1
hot_comments = []   # 精彩评论(只在第一页取一次)
all_comments = []   # 收集到的全部普通评论

while page_no <= max_pages:
    # 翻到设定的页数就停(page_limit>0 才生效;0/负数=不限,继续爬)
    if page_limit > 0 and page_no > page_limit:
        print(f"已按设定爬到第 {page_limit} 页,停止。")
        break

    # 每次请求前重设游标并重新加密(游标变了,加密结果也必须跟着变)
    req_data["cursor"] = cursor
    req_data["pageNo"] = "1"
    data1 = {"params": get_params(json.dumps(req_data)), "encSecKey": get_encSecKey()}
    resp = requests.post(url, headers=headers, data=data1)

    result = json.loads(resp.text)  # JSON字符串 → 字典
    if result.get("code") != 200:   # 成功时 code == 200
        print("请求失败:", result.get("msg") or result.get("message"))
        break

    d = result["data"]
    comments = d.get("comments") or []

    # 精彩评论只在第一页(cursor=-1)出现,只取一次
    if page_no == 1 and d.get("hotComments"):
        hot_comments = d["hotComments"]

    all_comments.extend(comments)  # 把本页评论累加进总列表
    print(f"第{page_no}页: 取到 {len(comments)} 条 | 累计 {len(all_comments)} / {d.get('totalCount')}")

    # 本页一条评论都没有 → 说明翻到底了,退出循环
    if not comments:
        break

    # 游标接力:用本页返回的游标去翻下一页(个别响应没有 cursor 就停,防死循环)
    if d.get("cursor"):
        cursor = str(d["cursor"])
    else:
        break
    page_no += 1

# ==================== 解析评论字段 + 打印结果 ====================
def extract_comment(c):
    """把一条评论的字典,提取成常用字段元组(昵称, 内容, 时间, 点赞, 属地, commentId)"""
    user = c.get("user", {})
    return (
        user.get("nickname", "未知"),                # 昵称
        c.get("content", ""),                        # 正文
        datetime.fromtimestamp(c.get("time", 0) / 1000).strftime("%Y-%m-%d %H:%M:%S"),  # 时间(毫秒→秒→可读)
        c.get("likedCount", 0),                      # 点赞
        (c.get("ipLocation") or {}).get("location") or "",  # IP属地(老评论可能没有)
        c.get("commentId", ""),                      # 评论ID
    )

# 打印统一走这个小函数,精彩评论和普通评论都调它
def print_comment(idx, c):
    nickname, content, time_str, liked, location, _ = extract_comment(c)
    print(f"第{idx}条 | {nickname} | 点赞{liked} | 属地:{location}")
    print(f"  内容: {content}")
    print(f"  时间: {time_str}")
    # (选学)如果是回复别人的,beReplied 里放着被回复的那条
    # if c.get("beReplied"):
    #     print(f"  ↳ 回复了: {c['beReplied'][0].get('content', '')}")
    print("-" * 60)

if print_detail:
    # 先打印精彩评论(高赞),再打印全部普通评论
    if hot_comments:
        print(f"\n========== 精彩评论 {len(hot_comments)} 条 ==========")
        for idx, c in enumerate(hot_comments, 1):
            print_comment(idx, c)
    print(f"\n========== 普通评论 {len(all_comments)} 条 ==========")
    for idx, c in enumerate(all_comments, 1):
        print_comment(idx, c)
else:
    print(f"\n爬取完成: 精彩评论 {len(hot_comments)} 条 | 普通评论 {len(all_comments)} 条")
    print("(想看评论正文,下次运行时第4个问题输入 y 即可)")

# ==================== 保存结果(可选) ====================
# 先把所有评论拼成表格:第一列是类型(精彩/普通),后面是提取的字段
header = ["类型", "昵称", "评论内容", "时间", "点赞", "IP属地", "commentId"]
rows = [["精彩"] + list(extract_comment(c)) for c in hot_comments]
rows += [["普通"] + list(extract_comment(c)) for c in all_comments]

if save_choice == "y":   # 存 CSV:纯文本,Excel 也能直接打开(utf-8-sig 带 BOM,防止中文乱码)
    import csv
    filename = f"{page_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([f"来源链接: {source_url}"])   # 第一行:附上来源链接
        writer.writerow([])                             # 空一行
        writer.writerow(header)
        writer.writerows(rows)
    print(f"\n✓ 已保存 {len(rows)} 条评论到: {filename}")

elif save_choice == "x":  # 存 Excel .xlsx(需要 openpyxl,你的环境已装)
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "评论"
    ws["A1"] = f"来源链接: {source_url}"   # 最上面附上来源链接
    ws.append(header)                       # 表头(从第2行开始)
    for row in rows:
        ws.append(row)
    filename = f"{page_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    wb.save(filename)
    print(f"\n✓ 已保存 {len(rows)} 条评论到: {filename}")