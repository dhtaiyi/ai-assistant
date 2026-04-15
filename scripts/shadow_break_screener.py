#!/usr/bin/env python3
"""
倍量上影线选股器 V3 (高效版)
=============================
条件：倍量(>=2x20日均量) + 上影线/实体>3% + 非ST/非退市
优化：先用严格的当日数据初筛，只对少量候选股票查K线
"""

import json, re, urllib.request
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

HIST_DIR   = Path("/home/dhtaiyi/.openclaw/workspace/stock-data/shadow-break")
HIST_DIR.mkdir(parents=True, exist_ok=True)
TODAY_KEY  = datetime.now().strftime("%Y%m%d")
TODAY_DISP = datetime.now().strftime("%Y-%m-%d")

# ─── 新浪全量今日数据 ──────────────────────────────────────────
def get_sina_all():
    stocks = []
    for page in range(1, 20):
        try:
            url = (f"http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php"
                   f"/Market_Center.getHQNodeDataSimple?page={page}&num=200"
                   f"&sort=symbol&asc=1&node=hs_a")
            r = urllib.request.urlopen(url, timeout=15)
            data = json.loads(r.read().decode("gbk", errors="replace"))
            if not data:
                break
            stocks.extend(data)
            if len(data) < 200:
                break
        except Exception as e:
            print(f"[sina] page{page} error: {e}")
            break
    return stocks

# ─── 腾讯单只K线 (20日均量) ───────────────────────────────────
def get_kline_tx(nc):
    """nc: 'sz300750' → 返回 (avg_20d_amount_wan, today_amount_wan)"""
    try:
        url = f"http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_dayhfq&param={nc},day,,,20,2024qfq"
        r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=6)
        text = r.read().decode("utf-8", errors="replace")
        m = re.search(r'=(\{.*\})', text)
        if not m:
            return (nc, 0, 0)
        obj = json.loads(m.group(1))
        # 腾讯格式: data.{code}.day = [[date,open,close,high,low,vol],...]
        all_data = obj.get("data", {}).get(nc, {}).get("day", [])
        if not all_data or len(all_data) < 21:
            return (nc, 0, 0)
        # 前20天(不算今天)
        amounts = []
        for d in all_data[-21:-1]:
            try:
                vol = float(d[5])   # vol in 手 (100 shares)
                close = float(d[2])
                if vol > 0:
                    amounts.append(vol * close / 10 / 10000)  # 手*价格/10万=万元
            except:
                continue
        if not amounts:
            return (nc, 0, 0)
        avg = sum(amounts) / len(amounts)
        # 今天
        try:
            today = all_data[-1]
            today_vol = float(today[5])
            today_close = float(today[2])
            today_amt = today_vol * today_close / 10 / 10000
        except:
            today_amt = 0
        return (nc, avg, today_amt)
    except Exception:
        return (nc, 0, 0)

