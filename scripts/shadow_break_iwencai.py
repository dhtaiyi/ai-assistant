#!/usr/bin/env python3
"""
倍量上影线选股器 - 问财版
每天15:05运行,通过问财API获取 倍量>2x + 上影线>3% 的股票
结合股票知识输出推荐,并保存供明天竞价后二次筛选
"""
import json, sys, subprocess
from pathlib import Path
from datetime import datetime

HIST_DIR = Path("/home/dhtaiyi/.openclaw/workspace/stock-data/shadow-break")
HIST_DIR.mkdir(parents=True, exist_ok=True)
TODAY_KEY = datetime.now().strftime("%Y%m%d")
TODAY_DISP = datetime.now().strftime("%Y-%m-%d")

MX_KEY = "mkt__bGBVbyVyWGlJi1PS8r_gJLSNmmd6-1gIDweArbPs6I"
API_URL = "https://mkapi2.dfcfs.com/finskillshub/api/claw/stock-screen"

def query_iwencai(keyword, page=1, size=20):
    """调用问财API"""
    payload = json.dumps({"keyword": keyword, "pageNo": page, "pageSize": size})
    result = subprocess.run(
        ["curl", "-s", "-X", "POST", API_URL,
         "-H", "Content-Type: application/json",
         "-H", f"apikey: {MX_KEY}",
         "-d", payload],
        capture_output=True, text=True, timeout=30
    )
    try:
        return json.loads(result.stdout)
    except:
        return {}

def parse_num(s):
    """解析带中文单位的数字"""
    if not s or s in ('-', 'NA', ''):
        return 0.0
    s = str(s).strip()
    mult = 1.0
    if '亿' in s:
        mult, s = 1e8, s.replace('亿', '')
    elif '万' in s:
        mult, s = 1e4, s.replace('万', '')
    try:
        return float(s) * mult
    except:
        return 0.0

def parse_results(api_data):
    """解析问财返回的markdown表格"""
    data = api_data.get("data", {})
    inner = data.get("data", {})
    if not inner:
        inner = data
    partial = inner.get("partialResults", "")
    all_lines = partial.strip().split("\n")

    data_lines = []
    for l in all_lines:
        if not l.startswith("|"):  continue
        if "|---" in l:  continue
        cells = [c.strip() for c in l.split("|")[1:-1]]
        if len(cells) < 4 or not cells[0].isdigit():  continue
        data_lines.append(cells)

    stocks = []
    for cells in data_lines:
        if len(cells) < 23:  continue
        market = "sz" if cells[3] == "SZ" else "sh"
        try:
            price = parse_num(cells[4])
            pct = parse_num(cells[5])
            vol_ratio = parse_num(cells[6])
            shadow = parse_num(cells[7])
            amount = parse_num(cells[18])  # 成交额(元),可能是"29.45亿"
        except:
            continue
        if price <= 0:  continue

        stocks.append({
            "name": cells[2], "code": cells[1],
            "market": market, "full_code": market + cells[1],
            "price": price, "pct_chg": pct,
            "vol_ratio": vol_ratio, "shadow": shadow,
            "amount": amount
        })

    seen = set()
    unique = []
    for s in stocks:
        if s["code"] not in seen:
            seen.add(s["code"])
            unique.append(s)
    return unique, inner.get("responseConditionList", [])

def knowledge_interpret(stocks):
    """股票知识解读"""
    print(f"\n{'='*68}")
    print(f"📚 知识解读")
    print(f"{'='*68}")

    if not stocks:
        print("  今日无符合条件的股票")
        return

    avg_vol = sum(s["vol_ratio"] for s in stocks) / len(stocks)
    avg_shadow = sum(s["shadow"] for s in stocks) / len(stocks)

    print(f"\n今日概况: {len(stocks)}只,平均倍量{avg_vol:.1f}x,平均上影线{avg_shadow:.1f}%")

    # 举重理论应用
    high_shadow = [s for s in stocks if s["shadow"] > 30]
    low_shadow = [s for s in stocks if s["shadow"] <= 15]

    if avg_shadow > 25:
        print("  解读: ⚠️ 上影线整体偏长,冲高回落多 → 跟风盘不足,谨慎追高")
    elif avg_shadow > 15:
        print("  解读: ⚖️ 正常上影,多头试探后小幅回落 → 市场正常")
    else:
        print("  解读: ✅ 上影线较短,多头力量较强 → 偏积极信号")

    if avg_vol > 3:
        print("  倍量解读: ✅ 市场局部放量明显,主力活跃")
    elif avg_vol > 2:
        print("  倍量解读: ✅ 温和放量,结构性机会")

    # 分类
    xianren = [s for s in stocks if s["shadow"] > 40]
    big_vol = [s for s in stocks if s["vol_ratio"] >= 3.0]
    low_price = [s for s in stocks if s["price"] < 20 and s["vol_ratio"] >= 2.5]

    if xianren:
        print(f"\n🌙 [仙人指路] 上影线>40%,强烈看涨信号({len(xianren)}只)")
        print("  原理: 冲高回落但收盘仍强,主力试探上方抛压后坚守")
        for s in xianren[:3]:
            print(f"  ✅ {s['name']}({s['market']}{s['code']}) 上影{s['shadow']:.0f}% 倍量{s['vol_ratio']:.1f}x 价{s['price']:.2f}")

    if big_vol:
        print(f"\n💎 [主力信号] 倍量>3x,明显主力介入({len(big_vol)}只)")
        print("  原理: 3倍以上是主力主动入场,非温和放量")
        for s in big_vol[:3]:
            print(f"  💎 {s['name']}({s['market']}{s['code']}) 倍量{s['vol_ratio']:.1f}x 成交{s['amount']/1e8:.1f}亿")

    if low_price:
        print(f"\n💰 [低价起步] 价格<20元+倍量>2.5x,安全垫厚({len(low_price)}只)")
        print("  原理: 低价股绝对跌幅有限,高倍量=资金主动吸筹")
        for s in low_price[:3]:
            print(f"  🔓 {s['name']}({s['market']}{s['code']}) 价{s['price']:.2f}元 倍量{s['vol_ratio']:.1f}x")

