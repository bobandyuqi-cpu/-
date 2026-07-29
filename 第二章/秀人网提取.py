import requests
import time
import re
import os
import random
import urllib.parse
import concurrent.futures

session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0",
    "Referer": "https://www.xiurenlu.com/",
    "X-Requested-With": "XMLHttpRequest",
}
api_url = "https://www.xiurenlu.com/tools/bohe-gallery-api.php"
SAVE_DIR = r"D:\Users\bobandyuqi\Desktop\爬虫图片"


def safe_filename(name):
    """将标题转为安全的文件夹/文件名"""
    # 去掉非法字符
    name = re.sub(r'[\\/:*?"<>|]', '', name)
    # 空格转下划线，压缩连续下划线
    name = re.sub(r'\s+', '_', name).strip('_')
    return name[:80]  # 限制长度


def init_session():
    """访问首页，拿到 Cloudflare cookies"""
    resp = session.get("https://www.xiurenlu.com/", headers=headers, timeout=15)
    return resp.status_code == 200


def get_work_id_from_url(url):
    """访问详情页，提取 data-work-id"""
    resp = session.get(url, headers=headers, timeout=15)
    if resp.status_code != 200:
        return None
    m = re.search(r'data-work-id="(\d+)"', resp.text)
    if m:
        return int(m.group(1))
    return None


def get_work_title_from_url(url):
    """访问详情页，提取标题"""
    resp = session.get(url, headers=headers, timeout=15)
    if resp.status_code != 200:
        return "未知"
    m = re.search(r'<title>(.*?)</title>', resp.text, re.DOTALL)
    if m:
        title = m.group(1).strip()
        # 去掉末尾的 " - 期刊作品在线浏览 - 秀人网"
        title = re.sub(r'\s*-\s*期刊作品在线浏览\s*-\s*秀人网\s*$', '', title)
        return title
    return "未知"


def get_work_info(url):
    """获取作品的完整信息"""
    resp = session.get(url, headers=headers, timeout=15)
    if resp.status_code != 200:
        return None
    html = resp.text
    work_id = re.search(r'data-work-id="(\d+)"', html)
    title = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
    # 找描述：锁定 article.xr-copy 里面的 p 标签
    desc = ""
    article_m = re.search(r'<article[^>]*class="xr-copy"[^>]*>(.*?)</article>', html, re.DOTALL)
    if article_m:
        p_m = re.search(r'<p>(.*?)</p>', article_m.group(1), re.DOTALL)
        if p_m:
            desc = re.sub(r'<[^>]+>', '', p_m.group(1)).strip()
    # 找张数
    total = re.search(r'data-total="(\d+)"', html)
    # 找预览图列表：取 gallery 中所有预览图，没有则取 feature-image
    preview_urls = []
    gallery_m = re.search(r'<div[^>]*class="xr-preview-gallery"[^>]*>(.*?)</div>\s*<div', html, re.DOTALL)
    if gallery_m:
        preview_urls = re.findall(r'<img[^>]*src="([^"]+)"', gallery_m.group(1))
    if not preview_urls:
        feature_m = re.search(r'<figure[^>]*class="xr-feature-image"[^>]*>.*?<img[^>]*src="([^"]+)"', html, re.DOTALL)
        if feature_m:
            preview_urls = [feature_m.group(1)]

    info = {
        "work_id": int(work_id.group(1)) if work_id else None,
        "title": re.sub(r'\s*-\s*期刊作品在线浏览\s*-\s*秀人网\s*$', '', title.group(1).strip()) if title else "未知",
        "description": desc,
        "total": int(total.group(1)) if total else 0,
        "preview_urls": preview_urls,
    }
    return info


def fetch_images(work_id, page=1, per_page=12):
    """获取图片列表"""
    # 先拿 token
    params_token = {
        "action": "token",
        "work_id": work_id,
        "page": page,
        "per_page": per_page,
        "_": int(time.time() * 1000),
    }
    resp = session.get(api_url, params=params_token, headers=headers, timeout=15)
    data = resp.json()
    if not data.get("ok"):
        return None
    token = data["token"]

    # 用 token 拿图片
    params_img = {
        "work_id": work_id,
        "page": page,
        "per_page": per_page,
        "token": token,
    }
    resp = session.get(api_url, params=params_img, headers=headers, timeout=15)
    return resp.json()


