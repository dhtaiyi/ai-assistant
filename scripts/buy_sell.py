#!/usr/bin/env python3
import requests

STOCKS = {
    "汇源通信": {"code": "sz000586", "boards": 5, "sector": "光纤涨价", "reason": "6板高位"},
    "东山精密": {"code": "sz002384", "boards": 1, "sector": "CPO光连接", "reason": "首板122亿"},
    "光迅科技": {"code": "sz002281", "boards": 1, "sector": "光纤光通信", "reason": "首板93亿"},
    "长飞光纤": {"code": "sh601869", "boards": 1, "sector": "光纤涨价", "reason": "首板81亿"},
    "长芯博创": {"code": "sz300548", "boards": 1, "sector": "算力AI", "reason": "首板70亿"},
    "益佰制药": {"code": "sh600594", "boards": 3, "sector": "创新药", "reason": "AACR大会催化"},
    "通鼎互联": {"code": "sz002491", "boards": 2, "sector": "光纤算力", "reason": "龙虎榜主力2.87亿"},
}

def get_rt(code):
    r = requests.get(f"http://qt.gtimg.cn/q={code}", timeout=5)
    p = r.text.split("~")
    return {"price": float(p[3]), "pct": float(p[32]), "amount": float(p[37]) / 1e8} if len(p) > 37 else {}

def main():
    print("=" * 60)
    print("[点] 买卖点工具 v1.0")
    print("=" * 60)

    buy_a, buy_b, buy_c, buy_d, avoid_l = [], [], [], [], []
    today = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
    print(f"\n分析日期: {today}")

    for name, info in STOCKS.items():
        code = info["code"]
        try:
            rt = get_rt(code)
        except:
            rt = {}
        boards = info["boards"]
        price = rt.get("price", 0)
        pct = rt.get("pct", 0)
        amt = rt.get("amount", 0)
        item = {"name": name, "code": code, "price": price, "pct": pct, **info}

        if boards >= 4:
            avoid_l.append(item)
        elif boards == 3:
            if pct >= 9.9:
                buy_c.append(item)
            else:
                buy_d.append(item)
        elif boards == 2:
            if pct >= 9.9:
                buy_b.append(item)
            else:
                buy_d.append(item)
        else:
            buy_a.append(item)

    print("\n[买点A] 首板战法（今日最强")
    for s in sorted(buy_a, key=lambda x: x.get("amount", 0), reverse=True)[:5]:
        print(f"  + {s['name']}({s['code'][-6:]}) {s['sector']} {s['reason']}")

    print("\n[买点B] 弱转强（观察")
    for s in buy_b[:3]:
        print(f"  ~ {s['name']} {s['pct']:+.1f}% {s['reason']}")

    print("\n[买点C] 分歧转一致")
    for s in buy_c[:3]:
        print(f"  * {s['name']} {s['sector']}")

    print("\n[买点D] 回调低吸")
    for s in buy_d[:3]:
        print(f"  - {s['name']} {s['sector']} {s['reason']}")

    print("\n[回避]")
    for s in avoid_l[:5]:
        print(f"  X {s['name']} {s['pct']:+.1f}% {s['reason']}")

    print("\n" + "=" * 60)
    print("仅分析参考，不构成投资建议")
    print("=" * 60)

main()
# 追加止损点位分析

def stop_loss_analysis():
    """止损点位分析"""
    print("\n【止损点位参考】")
    data = {
        "东山精密": {"price": 131.90, "stop_5d": 125.31, "stop_7p": 122.67},
        "光迅科技": {"price": 108.09, "stop_5d": 102.70, "stop_7p": 100.53},
        "长飞光纤": {"price": 398.31, "stop_5d": 378.39, "stop_7p": 370.43},
    }
    for name, d in data.items():
        print(f"  {name}: 现价{d['price']} 止损{d['stop_7p']} ({d['price']*0.93:.2f})")

# Stop loss data
# 分析完成