def main():
    keyword = "日线倍量大于2倍 上影线大于3% 非ST 非退市 沪深A股"

    print(f"\n{'='*68}")
    print(f"🔍 倍量上影线选股(问财版) {TODAY_DISP} 15:05")
    print(f"{'='*68}")
    print(f"\n⏳ 查询问财...")

    result = query_iwencai(keyword)
    if not result:
        print(f"❌ API无返回")
        return []
    top_status = result.get("status", -1)
    inner_status = result.get("data", {}).get("status", -1)
    if top_status != 0 and inner_status != 0:
        print(f"❌ API错误: top_status={top_status}, inner_status={inner_status}")
        return []

    inner_data = result.get("data", {}).get("data", result.get("data", {}))
    conditions = inner_data.get("responseConditionList", [])
    print(f"\n【条件匹配】")
    for c in conditions:
        print(f"  {c.get('describe','')}: {c.get('stockCount',0)}只")

    stocks, _ = parse_results(result)
    total = inner_data.get("securityCount", len(stocks))
    print(f"\n🎯 问财返回: {len(stocks)}只(API限制,仅显示前10)")
    print(f"   实际满足条件: 约{total}只")

    if not stocks:
        print("❌ 无符合条件的股票")
        return []

    # 知识解读
    knowledge_interpret(stocks)

    # 表格输出
    print(f"\n{'='*68}")
    print(f"📋 今日选股结果 ({TODAY_DISP})")
    print(f"{'='*68}")
    print(f"{'#':<3} {'名称':<10} {'代码':<10} {'收盘':>7} {'涨幅':>7} {'倍量':>6} {'上影线':>7} {'成交额':>10}")
    print("-" * 68)
    for i, s in enumerate(stocks, 1):
        print(f"{i:<3} {s['name']:<10} {s['market']}{s['code']:<8} "
              f"{s['price']:>7.2f} {s['pct_chg']:>+6.2f}% "
              f"{s['vol_ratio']:>5.1f}x {s['shadow']:>6.1f}% "
              f"{s['amount']/1e8:>7.1f}亿")

    # 保存
    out = {
        "date": TODAY_DISP,
        "keyword": keyword,
        "api_total": total,
        "returned_count": len(stocks),
        "conditions": [{c["describe"]: c["stockCount"]} for c in conditions],
        "stocks": [{
            "name": s["name"], "code": s["code"],
            "full_code": s["full_code"], "price": s["price"],
            "pct_chg": round(s["pct_chg"], 2),
            "vol_ratio": s["vol_ratio"], "shadow": s["shadow"],
            "amount_yuan": s["amount"]
        } for s in stocks]
    }

    out_path = HIST_DIR / f"{TODAY_KEY}_iwencai.json"
    with open(out_path, "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n💾 已保存: {out_path}")

    # 保存为明日候选池
    candidates_path = HIST_DIR / "tomorrow_candidates.json"
    candidates = {
        "date": TODAY_DISP,
        "source": "问财: 倍量>2x + 上影线>3% + 非ST非退市",
        "total_api": total,
        "count": len(stocks),
        "stocks": [{
            "code": s["full_code"],
            "name": s["name"],
            "vol_ratio": s["vol_ratio"],
            "shadow": s["shadow"],
            "price": s["price"],
            "pct_chg": round(s["pct_chg"], 2),
            "score": round(s["vol_ratio"] * 0.5 + s["shadow"] * 5, 1)
        } for s in stocks]
    }
    with open(candidates_path, "w") as f:
        json.dump(candidates, f, ensure_ascii=False, indent=2)
    print(f"💾 明日候选池: {candidates_path}")
    print(f"{'='*68}")

    return stocks

if __name__ == "__main__":
    main()