def search_works(keyword, max_pages=5):
    """搜索作品，返回列表"""
    results = []
    encoded = urllib.parse.quote(keyword)

    for page in range(1, max_pages + 1):
        url = f"https://www.xiurenlu.com/search/{encoded}/page/{page}/" if page > 1 else f"https://www.xiurenlu.com/search/{encoded}/"
        resp = session.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            break

        # 解析卡片
        pattern = r'<a class="xr-journal-card "[^>]*href="(/issue/[^"]+)"[^>]*>.*?<h3>(.*?)</h3>.*?<p>(.*?)</p>'
        cards = re.findall(pattern, resp.text, re.DOTALL)
        if not cards:
            break

        for href, title, desc in cards:
            clean_title = re.sub(r'\s+', ' ', title).strip()
            clean_desc = re.sub(r'\s+', ' ', desc).strip()
            full_url = "https://www.xiurenlu.com" + href
            results.append({"url": full_url, "title": clean_title, "desc": clean_desc})

    return results


def list_recent_works(pages=3):
    """列出最近的作品"""
    results = []
    for page in range(1, pages + 1):
        url = f"https://www.xiurenlu.com/works/page/{page}/"
        resp = session.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            break

        pattern = r'<a class="xr-journal-card "[^>]*href="(/issue/[^"]+)"[^>]*>.*?<h3>(.*?)</h3>.*?<p>(.*?)</p>'
        cards = re.findall(pattern, resp.text, re.DOTALL)
        if not cards:
            break

        for href, title, desc in cards:
            clean_title = re.sub(r'\s+', ' ', title).strip()
            clean_desc = re.sub(r'\s+', ' ', desc).strip()
            full_url = "https://www.xiurenlu.com" + href
            results.append({"url": full_url, "title": clean_title, "desc": clean_desc})

    return results




def download_image(url, save_path, max_retries=3):
    """下载单张图片，带重试"""
    for attempt in range(1, max_retries + 1):
        try:
            resp = session.get(url, headers=headers, timeout=30)
            if resp.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(resp.content)
                return True
            elif resp.status_code == 429:
                wait = random.uniform(5, 10)
                print(f"    [限流] 被限速，等待 {wait:.1f}s 后重试...")
                time.sleep(wait)
            else:
                if attempt < max_retries:
                    wait = random.uniform(2, 4)
                    print(f"    [重试] 状态码 {resp.status_code}，{wait:.1f}s 后重试 ({attempt}/{max_retries})")
                    time.sleep(wait)
        except Exception as e:
            if attempt < max_retries:
                wait = random.uniform(3, 6)
                print(f"    [重试] 异常: {e}，{wait:.1f}s 后重试 ({attempt}/{max_retries})")
                time.sleep(wait)
    return False


def download_one_task(args):
    """单个下载任务（给线程池用）"""
    url, save_path, idx, total = args
    fname = os.path.basename(save_path)
    print(f"  [{idx}/{total}] 下载中: {fname}")
    ok = download_image(url, save_path)
    print(f"  [{idx}/{total}] {'OK' if ok else '失败'}")
    return ok


def fetch_page_images(work_id, page, token):
    """用指定 token 获取某一页的图片"""
    params_img = {
        "work_id": work_id,
        "page": page,
        "per_page": 12,
        "token": token,
    }
    resp = session.get(api_url, params=params_img, headers=headers, timeout=15)
    return resp.json()


def collect_all_images(work_id):
    """收集某作品的全部图片 URL（带防封间隔）"""
    all_items = []
    # 第1页：先拿 token
    params_token = {
        "action": "token",
        "work_id": work_id,
        "page": 1,
        "per_page": 12,
        "_": int(time.time() * 1000),
    }
    resp = session.get(api_url, params=params_token, headers=headers, timeout=15)
    data = resp.json()
    if not data.get("ok"):
        return None

    token = data["token"]
    total = data.get("total", 0)

    # 用 token 拿第1页图片
    data = fetch_page_images(work_id, 1, token)
    if not data or not data.get("ok"):
        return None
    total = data.get("total", total)
    all_items.extend(data.get("items", []))
    has_more = data.get("has_more", False)
    next_token = data.get("next_token")
    page = 1
    print(f"  第1页: {len(all_items)}/{total} 张")

    while has_more and next_token:
        time.sleep(random.uniform(1.5, 3.0))  # 防封间隔
        page += 1
        data = fetch_page_images(work_id, page, next_token)
        if not data or not data.get("ok"):
            print(f"  [警告] 第{page}页获取失败: {data}")
            break
        all_items.extend(data.get("items", []))
        print(f"  第{page}页: {len(all_items)}/{total} 张")
        has_more = data.get("has_more", False)
        next_token = data.get("next_token")

    return all_items


