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
"csrf_token"
:"bc1b5a938f79d65b175ba0a26ec310a3",

"cursor"
:"-1",

"offset"
:"0",

"orderType"
:"1",

"pageNo"
:"1",

"pageSize"
:"20",

"rid"
:"A_PL_0_5127071989",

"threadId"
:"A_PL_0_5127071989"
}
data1={
    "params":get_params(json.dumps(data0)),#用json库把字典变为字符串
    "encSecKey":get_encSecKey()#网易拿到这个后反解i,只有得到正确的i,然后才可以用它来得到params,而我们提前固定i,得到encseckey相当于直接省略这一步了也就是不用再次复现加密过程了,也就是节省了解密时间
}
data = {
    "params": "1JvTggr0djpiUvRxxui6PYqnARXwV/yGSCmknKd37Wy0s2EAh2jJw9gvJHql/NDgsru6zTRD+POO7xt1KUdKPCjW4GQlhJ6BtBR7rbrg9E33kP2Ej0fuNhwJ4/YzdZQOSlBlNnu4lIGyPEsIG6KyJc+25UJ0RIVSWzLDV4iW4FnPPoqTRvdC+eZJGU4dWWQwSlY2XV9JjyGMX8gjCFGVNLZ/h6jRbliGnACFmN8nYAVxzoEvYNlnPzMzpucNwnDSV9s6yfC5yWTWIXBN0t3Jrm6b24fUOtfVionjGIhrZpfDfJzqzUdnfgpsuq6Koa/NJdGpV5y5VgKvbND3p8EqcffEKtZZDhlvYZbNNY9TT4s=",
    "encSecKey": "1c38432ad8f1d0c0c9091f9d9cf6c2e52412c77867bd7b0654bf2f3693bf047091ce74062cab17c4d71df6df1fb9a6cb9e5e28bdbf8fcd4983bc777f79534789ef8625bc2258775d86cd291073680edd0aadde83d038fd26fb91ccb51dbfb004f2ae13e9bf94f609162682563acad9ad3776c81ffe5190842b28541147c25c74"  # ⬅️ 取消注释并放入字典
}

resp = requests.post(url, headers=headers, data=data1)#必须传入data0的加密后的data1才可以返回结果
print(resp.text)