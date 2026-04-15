#!/usr/bin/env python3
"""分时结构分析器 v1.0

识别分时图形态：
- 高开高走（最强）/ 低开高走（强势）
- 高开低走（弱势）/ 低开低走（最弱）
- 横盘震荡（整理）
- V形反转 / A形反转
- 尾盘偷袭 / 竞价抢筹

基于：
- 开盘价 vs 昨日收盘价（高开/低开幅度）
- 盘中价格形态（均线排列、高点低点演进）
- 尾盘30分钟走势

用法：
  python3 market_structure.py --code 000586
  python3 market_structure.py --codes 000586,002491,600594
"""

import json
import os
import re
import sys
import requests
import time
from datetime import datetime, time as dtime
from pathlib import Path
from collections import defaultdict

# ─── 配置 ────────────────────────────────────────────────────────────────────
HIST_DIR = Path("/home/dhtaiyi/.openclaw/workspace/stock-data/minute")
os.makedirs(HIST_DIR, exist_ok=True)

# 指数代码
INDEX_CODES = {
    "sh000001": "上证指数",
    "sz399001": "深证成指",
    "sz399006": "创业板指",
}

# ─── 数据获取 ────────────────────────────────────────────────────────────────
def get_minute_data(code: str) -> list[dict]:
    """
    获取分时数据（用 mootdx 协议）
    返回: [{"time": "09:30", "price": 10.5, "pct": 0.5}, ...]
    """
    try:
        import mootdx
        from mootdx.tools import get_realtime

        # 使用 mootdx 批量获取
        client = mootdx.Quote()
        df = client.minute(code=code)

        if df is None or df.empty:
            return _get_minute_fallback(code)

        # 解析分时 DataFrame
        result = []
        for _, row in df.iterrows():
            t = str(row.get("time", row.get("datetime", "")))
            p = float(row.get("close", row.get("price", 0)))
            if p == 0:
                continue
            # time 格式化为 HH:MM
            if " " in t:
                t = t.split(" ")[1]
            t = t[:5]
            result.append({"time": t, "price": p})

        client.disconnect()
        return result
    except Exception as e:
        return _get_minute_fallback(code)

def _get_minute_fallback(code: str) -> list[dict]:
    """降级：使用腾讯分时接口"""
    if not code.startswith("sz") and not code.startswith("sh"):
        code = ("sz" + code) if code[0] in "03" else ("sh" + code)
    try:
        r = requests.get(f"http://web.ifzq.gtimg.cn/appstock/app/minute/query?param={code}", timeout=8)
        data = r.json()
        mdata = data.get("data", {}).get(code, {}).get("data", [])
        result = []
        for item in mdata:
            if isinstance(item, list) and len(item) >= 2:
                result.append({"time": item[0], "price": float(item[1])})
        return result
    except Exception:
        return []

def get_realtime_snapshot(codes: list[str]) -> dict:
    """获取实时快照（开盘价/当前价/最高/最低）"""
    if not codes:
        return {}
    full = []
    for c in codes:
        c = c.strip()
        if not c.startswith("sz") and not c.startswith("sh"):
            c = ("sz" + c) if c[0] in "03" else ("sh" + c)
        full.append(c)
    try:
        r = requests.get(f"http://qt.gtimg.cn/q={','.join(full)}", timeout=8)
        r.encoding = "gbk"
    except Exception:
        return {}

    result = {}
    for line in r.text.strip().split("\n"):
        if '"' not in line:
            continue
        m = re.search(r'v_(\w+)=.*?"([^"]+)"', line)
        if not m:
            continue
        code = m.group(1)
        parts = m.group(2).split("~")
        if len(parts) < 35:
            continue
        try:
            result[code] = {
                "name":   parts[1],
                "price":  float(parts[3])  if parts[3]  else 0,
                "prev":   float(parts[4])  if parts[4]  else 0,
                "open":   float(parts[5])  if parts[5]  else 0,
                "high":   float(parts[33]) if parts[33] else 0,
                "low":    float(parts[34]) if parts[34] else 0,
                "pct":    (float(parts[3]) - float(parts[4])) / float(parts[4]) * 100
                           if parts[3] and parts[4] and float(parts[4]) > 0 else 0,
            }
        except Exception:
            continue
    return result

