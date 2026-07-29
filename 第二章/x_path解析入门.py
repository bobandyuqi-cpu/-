"""
======================== XPath 解析入门 ========================

XPath 是一门在 XML 文档中查找信息的语言，HTML 是 XML 的一个子集，所以 XPath 也常用于 HTML 解析。

本文件通过 lxml 库演示 XPath 的各种用法，代码按照从基础到进阶的顺序排列。
"""

from lxml import etree

# ======================== 1. 准备测试数据 ========================

xml = """
<book>
    <id>1</id>
    <name>野花遍地香</name>
    <price>1.23</price>
    <nick>臭豆腐</nick>

    <author>
        <nick id="10086">周大强</nick>
        <nick id="10010">周芷若</nick>
        <nick class="joy">周杰伦</nick>
        <nick class="jolin">蔡依林</nick>
        <div>
            <nick>惹了</nick>
        </div>
    </author>

    <partner>
        <nick id="ppc">胖胖陈</nick>
        <nick id="ppbc">胖胖不陈</nick>
    </partner>

    <tags>
        <tag>Python</tag>
        <tag>爬虫</tag>
        <tag>XPath</tag>
    </tags>
</book>
"""

tree = etree.XML(xml)  # 解析 XML 字符串为 ElementTree 对象


# ======================== 2. 基础路径表达式 ========================
# XPath 路径表达式与文件系统路径类似：
#   /    → 从根节点选取（绝对路径）
#   //   → 从任意位置选取（相对路径）
#   .    → 当前节点
#   ..   → 父节点
#   @    → 选取属性

print("=" * 60)
print("【1】最基本的路径（绝对路径 和 双斜杠）")
print("=" * 60)

# ---- 2.1 绝对路径：/ ----
# /book/name   → 选取根 <book> 下的 <name> 子元素
result = tree.xpath("/book/name")
print(f"/book/name           → {result}")          # [<Element name at ...>]
print(f"  .text              → {result[0].text}")  # 野花遍地香

# /book/nick   → 直接子元素中的 <nick>
result = tree.xpath("/book/nick")
print(f"/book/nick           → {result}")
print(f"  文本内容            → {[el.text for el in result]}")  # ['臭豆腐']

# ---- 2.2 相对路径：// ----
# //nick  → 文档中所有 <nick> 元素（不关心层级）
result = tree.xpath("//nick")
print(f"\n//nick               → 共 {len(result)} 个元素")
for el in result:
    print(f"  - {el.text}")

# ---- 2.3 混合路径 ----
# /book/author//nick  → /book/author 后代中的所有 <nick>
result = tree.xpath("/book/author//nick")
print(f"\n/book/author//nick   → {[el.text for el in result]}")
# 输出: ['周大强', '周芷若', '周杰伦', '蔡依林', '惹了']


print("\n" + "=" * 60)
print("【2】选取属性值 和 文本内容")
print("=" * 60)

# ---- 2.4 获取属性 ----
# @id    → 选取 id 属性
result = tree.xpath("//nick/@id")
print(f"//nick/@id           → {result}")  # ['10086', '10010', 'ppc', 'ppbc']

result = tree.xpath("//nick/@class")
print(f"//nick/@class        → {result}")  # ['joy', 'jolin']

# ---- 2.5 获取文本 ----
# text() → 获取节点文本
result = tree.xpath("//price/text()")
print(f"//price/text()       → {result}")  # ['1.23']

result = tree.xpath("//nick/text()")
print(f"//nick/text()        → {result}")  # ['臭豆腐', '周大强', '周芷若', '周杰伦', '蔡依林', '惹了', '胖胖陈', '胖胖不陈']


print("\n" + "=" * 60)
print("【3】谓语（Predicate）— 带条件的筛选 []")
print("=" * 60)

# 谓语放在方括号 [] 中，用来筛选节点

