#!/usr/bin/env python3
"""
每日收盘后：更新候选股池 + 记录涨停历史

用法：
  python3 update_candidates.py                    # 交互式
  python3 update_candidates.py --auto               # 自动（从今日已知数据）
  python3 update_candidates.py --date 20260410     # 指定日期
"""

import json
import os
import sys
import requests
from datetime import datetime, timedelta

BASE = os.path.expanduser("~/.openclaw/workspace/stock-patterns")

def get_realtime(codes):
    if not codes:
        return {}
    url = "http://qt.gtimg.cn/q=" + ",".join(codes)
    r = requests.get(url, timeout=10)
    result = {}
    for line in r.text.strip().split("\n"):
        if "~" not in line: continue
        parts = line.split("~")
        if len(parts) < 50: continue
        code = line.split("=")[0].replace("v_", "")
        try:
            result[code] = {
                "name": parts[1],
                "price": float(parts[3]) if parts[3] else 0,
                "close": float(parts[4]) if parts[4] else 0,
                "pct": float(parts[32]) if parts[32] else 0,
                "circ_mv": float(parts[45]) if parts[45] else 0,
                "high": float(parts[33]) if parts[33] else 0,
                "low": float(parts[34]) if parts[34] else 0,
                "open": float(parts[5]) if parts[5] else 0,
            }
        except: pass
    return result

def update_candidates(date_str, auto=True):
    """
    更新候选股池
    策略：从涨停新闻/已知数据更新候选池
    """
    cand_path = f"{BASE}/candidates/{date_str}.json"
    
    # 尝试从昨日数据构建
    yesterday = (datetime.strptime(date_str, "%Y%m%d") - timedelta(days=1)).strftime("%Y%m%d")
    y_cand_path = f"{BASE}/candidates/{yesterday}.json"
    
    candidates = {}
    
    if os.path.exists(y_cand_path):
        with open(y_cand_path) as f:
            old_cands = json.load(f)
        # 更新价格为今日收盘
        codes = list(old_cands.keys())
        real = get_realtime(codes)
        for code, cand in old_cands.items():
            info = real.get(code, {})
            new_price = info.get("price", cand.get("close_y", 0))
            new_pct = info.get("pct", 0)
            new_circ = info.get("circ_mv", 0)
            new_close_y = cand.get("close_y", 0)
            
            candidates[code] = {
                "name": cand["name"],
                "close_y": new_close_y or new_price,  # 昨收=上日收盘
                "close_today": new_price,
                "pct_today": new_pct,
                "circ_mv": new_circ,
                "reason": cand.get("reason", ""),
                "prev_close_y": cand.get("close_y", 0),
            }
    else:
        print("昨日候选池不存在，请手动输入")
    
    with open(cand_path, "w") as f:
        json.dump(candidates, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 更新候选股池: {len(candidates)} 只")
    return candidates

def record_limitup(date_str, limitup_stocks):
    """
    记录今日涨停股+涨停前特征
    limitup_stocks: [(代码, 名称, 涨停前特征), ...]
    """
    path = f"{BASE}/limitup_history/{date_str}.json"
    
    data = {}
    for code, name, pre_pattern, today_info in limitup_stocks:
        data[code] = {
            "name": name,
            "date": date_str,
            "pre_pattern": pre_pattern,
            "today": today_info,
        }
    
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 记录涨停历史: {len(data)} 只")
    return data

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--date":
        date_str = sys.argv[2]
    else:
        date_str = datetime.now().strftime("%Y%m%d")
    
    update_candidates(date_str)
