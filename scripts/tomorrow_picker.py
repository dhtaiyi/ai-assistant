#!/usr/bin/env python3
"""明日预选工具 v3.0 - 问财增强版

集成问财选A股技能，获取更丰富的数据：
- 涨停原因（同花顺官方）
- 首次涨停时间
- 换手率、振幅
- 更准确的板块分类

用法：
  python3 tomorrow_picker.py
  python3 tomorrow_picker.py --date 20260415
"""

import json
import os
import re
import sys
import time
import requests
from datetime import datetime, timedelta, date
from pathlib import Path

# ─── 配置 ────────────────────────────────────────────────────────────────────
HEADERS    = {"User-Agent": "Mozilla/5.0", "Referer": "https://finance.sina.com.cn"}
HIST_DIR   = Path("/home/dhtaiyi/.openclaw/workspace/stock-data/candidates")
os.makedirs(HIST_DIR, exist_ok=True)

# 问财API配置
IWENCAI_CLI = os.path.expanduser("~/.local/bin/iwencai-skillhub-cli")
IWENCAI_SKILL = os.path.expanduser("~/.openclaw/workspace/skills/问财选A股/scripts/cli.py")
IWENCAI_API_KEY = os.environ.get("IWENCAI_API_KEY", "sk-proj-01-NAItJumXGkKAe1Ha8v-rPenhNjrfud7CDgoY0DEAymigKrbbZSIwxhjOQG5RrqWytp8AZApOyf4RsS-q5d2FbyTbPZAYJC262Vbgthv9IizhxH3W-5a2kNpR3ifa0nAobbl6NQ")

# ─── 问财数据获取 ────────────────────────────────────────────────────────────
def get_zt_stocks_iwencai(n: int = 100) -> list[dict]:
    """使用问财选A股获取今日涨停股（更丰富的字段）"""
    try:
        import subprocess
        cmd = [
            "python3", IWENCAI_SKILL,
            "--query", "今日涨停股票，按成交额排序",
            "--limit", str(n),
            "--api-key", IWENCAI_API_KEY
        ]
        env = os.environ.copy()
        env["IWENCAI_BASE_URL"] = "https://openapi.iwencai.com"
        env["IWENCAI_API_KEY"] = IWENCAI_API_KEY
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, env=env)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if data.get("success"):
                return data.get("datas", [])
    except Exception as e:
        print(f"[问财] 涨停股获取失败: {e}")
    return []

# ─── 传统新浪数据获取（备用）─────────────────────────────────────────────────
def get_zt_stocks_fallback(n: int = 100) -> list[dict]:
    """备用：使用新浪接口获取涨停股"""
    url = "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeDataSimple"
    params = {"page": 1, "num": n, "sort": "changepercent", "asc": 0,
              "node": "hs_a", "_s_r_a": "page"}
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=10)
        data = r.json()
        return [
            s for s in data
            if float(s.get("changepercent", 0)) >= 9.9
            and not s.get("name", "").startswith("C")
            and not s.get("name", "").startswith("N")
            and "ST" not in s.get("name", "")
        ]
    except Exception as e:
        print(f"[新浪] 涨停数据获取失败: {e}")
        return []

# ─── 市场统计 ────────────────────────────────────────────────────────────────
def get_market_stats() -> dict:
    """获取市场整体数据"""
    stats = {"涨停数": 0, "大涨数": 0, "指数": {}, "top_amount": []}
    try:
        url = "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeDataSimple"
        params = {"page": 1, "num": 200, "sort": "changepercent", "asc": 0, "node": "hs_a"}
        r = requests.get(url, params=params, headers=HEADERS, timeout=10)
        data = r.json()
        stats["涨停数"] = sum(1 for s in data if float(s.get("changepercent", 0)) >= 9.9)
        stats["大涨数"] = sum(1 for s in data if 5 <= float(s.get("changepercent", 0)) < 9.9)
    except Exception as e:
        print(f"[市场统计] 获取失败: {e}")
    return stats

