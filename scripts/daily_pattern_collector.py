#!/usr/bin/env python3
"""
每日图形收集器 v1.0

功能：
1. 每日收集候选股池（昨日涨停、强势股、热门板块）
2. 追踪候选股的量价关系
3. 复盘：标记今日涨停的股票，收集其涨停前的图形特征
4. 建立趋势图形库：记录趋势股的K线形态
5. 每日扫描：寻找与历史涨停前图形相似的股票

数据库结构：
  candidates/YYYYMMDD.json     # 当日候选股池
  limitup_history/YYYYMMDD.json  # 今日涨停股+涨停前数据
  trend_patterns/patterns.json # 历史趋势图形库
  daily_report/YYYYMMDD.md     # 每日复盘报告
"""

import requests
import json
import os
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.dirname(BASE_DIR) + "/stock-patterns"

CANDIDATES_DIR = DATA_DIR + "/candidates"
LIMITUP_DIR = DATA_DIR + "/limitup_history"
TREND_DIR = DATA_DIR + "/trend_patterns"
REPORT_DIR = DATA_DIR + "/daily_report"

for d in [CANDIDATES_DIR, LIMITUP_DIR, TREND_DIR, REPORT_DIR]:
    os.makedirs(d, exist_ok=True)

# 腾讯API字段：parts[3]=价格, [4]=昨收, [5]=今开, [6-10]=买卖盘口...
# [32]=涨跌幅, [36]=成交量(手), [37]=成交额(万元)
# [44]=总市值(亿), [45]=流通市值(亿)

def get_realtime(codes):
    """批量获取实时行情"""
    if not codes:
        return {}
    url = "http://qt.gtimg.cn/q=" + ",".join(codes)
    r = requests.get(url, timeout=10)
    result = {}
    for line in r.text.strip().split("\n"):
        if "~" not in line:
            continue
        parts = line.split("~")
        if len(parts) < 50:
            continue
        code = line.split("=")[0].replace("v_", "")
        try:
            result[code] = {
                "name": parts[1],
                "price": float(parts[3]) if parts[3] else 0,
                "open": float(parts[5]) if parts[5] else 0,
                "close": float(parts[4]) if parts[4] else 0,  # 昨收
                "high": float(parts[33]) if parts[33] else 0,
                "low": float(parts[34]) if parts[34] else 0,
                "vol": float(parts[36]) if parts[36] else 0,   # 成交量(手)
                "amount": float(parts[37]) if parts[37] else 0, # 成交额(万元)
                "pct": float(parts[32]) if parts[32] else 0,
                "circ_mv": float(parts[45]) if parts[45] else 0,  # 流通市值(亿)
            }
        except:
            pass
    return result

def load_candidates(date_str):
    """加载当日候选股池"""
    path = f"{CANDIDATES_DIR}/{date_str}.json"
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}

def save_candidates(date_str, data):
    """保存候选股池"""
    path = f"{CANDIDATES_DIR}/{date_str}.json"
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_limitup_history(date_str):
    """加载涨停历史"""
    path = f"{LIMITUP_DIR}/{date_str}.json"
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}

def save_limitup_history(date_str, data):
    """保存涨停历史"""
    path = f"{LIMITUP_DIR}/{date_str}.json"
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_trend_patterns():
    """加载趋势图形库"""
    path = f"{TREND_DIR}/patterns.json"
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {"patterns": [], "updated": ""}

