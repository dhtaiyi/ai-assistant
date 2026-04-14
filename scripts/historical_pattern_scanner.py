#!/usr/bin/env python3
"""
历史图形扫描器 - 扫描历史K线找涨停前兆

功能：
1. 获取任意股票的历史K线（前复权日线）
2. 分析历史涨停前N天的量价特征
3. 在涨停历史库中找相似图形
4. 扫描全市场历史数据，寻找"即将涨停"前的形态

用法：
  python3 historical_pattern_scanner.py                    # 扫描候选股历史
  python3 historical_pattern_scanner.py --scan sz000586     # 扫描单只
  python3 historical_pattern_scanner.py --full               # 全市场历史扫描
"""

import requests
import json
import re
import os
import sys
from datetime import datetime, timedelta
from collections import defaultdict

BASE = os.path.expanduser("~/.openclaw/workspace/stock-patterns")

# ==================== 历史K线获取 ====================

def get_history_kline(code, count=60):
    """获取前复权日线"""
    exchange = "sz" if code.startswith("sz") else "sh"
    full_code = exchange + code.lstrip("szh")
    
    url = (f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
           f"?_var=kline_dayhfq&param={full_code},day,2025-01-01,2026-04-10,{count},qfq")
    
    try:
        r = requests.get(url, timeout=10)
        m = re.search(r'=\{.*\}', r.text)
        if not m:
            return []
        
        data = json.loads(m.group(0)[1:])
        qfqdata = data.get('data', {}).get(full_code, {}).get('qfqday', [])
        
        result = []
        for item in qfqdata:
            if len(item) >= 6:
                result.append({
                    "date": item[0],
                    "open": float(item[1]),
                    "close": float(item[2]),
                    "high": float(item[3]),
                    "low": float(item[4]),
                    "vol": float(item[5]),
                })
        return result
    except:
        return []

# ==================== 形态分析 ====================

def analyze_single_kline(k, prev_k=None):
    """分析单根K线特征"""
    close = k["close"]
    open_p = k["open"]
    high = k["high"]
    low = k["low"]
    
    if close <= 0 or open_p <= 0:
        return None
    
    body = abs(close - open_p)
    upper_shadow = high - max(close, open_p)
    lower_shadow = min(close, open_p) - low
    
    # 涨幅
    pct = 0
    if prev_k and prev_k["close"] > 0:
        pct = (close - prev_k["close"]) / prev_k["close"] * 100
    
    # 上影比例
    if body > 0:
        upper_ratio = upper_shadow / body
        lower_ratio = lower_shadow / body
    else:
        upper_ratio = 0
        lower_ratio = 0
    
    # 振幅
    amp = (high - low) / close * 100 if close > 0 else 0
    
    # K线类型判断
    is_red = close > open_p  # 阳线
    is_upper_shadow = upper_ratio > 0.5  # 上影线>50%实体
    is_lower_shadow = lower_ratio > 0.5  # 下影线>50%实体
    is_doji = body < (high - low) * 0.1  # 十字星（实体<10%）
    
    return {
        "date": k["date"],
        "close": round(close, 2),
        "pct": round(pct, 2),
        "body": round(body, 2),
        "upper_shadow": round(upper_shadow, 2),
        "lower_shadow": round(lower_shadow, 2),
        "upper_ratio": round(upper_ratio, 2),
        "lower_ratio": round(lower_ratio, 2),
        "amplitude": round(amp, 2),
        "is_red": is_red,
        "is_upper_shadow": is_upper_shadow,
        "is_lower_shadow": is_lower_shadow,
        "is_doji": is_doji,
        "limit_up": pct >= 9.9,
        "limit_down": pct <= -9.9,
    }

def analyze_before_limitup(klines, lookback=10):
    """
    分析涨停前的图形特征
    找涨停日，然后往前看N天
    """
    results = []
    for i, k in enumerate(klines):
        analysis = analyze_single_kline(k, klines[i-1] if i > 0 else None)
        if not analysis:
            continue
        
        if analysis["limit_up"]:
            # 找到涨停，往前看lookback天
            before = []
            for j in range(max(0, i-lookback), i):
                a = analyze_single_kline(klines[j], klines[j-1] if j > 0 else None)
                before.append(a)
            
            # 分析涨停前特征
            features = analyze_before_features(before)
            
            results.append({
                "limitup_date": k["date"],
                "limitup_price": k["close"],
                "before": before,
                "features": features,
            })
    
    return results

