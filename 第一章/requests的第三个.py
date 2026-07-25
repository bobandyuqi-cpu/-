import requests
from typing import List, Dict, Any, Optional

l=int(input("请输入要查询的豆瓣恐怖片的排行数量:"))
# ─── 1. 数据处理模块（保持纯粹的解析逻辑） ──────────────────────

def parse_douban_movies(raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """解析豆瓣电影JSON数据，返回清洗后的结构化列表"""
    if not isinstance(raw_data, list):
        print(f"⚠️ 期望list类型，实际收到 {type(raw_data).__name__}")
        return []

    results = []
    for idx, item in enumerate(raw_data):
        if not isinstance(item, dict):
            print(f"⚠️ 索引 {idx} 不是有效字典，已跳过")
            continue

        movie = _extract_movie(item)
        if movie is None:
            print(f"⚠️ 索引 {idx} 缺少必要字段(id/title)，已跳过")
            continue
        results.append(movie)

    return results


def _extract_movie(item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """从单条原始数据中提取并清洗电影信息"""
    movie_id = item.get("id")
    title = item.get("title")
    if not movie_id or not title:
        return None

    score = _safe_parse_score(item.get("score"), item.get("rating"))
    return {
        "id": str(movie_id).strip(),
        "title": str(title).strip(),
        "score": score,
        "vote_count": _safe_int(item.get("vote_count")),
        "rank": _safe_int(item.get("rank")),
        "release_date": str(item.get("release_date", "")).strip() or None,
        "regions": _safe_list(item.get("regions")),
        "types": _safe_list(item.get("types")),
        "actors": _safe_list(item.get("actors")),
        "cover_url": str(item.get("cover_url", "")).strip() or None,
        "url": str(item.get("url", "")).strip() or None,
        "is_playable": bool(item.get("is_playable", False)),
    }


def _safe_parse_score(score: Any, rating: Any) -> Optional[float]:
    for candidate in [score, rating[0] if isinstance(rating, list) and rating else None]:
        try:
            val = float(candidate)
            return val if 0 <= val <= 10 else None
        except (TypeError, ValueError, IndexError):
            continue
    return None


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(v).strip() for v in value if v is not None]
    return []


# ─── 2. 网络请求模块（在你原有代码基础上增强） ──────────────────

def fetch_douban_top_list(start: int = 0, limit: int = l) -> List[Dict[str, Any]]:
    """
    请求豆瓣Top榜并返回清洗后的电影数据
    基于你原有的 url / params / headers 封装
    """
    url = "https://movie.douban.com/j/chart/top_list"
    params = {
        "type": "20",           # 电影类型ID
        "interval_id": "100:90", # 评分区间
        "action": "",
        "start": start,
        "limit": limit,
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0"
    }

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()  # 非2xx状态码自动抛异常
    except requests.exceptions.Timeout:
        print("⏰ 请求超时，请检查网络")
        return []
    except requests.exceptions.ConnectionError:
        print("🌐 网络连接失败")
        return []
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP错误: {e.response.status_code}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"💥 请求异常: {e}")
        return []

    # 校验响应内容是否为合法JSON列表
    try:
        raw_data = resp.json()
    except ValueError:
        print(f"⚠️ 响应非JSON格式，前200字符: {resp.text[:200]}")
        return []

    return parse_douban_movies(raw_data)


# ─── 3. 主程序入口 ───────────────────────────────────────────

if __name__ == "__main__":
    movies = fetch_douban_top_list(start=0, limit=l)

    if not movies:
        print("未获取到任何有效电影数据")
    else:
        for m in movies:
            regions_str = "/".join(m["regions"])
            types_str = "/".join(m["types"])
            actors_display = ", ".join(m["actors"][:3])
            if len(m["actors"]) > 3:
                actors_display += f" 等{len(m['actors'])}人"
            playable_tag = "▶ 可播放" if m["is_playable"] else "✗ 不可播放"

            print(f"[{m['rank']:>2}] {m['title']}")
            print(f"     ⭐ {m['score']} ({m['vote_count']:,}人评价) | {regions_str} | {types_str}")
            print(f"     🎬 {actors_display}")
            print(f"     📅 {m['release_date']} | {playable_tag}")
            print()
    print("已经获取所需数量")