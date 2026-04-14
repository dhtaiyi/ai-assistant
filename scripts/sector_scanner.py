#!/usr/bin/env python3
"""
板块热点分析工具 v3.0
基于股票名称关键词精确分类
使用方法：python3 sector_scanner.py
"""

import requests
from datetime import datetime

SINA_HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://finance.sina.com.cn"}

# 精确映射表（股票名 -> 板块）
STOCK_SECTOR = {
    # ===== 光纤/光通信 =====
    "光迅科技": "光纤光通信",
    "长飞光纤": "光纤光通信",
    "特发信息": "光纤光通信",
    "光智科技": "光纤光通信",
    "长江通信": "光纤光通信",
    "汇源通信": "光纤光通信",
    "通鼎互联": "光纤光通信",
    "永鼎股份": "光纤光通信",
    "剑桥科技": "光纤光通信",
    "中际旭创": "光纤光通信",
    "天孚通信": "光纤光通信",
    "新易盛": "光纤光通信",
    # ===== CPO/光连接 =====
    "东山精密": "CPO/光连接",
    "航天电器": "CPO/光连接",
    "意华股份": "CPO/光连接",
    "胜蓝股份": "CPO/光连接",
    "恒铭达": "CPO/光连接",
    "鼎通科技": "CPO/光连接",
    "立讯精密": "CPO/光连接",
    # ===== PCB/铜箔/覆铜板 =====
    "金安国纪": "PCB铜箔",
    "天通股份": "PCB铜箔",
    "沃格光电": "玻璃基板",
    "德福科技": "PCB铜箔",
    "中京电子": "PCB铜箔",
    "协和电子": "PCB铜箔",
    # ===== 算力/AI/服务器 =====
    "长芯博创": "算力AI",
    "中科曙光": "算力AI",
    "浪潮信息": "算力AI",
    "拓维信息": "算力AI",
    "光庭信息": "算力AI",
    # ===== 机器人/液冷 =====
    "飞龙股份": "机器人液冷",
    "博杰股份": "机器人液冷",
    "大为股份": "机器人液冷",
    "柯力传感": "机器人液冷",
    # ===== 储能 =====
    "圣阳股份": "储能",
    "正泰电源": "储能",
    "大元泵业": "储能",
    # ===== 创新药 =====
    "益佰制药": "创新药",
    "金陵药业": "创新药",
    "海王生物": "创新药",
    "金城医药": "创新药",
    "罗欣药业": "创新药",
    "瑞康医药": "创新药",
    # ===== 工业/制造 =====
    "巨力索具": "工业制造",
    "亚翔集成": "工业制造",
    "华宏科技": "工业制造",
    "海立股份": "工业制造",
    "新朋股份": "工业制造",
    "振江股份": "工业制造",
    "华懋科技": "汽车零部件",
    "田中精机": "工业制造",
    "法狮龙": "工业制造",
    "锴威特": "半导体",
}

# 板块关键词（兜底分类）
SECTOR_KEYWORDS = {
    "光纤光通信": ["光纤", "光通信", "光缆", "光模块", "光器件", "光弘"],
    "CPO/光连接": ["CPO", "共封装", "光连接", "连接器", "高速连接"],
    "PCB铜箔": ["铜箔", "覆铜板", "PCB", "印制电路板"],
    "机器人液冷": ["机器人", "液冷", "工业母机"],
    "储能": ["储能", "虚拟电网", "电力设备"],
    "创新药": ["创新药", "生物药", "医药", "ADC", "CXO", "制药"],
    "汽车零部件": ["汽车", "精密制造", "精密功能件"],
    "工业制造": ["集成", "装备", "重工", "机械"],
    "半导体": ["半导体", "芯片", "IC", "封测"],
}

def get_top_stocks(n=30):
    """获取成交额前N股票"""
    url = "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeDataSimple"
    params = {"page": 1, "num": n, "sort": "amount", "asc": 0, "node": "hs_a", "_s_r_a": "page"}
    try:
        r = requests.get(url, params=params, headers=SINA_HEADERS, timeout=10)
        return r.json()
    except Exception as e:
        print("Error:", e)
        return []

def guess_sector(name):
    if name in STOCK_SECTOR:
        return STOCK_SECTOR[name]
    for sector, keywords in SECTOR_KEYWORDS.items():
        for kw in keywords:
            if kw in name:
                return sector
    return "其他"

def main():
    print("\n" + "=" * 65)
    print("[FIRE] 板块热点分析 v3.0")
    print("时间: " + datetime.now().strftime("%Y-%m-%d %H:%M"))
    print("=" * 65)

    data = get_top_stocks(30)
    if not data:
        print("获取失败")
        return

    # 分类
    sector_map = {}
    for s in data:
        name = s["name"]
        pct = float(s["changepercent"])
        amt = float(s.get("amount", 0)) / 1e8
        is_zt = pct >= 9.9
        sector = guess_sector(name)
        if sector not in sector_map:
            sector_map[sector] = {"stocks": [], "total_amt": 0, "zt_amt": 0, "zt_count": 0}
        sector_map[sector]["stocks"].append({"name": name, "code": s["symbol"], "pct": pct, "amount": amt, "is_zt": is_zt})
        sector_map[sector]["total_amt"] += amt
        if is_zt:
            sector_map[sector]["zt_amt"] += amt
            sector_map[sector]["zt_count"] += 1

    # 按涨停成交额 > 涨停数量 > 总成交额 排序
    sectors = sorted(sector_map.items(),
                    key=lambda x: (x[1]["zt_amt"], x[1]["zt_count"], x[1]["total_amt"]),
                    reverse=True)

    print("\n[板块热点排行（按涨停成交额排序）]")
    for i, (sector, info) in enumerate(sectors, 1):
        stocks = sorted(info["stocks"], key=lambda x: x["amount"], reverse=True)
        zt_stocks = [s for s in stocks if s["is_zt"]]
        zt_amt = info["zt_amt"]
        zt_count = info["zt_count"]
        print("\n  %d. [%s] 涨停成交:%.1f亿 (%d只涨停)" % (i, sector, zt_amt, zt_count))
        for st in zt_stocks[:5]:
            print("     *%s(%s) %+.1f%% %.1f亿" % (
                st["name"], st["code"], st["pct"], st["amount"]))
        # 显示板块内其他大成交股
        non_zt = [s for s in stocks if not s["is_zt"]][:2]
        for st in non_zt:
            print("     %s(%s) %+.1f%% %.1f亿" % (
                st["name"], st["code"], st["pct"], st["amount"]))

    # 结论
    print("\n[结论]")
    if sectors:
        top = sectors[0]
        print("  今日最强主线: [%s]" % top[0])
        print("  成交额: %.1f亿  涨停: %d只" % (
            top[1]["total_amt"],
            len([s for s in top[1]["stocks"] if s["pct"] >= 9.9])))
        if len(sectors) >= 2:
            sec = sectors[1]
            print("  次主线: [%s] %.1f亿" % (sec[0], sec[1]["total_amt"]))
        if len(sectors) >= 3:
            thr = sectors[2]
            print("  第三: [%s] %.1f亿" % (thr[0], thr[1]["total_amt"]))
    print("\n" + "=" * 65)

if __name__ == "__main__":
    main()