# ===== 主程序 =====
def main():
    print("=" * 60)
    print("秀人网 · 图片提取工具")
    print("=" * 60)

    if not init_session():
        print("[失败] 无法访问秀人网，请检查网络")
        return

    print("[OK] 连接成功\n")

    while True:
        print("\n请选择操作：")
        print("  [1] 搜索作品")
        print("  [2] 浏览最新作品")
        print("  [3] 直接输入 work_id")
        print("  [q] 退出")

        choice = input("请输入: ").strip()

        if choice == "q":
            break

        works = []

        if choice == "1":
            keyword = input("请输入搜索关键词（模特名/编号等）: ").strip()
            if not keyword:
                continue
            print(f"正在搜索 \"{keyword}\"...")
            works = search_works(keyword)
            if not works:
                print("未找到相关作品")
                continue

        elif choice == "2":
            print("正在获取最新作品列表...")
            works = list_recent_works(3)
            if not works:
                print("获取失败")
                continue

        elif choice == "3":
            wid = input("请输入 work_id: ").strip()
            if not wid or not wid.isdigit():
                print("请输入有效数字")
                continue
            wid = int(wid)
            # 直接尝试用 work_id 获取 token，检查是否有效
            params_token = {
                "action": "token",
                "work_id": wid,
                "page": 1,
                "per_page": 12,
                "_": int(time.time() * 1000),
            }
            resp = session.get(api_url, params=params_token, headers=headers, timeout=15)
            data = resp.json()
            if not data.get("ok"):
                print(f"[失败] work_id={wid} 无效，API 返回: {data}")
                continue
            print(f"[OK] work_id={wid} 有效，开始获取图片...")
            img_data = fetch_images(wid)
            if not img_data or not img_data.get("ok"):
                print("[失败] 获取图片失败")
                continue
            show_images(wid, img_data, title=f"work_{wid}")
            continue

        else:
            print("无效输入")
            continue

        # 显示作品列表（搜索/浏览）
        print(f"\n{'='*60}")
        print(f"找到 {len(works)} 个作品：")
        print(f"{'='*60}")
        for i, w in enumerate(works, 1):
            print(f"  [{i}] {w['title']}")
            print(f"      {w['desc']}")
            print()
        print("  [b] 返回主菜单")

        # 选择作品
        while True:
            sel = input("请选择作品编号（输入数字，或按回车跳过）: ").strip().lower()
            if sel == "b":
                break
            if not sel or not sel.isdigit():
                continue
            sel = int(sel)
            if sel < 1 or sel > len(works):
                print("无效编号")
                continue

            selected = works[sel - 1]
            print(f"\n正在获取 \"{selected['title']}\" 的详细信息...")
            info = get_work_info(selected["url"])

            if not info or not info["work_id"]:
                print("[失败] 获取详细信息失败")
                continue

            print(f"\n{'='*60}")
            print(f" {info['title']}")
            print(f"  work_id: {info['work_id']}")
            if info["description"]:
                print(f"  描述: {info['description']}")
            print(f"  图片总数: {info['total']} 张" if info["total"] else "")
            previews = info.get("preview_urls", [])
            if previews:
                print(f"  预览 ({len(previews)}张):")
                for pi, pu in enumerate(previews, 1):
                    print(f"    [{pi}] {pu}")
            print(f"{'='*60}")

            # 子循环：查看图片 / 返回
            while True:
                view = input("\n[y] 查看图片列表 | [p 编号] 打开预览 | [b] 返回列表: ").strip()
                if view == "b":
                    break  # 返回作品列表
                if view.startswith("p"):
                    parts = view.split(maxsplit=1)
                    idx = 1  # 默认第一张
                    if len(parts) > 1 and parts[1].isdigit():
                        idx = int(parts[1])
                    if previews and 1 <= idx <= len(previews):
                        import webbrowser
                        webbrowser.open(previews[idx - 1])
                        print(f"  [已打开预览 [{idx}] 共 {len(previews)} 张，可输入 p 1~{len(previews)} 切换]")
                    else:
                        print(f"  [无效编号，可选 1~{len(previews)}]")
                    continue
                if view != "y":
                    continue

                img_data = fetch_images(info["work_id"])
                if not img_data or not img_data.get("ok"):
                    print("[失败] 获取图片列表失败")
                    continue
                show_images(info["work_id"], img_data, title=info["title"])
                # 从图片列表返回后，重新回到详情页
                continue
            # 回到作品列表，继续选择
            continue


