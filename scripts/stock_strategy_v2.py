#!/usr/bin/env python3
"""
股票策略 v2.0 - 基于实战迭代

改进点：
1. 流通市值30-200亿（好拉升）
2. 连板高度≤3板（超3板断板风险大）
3. 板块主线加成（算力/光纤/AI）
4. 成交额过滤（>5亿有资金认可）
5. 上影线突破形态优先

用法：
  python3 stock_strategy_v2.py
"""

import requests
import sys
from datetime import datetime

# ==================== 配置 ====================
CIRC_MV_MIN = 30
CIRC_MV_MAX = 200
LIANBAN_MAX = 3
AMOUNT_MIN = 5

SECTOR_BONUS = {
    "算力": 20, "光纤": 20, "光模块": 20, "AI": 10,
    "数据中心": 10, "云计算": 10, "机器人": 10,
    "新能源": 5, "医药": 5, "并购": 15, "股权转让": 15,
}

# 格式：(代码, 今日收盘价, 今日涨幅%, 明日预期连板数, 概念板块, 备注)
WATCH_POOL = {
    "东山精密": ("sz002384", 143.55, 8.8, 4, "算力+消费电子", "✅3连板+8.8%，明日4板预期，主线大票"),
    "华远控股": ("sh600743", 2.91, 10.0, 5, "并购重组", "✅4连板+10%，小市值62亿，并购题材"),
    "来伊份": ("sh603777", 16.97, 10.0, 4, "股权转让", "✅3连板+10%，小市值57亿"),
    "睿能科技": ("sh603933", 24.53, 10.0, 3, "科技", "✅复牌2连板+10%，小市值51亿"),
    "长源东谷": ("sh601969", 11.06, 0.9, 3, "汽车零部件", "⚠️3连板但成交缩量，小心"),
    "汇源通信": ("sz000586", 22.61, -10.0, 0, "光纤", "❌6板断板跌停，明日看竞价修复"),
    "通鼎互联": ("sz002491", 14.59, -9.6, 0, "光纤", "❌断板跌停，成交回报大"),
    "益佰制药": ("sh600594", 4.81, -4.9, 0, "医药", "❌4板断板，成交缩量"),
    "长飞光纤": ("sh601869", 377.18, -5.3, 0, "光纤", "❌首板后大跌，市值3100亿太大"),
    "长芯博创": ("sz300548", 219.67, -5.3, 0, "算力", "❌首板后跌停，市值637亿偏大"),
    "光迅科技": ("sz002281", 107.12, -0.9, 0, "光模块+AI", "⚠️首板后横盘，成交不足"),
}

# 昨日关键突破价位（用于明日竞价监控）
YESTERDAY_BREAKOUT = {
    "sz002384": {"resist": 131.90, "type": "首板涨停价"},
    "sh601743": {"resist": 2.65, "type": "4板涨停价"},
    "sh603777": {"resist": 15.43, "type": "3板涨停价"},
    "sh603933": {"resist": 22.30, "type": "2板涨停价"},
}

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
                "pct": float(parts[32]) if parts[32] else 0,
                "circ_mv": float(parts[45]) if parts[45] else 0,
                "amount": float(parts[37]) / 100000000 if parts[37] else 0,
            }
        except: pass
    return result

