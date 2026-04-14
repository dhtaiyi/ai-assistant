#!/usr/bin/env python3
"""
股票策略 v3.0 - 综合实战迭代

整合知识体系：
1. 养家心法：只做最强，板块龙头涨幅最大/涨停最快
2. 买点体系：
   - 买点A（首板战法）：昨日涨停，今日高开3-7%竞价超预期
   - 买点B（一进二接力）：首板后第二天，分歧转一致打板
   - 买点C（连板持筹/首阴反包）：连板进行中 or 首阴不破5日线
   - 买点D（空间板低吸）：龙回头，5日线附近低吸
3. 卖点体系：涨停封不住→卖 / 板块退潮→卖 / 跌破5日线→卖 / 止损-7%
4. 威科夫信号：Spring=假跌破=买入, UT=假突破=卖出
5. 举重理论：扩散=危险，收敛=安全
6. 小市值：30-200亿
7. 连板高度：≤3板（超3板断板概率大）
8. 【v3.1修正】4板小市值(≤80亿)+主线加成≥15 → 可以参与，但严格止损
   原因：2026-04-11验证华远控股4板+62亿小市值继续涨停
"""

import requests
from datetime import datetime

CIRC_MV_MIN = 30
CIRC_MV_MAX = 200
LIANBAN_MAX = 3
LIANBAN_SMALL_CAP = 80   # v3.1: 小市值4板的上限(亿)
STOP_LOSS = -7

SECTOR_BONUS = {
    "算力": 20, "光纤": 20, "光模块": 20, "AI": 15,
    "数据中心": 15, "云计算": 10, "机器人": 10,
    "并购": 20, "股权转让": 15, "重组": 15,
    "新能源": 5, "医药": 5, "军工": 10,
}

BUY_POINT = {
    "A": "✅买点A-首板战法（昨日涨停，今日高开3-7%超预期）",
    "B": "✅买点B-一进二接力（最强模式！首板后第二天分歧转一致）",
    "C": "🔒买点C-连板持筹（进行中，首阴不破5日线则持有）",
    "D": "🐉买点D-空间板低吸（龙回头，5日线附近低吸博反弹）",
    "S": "🟡威科夫Spring（假跌破，看涨信号）",
    "N": "⚠️普通关注/不参与",
}

# (代码, 今日收盘, 今日涨幅%, 连板天数, 概念板块, 备注)
TODAY_DATA = {
    "东山精密": ("sz002384", 143.55, 8.8, 3, "算力+消费电子", "✅3连板加速+8.8%，明日4板预期"),
    "华远控股": ("sh600743", 2.91, 10.0, 4, "并购重组", "✅4连板涨停，但4板高位风险大⚠️"),
    "来伊份": ("sh603777", 16.97, 10.0, 3, "股权转让", "✅3连板+10%，小市值57亿，明日4板"),
    "睿能科技": ("sh603933", 24.53, 10.0, 2, "科技+复牌", "✅2连板+10%，小市值51亿，一进二"),
    "长源东谷": ("sh601969", 11.06, 0.9, 3, "汽车零部件", "⚠️3连板但缩量，谨慎"),
    "汇源通信": ("sz000586", 22.61, -10.0, 6, "光纤", "❌6板断板跌停，高位扩散=危险"),
    "通鼎互联": ("sz002491", 14.59, -9.6, 2, "光纤", "❌断板跌停，成交回报过大"),
    "益佰制药": ("sh600594", 4.81, -4.9, 4, "医药", "❌4板断板，成交缩量"),
    "长飞光纤": ("sh601869", 384.38, -3.5, 1, "光纤", "❌首板后大跌，市值3182亿太大"),
    "长芯博创": ("sz300548", 223.80, -3.5, 1, "算力", "❌首板后跌停，市值653亿偏大"),
    "光迅科技": ("sz002281", 107.82, -0.2, 1, "光模块+AI", "⚠️首板后横盘，成交不足"),
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
            }
        except: pass
    return result

def judge_buy_point(pct, lianban, note, sector=""):
    """判断买点类型（v3.1修正版）"""
    # v3.1: 4板小市值(≤80亿)+主线加成≥15 可以参与
    # 判断是否属于主线
    is_main_sector = any(kw in sector for kw in ["算力", "光纤", "AI", "并购", "重组", "股权转让"])
    
    # 1. 连板≥4板大盘 → 高风险
    if lianban >= 4:
        if is_main_sector:
            return "B", "⚠️4板小市值+主线，可参与严格止损"
        else:
            return "N", "❌4板+高位，不参与"
    
    # 2. 今日涨停
    if pct >= 9.9 and lianban >= 1:
        if lianban == 1:
            return "A", "✅首板涨停"
        elif lianban == 2:
            return "B", "✅一进二涨停（最强模式）"
        elif lianban == 3:
            return "B", "✅二进三涨停（略高⚠️）"
    
    # 3. 连板进行中（涨但未涨停）→ 买点C持筹
    if lianban >= 1 and pct > 0 and pct < 9.9:
        return "C", f"🔒{lianban}板持筹中({pct:.1f}%)"
    
    # 4. 断板大跌
    if pct <= -10:
        return "D", "❌跌停不抄底"
    elif -10 < pct <= -5:
        return "S", f"🟡威科夫Spring?({pct:.1f}%)"
    
    # 5. 小涨小跌
    if -5 <= pct <= 0:
        return "N", f"调整中({pct:.1f}%)"
    
    return "N", "普通"