# ─── 指数数据 ────────────────────────────────────────────────────────────────
def get_index_data() -> dict:
    """获取主要指数数据"""
    indices = {}
    try:
        r = requests.get("http://qt.gtimg.cn/q=s_sh000001,s_sz399001,s_sz399006",
                         headers=HEADERS, timeout=5)
        for line in r.text.split("\n"):
            m = re.search(r'="([^"]+)"', line)
            if m:
                parts = m.group(1).split("~")
                if len(parts) > 5:
                    name = parts[1]
                    price = float(parts[3])
                    pct = float(parts[5])
                    indices[name] = {"price": price, "pct": pct}
    except:
        pass
    return indices

# ─── 涨停股分析 ──────────────────────────────────────────────────────────────
def analyze_zt_stocks(stocks: list[dict]) -> dict:
    """分析涨停股池"""
    if not stocks:
        return {"板块统计": {}, "首板列表": [], "连板列表": [], "成交额TOP": []}

    # 按涨停原因分组
    sector_map = {}
    for s in stocks:
        reason = s.get("涨停原因[20260415]", "") or s.get("reason", "其他")
        reason = reason.split("+")[0].strip()  # 取第一个标签
        if reason not in sector_map:
            sector_map[reason] = []
        sector_map[reason].append({
            "code": s.get("股票代码", ""),
            "name": s.get("股票简称", s.get("name", "")),
            "price": s.get("最新价", 0),
            "pct": s.get("最新涨跌幅", 0),
            "amount": s.get("成交额[20260415]", 0) or s.get("amount", 0),
            "reason": s.get("涨停原因[20260415]", ""),
            "first_zhangting": s.get("首次涨停时间[20260415]", ""),
            "换手率": s.get("换手率[20260415]", 0),
            "振幅": s.get("振幅[20260415]", 0),
        })

    # 按成交额排序各板块
    for sector in sector_map:
        sector_map[sector].sort(key=lambda x: x["amount"], reverse=True)

    # 成交额TOP
    top = sorted(stocks, key=lambda x: x.get("成交额[20260415]", 0) or x.get("amount", 0), reverse=True)[:10]
    top_amount = [{
        "code": s.get("股票代码", ""),
        "name": s.get("股票简称", s.get("name", "")),
        "amount": (s.get("成交额[20260415]", 0) or s.get("amount", 0)) / 1e8,
        "pct": s.get("最新涨跌幅", 0),
        "reason": s.get("涨停原因[20260415]", ""),
    } for s in top]

    # 首板 vs 连板（根据涨跌幅判断，涨停时间早的更可能是龙头）
    zhangting_time = {s.get("股票代码", ""): s.get("首次涨停时间[20260415]", "23:59:59")
                      for s in stocks if s.get("首次涨停时间[20260415]")}

    first_board = [s for s in stocks if s.get("首次涨停时间[20260415]", "")]
    first_board.sort(key=lambda x: x.get("首次涨停时间[20260415]", "99:99:99"))

    return {
        "板块统计": sector_map,
        "首板列表": first_board[:20],
        "连板列表": [],
        "成交额TOP": top_amount,
        "zhangting_time": zhangting_time,
    }

# ─── 情绪判断 ────────────────────────────────────────────────────────────────
def judge_sentiment(zt_count: int) -> tuple[str, str]:
    """判断市场情绪"""
    if zt_count >= 80:
        return "📈 上升期", "重仓龙头，积极参与连板"
    elif zt_count >= 40:
        return "⚖️ 混沌期", "轻仓试探，控制风险"
    else:
        return "📉 退潮期", "空仓休息，不抄底"

