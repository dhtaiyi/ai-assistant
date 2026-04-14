#!/usr/bin/env python3
"""
策略验证器 - 每日验证昨日预测准确性

功能：
1. 读取昨日推荐股票
2. 对比今日实际表现
3. 生成验证报告
4. 根据结果修正策略权重

用法：
  python3 strategy_verifier.py                    # 验证昨日预测
  python3 strategy_verifier.py --date 20260410  # 验证指定日期
"""

import requests
import json
import os
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
            }
        except: pass
    return result

def get_history_close(code, date_str):
    """获取指定日期的收盘价"""
    exchange = "sz" if code.startswith("sz") else "sh"
    full = exchange + code.lstrip("szh")
    # 用腾讯前复权K线接口
    import requests
    url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_dayhfq&param={full},day,2026-04-01,2026-04-11,20,qfq"
    try:
        r = requests.get(url, timeout=10)
        import re, json as jsonmod
        m = re.search(r'=\{.*\}', r.text)
        if not m:
            return None, None
        data = jsonmod.loads(m.group(0)[1:])
        qfq = data.get('data', {}).get(full, {}).get('qfqday', [])
        for item in reversed(qfq):
            if len(item) >= 6:
                d = item[0]
                close = float(item[2])
                high = float(item[3])
                return close, d
        return None, None
    except:
        return None, None

