#!/usr/bin/env python3
"""
竞价历史规律追踪
==================
分析每日竞价选股的历史表现，寻找规律

功能：
1. 统计每个股在历史竞价中出现的次数
2. 追踪高开股的后续走势（收盘vs开盘）
3. 找出"反复竞价"强势股
4. 总结规律，输出飞书报告
"""

import json, os, glob
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import urllib.request
import re

HIST_DIR = Path("/home/dhtaiyi/.openclaw/workspace/stock-data/auction")
FEISHU_USER = "ou_04add8ebe219f09799570c70e3cdc732"

# ─── 读取所有历史 ───────────────────────────────────────────────────────
def load_history(days: int = 10):
    """加载最近days天的历史数据"""
    files = sorted(HIST_DIR.glob("*.json"))[-days:]
    all_data = []
    for f in files:
        with open(f) as fp:
            d = json.load(fp)
            all_data.append(d)
    return all_data

# ─── 腾讯收盘价 ─────────────────────────────────────────────────────────
def get_close_prices(codes: list, date_str: str) -> dict:
    """获取当日收盘价"""
    if not codes:
        return {}
    batch = ",".join(codes)
    try:
        r = urllib.request.urlopen(f"http://qt.gtimg.cn/q={batch}", timeout=10)
        text = r.read().decode("gbk", errors="replace")
        result = {}
        for line in text.strip().split("\n"):
            m = re.search(r'="([^"]+)"', line)
            if not m:
                continue
            parts = m.group(1).split("~")
            if len(parts) > 5 and parts[2]:
                code_only = parts[2]
                for nc in codes:
                    if nc.replace("sz", "").replace("sh", "") == code_only:
                        try:
                            close = float(parts[3])  # 当前价/收盘价
                            result[nc] = close
                        except:
                            pass
                        break
        return result
    except Exception as e:
        print(f"[腾讯] 收盘价获取失败: {e}")
        return {}

# ─── 主分析 ────────────────────────────────────────────────────────────
def analyze(days: int = 10):
    print(f"\n{'='*60}")
    print(f"📊 竞价历史规律分析（最近{days}个交易日）")
    print(f"{'='*60}")

    history = load_history(days)
    if not history:
        print("❌ 没有历史数据")
        return

    # 1. 统计每只股出现次数
    cond1_counter = defaultdict(int)   # 竞价强势
    cond2_counter = defaultdict(int)   # 高开接力
    cond1_data = defaultdict(list)     # 详细记录

    for day in history:
        date = day.get("date", "?")
        for s in day.get("cond1", []):
            key = s["code"]
            cond1_counter[key] += 1
            cond1_data[key].append({
                "date": date,
                "name": s["name"],
                "auction_pct": s["auction_pct"],
                "auction_amt": s["auction_amt"],
                "gaokai_pct": s["gaokai_pct"],
                "open": s.get("today_open", 0),
                "prev_close": s.get("prev_close", 0),
            })
        for s in day.get("cond2", []):
            cond2_counter[s["code"]] += 1

    # 2. 找反复出现的股
    repeated_c1 = {k: v for k, v in cond1_counter.items() if v >= 2}
    repeated_c2 = {k: v for k, v in cond2_counter.items() if v >= 2}

    print(f"\n📅 分析日期范围: {history[0]['date']} ~ {history[-1]['date']}")
    print(f"   历史数据天数: {len(history)}天")
    print(f"   条件一共出现: {sum(cond1_counter.values())}次")
    print(f"   条件二共出现: {sum(cond2_counter.values())}次")

    # 3. 条件一反复竞价股
    print(f"\n{'─'*60}")
    print(f"🔥 【反复竞价强势股】（条件一出现≥2次）共{len(repeated_c1)}只")
    if repeated_c1:
        sorted_c1 = sorted(repeated_c1.items(), key=lambda x: x[1], reverse=True)
        print(f"{'股票名称':<10} {'代码':<12} {'出现次数':>6} {'最近一次竞价涨幅':>16}")
        print("-" * 50)
        for code, cnt in sorted_c1[:15]:
            records = cond1_data.get(code, [])
            latest = records[-1] if records else {}
            name = latest.get("name", code)
            latest_pct = latest.get("auction_pct", 0)
            print(f"{name:<10} {code:<12} {cnt:>6}次 {latest_pct:>+15.2f}%")
    else:
        print("  （无）")

    # 4. 条件二反复高开股
    print(f"\n{'─'*60}")
    print(f"🚀 【反复高开接力股】（条件二出现≥2次）共{len(repeated_c2)}只")
    if repeated_c2:
        sorted_c2 = sorted(repeated_c2.items(), key=lambda x: x[1], reverse=True)
        print(f"{'股票名称':<10} {'代码':<12} {'出现次数':>6}")
        print("-" * 35)
        for code, cnt in sorted_c2[:15]:
            # 找名称
            name = code
            for day in history:
                for s in day.get("cond2", []):
                    if s["code"] == code:
                        name = s["name"]
                        break
                if name != code:
                    break
            print(f"{name:<10} {code:<12} {cnt:>6}次")
    else:
        print("  （无）")

    # 5. 今日最新数据
    latest = history[-1]
    print(f"\n{'─'*60}")
    print(f"📋 今日最新（{latest['date']}）")
    print(f"   条件一: {latest['cond1_count']}只 | 条件二: {latest['cond2_count']}只")
    if latest.get("cond2"):
        print(f"\n   今日高开接力TOP5:")
        for s in latest["cond2"][:5]:
            print(f"     {s['name']}({s['code']}) 高开{s['gaokai_pct']:+.2f}% 竞价金额{s['auction_amt']/1e8:.1f}亿")

    # 6. 规律总结
    print(f"\n{'─'*60}")
    print(f"📝 规律总结")

    if repeated_c2:
        top_repeat = sorted(repeated_c2.items(), key=lambda x: x[1], reverse=True)[:5]
        names = []
        for code, cnt in top_repeat:
            for day in history:
                for s in day.get("cond2", []):
                    if s["code"] == code:
                        names.append(f"{s['name']}({cnt}次)")
                        break
                if len(names) >= 5:
                    break
        print(f"   反复高开股: {', '.join(names)}")
        print(f"   → 这些股连续出现说明资金在竞价阶段持续关注")
    else:
        print(f"   暂无反复高开股（市场轮动较快）")

    # 成交额分布
    all_amts = []
    for day in history:
        for s in day.get("cond1", []):
            all_amts.append(s["auction_amt"])
    if all_amts:
        avg = sum(all_amts) / len(all_amts)
        max_amt = max(all_amts)
        print(f"\n   竞价成交额：平均{avg/1e8:.1f}亿，最高{max_amt/1e8:.1f}亿")

    print(f"\n{'='*60}")

    # 7. 保存追踪报告
    report = {
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "period": f"{history[0]['date']}~{history[-1]['date']}",
        "days": len(history),
        "repeated_cond1": {k: v for k, v in sorted(repeated_c1.items(), key=lambda x: x[1], reverse=True)},
        "repeated_cond2": {k: v for k, v in sorted(repeated_c2.items(), key=lambda x: x[1], reverse=True)},
        "today_cond1_count": latest["cond1_count"],
        "today_cond2_count": latest["cond2_count"],
        "today_cond2": latest.get("cond2", [])[:10],
    }
    report_path = HIST_DIR / "tracker_summary.json"
    with open(report_path, "w") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"📁 追踪报告已更新: {report_path}")

    return report

if __name__ == "__main__":
    import sys
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    analyze(days)
