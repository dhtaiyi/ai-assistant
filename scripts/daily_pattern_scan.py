#!/usr/bin/env python3
"""
每日图形扫描器 - 基于历史涨停图形库寻找机会

功能：
1. 扫描候选股池的量价数据
2. 与历史涨停前图形对比
3. 输出相似匹配 + 明日重点关注

用法：
  python3 daily_pattern_scan.py              # 扫描今日候选
  python3 daily_pattern_scan.py --date 20260410  # 扫描指定日期
"""

import requests
import json
import os
import sys
from datetime import datetime, timedelta

BASE = os.path.expanduser("~/.openclaw/workspace/stock-patterns")

def get_realtime(codes):
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
                "open": float(parts[5]) if parts[5] else 0,
                "close": float(parts[4]) if parts[4] else 0,
                "high": float(parts[33]) if parts[33] else 0,
                "low": float(parts[34]) if parts[34] else 0,
                "vol": float(parts[36]) if parts[36] else 0,
                "amount": float(parts[37]) if parts[37] else 0,
                "pct": float(parts[32]) if parts[32] else 0,
                "circ_mv": float(parts[45]) if parts[45] else 0,
            }
        except: pass
    return result

def analyze_pattern(info, yesterday_close=None):
    """分析单只股票的量价形态"""
    price = info.get("price", 0)
    close_y = yesterday_close or info.get("close", 0)
    open_p = info.get("open", 0)
    high = info.get("high", 0)
    low = info.get("low", 0)
    pct = info.get("pct", 0)
    circ = info.get("circ_mv", 0)
    
    if price <= 0 or close_y <= 0:
        return None
    
    # 涨幅
    change = (price - close_y) / close_y * 100 if close_y > 0 else 0
    
    # 上影线
    if high > price:
        upper_shadow = high - price
        body = price - low if price > low else 0
        shadow_ratio = upper_shadow / body if body > 0 else 0
    else:
        upper_shadow = 0
        shadow_ratio = 0
    
    # 振幅
    amp = (high - low) / close_y * 100 if close_y > 0 else 0
    
    # 开盘方式
    if open_p > close_y * 1.03:
        open_type = "高开"
    elif open_p < close_y * 0.97:
        open_type = "低开"
    else:
        open_type = "平开"
    
    # 量能（成交额亿）
    amount_yi = info.get("amount", 0) / 10000
    
    return {
        "code": "",
        "name": info.get("name", ""),
        "price": round(price, 2),
        "pct": round(change, 2),
        "circ_mv": round(circ, 1),
        "open_type": open_type,
        "upper_shadow": round(upper_shadow, 2),
        "shadow_ratio": round(shadow_ratio, 2),
        "amplitude": round(amp, 2),
        "amount_yi": round(amount_yi, 2),
        "patterns": [],
    }

def recognize_patterns(analysis):
    """识别K线形态"""
    pcts = analysis["pct"]
    shadow_ratio = analysis["shadow_ratio"]
    amp = analysis["amplitude"]
    open_type = analysis["open_type"]
    amount = analysis["amount_yi"]
    circ = analysis["circ_mv"]
    patterns = []
    
    # 1. 上影线突破（仙人指路）
    if shadow_ratio > 0.5:
        patterns.append(("🔴上影线突破", f"上影比例{shadow_ratio:.1f}倍，仙人指路！"))
    
    # 2. 一字涨停（推土机）
    if pcts >= 9.9 and amp < 2:
        patterns.append(("🚀一字涨停", "最强封板！"))
    
    # 3. 高开超预期
    if open_type == "高开" and pcts >= 5:
        patterns.append(("🔥高开超预期", f"竞价强，板块共振信号"))
    
    # 4. 缩量整理
    if amp < 3 and -2 < pcts < 2:
        patterns.append(("📍缩量整理", "主力控盘，等待方向选择"))
    
    # 5. 小市值+主线
    if 30 <= circ <= 200 and abs(pcts) >= 5:
        patterns.append(("💎小市值异动", f"市值{circ:.0f}亿，弹性大！"))
    
    # 6. 成交额放大
    if amount > 10:
        patterns.append(("📊放量", f"成交{amount:.1f}亿，有资金参与"))
    
    return patterns