def analyze_before_features(before_list):
    """
    分析涨停前的综合特征
    """
    if not before_list:
        return {}
    
    # 最近3天的关键特征
    recent3 = before_list[-3:] if len(before_list) >= 3 else before_list
    last1 = before_list[-1] if before_list else {}
    
    # 统计
    red_count = sum(1 for k in before_list if k.get("is_red", False))
    upper_shadow_count = sum(1 for k in before_list if k.get("is_upper_shadow", False))
    avg_amp = sum(k.get("amplitude", 0) for k in before_list) / len(before_list)
    
    # 关键判断
    has_upper_shadow_before = any(k.get("is_upper_shadow", False) for k in recent3)
    avg_vol = sum(k.get("body", 0) for k in recent3) / len(recent3)
    
    # 收敛特征：振幅逐日收窄
    amps = [k.get("amplitude", 0) for k in before_list[-5:] if k.get("amplitude", 0) > 0]
    is_converging = len(amps) >= 3 and amps[-1] < amps[-2] < amps[-3]
    
    return {
        "days_before": len(before_list),
        "red_days": red_count,
        "upper_shadow_days": upper_shadow_count,
        "avg_amplitude": round(avg_amp, 2),
        "has_upper_shadow_before": has_upper_shadow_before,
        "last_day": {
            "date": last1.get("date", ""),
            "pct": last1.get("pct", 0),
            "upper_ratio": last1.get("upper_ratio", 0),
            "amplitude": last1.get("amplitude", 0),
        },
        "is_converging": is_converging,
        "pattern_type": classify_pattern(before_list),
    }

def classify_pattern(before_list):
    """根据涨停前图形分类"""
    if len(before_list) < 2:
        return "数据不足"
    
    last = before_list[-1]
    recent = before_list[-3:] if len(before_list) >= 3 else before_list
    
    # 1. 仙人指路：前一天上影线明显
    if len(before_list) >= 2:
        prev = before_list[-2]
        if prev.get("is_upper_shadow", False) and prev.get("upper_ratio", 0) > 0.5:
            return "上影线突破（仙人指路）"
    
    # 2. 小市值+连续阳线
    if last.get("is_red", False) and sum(1 for k in recent if k.get("is_red", False)) >= 2:
        return "连续阳线吸筹"
    
    # 3. 收敛整理后涨停
    amps = [k.get("amplitude", 0) for k in before_list if k.get("amplitude", 0) > 0]
    if len(amps) >= 3 and amps[-1] < amps[-2] < amps[-3]:
        return "收敛整理后突破"
    
    # 4. 低位涨停
    if last.get("pct", 0) >= 9.9 and last.get("amplitude", 0) > 7:
        return "低位首板"
    
    # 5. 跳空高开
    if len(before_list) >= 2:
        prev = before_list[-2]
        if prev.get("close", 0) > 0 and last.get("open", 0) > prev.get("close", 0) * 1.05:
            return "跳空高开"
    
    # 6. 缩量整理
    if last.get("amplitude", 0) < 3 and last.get("is_red", False):
        return "缩量小阳线"
    
    return "普通形态"

def scan_stock_history(code, name, lookback=30):
    """
    扫描单只股票的历史涨停前图形
    """
    klines = get_history_kline(code, lookback + 20)
    if len(klines) < 5:
        return None
    
    limitup_records = analyze_before_limitup(klines, lookback)
    if not limitup_records:
        return {
            "code": code,
            "name": name,
            "total_klines": len(klines),
            "limitup_count": 0,
            "records": [],
        }
    
    return {
        "code": code,
        "name": name,
        "total_klines": len(klines),
        "limitup_count": len(limitup_records),
        "records": limitup_records,
    }

def find_similar_pattern(new_klines, pattern_db):
    """
    在历史库中找相似图形
    new_klines: 最近几天的K线分析
    pattern_db: 历史涨停前图形库
    """
    if not new_klines or not pattern_db:
        return []
    
    last = new_klines[-1]
    results = []
    
    for entry in pattern_db:
        for rec in entry.get("records", []):
            feat = rec.get("features", {})
            last_feat = feat.get("last_day", {})
            
            # 相似度计算
            score = 0
            
            # 上影线特征相似
            if last.get("is_upper_shadow") and last_feat.get("upper_ratio", 0) > 0.3:
                score += 30
            
            # 振幅相似
            if abs(last.get("amplitude", 0) - last_feat.get("amplitude", 0)) < 2:
                score += 25
            
            # 图形类型相同
            if last.get("is_upper_shadow") and feat.get("has_upper_shadow_before"):
                score += 30
            
            # 收敛形态
            if feat.get("is_converging"):
                score += 15
            
            if score >= 40:
                results.append({
                    "stock": entry["name"],
                    "limitup_date": rec.get("limitup_date", ""),
                    "pattern": feat.get("pattern_type", ""),
                    "score": score,
                    "before_days": feat.get("days_before", 0),
                })
    
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:5]

