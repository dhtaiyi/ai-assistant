#!/usr/bin/env python3
"""
小红书爆款笔记全维度数据采集脚本
按 4 大维度采集：基础标识、流量数据、内容特征、用户互动
"""

import requests
import json
import time
import jieba
import pandas as pd
from datetime import datetime
import os
import random

# ========== 配置 ==========
CONFIG = {
    "keywords": [
        "主播灯光调试", "直播美颜参数", "直播间颜值优化",
        "新人主播灯光", "直播显白技巧", "美颜参数调试",
        "直播间补光", "网红直播间灯光"
    ],
    "filter": {
        "like_min": 500,
        "collect_min": 200,
        "comment_min": 50,
        "publish_days": 30,
        "page_num": 5
    },
    "anti_crawl": {
        "req_interval": 2,      # 单条请求间隔(秒)
        "batch_interval": 10,   # 每10条笔记后暂停(秒)
        "retry_times": 3
    },
    "storage": {
        "root_path": "./xhs_data/collect/"
    }
}

# User-Agent 池
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
]

def get_headers():
    """生成随机请求头"""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Cookie": CONFIG.get("cookie", ""),
        "X-Sign": CONFIG.get("token", ""),
        "Referer": "https://www.xiaohongshu.com/"
    }

def parse_number(s):
    """解析数字（支持万、+等）"""
    if not s or s == '':
        return 0
    s = str(s)
    if '万' in s:
        return int(float(s.replace('万', '')) * 10000)
    elif '+' in s:
        return int(s.replace('+', ''))
    else:
        try:
            return int(s)
        except:
            return 0

def extract_keywords(text):
    """用 jieba 提取关键词（搜索引擎模式）"""
    if not text:
        return []
    return list(jieba.cut_for_search(text))

def extract_pain_points(text):
    """提取痛点关键词"""
    pain_words = ["显黄", "显脏", "假白", "不上镜", "脸脏", "模糊", "黑", "丑", "胖"]
    return [w for w in pain_words if w in text]

def extract_solutions(text):
    """提取解决方案关键词"""
    solution_words = ["色温", "磨皮", "补光", "角度", "亮度", "柔光", "美颜", "参数"]
    return [w for w in solution_words if w in text]

def extract_cta(text):
    """提取引流动作"""
    cta_words = ["私我", "评论扣1", "加V", "领取", "私聊", "关注", "扣"]
    return [w for w in cta_words if w in text]

def get_note_detail(note_id, xsec_token=""):
    """采集单条笔记全维度数据"""
    url = f"https://edith.xiaohongshu.com/api/sns/web/v1/note/{note_id}"
    headers = get_headers()
    
    for i in range(CONFIG["anti_crawl"]["retry_times"]):
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json().get("data", {})
                break
        except Exception as e:
            print(f"  重试 {i+1}: {e}")
            time.sleep(CONFIG["anti_crawl"]["req_interval"])
    else:
        return None
    
    # 解析数据
    user = data.get("user", {})
    interact = data.get("interactInfo", {})
    
    note_data = {
        # === 维度1: 基础标识信息 ===
        "note_id": note_id,
        "author_id": user.get("userId", ""),
        "author_nickname": user.get("nickname", ""),
        "author_fans": parse_number(user.get("fans_count", 0)),
        "publish_time": data.get("publish_time", ""),
        "note_type": "图文" if data.get("type") == "normal" else "短视频",
        "note_tags": [tag.get("name") for tag in data.get("tag_list", [])],
        "note_url": f"https://www.xiaohongshu.com/explore/{note_id}",
        
        # === 维度2: 流量核心数据 ===
        "view_count": parse_number(interact.get("play_count", 0)),
        "likes_count": parse_number(interact.get("liked_count", 0)),
        "collect_count": parse_number(interact.get("collected_count", 0)),
        "comment_count": parse_number(interact.get("comment_count", 0)),
        "share_count": parse_number(interact.get("share_count", 0)),
        "like_rate": 0,  # 后续计算
        "collect_rate": 0,  # 后续计算
        
        # === 维度3: 内容特征数据 ===
        "title": data.get("title", ""),
        "content": data.get("desc", ""),
        "content_word_count": len(data.get("desc", "")),
        "image_count": len(data.get("image_list", [])),
        "video_duration": data.get("video", {}).get("duration", -1),
        "core_keywords": extract_keywords(data.get("desc", "")),
        "pain_point": extract_pain_points(data.get("desc", "")),
        "solution": extract_solutions(data.get("desc", "")),
        "call_to_action": extract_cta(data.get("desc", "")),
        
        # === 维度4: 用户互动数据 ===
        "top5_comments": [],
        "hot_comment_keywords": [],
        "author_reply_rate": -1
    }
    
    # 计算比率
    view = max(note_data["view_count"], 1)
    note_data["like_rate"] = round(note_data["likes_count"] / view, 4)
    note_data["collect_rate"] = round(note_data["collect_count"] / view, 4)
    
    # 采集评论
    try:
        comment_url = f"https://edith.xiaohongshu.com/api/sns/web/v1/comment/list?note_id={note_id}&page_size=5&sort=hot"
        comment_resp = requests.get(comment_url, headers=headers, timeout=10)
        comments = comment_resp.json().get("data", {}).get("comments", [])
        note_data["top5_comments"] = [
            {
                "content": c.get("content", ""),
                "likes_count": parse_number(c.get("liked_count", 0)),
                "reply_count": parse_number(c.get("reply_count", 0))
            } for c in comments[:5]
        ]
        # 热评关键词
        comment_text = " ".join([c.get("content", "") for c in comments])
        note_data["hot_comment_keywords"] = extract_keywords(comment_text)
    except Exception as e:
        print(f"  评论采集失败: {e}")
    
    return note_data

