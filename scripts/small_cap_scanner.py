#!/usr/bin/env python3
"""
小而美股票筛选器
流通市值：30-200亿（好拉升）
涨幅：>0%（有资金关注）
用法：python3 small_cap_scanner.py [涨幅阈值] [市值上限]
"""

import requests
import sys
import json
from datetime import datetime

def get_realtime_all(codes):
    """批量获取实时行情"""
    url = "http://qt.gtimg.cn/q=" + ",".join(codes)
    r = requests.get(url, timeout=10)
    result = {}
    for line in r.text.strip().split("\n"):
        if "~" not in line:
            continue
        parts = line.split("~")
        if len(parts) < 46:
            continue
        code = line.split("=")[0].replace("v_", "")
        try:
            price = float(parts[3]) if parts[3] else 0
            pct = float(parts[32]) if parts[32] else 0
            circ_mv = float(parts[45]) if parts[45] else 0
            total_mv = float(parts[44]) if parts[44] else 0
            name = parts[1]
            vol = float(parts[36]) if parts[36] else 0  # 成交量(手)
            result[code] = {
                "name": name,
                "price": price,
                "pct": pct,
                "circ_mv": circ_mv,
                "total_mv": total_mv,
                "vol": vol,
            }
        except:
            pass
    return result

def score_stock(pct, circ_mv):
    """
    综合评分：涨幅越高越好，市值越小越好（但不能太小）
    最佳区间：30-100亿，评分最高
    """
    if circ_mv == 0 or pct == 0:
        return 0
    
    # 市值评分：30-100亿得满分，<30亿或>200亿扣分
    if 30 <= circ_mv <= 100:
        mv_score = 50
    elif 100 < circ_mv <= 200:
        mv_score = 40
    elif 10 <= circ_mv < 30:
        mv_score = 25
    else:
        mv_score = 0
    
    # 涨幅评分：涨幅越高分数越高（封板10%满分）
    pct_score = min(pct / 10.0 * 50, 50)
    
    return mv_score + pct_score

def main():
    now = datetime.now()
    print(f"📊 小而美股票筛选 | {now.strftime('%Y-%m-%d %H:%M')}\n")
    
    # 默认参数
    min_pct = float(sys.argv[1]) if len(sys.argv) > 1 else 0
    max_circ = float(sys.argv[2]) if len(sys.argv) > 2 else 200
    
    # 重点关注的股票池（来自昨日涨停板 + 近期强势）
    watch_pool = [
        # 昨日涨停/强势股
        "sz000586", "sz002491", "sh600594",  # 昨日竞价提到的
        "sz002384", "sz002281", "sh601869", "sz300548",
        # 今日热点：小市值+强势
        "sh600476", "sz002528", "sz301090", "sz300364",
        "sh601069", "sz300618", "sh688336", "sz002649",
        # 昨日连板候选
        "sz300740", "sz002761", "sz003816", "sh603212",
        # 热门题材小盘股
        "sz300077", "sz002916", "sh688256", "sz002049",
    ]
    
    data = get_realtime_all(watch_pool)
    
    # 筛选：涨幅>阈值 AND 流通市值30-max_circ亿
    candidates = []
    for code, info in data.items():
        pct = info["pct"]
        circ = info["circ_mv"]
        
        if abs(pct) < min_pct or pct < -3:  # 跌幅太大不看
            continue
        if circ < 30 or circ > max_circ:
            continue
        if info["price"] <= 0:
            continue
            
        score = score_stock(pct, circ)
        candidates.append({
            **info,
            "code": code,
            "score": score,
        })
    
    # 按评分排序
    candidates.sort(key=lambda x: x["score"], reverse=True)
    
    if not candidates:
        print("😴 暂无符合条件的股票")
        return
    
    print(f"筛选条件：涨幅>={min_pct}% | 流通市值30-{max_circ}亿\n")
    print(f"{'股票':<10} {'现价':>7} {'涨幅':>8} {'流通市值':>10} {'评分':>6} {'综合评价'}")
    print("-" * 65)
    
    for s in candidates[:15]:
        tag = "🚀强烈推荐" if s["score"] >= 70 else "✅推荐" if s["score"] >= 50 else "📊可关注"
        print(f"{s['name']:<10} {s['price']:>6.2f} {s['pct']:>+7.1f}% {s['circ_mv']:>9.1f}亿 {s['score']:>5.1f} {tag}")
    
    print("\n💡 说明：评分综合考虑市值区间(30-100亿最佳)和涨幅，>70分值得重点关注")

if __name__ == "__main__":
    main()
