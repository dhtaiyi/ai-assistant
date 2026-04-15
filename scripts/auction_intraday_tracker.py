#!/usr/bin/env python3
"""
竞价股盘中跟踪器
每天9:25竞价结果保存后，在盘中(10:00/11:30/14:30)自动跟踪
"""

import json, os, re, sys, urllib.request
from pathlib import Path
from datetime import datetime

HIST_DIR  = Path("/home/dhtaiyi/.openclaw/workspace/stock-data/auction")
TODAY_KEY = datetime.now().strftime("%Y%m%d")

# 批量获取实时行情
def batch_quote(codes):
    if not codes:
        return {}
    unique = list(dict.fromkeys(codes))
    batch = ",".join(unique)
    try:
        r = urllib.request.urlopen(f"http://qt.gtimg.cn/q={batch}", timeout=10)
        text = r.read().decode("gbk", errors="replace")
        result = {}
        for line in text.strip().split("\n"):
            m = re.search(r'="([^"]+)"', line)
            if not m:
                continue
            parts = m.group(1).split("~")
            if len(parts) < 6 or not parts[2]:
                continue
            code_only = parts[2]
            for nc in unique:
                if nc.replace("sz","").replace("sh","") == code_only:
                    try:
                        result[nc] = {
                            "name":       parts[1],
                            "price":      float(parts[3]),
                            "prev_close": float(parts[4]),
                            "open":       float(parts[5]),
                            "high":       float(parts[33]) if parts[33] else 0,
                            "low":        float(parts[34]) if parts[34] else 0,
                        }
                    except:
                        pass
                    break
        return result
    except Exception as e:
        print(f"[腾讯] 行情获取失败: {e}")
        return {}

def load_today():
    path = HIST_DIR / f"{TODAY_KEY}.json"
    if not path.exists():
        print(f"no data: {path}")
        return {}
    with open(path) as f:
        return json.load(f)