# ─── 主函数 ─────────────────────────────────────────────────────────────────
def main():
    target_date = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y%m%d")
    today_str = datetime.now().strftime("%Y-%m-%d")

    print(f"============================================================")
    print(f"📋 明日预选报告 v3.0 (问财增强版) | {today_str}")
    print(f"============================================================")

    # 获取涨停股（优先问财，备用新浪）
    print("\n⏳ 获取今日涨停股数据...")
    stocks = get_zt_stocks_iwencai(100)
    if not stocks:
        print("   → 问财无数据，切换新浪备用...")
        stocks = get_zt_stocks_fallback(100)

    # 市场统计
    stats = get_market_stats()
    indices = get_index_data()

    print(f"\n【今日概况】")
    zt_count = stats.get("涨停数", len(stocks))
    print(f"  涨停: {zt_count}只")
    print(f"  大涨5-9%: {stats.get('大涨数', 0)}只")

    if indices:
        for name, data in list(indices.items())[:3]:
            print(f"  {name}: {data['price']:.2f} {data['pct']:+.2f}%")

    sentiment, strategy = judge_sentiment(zt_count)
    print(f"  情绪: {sentiment}")

    # 分析涨停股
    if stocks:
        analysis = analyze_zt_stocks(stocks)
    else:
        analysis = {"板块统计": {}, "成交额TOP": [], "首板列表": []}

    # 主线板块
    print(f"\n【主线板块】(按成交额排序)")
    if analysis["板块统计"]:
        sorted_sectors = sorted(analysis["板块统计"].items(),
                                key=lambda x: sum(s["amount"] for s in x[1]), reverse=True)
        for i, (sector, members) in enumerate(sorted_sectors[:6], 1):
            total_amount = sum(s["amount"] for s in members) / 1e8
            top_stocks = ",".join(s["name"] for s in members[:3])
            print(f"  {i}. {sector}  {total_amount:.0f}亿 ({len(members)}只)")
            print(f"     {top_stocks}")

    # 明日首板关注
    print(f"\n【明日首板关注】(成交额排序)")
    for i, s in enumerate(analysis.get("成交额TOP", [])[:8], 1):
        amount = s.get("amount", 0)
        reason = s.get("reason", "")
        zt_time = ""
        for st in analysis.get("首板列表", []):
            if st.get("股票代码") == s.get("code"):
                zt_time = st.get("首次涨停时间[20260415]", "")[11:16] if st.get("首次涨停时间[20260415]") else ""
                break
        time_str = f" {zt_time}" if zt_time else ""
        print(f"  📈 {s['name']}({s['code']}) {s['pct']:+.1f}% {amount:.0f}亿{time_str}")
        if reason:
            print(f"     原因: {reason}")

    # 操作计划
    print(f"\n────────────────────────────────────────────────────────────")
    print(f"【操作计划】")
    print(f"  仓位:   {'50-70%' if '上升' in sentiment else '20-30%' if '混沌' in sentiment else '0%'}")
    print(f"  策略:   {strategy}")
    if analysis["成交额TOP"]:
        top1 = analysis["成交额TOP"][0]
        print(f"  重点:   {top1['name']} {top1['pct']:+.1f}% {top1['amount']:.0f}亿")
    print(f"  止损:   -7%无条件出")
    print(f"  禁止:   涨停<30家时不追连板")

    print(f"\n⚠️ 以上仅为小小雨的分析，不构成投资建议，股市有风险！")
    print(f"============================================================")

    # 保存报告
    report = {
        "date": today_str,
        "zt_count": zt_count,
        "sentiment": sentiment,
        "strategy": strategy,
        "sectors": {k: [{"code": s["code"], "name": s["name"], "amount": s["amount"], "pct": s["pct"], "reason": s["reason"]}
                        for s in v] for k, v in analysis.get("板块统计", {}).items()},
        "top_stocks": analysis.get("成交额TOP", []),
    }
    out_path = HIST_DIR / f"tomorrow_{target_date}.json"
    with open(out_path, "w") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n📁 报告已保存: {out_path}")

if __name__ == "__main__":
    main()