def strategy_score(bp, pct, circ, sector, lianban, note):
    """综合评分"""
    bp_s = {"A": 40, "B": 35, "C": 30, "D": 20, "S": 25, "N": 10}.get(bp, 10)
    
    if circ < CIRC_MV_MIN:
        mv_s = 15
    elif circ <= 80:
        mv_s = 30
    elif circ <= 150:
        mv_s = 25
    elif circ <= CIRC_MV_MAX:
        mv_s = 20
    else:
        mv_s = 0
    
    sec_s = 0
    for kw, bonus in SECTOR_BONUS.items():
        if kw in sector:
            sec_s = bonus
            break
    
    if lianban == 2:
        lb_s = 10
    elif lianban == 1:
        lb_s = 8
    elif lianban == 3:
        lb_s = 5
    elif lianban >= 4:
        # v3.1: 4板小市值+主线可以参与
        is_main = any(kw in sector for kw in ["算力", "光纤", "AI", "并购", "股权转让", "重组"])
        if circ <= LIANBAN_SMALL_CAP and is_main:
            lb_s = 8  # 4板小市值+主线，给8分
        else:
            lb_s = 0  # 4板大盘不做
    else:
        lb_s = 0
    
    base = bp_s + mv_s + sec_s + lb_s
    
    if "❌" in note:
        base *= 0.15
    elif "⚠️" in note:
        base *= 0.5
    
    return round(base, 1), bp_s, mv_s, sec_s, lb_s

def main():
    now = datetime.now()
    print(f"📊 股票策略 v3.0 | {now.strftime('%Y-%m-%d %H:%M')} 收盘版")
    print("=" * 78)
    print("整合：养家心法 + 退学炒股 + 威科夫 + 举重理论 + 小市值筛选")
    
    codes = [v[0] for v in TODAY_DATA.values()]
    data = get_realtime(codes)
    
    print(f"\n{'股票':<10} {'收盘':>7} {'涨幅':>8} {'连板':>4} {'买点判断':>24} {'评分'}")
    print("-" * 78)
    
    results = []
    for name, (code, close, pct, lianban, sector, note) in TODAY_DATA.items():
        info = data.get(code, {})
        price = info.get("price", close) or close
        pct_r = info.get("pct", pct) or pct
        circ = info.get("circ_mv", 0) or 0
        
        bp, bp_text = judge_buy_point(pct_r, lianban, note)
        total, bp_s, mv_s, sec_s, lb_s = strategy_score(bp, pct_r, circ, sector, lianban, note)
        
        lb_str = f"{lianban}板" if lianban > 0 else "-"
        circ_str = f"{circ:.0f}亿" if circ > 0 else "-"
        tag = "✅" if total >= 60 else "⚠️" if total >= 35 else "❌"
        
        print(f"{name:<10} {price:>6.2f} {pct_r:>+7.1f}% {lb_str:>5} {bp_text:>24} {total:>5}{tag}")
        
        results.append({
            "name": name, "code": code, "price": price, "pct": pct_r,
            "lianban": lianban, "circ": circ, "sector": sector,
            "note": note, "bp": bp, "bp_text": bp_text, "total": total,
        })
    
    print()
    print("=" * 78)
    print("🎯 明日策略建议（按买点类型）")
    print("-" * 78)
    
    by_bp = {"A": [], "B": [], "C": [], "D": [], "S": [], "N": []}
    for r in results:
        by_bp[r["bp"]].append(r)
    
    for bp_type in ["A", "B", "C", "D", "S"]:
        items = [x for x in by_bp[bp_type] if x["total"] >= 15]
        if not items:
            continue
        items.sort(key=lambda x: x["total"], reverse=True)
        print(f"\n{BUY_POINT[bp_type]}")
        for r in items:
            stop = round(r["price"] * 0.93, 2)
            risk = "⚠️高位" if r["lianban"] >= 3 else ""
            print(f"  {r['name']}({r['code'][-6:]}) 评分:{r['total']} "
                  f"| 市值:{r['circ']:.0f}亿 | 止损:{stop}元 | {r['sector']} {risk}")
    
    print()
    print("=" * 78)
    print("📋 核心口诀（养家心法+退学炒股）")
    print("-" * 78)
    print("""
  🎯 选股：人气 > 强度 > 题材纯度 > 盘子大小
  💰 买点：竞价超预期（高开3-7%）/ 分歧转一致打板 / 首阴反包
  🛡️ 卖点：涨停封不住 / 板块退潮 / 跌破5日线 / 止损-7%
  ⚠️ 不做：连板≥4板加速段（断板风险大！）
  🚫 不抄底：跌停断板股（举重理论：扩散=危险！）
  🟡 Spring：威科夫假跌破，快速拉回 = 买入机会
    """)
    print("⚠️ 投资有风险，仅供参考～", now.strftime("%H:%M"))

if __name__ == "__main__":
    main()