def track():
    today_disp = datetime.now().strftime("%Y-%m-%d")
    now_hm = datetime.now().strftime("%H:%M")
    sep = "=" * 60
    print(f"\n{sep}")
    print(f"竞价股盘中跟踪 {today_disp} {now_hm}")
    print(sep)

    today = load_today()
    if not today:
        return

    cond1 = today.get("cond1", [])
    cond2 = today.get("cond2", [])
    all_codes = [s["code"] for s in cond1 + cond2 if s.get("code")]

    if not all_codes:
        print("no codes")
        return

    print(f"  竞价强势(条件一): {len(cond1)}只")
    print(f"  高开接力(条件二): {len(cond2)}只")

    quotes = batch_quote(all_codes)
    if not quotes:
        print("quote failed")
        return

    # 分析条件二
    gk_list = []
    for s in cond2:
        nc = s["code"]
        q = quotes.get(nc)
        if not q or q["price"] <= 0:
            continue
        open_p  = q["open"]
        cur_p   = q["price"]
        prev_c  = s.get("prev_close", q["prev_close"])
        high_p  = q["high"]

        cur_pct    = (cur_p - prev_c) / prev_c * 100 if prev_c > 0 else 0
        open2cur   = (cur_p - open_p) / open_p * 100 if open_p > 0 else 0

        # 涨停价判断
        limit_price = round(prev_c * 1.10, 2) if prev_c else 0
        is_limit = (limit_price > 0 and abs(cur_p - limit_price) < 0.02 and cur_pct > 9)
        touched   = (limit_price > 0 and high_p >= limit_price)
        zhaban    = touched and not is_limit and cur_pct > 7

        if is_limit:
            status = "[封板]"
        elif zhaban:
            status = "[炸板]"
        elif cur_pct > 5:
            status = "[强势]"
        elif open2cur > 0:
            status = "[续涨]"
        elif open2cur < -3:
            status = "[回落]"
        else:
            status = "[震荡]"

        pullback_pct_val = (high_p - cur_p) / high_p * 100 if high_p > 0 else 0

        gk_list.append({
            "name": s["name"], "code": nc,
            "prev_close": prev_c, "open": open_p, "current": cur_p,
            "high": high_p,
            "cur_pct": cur_pct, "open2cur": open2cur,
            "auction_amt": s.get("auction_amt", 0),
            "gaokai_pct": s.get("gaokai_pct", 0),
            "status": status,
            "is_limit": is_limit, "zhaban": zhaban,
            "pullback_pct": pullback_pct_val,
        })

    gk_list.sort(key=lambda x: (x["is_limit"], x["zhaban"], x["cur_pct"]), reverse=True)

    print(f"\n--- 条件二高开接力股 ({now_hm}) ---")
    print(f"{'名称':<10} {'代码':<12} {'昨收':>7} {'开盘':>7} {'当前':>7} {'涨幅':>7} {'开盘->当前':>10} {'状态'}")
    print("-" * 72)
    for s in gk_list:
        print(f"{s['name']:<10} {s['code']:<12} {s['prev_close']:>7.2f} {s['open']:>7.2f} {s['current']:>7.2f} {s['cur_pct']:>+6.2f}% {s['open2cur']:>+9.2f}% {s['status']}")

    # 条件一
    c1_list = []
    for s in cond1[:30]:
        nc = s["code"]
        q = quotes.get(nc)
        if not q or q["price"] <= 0:
            continue
        prev_c  = s.get("prev_close", q["prev_close"])
        open_p  = q["open"]
        cur_p   = q["price"]
        cur_pct = (cur_p - prev_c) / prev_c * 100 if prev_c > 0 else 0
        c1_list.append({
            "name": s["name"], "code": nc,
            "prev_close": prev_c, "open": open_p, "current": cur_p,
            "cur_pct": cur_pct,
            "auction_amt": s.get("auction_amt", 0),
        })

    c1_list.sort(key=lambda x: x["cur_pct"], reverse=True)
    print(f"\n--- 条件一竞价强势股TOP20 ---")
    print(f"{'名称':<10} {'代码':<12} {'昨收':>7} {'当前涨幅':>8} {'竞价金额':>10}")
    print("-" * 50)
    for s in c1_list[:20]:
        print(f"{s['name']:<10} {s['code']:<12} {s['prev_close']:>7.2f} {s['cur_pct']:>+7.2f}% {s['auction_amt']/1e8:>8.1f}亿")

    # 判断是否收盘后（>15:00）
    now_h = int(now_hm.split(":")[0])
    is_close = now_h >= 15

    # 盘中/收盘总结
    limit_names  = [s["name"] for s in gk_list if s["is_limit"]]
    zhaban_names = [s["name"] for s in gk_list if s["zhaban"]]
    strong_names = [s["name"] for s in gk_list if not s["is_limit"] and not s["zhaban"] and s["cur_pct"] > 5]
    weak_names   = [s["name"] for s in gk_list if s["open2cur"] < -3]

    if is_close:
        # ── 收盘复盘报告 ──
        gk_winners = [s for s in gk_list if s["cur_pct"] > 0]
        gk_losers  = [s for s in gk_list if s["cur_pct"] <= 0]
        limit_win   = [s for s in gk_list if s["is_limit"]]
        zhaban_win  = [s for s in gk_list if s["zhaban"]]

        print(f"\n{'='*60}")
        print(f"📊 【收盘复盘报告】高开接力股全天表现")
        print(f"{'='*60}")

        print(f"\n  📈 胜率: {len(gk_winners)}/{len(gk_list)} "
              f"({len(gk_winners)*100//len(gk_list)}%)")
        print(f"  🔴 封板: {len(limit_win)}只 | "
              f"⚠️ 炸板: {len(zhaban_win)}只 | "
              f"💀 收阴: {len(gk_losers)}只")

        print(f"\n  【封板股】（高开→封住涨停）")
        for s in limit_win:
            print(f"    ✅ {s['name']} 竞价{s.get('gaokai_pct',0):+.1f}%→收{s['cur_pct']:+.1f}% 封板")

        print(f"\n  【炸板股】（曾摸板未封住）")
        for s in zhaban_win:
            print(f"    ⚠️ {s['name']} 开{s['open']}({s.get('gaokai_pct',0):+.1f}%) "
                  f"高{s['high']} 收{s['cur_pct']:+.1f}% 回落{s.get('pullback_pct',0):.1f}%")

        print(f"\n  【收阴股】（收盘涨幅≤0）")
        for s in gk_losers:
            print(f"    ❌ {s['name']} 开{s['open']}({s.get('gaokai_pct',0):+.1f}%) "
                  f"收{s['cur_pct']:+.1f}%")

        print(f"\n  【强势股】（收涨>5%未涨停）")
        for s in strong_names:
            sv = next((x for x in gk_list if x["name"] == s), None)
            if sv:
                print(f"    🚀 {s} 竞价{sv.get('gaokai_pct',0):+.1f}%→收{sv['cur_pct']:+.1f}%")

        # 竞价金额 vs 收盘表现相关性
        print(f"\n  【大单追踪】（竞价金额>1亿）")
        big = [s for s in gk_list if s.get("auction_amt", 0) >= 1e8]
        for s in big:
            print(f"    💰 {s['name']} 竞价{s['auction_amt']/1e8:.1f}亿 → "
                  f"高开{s.get('gaokai_pct',0):+.1f}% 收{s['cur_pct']:+.1f}% {s['status']}")

        print(f"\n{'='*60}")
    else:
        print(f"\n--- {now_hm} 盘中总结 ---")
        if limit_names: print(f"  封板: {', '.join(limit_names)}")
        if zhaban_names: print(f"  炸板: {', '.join(zhaban_names)}")
        if strong_names: print(f"  强势: {', '.join(strong_names[:5])}")
        if weak_names:   print(f"  回落: {', '.join(weak_names[:5])}")

    # 保存快照
    snap = {
        "time": now_hm,
        "gk": [{"name": s["name"], "code": s["code"], "cur_pct": s["cur_pct"],
                "status": s["status"]} for s in gk_list],
    }
    snap_path = HIST_DIR / f"{TODAY_KEY}_snapshots.json"
    all_snaps = []
    if snap_path.exists():
        with open(snap_path) as f:
            all_snaps = json.load(f)
    all_snaps.append(snap)
    with open(snap_path, "w") as f:
        json.dump(all_snaps, f, ensure_ascii=False, indent=2)
    print(f"\n  快照已保存: {snap_path}")
    print(sep)

if __name__ == "__main__":
    track()
