#!/usr/bin/env python3
"""
明日预选工具 v1.1
整合今日所有数据，输出明日操作计划
使用方法：python3 tomorrow_picker.py
"""

import requests
from datetime import datetime

SINA_HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://finance.sina.com.cn"}

def get_zt_all(n=100):
    url = "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeDataSimple"
    params = {"page": 1, "num": n, "sort": "changepercent", "asc": 0, "node": "hs_a", "_s_r_a": "page"}
    r = requests.get(url, params=params, headers=SINA_HEADERS, timeout=10)
    data = r.json()
    return [s for s in data
           if float(s.get("changepercent", 0)) >= 9.9
           and not s.get("name", "").startswith("C")
           and not s.get("name", "").startswith("N")]

STOCK_SECTOR = {
    "光迅科技": "光纤光通信", "长飞光纤": "光纤光通信", "特发信息": "光纤光通信",
    "光智科技": "光纤光通信", "汇源通信": "光纤光通信", "通鼎互联": "光纤光通信",
    "长江通信": "光纤光通信", "永鼎股份": "光纤光通信", "中际旭创": "光纤光通信",
    "天孚通信": "光纤光通信", "新易盛": "光纤光通信",
    "东山精密": "CPO光连接", "航天电器": "CPO光连接", "胜蓝股份": "CPO光连接",
    "恒铭达": "CPO光连接", "立讯精密": "CPO光连接", "意华股份": "CPO光连接",
    "长芯博创": "算力AI", "浪潮信息": "算力AI",
    "金安国纪": "PCB铜箔", "天通股份": "PCB铜箔",
    "德福科技": "PCB铜箔", "沃格光电": "玻璃基板",
    "飞龙股份": "机器人液冷", "博杰股份": "机器人液冷", "大为股份": "机器人液冷",
    "益佰制药": "创新药", "金陵药业": "创新药", "海王生物": "创新药",
    "圣阳股份": "储能", "正泰电源": "储能",
    "华懋科技": "汽车零部件",
}

BOARD_STOCKS = [
    {"code": "sz000586", "name": "汇源通信", "boards": 5, "sector": "光纤涨价", "note": "6板高位，炸板风险"},
    {"code": "sz002491", "name": "通鼎互联", "boards": 2, "sector": "光纤+算力", "note": "龙虎榜主力2.87亿，断板"},
    {"code": "sz000919", "name": "金陵药业", "boards": 3, "sector": "创新药", "note": "AACR大会，断板"},
    {"code": "sh600594", "name": "益佰制药", "boards": 3, "sector": "创新药", "note": "AACR大会，逻辑硬"},
    {"code": "sh600654", "name": "中安科", "boards": 4, "sector": "算力", "note": "炸板，修复中"},
]

def main():
    print("\n" + "=" * 65)
    print("[TARGET] 明日预选工具 v1.1")
    print("分析日期: " + datetime.now().strftime("%Y-%m-%d"))
    print("=" * 65)

    zt = get_zt_all()
    print("\n[一、今日数据汇总]")
    print("  涨停: %d只（非ST非新股）" % len(zt))

    # 板块分析
    sector_map = {}
    for s in zt:
        name = s["name"]
        pct = float(s["changepercent"])
        amt = float(s.get("amount", 0)) / 1e8
        sector = STOCK_SECTOR.get(name, "其他")
        if sector not in sector_map:
            sector_map[sector] = []
        sector_map[sector].append({"name": name, "code": s["symbol"], "pct": pct, "amt": amt})

    for sec in sector_map:
        sector_map[sec].sort(key=lambda x: x["amt"], reverse=True)

    sectors = sorted(sector_map.items(), key=lambda x: sum(s["amt"] for s in x[1]), reverse=True)

    print("\n[二、主线分析（按涨停成交额排序）]")
    for i, (sector, stocks) in enumerate(sectors[:4], 1):
        total = sum(s["amt"] for s in stocks)
        print("\n  %d. [%s] 总成交%.1f亿 (%d只)" % (i, sector, total, len(stocks)))
        for st in stocks[:4]:
            print("     %s(%s) +%.1f%% %.1f亿" % (
                st["name"], st["code"][-6:], st["pct"], st["amt"]))

    # 今日首板
    today_first = [s for s in zt if s.get("symbol") in [
        "sz300489", "sz300548", "sz002384", "sh601869", "sz002636", "sz002536", "sz002342"]]
    today_first.sort(key=lambda x: float(x.get("amount", 0)), reverse=True)

    print("\n[三、今日首板（明日关注二板机会）]")
    for s in today_first[:6]:
        amt = float(s.get("amount", 0)) / 1e8
        print("  %s(%s) +%.1f%% %.1f亿" % (
            s["name"], s["symbol"][-6:], float(s["changepercent"]), amt))

    print("\n[四、风险标（明日回避）]")
    for s in BOARD_STOCKS:
        if s["boards"] >= 4:
            print("  XX %s [%s] %d板  %s" % (
                s["name"], s["sector"], s["boards"] + 1, s["note"]))

    print("\n[五、操作计划（分化期版本）]")
    print("  仓位: 30-40%")
    print("  策略: 聚焦主线首板二板，不追高位连板")
    print("  买入: 10:30前成交>5000万的率先涨停股")
    print("  止损: -7%无条件出")
    print("  禁止: 涨停数量<30家时不追连板")

    print("\n" + "=" * 65)
    print("以上仅为小小雨的分析，不构成投资建议，股市有风险！")
    print("=" * 65)

if __name__ == "__main__":
    main()