# ---- 3.1 索引筛选（注意：XPath 索引从 1 开始！） ----
# //nick[1]   → 文档中第一个 <nick>
result = tree.xpath("//nick[1]/text()")
print(f"//nick[1]/text()     → {result}")  # ['臭豆腐']   ← 注意第一个 nick 是 /book/nick

# 更精确：/book/author/nick[1]
result = tree.xpath("/book/author/nick[1]/text()")
print(f"/book/author/nick[1] → {result}")  # ['周大强']

result = tree.xpath("/book/author/nick[last()]/text()")
print(f"/book/author/nick[last()] → {result}")  # ['蔡依林']

result = tree.xpath("/book/author/nick[last()-1]/text()")
print(f"/book/author/nick[last()-1] → {result}")  # ['周杰伦']

# ---- 3.2 属性筛选 ----
# //nick[@id]  → 所有带有 id 属性的 <nick>
result = tree.xpath("//nick[@id]/text()")
print(f"\n//nick[@id]          → {result}")  # ['周大强', '周芷若', '胖胖陈', '胖胖不陈']

# //nick[@id="10086"]  → id 属性等于 "10086" 的 <nick>
result = tree.xpath('//nick[@id="10086"]/text()')
print(f'//nick[@id="10086"]  → {result}')  # ['周大强']

# //nick[@class="joy"]
result = tree.xpath('//nick[@class="joy"]/text()')
print(f'//nick[@class="joy"] → {result}')  # ['周杰伦']

# ---- 3.3 位置+条件组合 ----
result = tree.xpath("/book/author/nick[position()>2]/text()")
print(f"/book/author/nick[position()>2] → {result}")  # ['周杰伦', '蔡依林']


print("\n" + "=" * 60)
print("【4】通配符 和 运算符")
print("=" * 60)

# ---- 4.1 通配符 * 匹配任意元素节点 ----
# /book/author/*    → author 下所有直接子元素
result = tree.xpath("/book/author/*")
print(f"/book/author/*     → {[el.tag for el in result]}")
# 输出: ['nick', 'nick', 'nick', 'nick', 'div']

# //*                → 所有元素
result = tree.xpath("//*")
print(f"//*                → {[el.tag for el in result]}")
# 输出: ['book', 'id', 'name', 'price', 'nick', 'author', ...]

# ---- 4.2 运算符：|（管道）合并多个路径 ----
result = tree.xpath("//name | //price")
print(f"\n//name | //price   → {[el.tag for el in result]}")
# 多个路径的结果集合并


print("\n" + "=" * 60)
print("【5】常用函数")
print("=" * 60)

# ---- 5.1 contains() 包含关系 ----
# contains(@class, "joy")  → class 属性包含 "joy"
result = tree.xpath('//nick[contains(@class, "joy")]/text()')
print(f'//nick[contains(@class, "joy")] → {result}')  # ['周杰伦']

# contains(text(), "胖")  → 文本包含 "胖" 字
result = tree.xpath('//nick[contains(text(), "胖")]/text()')
print(f'//nick[contains(text(), "胖")]  → {result}')  # ['胖胖陈', '胖胖不陈']

# ---- 5.2 starts-with() 开头匹配 ----
result = tree.xpath('//nick[starts-with(text(), "周")]/text()')
print(f'//nick[starts-with(text(), "周")] → {result}')  # ['周大强', '周芷若', '周杰伦']

# ---- 5.3 not() 取反 ----
# 没有 class 属性的 <nick>
result = tree.xpath("//author/nick[not(@class)]/text()")
print(f'//author/nick[not(@class)] → {result}')  # ['周大强', '周芷若']

# ---- 5.4 字符串长度 ----
result = tree.xpath("//nick[string-length(text()) > 2]/text()")
print(f"//nick[string-length(text())>2] → {result}")  # 3个字及以上的 nick


print("\n" + "=" * 60)
print("【6】轴（Axes）— 更灵活的节点关系导航")
print("=" * 60)

# XPath 轴让你可以按节点关系（父、子、兄弟、祖先、后代）来导航