def save_trend_patterns(data):
    """保存趋势图形库"""
    path = f"{TREND_DIR}/patterns.json"
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def analyze_pre_limitup(stock_data, days=5):
    """
    分析涨停前的量价特征
    返回关键指标
    """
    close = stock_data.get("close", 0)
    open_p = stock_data.get("open", 0)
    high = stock_data.get("high", 0)
    low = stock_data.get("low", 0)
    vol = stock_data.get("vol", 0)
    amount = stock_data.get("amount", 0)
    pct = stock_data.get("pct", 0)
    
    if close <= 0:
        return None
    
    # 1. 涨幅
    change_pct = stock_data.get("pct", 0)
    
    # 2. 开盘方式（竞价高开/低开/平开）
    if open_p > close * 1.02:
        open_type = "高开"
    elif open_p < close * 0.98:
        open_type = "低开"
    else:
        open_type = "平开"
    
    # 3. 上影线分析（关键！涨停前往往有上影线）
    if high > close:
        upper_shadow = high - close
        body = close - low if close > low else 0
        if body > 0:
            shadow_ratio = upper_shadow / body
        else:
            shadow_ratio = 0
        has_upper_shadow = shadow_ratio > 0.5  # 上影线>50%实体
    else:
        upper_shadow = 0
        shadow_ratio = 0
        has_upper_shadow = False
    
    # 4. 下影线分析
    if close > open_p:
        lower_shadow = open_p - low
        body = close - open_p
        if body > 0:
            lsr = lower_shadow / body
        else:
            lsr = 0
    else:
        lower_shadow = 0
        lsr = 0
    
    # 5. 振幅
    amplitude = (high - low) / close * 100 if close > 0 else 0
    
    # 6. 成交额（万元）
    amount_yi = amount / 10000  # 转为亿元
    
    # 7. 量比估算（用今日成交量对比平时）
    vol_ratio = stock_data.get("vol_ratio", 1.0)  # 外部传入
    
    return {
        "收盘": round(close, 2),
        "涨幅": round(change_pct, 2),
        "开盘方式": open_type,
        "上影线": round(upper_shadow, 2),
        "上影比例": round(shadow_ratio, 2),
        "有上影线": has_upper_shadow,
        "振幅": round(amplitude, 2),
        "成交额亿": round(amount_yi, 2),
        "量比": round(vol_ratio, 2),
    }

def recognize_pattern(stock_info):
    """
    识别K线形态（基于已学知识）
    """
    patterns = []
    
    close = stock_info.get("收盘", 0)
    high = stock_info.get("high", 0)
    low = stock_info.get("low", 0)
    open_p = stock_info.get("open", 0)
    pct = stock_info.get("涨幅", 0)
    upper_ratio = stock_info.get("上影比例", 0)
    amplitude = stock_info.get("振幅", 0)
    
    if close <= 0:
        return patterns
    
    # 1. 上影线突破形态（仙人指路）
    # 定义：上影线>50%实体，第二天或第三天涨停
    if upper_ratio > 0.5 and high > close * 1.03:
        patterns.append({
            "pattern": "上影线突破（仙人指路）",
            "confidence": "高" if upper_ratio > 1.0 else "中",
            "signal": "次日涨停概率高",
            "source": "shadow_break.py"
        })
    
    # 2. 缩量小K线（主力控盘）
    # 定义：振幅<3%，成交额萎缩
    if amplitude < 3 and pct > -2 and pct < 2:
        patterns.append({
            "pattern": "缩量小K线",
            "confidence": "高",
            "signal": "主力控盘，等待突破",
            "source": "威科夫"
        })
    
    # 3. 跳空高开
    if open_p > close * 1.05:
        patterns.append({
            "pattern": "跳空高开",
            "confidence": "高" if pct > 9 else "中",
            "signal": "超预期高开，板块共振",
            "source": "养家心法"
        })
    
    # 4. 加速赶底
    # 定义：连续下跌后突然放量大涨
    if pct > 5 and amplitude > 8:
        patterns.append({
            "pattern": "加速赶底（反弹）",
            "confidence": "中",
            "signal": "可能是超跌反弹，需确认",
            "source": "第二章"
        })
    
    # 5. 推土机（一字板）
    if pct >= 9.9 and amplitude < 1:
        patterns.append({
            "pattern": "一字涨停（推土机）",
            "confidence": "高",
            "signal": "最强封板，明日高溢价",
            "source": "第二章"
        })
    
    # 6. 尾盘大阳线
    if high > close * 1.05 and high == close:  # 接近涨停
        patterns.append({
            "pattern": "尾盘涨停",
            "confidence": "高",
            "signal": "主力试探，次日看竞价",
            "source": "第二章"
        })
    
    # 7. 收敛形态（旗型整理末端）
    # 定义：振幅逐渐收窄（3%,2%,1%...）
    # 这个需要历史数据对比，暂时标记
    if amplitude < 2 and pct > 0:
        patterns.append({
            "pattern": "收敛整理（举重理论：收敛=安全）",
            "confidence": "中",
            "signal": "方向选择，注意突破信号",
            "source": "举重理论"
        })
    
    return patterns

