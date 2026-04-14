#!/usr/bin/env python3
"""集合竞价分析 v1.0 - 用腾讯行情接口"""
import requests
from datetime import datetime

# 昨日涨停股池（手动填入）
STOCKS = {
    "sz000586": "汇源通信",
    "sz002491": "通鼎互联",
    "sz000919": "金陵药业",
    "sh600594": "益佰制药",
    "sh600654": "中安科",
    "sz002384": "东山精密",
    "sz002281": "光迅科技",
    "sh601869": "长飞光纤",
    "sz300548": "长芯博创",
}

def main():
    print("集合竞价 v1.0 | " + datetime.now().strftime("%Y-%m-%d %H:%M"))
    codes = ",".join(STOCKS.keys())
    r = requests.get("http://qt.gtimg.cn/q=" + codes, timeout=10)
    results = {}
    for line in r.text.strip().split("\n"):
        if "~" not in line:
            continue
        code = line.split("=")[0].replace("v_", "")
        p = line.split("~")
        if len(p) < 33:
            continue
        name = STOCKS.get(code, code)
        prev = float(p[4]) if p[4] else 0
        price = float(p[3]) if p[3] else 0
        pct = (price - prev) / prev * 100 if prev > 0 else 0
        results[name] = (code, prev, price, pct)
        print("  %s %s %.2f %+.2f%%" % (name, code, prev, pct))
    ups = sum(1 for _, _, _, p in results.values() if p > 3)
    dns = sum(1 for _, _, _, p in results.values() if p < -3)
    avgp = sum(p for _, _, _, p in results.values()) / max(len(results), 1)
    print("\n情绪: 高开%d只 低开%d只 均值%+.2f%%" % (ups, dns, avgp))

if __name__ == "__main__":
    main()