# ==================== 主扫描 ====================

def main():
    print(f"📊 历史图形扫描器 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 72)
    
    # 加载涨停历史库
    patterns_path = f"{BASE}/trend_patterns/patterns.json"
    with open(patterns_path) as f:
        patterns_db_data = json.load(f)
    pattern_db = patterns_db_data.get("patterns", [])
    
    # 加载候选股
    today = datetime.now().strftime("%Y%m%d")
    cand_path = f"{BASE}/candidates/{today}.json"
    
    if os.path.exists(cand_path):
        with open(cand_path) as f:
            candidates = json.load(f)
    else:
        print("❌ 今日候选股池为空，先运行 daily_pattern_scan.py")
        return
    
    print(f"候选股池: {len(candidates)} 只 | 历史图形库: {len(pattern_db)} 条\n")
    
    # 扫描候选股的历史K线
    print("=" * 72)
    print("🔍 历史涨停前图形扫描")
    print("-" * 72)
    
    all_records = []
    
    for code, cand in candidates.items():
        name = cand.get("name", code)
        result = scan_stock_history(code, name, lookback=30)
        
        if result and result["limitup_count"] > 0:
            print(f"\n【{name}】{code[-6:]}  历史涨停 {result['limitup_count']} 次")
            
            for rec in result["records"]:
                feat = rec.get("features", {})
                last_f = feat.get("last_day", {})
                pattern = feat.get("pattern_type", "")
                
                print(f"  📅 {rec['limitup_date']} 涨停前特征:")
                print(f"     涨停前{feat.get('days_before', '?')}天 | "
                      f"红{feat.get('red_days', 0)}天 | "
                      f"上影{feat.get('upper_shadow_days', 0)}次 | "
                      f"均振幅{feat.get('avg_amplitude', 0):.1f}%")
                print(f"     图形类型: {pattern}")
                
                all_records.append({
                    "code": code,
                    "name": name,
                    "record": rec,
                })
        else:
            print(f"\n【{name}】{code[-6:]}  近30天无涨停记录")
    
    print()
    print("=" * 72)
    print("📋 历史涨停前图形汇总")
    print("-" * 72)
    
    # 按图形类型分组
    pattern_groups = defaultdict(list)
    for rec in all_records:
        pattern = rec["record"]["features"].get("pattern_type", "")
        pattern_groups[pattern].append(rec)
    
    for pattern, recs in sorted(pattern_groups.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"\n【{pattern}】共 {len(recs)} 次历史验证")
        for rec in recs[:3]:  # 最多显示3个
            r = rec["record"]
            print(f"  • {rec['name']} 于 {r['limitup_date']} 涨停，"
                  f"涨停前特征: {r['features'].get('last_day', {}).get('date', '')} "
                  f"涨{r['features'].get('last_day', {}).get('pct', 0):+.1f}%")
    
    print()
    print("=" * 72)
    print("🔮 明日图形预测（基于历史规律）")
    print("-" * 72)
    
    # 扫描今日候选的最近形态
    for code, cand in list(candidates.items())[:5]:
        name = cand.get("name", code)
        klines = get_history_kline(code, 10)
        if len(klines) < 2:
            continue
        
        kline_analysis = []
        for i, k in enumerate(klines[-5:]):
            a = analyze_single_kline(k, klines[i-1] if i > 0 else None)
            if a:
                kline_analysis.append(a)
        
        if not kline_analysis:
            continue
        
        last = kline_analysis[-1]
        similar = find_similar_pattern(kline_analysis, all_records)
        
        print(f"\n【{name}】近期形态分析:")
        print(f"  最近5天: ", end="")
        for k in kline_analysis[-5:]:
            pct = k.get("pct", 0)
            flag = "🔴" if k.get("is_upper_shadow") else ("阳" if k.get("is_red") else "阴")
            print(f"{k['date'][5:]}({pct:+.1f}%{flag}) ", end="")
        print()
        
        print(f"  最新: {last['date']} 涨跌幅{last['pct']:+.1f}% "
              f"上影比{last['upper_ratio']:.2f} 振幅{last['amplitude']:.1f}%")
        
        if similar:
            items = [f"{s['stock']}({s['pattern']},{s['score']}分)" for s in similar[:3]]
            print(f"  🏆历史相似: {', '.join(items)}")
        else:
            print(f"  📍无历史相似涨停记录")

if __name__ == "__main__":
    main()