def add_to_limitup_history(date_str, name, code, pre_data, today_data):
    """添加涨停历史"""
    history = load_limitup_history(date_str)
    if code not in history:
        history[code] = {
            "name": name,
            "code": code,
            "date": date_str,
            "pre_pattern": pre_data,      # 涨停前的数据
            "today": today_data,          # 涨停日数据
            "limitup_price": pre_data.get("收盘", 0) * 1.1,  # 估算涨停价
        }
    save_limitup_history(date_str, history)

def find_similar_patterns(new_stock, patterns_db, top_n=5):
    """
    在历史涨停库中找相似图形
    """
    results = []
    pre_pct = new_stock.get("涨幅", 0)
    pre_upper = new_stock.get("上影比例", 0)
    pre_amp = new_stock.get("振幅", 0)
    
    for entry in patterns_db:
        pre = entry.get("pre_pattern", {})
        # 相似度评分
        score = 0
        if abs(pre.get("涨幅", 0) - pre_pct) < 3:
            score += 30
        if abs(pre.get("上影比例", 0) - pre_upper) < 0.3:
            score += 30
        if abs(pre.get("振幅", 0) - pre_amp) < 2:
            score += 20
        if pre.get("有上影线") == new_stock.get("有上影线"):
            score += 20
        
        if score >= 40:
            results.append({
                "stock": entry["name"],
                "date": entry.get("date", ""),
                "score": score,
                "outcome": entry.get("today", {}).get("涨停次日", "未知")
            })
    
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_n]

def daily_scan(today_date):
    """
    每日扫描：收集候选股池 + 分析图形 + 寻找机会
    """
    print(f"📊 每日图形扫描 | {today_date}")
    print("=" * 60)
    
    candidates = load_candidates(today_date)
    limitup_today = load_limitup_history(today_date)
    patterns_db = load_trend_patterns()
    
    print(f"候选股池：{len(candidates)} 只")
    print(f"涨停历史：{len(limitup_today)} 只")
    print(f"趋势图形库：{len(patterns_db.get('patterns', []))} 条")
    print()

def init_candidates_from_watch(date_str):
    """
    从昨日强势股初始化今日候选股池
    格式：(代码, 名称, 昨日收盘, 昨日涨幅, 关注理由)
    """
    # 手动更新候选股池（每日收盘后）
    # 这个由用户或定时任务更新
    default_pool = {
        "sz000586": {"name": "汇源通信", "close": 25.12, "pct": 10.0, "reason": "光纤龙头5连板"},
        "sz002384": {"name": "东山精密", "close": 131.90, "pct": 10.0, "reason": "算力首板"},
        "sz002281": {"name": "光迅科技", "close": 98.20, "pct": 10.0, "reason": "光模块首板"},
        "sh601869": {"name": "长飞光纤", "close": 362.18, "pct": 10.0, "reason": "光纤首板"},
    }
    save_candidates(date_str, default_pool)
    return default_pool

if __name__ == "__main__":
    import sys
    today = datetime.now().strftime("%Y%m%d")
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "--scan":
            daily_scan(today)
        elif cmd == "--init":
            data = init_candidates_from_watch(today)
            print(f"✅ 已初始化 {len(data)} 只候选股")
        elif cmd == "--collect":
            # 收集实时数据
            cands = load_candidates(today)
            if not cands:
                cands = init_candidates_from_watch(today)
            codes = list(cands.keys())
            data = get_realtime(codes)
            print(f"收集了 {len(data)} 只股票数据")
    else:
        daily_scan(today)
