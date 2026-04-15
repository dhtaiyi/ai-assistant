#!/usr/bin/env python3
"""
每日市场情绪判断 V3.0 - 问财增强版
=====================================
改进点（对比V2.1）：
1. 问财涨停原因替代SECTOR_MAP猜测
2. 官方涨停原因识别主线板块
3. 连板数据结合问财历史
4. 成交额数据更准确
"""
import requests
import json
import re
import os
import subprocess
import time
from datetime import datetime, time as dtime

LOG_FILE = "/tmp/market_sentiment.log"

# 问财配置
IWENCAI_SKILL = os.path.expanduser("~/.openclaw/workspace/skills/问财选A股/scripts/cli.py")
IWENCAI_API_KEY = os.environ.get(
    "IWENCAI_API_KEY",
    "sk-proj-01-NAItJumXGkKAe1Ha8v-rPenhNjrfud7CDgoY0DEAymigKrbbZSIwxhjOQG5RrqWytp8AZApOyf4RsS-q5d2FbyTbPZAYJC262Vbgthv9IizhxH3W-5a2kNpR3ifa0nAobbl6NQ"
)

# ─── 问财数据 ────────────────────────────────────────────────────────────
def get_iwencai_zt(n=200) -> tuple[list[dict], dict]:
    """获取问财涨停股 + 按涨停原因分组"""
    try:
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
                stocks = data.get("datas", [])
                # 按涨停原因分组
                sectors = {}
                for s in stocks:
                    reason = s.get("涨停原因[20260415]", "") or "其他"
                    primary = reason.split("+")[0].split("(")[0].strip()
                    if primary not in sectors:
                        sectors[primary] = []
                    amt = s.get("成交额[20260415]", 0) or 0
                    sectors[primary].append({
                        "code": s.get("股票代码", "").replace(".SZ", "").replace(".SH", ""),
                        "name": s.get("股票简称", ""),
                        "pct": s.get("最新涨跌幅", 0),
                        "amount": amt,
                        "换手率": s.get("换手率[20260415]", 0),
                        "reason": reason,
                        "zt_time": s.get("首次涨停时间[20260415]", ""),
                    })
                return stocks, sectors
    except Exception as e:
        print(f"[问财] 涨停数据获取失败: {e}")
    return [], {}

# ─── 新浪数据（备用/辅助）─────────────────────────────────────────────────
def get_sina_data() -> tuple[list, list, dict]:
    url = "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeDataSimple"
    by_pct, by_amt = [], []
    try:
        r1 = requests.get(url, params={"page": 1, "num": 200, "sort": "changepercent", "asc": 0, "node": "hs_a"}, timeout=10)
        by_pct = r1.json()
    except:
        pass
    try:
        r2 = requests.get(url, params={"page": 1, "num": 100, "sort": "amount", "asc": 0, "node": "hs_a"}, timeout=10)
        by_amt = r2.json()
    except:
        pass

    indices = {}
    try:
        r_idx = requests.get("http://qt.gtimg.cn/q=s_sh000001,s_sz399001,s_sz399006", timeout=5)
        for line in r_idx.text.strip().split("\n"):
            if '"' not in line:
                continue
            m = re.search(r'="([^"]+)"', line)
            if not m:
                continue
            parts = m.group(1).split("~")
            try:
                if len(parts) > 5 and parts[1]:
                    name = parts[1]
                    price = float(parts[3]) if parts[3] else 0
                    pct = float(parts[5]) if len(parts) > 5 and parts[5] else 0
                    indices[name] = {"price": price, "pct": pct}
            except:
                continue
    except:
        pass
    return by_pct, by_amt, indices

# ─── 市场情绪判断 ────────────────────────────────────────────────────────
def check_market_status(by_pct):
    if not by_pct:
        return "未知", "无数据"
    top = by_pct[:20]
    avg_pct = sum(float(s.get("changepercent", 0)) for s in top) / len(top)
    if avg_pct >= 5:
        return "极强", "主线爆发，指数行情"
    elif avg_pct >= 2:
        return "偏强", "结构性机会"
    elif avg_pct >= 0:
        return "偏弱", "谨慎观望"
    else:
        return "极弱", "控制风险"

# ─── 主函数 ─────────────────────────────────────────────────────────────
def main():
    print(f"\n{'='*60}")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"📊 市场情绪 V3.0 (问财增强版) | {ts}")
    print(f"{'='*60}")

    print("\n⏳ 获取问财涨停数据...")
    zt_stocks, sectors = get_iwencai_zt(200)

    _, _, indices = get_sina_data()

    zt_count = len(zt_stocks)
    sh_pct = indices.get("上证指数", {}).get("pct", 0)

    # 情绪判断
    if zt_count >= 80:
        sentiment, advice = "📈 上升期", "重仓龙头，积极参与连板"
    elif zt_count >= 40:
        sentiment, advice = "⚖️ 混沌期", "轻仓试探，控制风险"
    else:
        sentiment, advice = "📉 退潮期", "空仓休息，不抄底"

    print(f"\n【市场概况】")
    print(f"  涨停: {zt_count}只  情绪: {sentiment}")
    if indices:
        for name, d in list(indices.items())[:3]:
            print(f"  {name}: {d['price']:.2f} {d['pct']:+.2f}%")

    # 成交额TOP5（机构信号）
    amount_top = sorted(zt_stocks, key=lambda x: x.get("成交额[20260415]", 0), reverse=True)[:5]
    print(f"\n【成交额TOP5】（机构资金信号）")
    for i, s in enumerate(amount_top, 1):
        amt = s.get("成交额[20260415]", 0) or 0
        pct = s.get("最新涨跌幅", 0)
        name = s.get("股票简称", "")
        reason = s.get("涨停原因[20260415]", "")[:20]
        print(f"  {i}. {name} {pct:+.1f}% {amt/1e8:.0f}亿")
        if reason:
            print(f"     {reason}")

    # 主线板块
    print(f"\n【主线板块】（官方涨停原因）")
    sorted_sectors = sorted(sectors.items(),
                            key=lambda x: sum(s.get("amount", 0) for s in x[1]), reverse=True)
    for i, (sec, members) in enumerate(sorted_sectors[:6], 1):
        total_amt = sum(s.get("amount", 0) for s in members) / 1e8
        names = ",".join(m["name"] for m in sorted(members, key=lambda x: x.get("amount", 0), reverse=True)[:3])
        print(f"  {i}. {sec} {total_amt:.0f}亿 ({len(members)}只)")
        print(f"     {names}")

    # 早盘强势板块（涨幅超5%的非涨停）
    print(f"\n【强势股关注】")
    print(f"  策略: {advice}")
    if sorted_sectors:
        top_sector = sorted_sectors[0][0]
        top_stocks = sorted(sectors[top_sector], key=lambda x: x.get("amount", 0), reverse=True)[:3]
        print(f"  主线龙头: {','.join(s['name'] for s in top_stocks)}")

    print(f"\n{'='*60}")

if __name__ == "__main__":
    main()