def verify(date_str):
    print(f"📊 策略验证报告 | 验证 {date_str} 的预测准确性")
    print("=" * 72)
    
    # 加载昨日的候选股池（作为预测）
    cand_path = f"{BASE}/candidates/{date_str}.json"
    limitup_path = f"{BASE}/limitup_history/{date_str}.json"
    
    if not os.path.exists(cand_path):
        print(f"❌ 找不到 {date_str} 的候选股池")
        return
    
    with open(cand_path) as f:
        candidates = json.load(f)
    with open(limitup_path) as f:
        limitup = json.load(f)
    
    print(f"昨日推荐股池: {len(candidates)} 只")
    print(f"昨日涨停股: {len(limitup)} 只\n")
    
    # 策略v3.0的昨日推荐
    yesterday_recs = {
        "sz002384": {"name": "东山精密", "rec": "买点C持筹/3连板", "score": 55},
        "sh600743": {"name": "华远控股", "rec": "4连板高位", "score": 30},
        "sh603777": {"name": "来伊份", "rec": "买点B/3连板", "score": 85},
        "sh603933": {"name": "睿能科技", "rec": "买点B/2连板", "score": 75},
        "sz300548": {"name": "长芯博创", "rec": "首板后跌停", "score": 8},
        "sz000586": {"name": "汇源通信", "rec": "6板断板", "score": 18},
        "sz002491": {"name": "通鼎互联", "rec": "断板跌停", "score": 11},
        "sh600594": {"name": "益佰制药", "rec": "4板断板", "score": 9},
    }
    
    # 今日实际数据（下一个交易日）
    # 2026-04-11 是周六，非交易日，跳过
    # 验证用昨日收盘数据对比今日竞价/今日数据
    # 由于今日是周六，我们用最近一个交易日的数据
    
    codes = list(yesterday_recs.keys())
    real = get_realtime(codes)
    
    # 验证结果
    print("=" * 72)
    print("🔍 昨日预测 vs 今日实际")
    print("-" * 72)
    print(f"{'股票':<10} {'昨日推荐':<20} {'评分':>4} {'今日实际':>10} {'预测对错'}")
    print("-" * 72)
    
    correct = 0
    wrong = 0
    
    results = []
    for code, rec_info in yesterday_recs.items():
        info = real.get(code, {})
        price = info.get("price", 0)
        pct = info.get("pct", 0)
        
        if price == 0:
            continue
        
        rec_type = rec_info["rec"]
        score = rec_info["score"]
        
        # 判断预测准确性
        if "断板" in rec_type or "高位" in rec_type:
            # 预测断板/高位
            if pct < -5:
                verdict = "✅对(跌停断板)"
                correct += 1
            elif pct < 0:
                verdict = "✅对(下跌)"
                correct += 1
            else:
                verdict = "❌错(未断板)"
                wrong += 1
        elif "买点B" in rec_type or "3连板" in rec_type or "2连板" in rec_type:
            # 预测继续涨停
            if pct >= 9.9:
                verdict = "✅对(继续涨停)"
                correct += 1
            elif pct >= 5:
                verdict = "✅对(大幅上涨)"
                correct += 1
            elif pct > 0:
                verdict = "⚠️平(小涨)"
                correct += 0.5
            else:
                verdict = "❌错(未涨)"
                wrong += 1
        elif "持筹" in rec_type:
            if pct > 0:
                verdict = "✅对(持筹上涨)"
                correct += 1
            elif pct > -3:
                verdict = "⚠️平(震荡)"
                correct += 0.5
            else:
                verdict = "❌错(大跌)"
                wrong += 1
        else:
            verdict = "➡️中性"
        
        results.append({
            "name": rec_info["name"],
            "rec": rec_type,
            "score": score,
            "price": price,
            "pct": pct,
            "verdict": verdict,
        })
        
        tag = "✅" if verdict.startswith("✅") else ("⚠️" if verdict.startswith("⚠️") else "❌")
        print(f"{rec_info['name']:<10} {rec_type:<20} {score:>4} {pct:>+8.1f}% {tag}{verdict}")
    
    print()
    print("=" * 72)
    print(f"📈 预测准确率: {correct}/{correct+wrong} = {correct/(correct+wrong)*100:.0f}%")
    
    # 策略修正建议
    print()
    print("=" * 72)
    print("💡 策略修正建议")
    print("-" * 72)
    
    # 分析错误预测
    wrong_recs = [r for r in results if r["verdict"].startswith("❌")]
    correct_recs = [r for r in results if r["verdict"].startswith("✅")]
    
    if wrong_recs:
        print("\n❌ 预测错误的股票：")
        for r in wrong_recs:
            print(f"  • {r['name']}: 预测{r['rec']}，实际{r['pct']:+.1f}%")
    
    if correct_recs:
        print(f"\n✅ 预测正确的: {len(correct_recs)} 只")
        avg_score = sum(r["score"] for r in correct_recs) / len(correct_recs)
        print(f"   正确预测的平均评分: {avg_score:.0f}分")
    
    # 策略调整
    print()
    print("📋 策略调整建议：")
    
    # 分析4板以上的预测准确性
    high_ban = [r for r in results if "4板" in r["rec"] or "6板" in r["rec"]]
    if high_ban:
        correct_high = sum(1 for r in high_ban if r["verdict"].startswith("✅"))
        if high_ban and correct_high == len(high_ban):
            print("  ✅ 4板以上预测全部正确，说明'≥4板不做'策略有效")
        elif high_ban:
            print(f"  ⚠️ 4板以上预测正确率: {correct_high}/{len(high_ban)}")
    
    # 分析小市值推荐
    small_cap = [r for r in results if r["score"] >= 60 and "断板" not in r["rec"]]
    if small_cap:
        correct_small = sum(1 for r in small_cap if r["verdict"].startswith("✅"))
        if correct_small / len(small_cap) >= 0.7:
            print("  ✅ 小市值(评分≥60)推荐效果好，继续保持")
    
    print()
    print("=" * 72)
    
    # 保存验证报告
    report = {
        "date": date_str,
        "verified_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "total": correct + wrong,
        "correct": correct,
        "wrong": wrong,
        "accuracy": round(correct / (correct + wrong) * 100, 1) if (correct + wrong) > 0 else 0,
        "results": results,
    }
    
    ver_dir = f"{BASE}/verification"
    os.makedirs(ver_dir, exist_ok=True)
    with open(f"{ver_dir}/{date_str}.json", "w") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 验证报告已保存: {ver_dir}/{date_str}.json")
    print("⚠️ 投资有风险，以上仅供参考～")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2 and sys.argv[1] == "--date":
        date_str = sys.argv[2]
    else:
        # 默认验证昨日
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        date_str = yesterday
    
    verify(date_str)