# ---- 6.1 ancestor 轴：祖先节点 ----
# //nick[@class="joy"]/ancestor::*  → 所有祖先元素
result = tree.xpath('//nick[@class="joy"]/ancestor::*')
print(f'//nick[@class="joy"]/ancestor::*')
for el in result:
    print(f"  ← {el.tag}")

# ---- 6.2 following-sibling 轴：后续兄弟节点 ----
result = tree.xpath('/book/name/following-sibling::*')
print(f'\n/book/name/following-sibling::* → {[el.tag for el in result]}')
# 输出: ['price', 'nick', 'author', 'partner', 'tags']

# ---- 6.3 preceding-sibling 轴：前面兄弟节点 ----
result = tree.xpath('/book/price/preceding-sibling::*')
print(f'/book/price/preceding-sibling::* → {[el.tag for el in result]}')
# 输出: ['id', 'name']

# ---- 6.4 child / parent ----
result = tree.xpath('/book/author/child::*')
print(f'\n/book/author/child::* → {[el.tag for el in result]}')
# 输出: ['nick', 'nick', 'nick', 'nick', 'div']

result = tree.xpath('//nick[@id="ppc"]/parent::*/child::nick/text()')
print(f'//nick[@id="ppc"]/parent::*/child::nick → {result}')
# 胖胖陈的父节点(partner)下的所有nick
# 输出: ['胖胖陈', '胖胖不陈']

# ---- 6.5 descendant 轴：所有后代（等价于 //）----
result = tree.xpath('/book/descendant::nick')
print(f'\n/book/descendant::nick → {[el.text for el in result]}')


print("\n" + "=" * 60)
print("【7】进阶综合示例")
print("=" * 60)

# ---- 7.1 多个条件组合（and / or）----
result = tree.xpath('//author/nick[@id and not(@class)]/text()')
print(f'//author/nick[@id and not(@class)] → {result}')
# 有 id 属性且没有 class 属性：['周大强', '周芷若']

# ---- 7.2 按层级筛选（找 div 里的 nick）----
result = tree.xpath('/book/author/div/nick/text()')
print(f'/book/author/div/nick/text() → {result}')  # ['惹了']

# ---- 7.3 获取标签名 ----
result = tree.xpath("name(/*)")
print(f"name(/*)            → {result}")  # book

# ---- 7.4 获取节点数量 ----
result = tree.xpath("count(//nick)")
print(f"count(//nick)       → {result}")  # 8

# ---- 7.5 归一化空格（去掉首尾空格、合并连续空格） ----
xml2 = "<root><text>   你好   世界   </text></root>"
tree2 = etree.XML(xml2)
result1 = tree2.xpath("//text/text()")
result2 = tree2.xpath("normalize-space(//text/text())")
print(f"\nraw text           → {result1}")    # ['   你好   世界   ']
print(f"normalize-space    → {result2}")    # 你好 世界


print("\n" + "=" * 60)
print("【8】在 HTML 场景中的常用写法参考")
print("=" * 60)
print("""
以下是在爬虫中解析 HTML 时的常见 XPath 模式：

  //a/@href                    → 提取所有链接
  //img/@src                   → 提取所有图片地址
  //div[@class="content"]      → 按 class 找 div
  //div[@id="main"]            → 按 id 找 div
  //h1/text()                  → 提取 h1 标题
  //table//tr                  → 提取表格行
  //li[position()<5]           → 前 4 个 li
  //div[contains(@class, "title")]  → class 包含 "title" 的 div
  //ul/li/a/text()             → 列表中的链接文字
  //meta[@name="description"]/@content  → meta 描述

小技巧：
  - 在 Chrome 按 F12 → Elements，右键元素 → Copy → Copy XPath
  - lxml 的 HTML 解析用 etree.HTML(html_str)，XML 解析用 etree.XML(xml_str)
""")

print("=" * 60)
print("[完成] 示例运行完毕！你可以修改 XML 数据来反复练习。")