# ─── 分时结构分析 ────────────────────────────────────────────────────────────
class MarketStructure:
    """分时图结构分析"""

    @staticmethod
    def get_open_type(open_pct: float) -> str:
        """根据开盘涨幅判断高开/低开"""
        if open_pct >= 3:
            return "大幅高开"
        elif open_pct >= 1:
            return "高开"
        elif open_pct >= -1:
            return "平开"
        elif open_pct >= -3:
            return "低开"
        else:
            return "大幅低开"

    @staticmethod
    def analyze_structure(minute_data: list, open_pct: float,
                         close_pct: float, high_pct: float, low_pct: float) -> dict:
        """
        分析分时结构
        minute_data: [{"time": "09:30", "price": 10.5}, ...]
        """
        if not minute_data or len(minute_data) < 10:
            return {"type": "数据不足", "strength": 0, "desc": "分时数据不足"}

        prices = [m["price"] for m in minute_data]
        times  = [m["time"] for m in minute_data]

        # 找到早盘(9:30-10:00)、午盘(10:00-13:00)、尾盘(14:00-15:00)
        early_prices  = [p for t, p in zip(times, prices) if "09:3" <= t <= "10:00"]
        midday_prices = [p for t, p in zip(times, prices) if "10:00" <= t <= "13:00"]
        late_prices   = [p for t, p in zip(times, prices) if "14:00" <= t]

        # 计算各段均值
        early_avg  = sum(early_prices)  / len(early_prices)  if early_prices  else prices[0]
        late_avg   = sum(late_prices)   / len(late_prices)   if late_prices   else prices[-1]
        mid_high   = max(midday_prices) if midday_prices else prices[len(prices)//2]

        # 判断结构类型
        open_type  = MarketStructure.get_open_type(open_pct)
        structure = "震荡"
        strength   = 0

        # ── 形态识别 ──────────────────────────────────────────────────────
        if open_pct >= 2 and close_pct >= 2 and late_avg > early_avg:
            structure = "高开高走"
            strength   = 5
        elif open_pct >= 2 and close_pct < 0:
            structure = "高开低走"
            strength   = 1
        elif open_pct <= -2 and close_pct >= 2:
            structure = "低开高走"
            strength   = 4
        elif open_pct <= -2 and close_pct <= -2:
            structure = "低开低走"
            strength   = 0
        elif abs(open_pct) < 1 and abs(close_pct - open_pct) < 1:
            # 检查是否尾盘偷袭
            if len(late_prices) >= 3 and late_prices[-1] > late_prices[0] * 1.02:
                structure = "尾盘偷袭"
                strength   = 3
            else:
                structure = "横盘震荡"
                strength   = 2

        # V形反转：早盘跌 → 午盘/尾盘持续反弹
        if early_prices and midday_prices and late_prices:
            early_min = min(early_prices)
            late_max  = max(late_prices)
            if early_min == min(prices) and late_max == max(prices):
                if late_max / early_min > 1.03:
                    structure = "V形反转"
                    strength  = 4

        # A形反转：早盘冲高 → 之后持续回落
        early_max = max(early_prices)
        if early_max == max(prices) and prices[-1] < early_max * 0.97:
            structure = "A形反转"
            strength  = 1

        # 尾盘竞价抢筹（最后10分钟持续上涨）
        if len(late_prices) >= 5:
            last_5 = late_prices[-5:]
            if all(last_5[i] < last_5[i+1] for i in range(len(last_5)-1)):
                if close_pct > open_pct:
                    structure = "尾盘抢筹"
                    strength  = max(strength, 3)

        return {
            "type":     structure,
            "strength": strength,
            "open_type": open_type,
            "early_avg": round(early_avg, 3),
            "late_avg":  round(late_avg, 3),
            "mid_high":  round(mid_high, 3),
        }

    @staticmethod
    def get_buy_signal(struct: dict, pct: float) -> tuple[str, str]:
        """
        根据结构给出买入/卖出信号
        返回: (signal, reason)
        signal: BUY / SELL / HOLD / WATCH
        """
        t = struct["type"]
        s = struct["strength"]

        if t == "高开高走" and pct < 9.5:
            return "BUY", "强势高开高走，量价配合好"
        if t == "低开高走" and pct < 9.5:
            return "BUY", "低开高走反弹，积极"
        if t == "V形反转" and pct > 0:
            return "BUY", "V形反转，短线积极"
        if t == "尾盘抢筹":
            return "WATCH", "尾盘抢筹，明日重点关注"
        if t == "高开低走" and pct < 0:
            return "SELL", "高开低走，弱势出逃"
        if t == "A形反转":
            return "SELL", "A形反转，冲高回落减仓"
        if t == "横盘震荡" and s >= 2:
            return "HOLD", "横盘整理，方向不明"
        return "HOLD", "结构不明确，观望"

# ─── 主分析函数 ──────────────────────────────────────────────────────────────
def analyze_stock(code: str) -> dict:
    """分析单只股票"""
    # 实时快照
    snap = get_realtime_snapshot([code])
    code_full = ("sz" + code) if not code.startswith("sz") and not code.startswith("sh") else code
    data = snap.get(code_full, {})

    name   = data.get("name", code)
    price  = data.get("price", 0)
    prev   = data.get("prev", 0)
    open_  = data.get("open", 0)
    high   = data.get("high", 0)
    low    = data.get("low", 0)
    pct    = data.get("pct", 0)

    if price == 0 or prev == 0:
        return {"code": code, "name": name, "error": "无法获取数据"}

    # 开盘涨幅
    open_pct  = (open_ - prev) / prev * 100 if prev > 0 else 0
    high_pct  = (high - prev) / prev * 100 if prev > 0 else 0
    low_pct   = (low - prev)  / prev * 100 if prev > 0 else 0

    # 分时数据
    minute_data = get_minute_data(code)

    # 分析结构
    struct = MarketStructure.analyze_structure(
        minute_data, open_pct, pct, high_pct, low_pct
    )
    signal, reason = MarketStructure.get_buy_signal(struct, pct)

    return {
        "code":       code,
        "name":       name,
        "price":      price,
        "pct":        pct,
        "open_pct":   round(open_pct, 2),
        "high_pct":   round(high_pct, 2),
        "low_pct":    round(low_pct, 2),
        "structure":  struct,
        "signal":     signal,
        "reason":     reason,
    }

def analyze_market() -> dict:
    """分析大盘指数"""
    snap = get_realtime_snapshot(list(INDEX_CODES.keys()))
    result = {}
    for code, name in INDEX_CODES.items():
        data = snap.get(code, {})
        if not data:
            continue
        price = data.get("price", 0)
        prev  = data.get("prev", 0)
        pct   = data.get("pct", 0)
        open_ = data.get("open", 0)
        if price and prev:
            result[code] = {
                "name": name,
                "price": price,
                "pct": pct,
                "open_pct": round((open_ - prev) / prev * 100, 2) if prev else 0,
            }
    return result

# ─── 格式化输出 ──────────────────────────────────────────────────────────────
def print_stock_analysis(result: dict):
    s = result["structure"]
    sig_emoji = {"BUY": "🟢", "SELL": "🔴", "WATCH": "🟡", "HOLD": "⚪"}
    emoji = sig_emoji.get(result["signal"], "⚪")

    print(f"\n{'─'*50}")
    print(f"📊 {result['name']}({result['code']}) 分时结构分析")
    print(f"{'─'*50}")
    print(f"  当前:   {result['price']}  {result['pct']:+.2f}%")
    print(f"  开盘:   {result['open_pct']:+.2f}%")
    print(f"  最高:   {result['high_pct']:+.2f}%")
    print(f"  最低:   {result['low_pct']:+.2f}%")
    print(f"  ───────────────────────────")
    print(f"  结构:   {s['type']}  (强度{s['strength']}/5)")
    print(f"  开盘:   {s['open_type']}")
    print(f"  信号:   {emoji} {result['signal']}")
    print(f"  理由:   {result['reason']}")

def print_market(market_data: dict):
    print(f"\n{'='*50}")
    print(f"📈 大盘指数")
    print(f"{'='*50}")
    for code, d in market_data.items():
        pct  = d["pct"]
        emoji = "📈" if pct > 0 else "📉" if pct < 0 else "➡️"
        print(f"  {emoji} {d['name']} {d['price']}  {pct:+.2f}%  "
              f"(开盘{pct - d['open_pct']:+.2f}%)")

# ─── 主函数 ──────────────────────────────────────────────────────────────────
def main():
    if "--codes" in sys.argv:
        idx   = sys.argv.index("--codes")
        codes = sys.argv[idx+1].split(",")
    elif len(sys.argv) > 1:
        codes = [sys.argv[1]]
    else:
        # 默认：大盘 + 自选
        market = analyze_market()
        print_market(market)
        print("\n用法: python3 market_structure.py --codes 000586,002491")
        return

    market = analyze_market()
    print_market(market)

    results = []
    for code in codes:
        code = code.strip()
        if not code:
            continue
        r = analyze_stock(code)
        print_stock_analysis(r)
        results.append(r)

    # 汇总信号
    if results:
        print(f"\n{'='*50}")
        print(f"📋 信号汇总")
        print(f"{'='*50}")
        buys  = [r for r in results if r.get("signal") == "BUY"]
        sells = [r for r in results if r.get("signal") == "SELL"]
        watch = [r for r in results if r.get("signal") == "WATCH"]
        if buys:
            print("  买入:", " ".join(f"{r['name']}({r['code']})" for r in buys))
        if watch:
            print("  关注:", " ".join(f"{r['name']}({r['code']})" for r in watch))
        if sells:
            print("  卖出:", " ".join(f"{r['name']}({r['code']})" for r in sells))

if __name__ == "__main__":
    main()