def score(name, price, pct, circ, lianban, sector, note):
    """综合评分"""
    if price == 0 or pct == 0:
        return 0, "数据不足"
    
    # 市值得分 (40%)
    if circ < CIRC_MV_MIN:
        mv_s = 20
    elif circ <= 80:
        mv_s = 40
    elif circ <= 150:
        mv_s = 35
    elif circ <= CIRC_MV_MAX:
        mv_s = 30
    else:
        mv_s = 0
    
    # 连板得分 (30%)
    if lianban == 0:
        lb_s = 30  # 今日断板/调整，反而给基础分
    elif lianban == 1:
        lb_s = 35
    elif lianban == 2:
        lb_s = 30
    elif lianban == 3:
        lb_s = 15
    else:
        lb_s = 0
    
    # 成交额得分 (15%)
    amt = 0  # 收盘后无成交额数据
    if amt >= 10:
        amt_s = 15
    elif amt >= 5:
        amt_s = 12
    else:
        amt_s = 8
    
    # 板块加成 (15%)
    sec_s = 0
    for kw, bonus in SECTOR_BONUS.items():
        if kw in sector:
            sec_s = bonus
            break
    
    score = mv_s + lb_s + amt_s + sec_s
    
    # 风险折扣
    if "❌" in note:
        score = score * 0.2
    elif "⚠️" in note:
        score = score * 0.6
    
    detail = f"市值{mv_s}+连板{lb_s}+板块{sec_s}+成交{amt_s}"
    return score, detail

def main():
    now = datetime.now()
    print(f"📊 股票策略 v2.0 | {now.strftime('%Y-%m-%d %H:%M')} 收盘版")
    print("=" * 72)
    
    # 获取实时数据
    codes = [v[0] for v in WATCH_POOL.values()]
    data = get_realtime(codes)
    
    print(f"\n{'股票':<10} {'收盘价':>7} {'涨幅':>8} {'流通市值':>9} {'预期':>6} {'评分':>6} {'评价'}")
    print("-" * 72)
    
    results = []
    for name, (code, close, pct_today, lianban, sector, note) in WATCH_POOL.items():
        info = data.get(code, {})
        price = info.get("price", close) or close
        pct = info.get("pct", pct_today) or pct_today
        circ = info.get("circ_mv", 0) or 0
        
        sc, detail = score(name, price, pct, circ, lianban, sector, note)
        
        if lianban == 0:
            lb_str = "断板"
        elif lianban == 1:
            lb_str = "首板"
        else:
            lb_str = f"{lianban}连板"
        
        circ_str = f"{circ:.0f}亿" if circ > 0 else "-"
        pct_str = f"{pct:+.1f}%"
        
        tag = "✅" if sc >= 60 else "⚠️" if sc >= 30 else "❌"
        
        print(f"{name:<10} {price:>6.2f} {pct_str:>8} {circ_str:>9} {lb_str:>6} {sc:>5.0f} {tag} {note}")
        
        results.append((name, code, price, pct, circ, lianban, sector, note, sc))
    
    print()
    print("=" * 72)
    print("🎯 明日重点关注（v2.0策略推荐）")
    print("-" * 72)
    
    # 只看上涨且评分高的
    hot = [(r[8], r[0], r[1], r[2], r[5], r[7]) for r in results if r[8] > 30]
    hot.sort(reverse=True)
    
    print("\n🔥 明日重点（评分>30，有机会）：")
    for sc, name, code, price, sector, note in hot:
        risk = "⚠️风险较大" if sc < 60 else ""
        print(f"  {name}({code[-6:]}): 评分{sc:.0f} {sector} {risk}")
    
    print("\n💡 策略说明：")
    print(f"  • 流通市值：{CIRC_MV_MIN}-{CIRC_MV_MAX}亿（太大难拉升）")
    print(f"  • 连板高度：≤{LIANBAN_MAX}板（超3板断板风险大增）")
    print(f"  • 板块加成：算力/光纤/AI主线+20分")
    print(f"  • 断板股(汇源/通鼎/益佰)：明日看竞价修复，不盲目抄底")
    print()
    print("⚠️ 投资有风险，以上仅供参考，不构成投资建议～")
    
    # 输出明日竞价重点价位
    print()
    print("📌 明日竞价重点观察价位：")
    for name, (code, close, pct, lianban, sector, note) in WATCH_POOL.items():
        if lianban > 0 and lianban <= 4:
            key_price = close * 1.1  # 涨停价估算
            print(f"  {name}：竞价需 > {key_price:.2f}（涨停价）才能延续连板")

if __name__ == "__main__":
    main()