def match_similar_history(analysis, limitup_db):
    """在涨停历史库中找相似图形"""
    results = []
    
    for code, entry in limitup_db.items():
        # 简单相似度（基于我们实际有的数据）
        score = 0
        curr_pct = analysis["pct"]
        hist_pct = entry.get("pct", 0)
        
        # 涨幅相似度
        if abs(hist_pct - curr_pct) < 3:
            score += 30
        
        # 小市值优先
        if 30 <= analysis.get("circ_mv", 0) <= 200:
            score += 20
        
        # 成交额适中
        amount = entry.get("amount_yi", 0)
        if 5 <= amount <= 50:
            score += 20
        
        # 同样涨停
        if hist_pct >= 9.9 and curr_pct >= 9.9:
            score += 20
        
        if score >= 40:
            results.append((entry.get("name", code), entry.get("name", ""), score))
    
    results.sort(key=lambda x: x[2], reverse=True)
    return results[:3]

def generate_report(date_str):
    """生成每日图形扫描报告"""
    print(f"📊 每日图形扫描报告 | {date_str}")
    print("=" * 70)
    
    # 加载数据
    cand_path = f"{BASE}/candidates/{date_str}.json"
    limitup_path = f"{BASE}/limitup_history/{date_str}.json"
    patterns_path = f"{BASE}/trend_patterns/patterns.json"
    
    if not os.path.exists(cand_path):
        print("❌ 今日候选股池为空，请先运行初始化")
        return
    
    with open(cand_path) as f:
        candidates = json.load(f)
    with open(limitup_path) as f:
        limitup_raw = json.load(f)
    # 转换为 dict: {code: entry}
    limitup_db = {item['code']: item for item in limitup_raw}
    with open(patterns_path) as f:
        patterns_db = json.load(f)
    
    print(f"候选股池：{len(candidates)} 只 | 涨停历史：{len(limitup_db)} 只")
    print(f"历史图形库：{len(patterns_db['patterns'])} 条")
    print()
    
    # 获取实时数据
    codes = list(candidates.keys())
    real_data = get_realtime(codes)
    
    print("=" * 70)
    print("📈 今日候选股实时形态")
    print("-" * 70)
    
    # 分类输出
    hot_candidates = []
    
    for code, cand in candidates.items():
        info = real_data.get(code, {})
        if not info:
            continue
        
        y_close = cand.get("close_y", 0)
        analysis = analyze_pattern(info, y_close)
        if not analysis:
            continue
        
        patterns = recognize_patterns(analysis)
        similar = match_similar_history(analysis, limitup_db)
        
        print(f"\n【{cand['name']}】{code[-6:]} | {analysis['price']}元 {analysis['pct']:+.1f}%")
        print(f"  昨日收盘: {y_close} | 流通市值: {analysis['circ_mv']}亿 | 成交: {analysis['amount_yi']:.1f}亿")
        print(f"  开盘:{analysis['open_type']} | 上影线:{analysis['upper_shadow']} | 振幅:{analysis['amplitude']:.1f}%")
        
        if patterns:
            for p, desc in patterns:
                print(f"  {p}: {desc}")
        else:
            print(f"  📍无明显形态，继续观察")
        
        if similar:
            print(f"  🏆历史相似: {', '.join([f'{n}({s}分)' for n,_,s in similar])}")
        
        # 标记重点候选
        if any(p[0] in ["🔴上影线突破", "🚀一字涨停", "💎小市值异动", "🔥高开超预期"] for p in patterns):
            hot_candidates.append((cand["name"], code, analysis, patterns, similar))
    
    print()
    print("=" * 70)
    print("🎯 明日重点关注（符合历史涨停前图形）")
    print("-" * 70)
    
    if hot_candidates:
        hot_candidates.sort(key=lambda x: len(x[3]), reverse=True)
        for name, code, ana, pats, sim in hot_candidates[:5]:
            main_pattern = [p[0] for p in pats]
            print(f"\n👉 {name}({code[-6:]}) 评分:{len(pats)}个形态")
            print(f"   形态: {' / '.join([p[0] for p in pats])}")
            print(f"   流通市值: {ana['circ_mv']:.0f}亿 | 明日止损参考: {ana['price']*0.93:.2f}元")
    else:
        print("今日暂无符合历史涨停图形的标的，建议明日继续观察")
    
    print()
    print("=" * 70)
    print("📚 历史验证过的涨停前图形（图形库）")
    print("-" * 70)
    for p in patterns_db["patterns"]:
        print(f"  {p['id']} {p['名称']}: {p['特征']}（置信度:{p['置信度']}）")
    
    print()
    print("⚠️ 投资有风险，以上仅供参考～")
    print(f"📅 生成时间: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--date":
        date_str = sys.argv[2]
    else:
        date_str = datetime.now().strftime("%Y%m%d")
    
    generate_report(date_str)
