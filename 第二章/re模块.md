# Python `re` 模块学习总结

## 概述
`re` 是 Python 内置的正则表达式模块，用于对字符串进行模式匹配和提取操作。

---

## 一、常用匹配方法

### 1. `re.findall(pattern, string)`
匹配字符串中**所有**符合正则规则的内容，返回一个**列表**。

```python
import re
lst = re.findall(r"\d+", "我的电话是:10086, 女朋友电话:10010")
print(lst)  # ['10086', '10010']
```

### 2. `re.finditer(pattern, string)`
匹配所有符合正则的内容，返回一个**迭代器**。需要通过 `.group()` 拿到匹配的字符串。

```python
it = re.finditer(r"\d+", "我的电话是:10086, 女朋友电话:10010")
for i in it:
    print(i.group())  # 10086  10010
```

> **适用场景**：当匹配结果较多时，`finditer` 比 `findall` 更节省内存。

### 3. `re.search(pattern, string)`
**搜索**整个字符串，找到**第一个**匹配结果就返回。返回 match 对象，需用 `.group()` 取值。

```python
s = re.search(r"\d+", "我的电话是10086, 女朋友电话10010")
print(s.group())  # 10086（只返回第一个）
```

### 4. `re.match(pattern, string)`
从字符串的**开头**开始匹配，相当于在正则表达式前加了 `^`。如果开头不匹配则返回 `None`。

```python
s = re.match(r"\d+", "10086, 女朋友电话10010")
print(s.group())  # 10086
```

> **`match` vs `search`**：`match` 必须从开头匹配，`search` 可以在任意位置找第一个。

---

## 二、匹配对象方法 `.group()`

| 方法 | 作用 |
|------|------|
| `.group()` | 获取整个匹配到的字符串 |
| `.group(n)` | 获取第 n 个捕获组的内容 |
| `.group("name")` | 获取指定名称的捕获组内容（见命名分组） |

---

## 三、预加载正则表达式 `re.compile()`

提前编译正则表达式，提高重复使用时的效率。

```python
obj = re.compile(r"\d+")
ret = obj.finditer("我的电话是:10086, 女朋友电话:10010")
for i in ret:
    print(i.group())
```

### 常用 flags（标志位）
在 `compile()` 中可以指定标志位，多个标志用 `|` 连接：

| 标志 | 作用 |
|------|------|
| `re.S`（`re.DOTALL`） | 让 `.` 匹配**换行符**，避免跨行匹配断开 |
| `re.I`（`re.IGNORECASE`） | 忽略大小写 |
| `re.M`（`re.MULTILINE`） | 多行模式，`^` 和 `$` 匹配每一行的开头和结尾 |

```python
obj = re.compile(r"<div>.*?</div>", re.S)  # 让 . 匹配换行符
```

---

## 四、命名分组 `(?P<name>pattern)`

在正则中使用 `(?P<name>pattern)` 给捕获组**起名字**，方便从复杂的匹配结果中提取指定内容。

### 语法
```
(?P<组名>正则表达式)
```

### 示例：从 HTML 中提取数据
```python
import re

html = """<div class='jay'><span id='1'>郭麒麟</span></div>
<div class='jj'><span id='2'>宋铁</span></div>
<div class='jolin'><span id='3'>大聪明</span></div>
<div class='sylar'><span id='4'>范思哲</span></div>
<div class='tory'><span id='5'>胡说八道</span></div>"""

obj = re.compile(
    r"<div class='.*?'><span id='(?P<ID>\d)'>(?P<figure>.*?)</span></div>"
)
ret = obj.finditer(html)
for i in ret:
    print(i.group("ID"))      # 1 2 3 4 5
    print(i.group("figure"))  # 郭麒麟 宋铁 大聪明 范思哲 胡说八道
```

> **优势**：命名后不需要数括号位置，代码可读性大大提高。

---

## 五、常用正则元字符速查

| 元字符 | 含义 |
|--------|------|
| `.` | 匹配任意一个字符（默认不包含换行）|
| `\d` | 匹配一个数字（0-9）|
| `\w` | 匹配一个字母、数字或下划线 |
| `\s` | 匹配一个空白字符（空格、换行、制表符）|
| `+` | 匹配前一个字符 **1 次或多次** |
| `*` | 匹配前一个字符 **0 次或多次** |
| `?` | 匹配前一个字符 **0 次或 1 次** |
| `.*?` | **非贪婪**匹配任意字符（尽可能少匹配）|
| `.*` | **贪婪**匹配任意字符（尽可能多匹配）|

---

## 六、整体流程图

```
  原始字符串
      │
      ├── re.findall()  ──→  列表（所有结果）
      ├── re.finditer() ──→  迭代器 → .group() 逐个取出
      ├── re.search()   ──→  match对象（第一个结果）→ .group()
      ├── re.match()    ──→  match对象（从头匹配） → .group()
      └── re.compile()  ──→ 正则对象 ──→ 重复使用上述方法
             │
             └── (?P<name>pattern) 命名分组 → .group("name") 提取
```