# ─── 知识解读 ─────────────────────────────────────────────────
def interpret(matched):
    """结合股票课程知识，对结果进行解读"""
    results = {
        "date": TODAY_DISP,
        "count": len(matched),
        "total_scanned": 0,
        "stocks": [],
        "summary": {
            "xianren": [],   # 仙人指路: shadow/body > 50%
            "big_shadow": [], # 大上影: shadow 20-50%
            "low_price": [],  # 低价起步: <15元 + vol>2.5x
            "smart_money": [], # 主力介入: vol>3x
            "breakeven": [],  # 昨日涨停今日炸板
        }
    }

    xianren = [s for s in matched if s.get("shadow_ratio", 0) > 0.5]
    big_shadow = [s for s in matched if 0.2 < s.get("shadow_ratio", 0) <= 0.5]
    low_price = [s for s in matched if s.get("close", 999) < 15 and s.get("vol_ratio", 0) >= 2.5]
    smart_money = [s for s in matched if s.get("vol_ratio", 0) >= 3.0]

    # 低价+高量+大影线 = 重点关注
    key_stocks = sorted(matched,
        key=lambda x: (x.get("vol_ratio", 0) * 0.4 + x.get("shadow_ratio", 0) * 100 * 0.3 + (15 - min(x.get("close", 15), 15)) * 0.3),
        reverse=True
    )[:15]

    # 知识解读
    print(f"\n{'='*68}")
    print(f"📚 知识解读")
    print(f"{'='*68}")

    if matched:
        avg_vol = sum(s.get("vol_ratio", 0) for s in matched) / len(matched)
        avg_shadow = sum(s.get("shadow_ratio", 0) for s in matched) / len(matched) * 100
        print(f"\n今日概况: 符合条件的{len(matched)}只，平均倍量{avg_vol:.1f}x，平均上影{avg_shadow:.1f}%")
        print(f"   解读: ", end="")
        if avg_vol > 3:
            print("⚠️  市场整体放量，主力活跃信号")
        elif avg_vol > 2:
            print("✅  局部放量，结构性机会")
        else:
            print("⚪  缩量环境，谨慎")

        if avg_shadow > 30:
            print("   上影解读: 上影线普遍偏长，冲高回落较多 → 跟风盘不足，谨慎追高")
        elif avg_shadow > 15:
            print("   上影解读: 正常上影线，多头试探后有所回落 → 正常")
        else:
            print("   上影解读: 上影线较短，多头力量较强 → 偏积极")

    if xianren:
        print(f"\n🌙 [仙人指路] 上影/实体>50%，强烈看涨信号（{len(xianren)}只）")
        print("   原理: 冲高后回落但收盘仍强，说明主力在试探上方抛压")
        print("   历史案例: 光迅科技(+9.9%), 汇源通信(+10%), 通鼎互联(+10.1%)")
        for s in xianren[:5]:
            print(f"   ✅ {s['name']}({s['code']}) 上影{s.get('shadow_ratio',0):.0%} 涨幅{s.get('pct_chg',0):+.2f}% 倍量{s.get('vol_ratio',0):.1f}x")

    if big_shadow:
        print(f"\n📊 [大上影线] 上影/实体20-50%，中性偏多（{len(big_shadow)}只）")
        print("   原理: 有上攻意图但遭遇抛压，可能是洗盘或试探")
        for s in big_shadow[:5]:
            print(f"   ⚖️ {s['name']}({s['code']}) 上影{s.get('shadow_ratio',0):.0%} 涨幅{s.get('pct_chg',0):+.2f}% 倍量{s.get('vol_ratio',0):.1f}x")

    if low_price:
        print(f"\n💰 [低价起步] 价格<15元+倍量>2.5x，安全垫厚（{len(low_price)}只）")
        print("   原理: 低价股绝对跌幅有限，高倍量说明资金主动吸筹")
        for s in low_price[:5]:
            print(f"   🔓 {s['name']}({s['code']}) 价{s.get('close',0):.2f}元 倍量{s.get('vol_ratio',0):.1f}x")

    if smart_money:
        print(f"\n💎 [主力信号] 倍量>3x，资金明显介入（{len(smart_money)}只）")
        print("   原理: 2倍量以下是温和放量，3倍以上是主力主动入场")
        for s in smart_money[:5]:
            print(f"   💎 {s['name']}({s['code']}) 倍量{s.get('vol_ratio',0):.1f}x 上影{s.get('shadow_ratio',0):.0%}")

    # 重点关注 TOP5
    if key_stocks:
        print(f"\n🎯 [重点关注] 综合评分TOP5:")
        for i, s in enumerate(key_stocks[:5], 1):
            score = s.get("vol_ratio", 0) * 0.4 + s.get("shadow_ratio", 0) * 100 * 0.3
            score += (15 - min(s.get("close", 15), 15)) * 0.3 if s.get("close", 15) < 15 else 0
            print(f"   {i}. {s['name']}({s['code']}) 评分{score:.1f}")
            print(f"      价{s.get('close',0):.2f} 涨幅{s.get('pct_chg',0):+.2f}% 倍量{s.get('vol_ratio',0):.1f}x 上影{s.get('shadow_ratio',0):.0%} 亿{s.get('amount',0)/1e8:.1f}亿")

    return results

