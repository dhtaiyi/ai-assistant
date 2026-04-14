#!/usr/bin/env python3
"""
每日涨停首板形态分析 v1.0
每天15:05自动运行，分析今日首板股涨停前的形态特征
使用方法：python3 daily_pattern_analysis.py
"""

import requests
import pandas as pd
from mootdx.quotes import Quotes
from datetime import datetime, timedelta
import json
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.bool_): return bool(obj)
        if isinstance(obj, np.integer): return int(obj)
        if isinstance(obj, np.floating): return float(obj)
        return super().default(obj)
import os

SINA_HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://finance.sina.com.cn"}

def get_today_zt_pool():
    """获取今日涨停股池（前100只）"""
    url = "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeDataSimple"
    params = {
        "page": 1, "num": 100,
        "sort": "changepercent", "asc": 0,
        "node": "hs_a", "_s_r_a": "page"
    }
    r = requests.get(url, params=params, headers=SINA_HEADERS, timeout=10)
    data = r.json()
    zt_stocks = []
    for s in data:
        pct = float(s.get("changepercent", 0))
        if pct >= 9.9:
            zt_stocks.append({
                "name": s.get("name", ""),
                "code": s.get("symbol", ""),
                "pct": pct,
                "price": float(s.get("trade", 0)),
            })
    return zt_stocks

def get_prev_zt_pool():
    """获取昨日涨停股池（用于判断首板）"""
    # 用前一日的历史数据
    # 这里简化处理：昨日涨跌停数据需要前一天存储
    # 替代方案：用腾讯接口获取前一天涨停数据
    return []

def identify_first_board(today_zt, prev_zt_names):
    """识别今日首板股"""
    first_board = []
    for stock in today_zt:
        if stock["name"] not in prev_zt_names:
            first_board.append(stock)
    return first_board

def analyze_pre_zt_pattern(code, market=0, lookback=10):
    """分析涨停前的形态特征"""
    c = Quotes.factory(market="std")
    sym = code[2:] if code.startswith(("sz", "sh")) else code
    mkt = 0 if code.startswith("sz") else 1
    df = c.bars(symbol=sym, frequency=9, market=mkt, offset=lookback + 5)
    c.close()
    if df is None or len(df) < lookback:
        return None

    df = df.tail(lookback + 3).copy()
    df["pct"] = df["close"].pct_change() * 100
    df["body"] = abs(df["close"] - df["open"])
    df["upper_shadow"] = df["high"] - df[["open", "close"]].max(axis=1)
    df["vol_ratio"] = df["vol"] / df["vol"].rolling(5).mean()

    zt_days = df[df["pct"] >= 9.9]
    if zt_days.empty:
        return None

    last_zt = zt_days.index[-1]
    pos = df.index.get_loc(last_zt)

    result = {
        "d1_date": str(df.index[pos - 1].date()) if pos >= 1 else None,
        "d2_date": str(df.index[pos - 2].date()) if pos >= 2 else None,
        "d3_date": str(df.index[pos - 3].date()) if pos >= 3 else None,
        "patterns": [],
    }

    if pos >= 1:
        d1 = df.iloc[pos - 1]
        result["d1_pct"] = round(d1["pct"], 1)
        result["d1_vol_ratio"] = round(d1["vol_ratio"], 2)
        result["d1_shrink"] = d1["vol_ratio"] < 0.9
        result["d1_upper_shadow"] = (d1["upper_shadow"] / d1["body"]) > 0.5 if d1["body"] > 0.5 else False
        result["d1_small_body"] = d1["body"] / d1["close"] < 0.02
        result["d1_gap_up"] = d1["open"] > df.iloc[pos - 2]["close"] * 1.01 if pos >= 2 else False

        # 形态标签
        if result["d1_upper_shadow"]:
            result["patterns"].append("上影线")
        if result["d1_shrink"]:
            result["patterns"].append("缩量")
        if result["d1_small_body"]:
            result["patterns"].append("小K线")
        if result["d1_gap_up"]:
            result["patterns"].append("跳空")
        if result["d1_pct"] > 5:
            result["patterns"].append("大阳")

    if pos >= 2:
        d2 = df.iloc[pos - 2]
        result["d2_pct"] = round(d2["pct"], 1)
        result["d2_vol_ratio"] = round(d2["vol_ratio"], 2)

    if pos >= 3:
        d3 = df.iloc[pos - 3]
        result["d3_pct"] = round(d3["pct"], 1)

    # 3天形态
    if pos >= 3:
        three_day = result.get("d1_pct", 0) + result.get("d2_pct", 0) + result.get("d3_pct", 0)
        result["three_day_pct"] = round(three_day, 1)

    return result