def show_images(work_id, img_data, title="work"):
    """显示图片列表，支持分页"""
    total = img_data.get("total", 0)
    items = img_data.get("items", [])
    has_more = img_data.get("has_more", False)
    current_page = img_data.get("page", 1)
    next_token = img_data.get("next_token")
    per_page = img_data.get("per_page", 12)
    folder_name = safe_filename(title)
    save_dir = os.path.join(SAVE_DIR, folder_name)

    print(f"\n{'='*60}")
    print(f" 共 {total} 张图片 (当前第 {current_page} 页)")
    print(f"{'='*60}")
    for i, url in enumerate(items, 1):
        print(f"  {i + (current_page-1)*per_page}. {url}")

    action = input(f"\n[回车] 下一页 | [d] 下载当前页 | [a] 下载全部({MAX_WORKERS}线程) | [s] 保存链接 | [b/q] 返回: ").strip().lower()

    if action in ("q", "b"):
        return
    elif action == "s":
        os.makedirs(save_dir, exist_ok=True)
        links_path = os.path.join(save_dir, "urls.txt")
        with open(links_path, "w", encoding="utf-8") as f:
            for url in items:
                f.write(url + "\n")
        print(f"[OK] 已保存到 {links_path}")
    elif action == "d":
        download_image_list(items, save_dir, folder_name, start_index=(current_page - 1) * per_page)
    elif action == "a":
        download_all_images(work_id, save_dir, folder_name, total)
    elif action == "" and has_more and next_token:
        params_img = {
            "work_id": work_id,
            "page": current_page + 1,
            "per_page": per_page,
            "token": next_token,
        }
        resp = session.get(api_url, params=params_img, headers=headers, timeout=15)
        next_data = resp.json()
        show_images(work_id, next_data, title=title)


MAX_WORKERS = 3  # 并发下载数


def download_image_list(urls, save_dir, folder_name, start_index=0):
    """并发下载一批图片（兼顾速度和防封）"""
    os.makedirs(save_dir, exist_ok=True)
    total = len(urls)
    # 准备任务列表
    tasks = []
    for i, url in enumerate(urls, 1):
        fname = f"{folder_name}_{start_index + i:03d}.jpg"
        save_path = os.path.join(save_dir, fname)
        tasks.append((url, save_path, i, total))

    success = 0
    # 用线程池并发下载，每提交一个间隔 0.3~0.5s 避免突刺
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for task in tasks:
            futures.append(executor.submit(download_one_task, task))
            time.sleep(random.uniform(0.3, 0.5))  # 错开请求，防突刺

        for future in concurrent.futures.as_completed(futures):
            if future.result():
                success += 1

    print(f"  -> 完成: {success}/{total} 张")


def download_all_images(work_id, save_dir, folder_name, total):
    """下载某个作品的全部图片"""
    print(f"\n正在收集全部 {total} 张图片...")
    all_urls = collect_all_images(work_id)
    if not all_urls:
        print("[失败] 收集图片列表失败")
        return
    print(f"共收集到 {len(all_urls)} 张图片，开始下载...")
    print(f"保存到: {save_dir}")
    print("[注意] 防封间隔已启用，下载速度较慢\n")
    download_image_list(all_urls, save_dir, folder_name)


if __name__ == "__main__":
    main()