# ─── 主筛选 ─────────────────────────────────────────────────────
def screen():
    print(f"\n{'='*60}")
    print(f"🔍 倍量上影线选股 V3  {TODAY_DISP} 15:05")
    print(f"{'='*60}")

    # Step 1: 新浪全量今日数据
    print("\n⏳ 获取全量A股今日行情...")
    all_data = get_sina_all()
    print(f"   获取到 {len(all_data)} 只")
    results = {"total_scanned": len(all_data)}

    # Step 2: 当日数据初筛（严格条件，减少K线查询量）
    candidates = []
    for s in all_data:
        name = s.get("name", "")
        sym  = s.get("symbol", "").lower()

        # 排除ST/退市/北交所
        nl = name.upper()
        if any(x in nl for x in ["ST","*ST","N ","退","S "]):
            continue
        if sym.startswith("bj"):  # 排除北交所
            continue

        try:
            close   = float(s.get("trade", 0))
            open_p  = float(s.get("open", 0))
            high    = float(s.get("high", 0))
            prev_c  = float(s.get("settlement", 0))
            amount  = float(s.get("amount", 0))  # 万元
        except:
            continue

        if not close or close <= 0 or not prev_c or prev_c <= 0:
            continue

        # 排除涨跌停（涨停=封板没意义，跌停=流动性枯竭）
        pct_chg = (close - prev_c) / prev_c * 100
        if pct_chg >= 9.5 or pct_chg <= -9.5:
            continue

        # 排除价格异常
        if close < 2 or close > 500:
            continue

        # 上影线计算
        if close >= open_p:
            us = high - close
            body = close - open_p
        else:
            us = high - open_p
            body = open_p - close

        if body <= 0:
            continue

        shadow_ratio = us / body

        # 严格初筛: 上影线/实体 > 10% (更严格，减少K线查询量)
        if shadow_ratio <= 0.10:
            continue

        # 成交额门槛：<1000万直接排除（流动性差）
        if amount < 1000 * 10000:
            continue

        candidates.append({
            "name": name, "code": sym,
            "close": close, "open": open_p, "high": high,
            "prev_close": prev_c, "amount": amount,
            "pct_chg": pct_chg,
            "shadow_ratio": shadow_ratio,
        })

    print(f"   当日初筛(上影>10%+排除ST/涨跌停): {len(candidates)} 只")
    if not candidates:
        print("❌ 没有候选股票")
        return []

    # 预排序：优先查成交额大的（更可能是主力）
    candidates.sort(key=lambda x: x["amount"], reverse=True)
    # 最多查300只（够用了）
    candidates = candidates[:300]

    # Step 3: 并行获取K线（只查300只，大幅提速）
    print(f"\n⏳ 获取历史K线计算20日均量 ({len(candidates)}只)...")
    vol_map = {}
    done = [0]

    with ThreadPoolExecutor(max_workers=50) as ex:
        futures = {ex.submit(get_kline_tx, c["code"]): c for c in candidates}
        for fut in as_completed(futures):
            nc, avg, today_amt = fut.result()
            if nc and avg > 0:
                vol_map[nc] = (avg, today_amt)
            done[0] += 1
            if done[0] % 100 == 0:
                print(f"   进度: {done[0]}/{len(candidates)}")

    print(f"   获取到K线数据: {len(vol_map)} 只")

    # Step 4: 最终筛选（倍量>=2x）
    matched = []
    for c in candidates:
        nc = c["code"]
        if nc not in vol_map:
            continue
        avg_amt, today_kline_amt = vol_map[nc]
        if avg_amt <= 0:
            continue
        # 优先用K线的今日金额（更准确）
        today_amt = today_kline_amt if today_kline_amt > 0 else c["amount"]
        vol_ratio = today_amt / avg_amt
        if vol_ratio < 2.0:
            continue
        c["vol_ratio"] = round(vol_ratio, 2)
        c["avg_amount"] = round(avg_amt, 0)
        c["today_amount"] = round(today_amt, 0)
        matched.append(c)

    print(f"\n🎯 最终结果: {len(matched)} 只同时满足倍量>=2x + 上影/实体>10%")

    if not matched:
        print("❌ 没有符合条件的股票（可适当放宽条件重试）")
        return []

    matched.sort(key=lambda x: (x["vol_ratio"], x["shadow_ratio"]), reverse=True)

    # ── 表格输出 ───────────────────────────────────────────────
    sep = "─" * 70
    print(f"\n{sep}")
    print(f"📋 倍量上影线结果 ({TODAY_DISP})")
    print(f"{sep}")
    hdr = f"{'#':<3} {'名称':<10} {'代码':<12} {'收盘':>7} {'涨幅':>7} {'倍量':>6} {'上影':>7} {'成交':>8}"
    print(hdr)
    print(sep)
    for i, s in enumerate(matched[:30], 1):
        print(f"{i:<3} {s['name']:<10} {s['code']:<12} "
              f"{s['close']:>7.2f} {s['pct_chg']:>+6.2f}% "
              f"{s.get('vol_ratio',0):>5.1f}x {s.get('shadow_ratio',0):>7.1%} "
              f"{s.get('amount',0)/1e8:>6.1f}亿")

    # ── 知识解读 ────────────────────────────────────────────────
    results["stocks"] = matched
    results["interpret"] = interpret(matched)

    # ── 保存 ────────────────────────────────────────────────────
    out = {
        "date": TODAY_DISP,
        "count": len(matched),
        "total_scanned": len(all_data),
        "stocks": [{
            "name": s["name"], "code": s["code"],
            "close": s["close"], "pct_chg": round(s["pct_chg"], 2),
            "vol_ratio": s.get("vol_ratio", 0),
            "shadow_ratio": round(s.get("shadow_ratio", 0), 4),
            "amount_2": round(s.get("amount", 0) / 1e8, 2),
        } for s in matched]
    }
    out_path = HIST_DIR / f"{TODAY_KEY}.json"
    with open(out_path, "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n💾 已保存: {out_path}")
    print(f"{'='*60}")
    return matched

if __name__ == "__main__":
    screen()