def main():
    today = datetime.now().strftime("%Y-%m-%d")
    output_dir = "/home/dhtaiyi/.openclaw/workspace/stock-learning/daily-patterns"
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 65)
    print(f"[形态] 每日涨停首板形态分析 {today}")
    print("=" * 65)

    # 读取昨日涨停股数据（如果有）
    prev_file = os.path.join(output_dir, f"zt_pool_{datetime.now().strftime('%Y%m%d')}.json")
    prev_day = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    prev_file_auto = os.path.join(output_dir, f"zt_pool_{prev_day}.json")

    prev_zt_names = []
    if os.path.exists(prev_file_auto):
        with open(prev_file_auto) as f:
            prev_data = json.load(f)
            prev_zt_names = [s["name"] for s in prev_data]

    # 获取今日涨停池
    print("\n获取今日涨停数据...")
    today_zt = get_today_zt_pool()
    print(f"今日涨停: {len(today_zt)} 只")

    # 保存今日涨停池
    with open(os.path.join(output_dir, f"zt_pool_{datetime.now().strftime('%Y%m%d')}.json"), "w") as f:
        json.dump(today_zt, f, cls=NumpyEncoder)

    # 识别首板股
    first_board = identify_first_board(today_zt, prev_zt_names)
    print(f"今日首板: {len(first_board)} 只")

    if not first_board:
        print("未发现首板股（可能昨日涨停数据缺失）")
        first_board = today_zt[:10]  #  fallback到涨停股前10

    # 分析首板股形态
    print("\n分析涨停前形态...")
    results = []
    for stock in first_board[:15]:  # 最多分析15只
        code = stock["code"]
        mkt = 0 if code.startswith("sz") else 1
        pattern = analyze_pre_zt_pattern(code, mkt, lookback=10)
        if pattern:
            results.append({
                "name": stock["name"],
                "code": code,
                "price": stock["price"],
                "pct": stock["pct"],
                **pattern
            })

    # 输出结果
    print("\n" + "=" * 65)
    print("[今日首板股形态分析]")
    print("=" * 65)

    print("\n%-8s %-6s %6s %6s %6s %6s  形态标签" % (
        "股票", "代码", "昨1%", "昨2%", "昨3%", "3日%"))
    print("-" * 65)

    for r in sorted(results, key=lambda x: x.get("three_day_pct", 0), reverse=True):
        d1 = r.get("d1_pct", 0)
        d2 = r.get("d2_pct", 0)
        d3 = r.get("d3_pct", 0)
        td = r.get("three_day_pct", 0)
        pat = "/".join(r.get("patterns", [])) or "-"
        print("%-8s %-6s %+5.1f%% %+5.1f%% %+5.1f%% %+6.1f%%  %s" % (
            r["name"][:8], r["code"][-6:],
            d1, d2, d3, td, pat
        ))

    # 规律总结
    total = len(results)
    shrink_count = sum(1 for r in results if r.get("d1_shrink"))
    shadow_count = sum(1 for r in results if "上影线" in r.get("patterns", []))
    gap_count = sum(1 for r in results if "跳空" in r.get("patterns", []))
    small_count = sum(1 for r in results if "小K线" in r.get("patterns", []))

    print("\n" + "=" * 65)
    print("[今日首板形态规律]")
    print("=" * 65)
    print(f"  样本: {total} 只首板")
    print(f"  昨日缩量: {shrink_count}只 ({shrink_count/max(total,1)*100:.0f}%%)")
    print(f"  昨日上影线: {shadow_count}只 ({shadow_count/max(total,1)*100:.0f}%%)")
    print(f"  昨日跳空: {gap_count}只 ({gap_count/max(total,1)*100:.0f}%%)")
    print(f"  昨日小K线: {small_count}只 ({small_count/max(total,1)*100:.0f}%%)")

    # 判断明日方向
    print("\n[明日预判]")
    if shadow_count >= total * 0.4:
        print("  上影线洗盘型较多 → 明日关注回调后的反弹机会")
    if gap_count >= total * 0.3:
        print("  跳空高开型较多 → 明日注意高开溢价")
    if shrink_count >= total * 0.3:
        print("  缩量整理型较多 → 次日容易变盘")

    # 保存报告（转换numpy类型）
    def to_python(obj):
        if isinstance(obj, dict):
            return {k: to_python(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [to_python(v) for v in obj]
        elif str(type(obj)) in ("<class 'numpy.bool_'>", "<class 'numpy.int64'>", "<class 'numpy.float64'>"):
            return obj.item()
        return obj

    report_file = os.path.join(output_dir, f"pattern_report_{datetime.now().strftime('%Y%m%d')}.json")
    report_data = to_python({
        "date": today,
        "total_zt": len(today_zt),
        "first_board_count": len(first_board),
        "results": results,
        "summary": {
            "shrink": shrink_count,
            "shadow": shadow_count,
            "gap": gap_count,
            "small": small_count
        }
    })
    with open(report_file, "w") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2, cls=NumpyEncoder)

    print(f"\n报告已保存: {report_file}")
    print("\n" + "=" * 65)
    print("仅供参参考，不构成投资建议")
    print("=" * 65)

if __name__ == "__main__":
    main()