def search_notes(keyword, page=1, sort="general"):
    """搜索笔记"""
    url = f"https://edith.xiaohongshu.com/api/sns/web/v1/search/notes"
    params = {
        "keyword": keyword,
        "page": page,
        "page_size": 20,
        "sort": sort,
        "search_id": f"{int(time.time())}{random.randint(1000,9999)}"
    }
    headers = get_headers()
    
    try:
        resp = requests.post(url, json=params, headers=headers, timeout=10)
        return resp.json().get("data", {}).get("items", [])
    except Exception as e:
        print(f"搜索失败: {e}")
        return []

def collect_hot_notes():
    """批量采集爆款笔记"""
    today = datetime.now().strftime("%Y%m%d")
    storage_path = os.path.join(CONFIG["storage"]["root_path"], today)
    os.makedirs(storage_path, exist_ok=True)
    
    all_notes = []
    
    # 遍历关键词
    for keyword in CONFIG["keywords"]:
        print(f"\n📥 采集关键词: {keyword}")
        
        for page in range(1, CONFIG["filter"]["page_num"] + 1):
            print(f"  第 {page} 页...", end=" ")
            
            items = search_notes(keyword, page)
            if not items:
                print("无数据")
                break
            
            count = 0
            for item in items:
                # 基础筛选
                likes = parse_number(item.get("liked_count", 0))
                collects = parse_number(item.get("collected_count", 0))
                comments = parse_number(item.get("comment_count", 0))
                
                if likes < CONFIG["filter"]["like_min"]:
                    continue
                
                note_id = item.get("note_id", "")
                if not note_id:
                    continue
                
                # 采集详情
                detail = get_note_detail(note_id)
                if detail:
                    all_notes.append(detail)
                    count += 1
                
                time.sleep(CONFIG["anti_crawl"]["req_interval"])
            
            print(f"获取 {count} 条")
            time.sleep(CONFIG["anti_crawl"]["batch_interval"])
    
    # 清洗去重
    unique_notes = []
    seen_ids = set()
    for note in all_notes:
        if note["note_id"] not in seen_ids:
            seen_ids.add(note["note_id"])
            # 过滤广告
            if not any(w in note.get("content", "") for w in ["招代理", "卖设备", "加盟"]):
                unique_notes.append(note)
    
    # 保存文件
    # 1. 主文件 JSON
    with open(os.path.join(storage_path, f"hot_notes_{today}.json"), "w", encoding="utf-8") as f:
        json.dump(unique_notes, f, ensure_ascii=False, indent=2)
    
    # 2. 关键词排名 CSV
    all_kw = []
    for note in unique_notes:
        all_kw.extend(note.get("core_keywords", []))
    if all_kw:
        kw_df = pd.Series(all_kw).value_counts().reset_index()
        kw_df.columns = ["keyword", "count"]
        kw_df.to_csv(os.path.join(storage_path, f"keywords_rank_{today}.csv"), 
                     index=False, encoding="utf-8-sig")
    
    # 3. 最佳发布时间
    hours = [n["publish_time"].split(" ")[1].split(":")[0] for n in unique_notes if n.get("publish_time")]
    if hours:
        best_hour = pd.Series(hours).value_counts().index[0]
        with open(os.path.join(storage_path, f"best_publish_time_{today}.txt"), "w") as f:
            f.write(f"最佳发布时段: {best_hour}:00-{int(best_hour)+1}:00")
    
    print(f"\n✅ 采集完成! 共 {len(unique_notes)} 条, 存储在 {storage_path}")
    return unique_notes

if __name__ == "__main__":
    # 需要配置 cookie 和 token
    print("请先配置 CONFIG 中的 cookie 和 token!")
    # collect_hot_notes()
