import requests

url = "https://fanyi.baidu.com/sug"

print("=== 百度翻译持续查询工具 ===")
print("💡 输入 'q' 或 'quit' 退出程序\n")

while True:
    s = input("请输入要查询的单词: ").strip()

    # 退出机制
    if s.lower() in ('q', 'quit', 'exit'):
        print("👋 已退出，再见！")
        break

    # 空输入检查
    if not s:
        print("⚠️ 输入不能为空，请重新输入\n")
        continue

    try:
        resp = requests.post(url, data={"kw": s}, timeout=5)
        result = resp.json()

        if result.get("errno") == 0 and result.get("data"):
            for item in result["data"]:
                print(f"  {item['k']} → {item['v']}")
        else:
            print("  ❌ 未找到相关翻译")

    except requests.exceptions.Timeout:
        print("  ⏰ 请求超时，请检查网络后重试")
    except requests.exceptions.ConnectionError:
        print("  🌐 网络连接失败，请检查网络")
    except Exception as e:
        print(f"  💥 发生未知错误: {e}")

    print()  # 每次查询后空一行，保持输出整洁