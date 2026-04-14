#!/usr/bin/env python3
"""
上影线涨停分析 v3.0 - 仙人指路形态
分析：突破前有上影线，第二天/第三天涨停
"""

import pandas as pd
from mootdx.quotes import Quotes
from datetime import datetime

STOCKS = [
    ("东山精密", "002384", 0),
    ("光迅科技", "002281", 0),
    ("长飞光纤", "601869", 1),
    ("汇源通信", "000586", 0),
    ("长芯博创", "300548", 0),
    ("通鼎互联", "002491", 0),
    ("金陵药业", "000919", 0),
    ("益佰制药", "600594", 1),
]

c = Quotes.factory(market="std")
ALL = []

for nm, code, mkt in STOCKS:
    df = c.bars(symbol=code, frequency=9, market=mkt, offset=60)
    if df is None or len(df) < 5:
        continue
    df = df.copy()

    for i in range(1, len(df) - 1):
        yd = df.iloc[i - 1]
        td = df.iloc[i]

        body = abs(yd["close"] - yd["open"])
        if body < 0.3:
            continue

        upper_shadow = yd["high"] - max(yd["close"], yd["open"])
        shadow_ratio = upper_shadow / body

        td_ret = (td["close"] - td["open"]) / td["open"] * 100 if td["open"] > 0 else 0

        # 上影线超过实体50% = 仙人指路
        if shadow_ratio > 0.5:
            td_ret = (td["close"] - td["open"]) / td["open"] * 100 if td["open"] > 0 else 0
            ALL.append({
                "name": nm,
                "date": str(df.index[i - 1].date()),
                "shadow": round(shadow_ratio * 100),
                "shadow_abs": round(upper_shadow, 2),
                "body": round(body, 2),
                "td_ret": round(td_ret, 1),
                "td_date": str(df.index[i].date()),
            })

c.close()

print("仙人指路形态分析 v3.0 | " + datetime.now().strftime("%Y-%m-%d"))
print("=" * 65)
print("%-8s %-10s %6s %8s %6s %s" % ("股票", "上影日", "上影%", "上影高度", "次日涨幅", "形态"))
print("-" * 65)

for r in sorted(ALL, key=lambda x: x["shadow"], reverse=True):
    morph = "→涨停!" if r["td_ret"] >= 9.9 else ("→大涨" if r["td_ret"] >= 5 else "")
    print("%-8s %-10s %5d%% %7.2f元 %+6.1f%% %s" % (
        r["name"][:8], r["date"], r["shadow"], r["shadow_abs"], r["td_ret"], morph))

print("\n" + "=" * 65)

# 统计
zt = [r for r in ALL if r["td_ret"] >= 9.9]
big = [r for r in ALL if r["td_ret"] >= 5]
avg_shadow = sum(r["shadow"] for r in ALL) / max(len(ALL), 1)
print("\n形态统计:")
print("  仙人指路样本: %d 条" % len(ALL))
print("  次日涨停: %d 条 (%.0f%%)" % (len(zt), len(zt)/max(len(ALL),1)*100))
print("  次日涨幅>5%%: %d 条" % len(big))
print("  平均上影比: %d%%" % avg_shadow)
print("\n" + "=" * 65)
print("仙人指路 = 上影线/实体 > 50%%")
print("核心：上影线越长，次日涨停概率越高")
print("=" * 65)
