#!/usr/bin/env python3
"""
连板股追踪器 v2.0
使用方法：python3 lianban_tracker.py
"""

import requests
from datetime import datetime

SINA_HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://finance.sina.com.cn"}

# 已知连板股实时数据（收盘后更新）
BOARD_STOCKS = {
    # 代码: (名称, 昨板数, 今日涨幅, 今日涨停状态, 题材, 备注)
    "sz000586": ("汇源通信", 5, 9.98, False, "光纤涨价", "尾盘炸板，6板"),
    "sz002491": ("通鼎互联", 2, 6.18, False, "光纤+算力", "龙虎榜主力买入2.87亿，今日断板"),
    "sz000919": ("金陵药业", 3, -3.70, False, "创新药", "AACR大会催化，今日回落"),
    "sh600594": ("益佰制药", 3, 10.00, True, "创新药", "AACR大会，逻辑硬，继续涨停"),
    "sh600654": ("中安科", 4, 1.82, False, "算力", "昨日炸板，今日修复中"),
}

def get_realtime_multi(codes_str):
    """腾讯接口批量获取实时行情"""
    url = "http://qt.gtimg.cn/q=" + codes_str
    try:
        r = requests.get(url, timeout=10)
        result = {}
        for line in r.text.strip().split("\n"):
            if "=" not in line:
                continue
            code = line.split("=")[0].replace("v_", "")
            parts = line.split("~")
            if len(parts) > 37:
                result[code] = {
                    "name": parts[1],
                    "price": float(parts[3]) if parts[3] else 0,
                    "pct": float(parts[32]) if parts[32] else 0,
                    "amount": float(parts[37]) / 1e8 if parts[37] else 0,
                }
        return result
    except Exception as e:
        print("Error:", e)
        return {}

def main():
    print("\n" + "=" * 65)
    print("[BETA] 连板股追踪器 v2.0")
    print("时间: " + datetime.now().strftime("%Y-%m-%d %H:%M"))
    print("=" * 65)

    codes = ",".join(BOARD_STOCKS.keys())
    data = get_realtime_multi(codes)

    print("\n[连板股现状]")
    results = []
    for code, (name, prev_boards, prev_pct, was_zt, sector, note) in BOARD_STOCKS.items():
        d = data.get(code, {})
        price = d.get("price", 0)
        pct = d.get("pct", 0)
        amt = d.get("amount",  0)

        # 今日是否涨停
        is_zt = pct >= 9.9

        # 风险评估
        board_days = prev_boards if is_zt else prev_boards
        if board_days >= 5:
            risk = "MAX"
        elif board_days >= 4:
            risk = "HIGH"
        elif board_days >= 3:
            risk = "MED"
        else:
            risk = "LOW"

        results.append({
            "name": name, "code": code, "price": price,
            "pct": pct, "amount": amt,
            "board_days": board_days, "is_zt": is_zt,
            "sector": sector, "note": note, "risk": risk
        })

    # 按板数>成交额排序
    results.sort(key=lambda x: (x["board_days"], x["amount"]), reverse=True)

    for s in results:
        risk_icon = {"MAX": "MAX", "HIGH": "HIGH", "MED": "MED", "LOW": "LOW"}
        zt_icon = "涨停" if s["is_zt"] else ("断板" if s["pct"] < 9.5 else "未封")
        print("\n  [%s] %s(%s) %s" % (
            risk_icon[s["risk"]], s["name"], s["code"], zt_icon))
        print("     现价:%.2f 涨幅:%+.1f%%  昨板:%d->%s" % (
            s["price"], s["pct"], s["board_days"],
            "涨停" if s["is_zt"] else "断" if s["pct"] < 9.5 else "烂板"))
        print("     题材: %s" % s["sector"])
        print("     备注: %s" % s["note"])

    print("\n[明日预判]")
    for s in results:
        # 预测
        if s["is_zt"]:
            if s["board_days"] >= 5:
                pred = "高位，观察是否继续"
            else:
                pred = "强势，继续关注"
        elif s["risk"] in ("HIGH", "MAX"):
            pred = "高位断板，谨慎"
        elif s["risk"] == "MED":
            pred = "观察修复情况"
        else:
            pred = "正常，关注二波"
        print("  %s -> %s" % (s["name"], pred))

    print("\n[选股建议]")
    buy = [s["name"] for s in results if s["is_zt"] and s["board_days"] <= 3]
    watch = [s["name"] for s in results if s["risk"] in ("HIGH", "MAX")]
    if buy:
        print("  可关注: %s" % ", ".join(buy))
    if watch:
        print("  回避: %s" % ", ".join(watch))

    print("\n" + "=" * 65)

if __name__ == "__main__":
    main()
