#!/usr/bin/env python3
"""连板晋级追踪器 v2.0

功能：
1. 追踪昨日涨停 → 今日连板晋级（1→2→3→4→5板）
2. 识别炸板风险（从涨停打开）
3. 识别冲高回落（未封板）
4. 生成晋级日报

用法：
  python3 breakeven_tracker.py          # 今日追踪
  python3 breakeven_tracker.py --date 20260415  # 指定日期昨日
  python3 breakeven_tracker.py --history 5      # 最近5天历史
"""

import json
import os
import re
import sys
import requests
from datetime import datetime, timedelta, date
from pathlib import Path

# ─── 配置 ────────────────────────────────────────────────────────────────────
HIST_DIR  = Path("/home/dhtaiyi/.openclaw/workspace/stock-data/lianban")
os.makedirs(HIST_DIR, exist_ok=True)

# ─── 工具函数 ────────────────────────────────────────────────────────────────
def is_clean(name: str) -> bool:
    return not any(x in name for x in ["ST", "*ST", "N ", "退", "S "])

def norm_code(symbol: str) -> str:
    return symbol.replace("sz", "").replace("sh", "")

def get_prev_trading_day(dt: datetime = None) -> str:
    """获取前一交易日"""
    dt = dt or datetime.now()
    days = 1 if dt.weekday() != 0 else 3
    prev = dt - timedelta(days=days)
    return prev.strftime("%Y%m%d")

# ─── 数据获取 ────────────────────────────────────────────────────────────────
def load_candidates(day_str: str) -> list[dict]:
    """加载指定日期的候选池（昨日涨停）"""
    # 优先从 candidates 目录
    cand_path = Path(f"/home/dhtaiyi/.openclaw/workspace/stock-data/candidates/{day_str}.json")
    if cand_path.exists():
        try:
            data = json.loads(cand_path.read_text())
            return [
                {"code": _norm_c(c), "name": v.get("name", ""),
                 "yesterday_pct": v.get("pct", 10)}
                for c, v in data.items()
                if is_clean(v.get("name", ""))
                and v.get("type") in ["涨停", "首板", "强势"]
            ]
        except Exception:
            pass

    # 降级：从 lianban 目录
    path = HIST_DIR / f"{day_str}.json"
    if path.exists():
        try:
            data = json.loads(path.read_text())
            result = []
            for key in ["lianban_3plus", "lianban_2", "lianban_1"]:
                for s in data.get(key, []):
                    result.append({
                        "code": norm_code(s.get("code", "")),
                        "name": s.get("name", ""),
                        "yesterday_pct": s.get("yesterday_pct", 10),
                    })
            return result
        except Exception:
            pass
    return []

def get_realtime_batch(codes: list[str]) -> dict:
    """批量获取实时行情"""
    if not codes:
        return {}
    full = []
    for c in codes:
        c = c.strip()
        if not c.startswith("sz") and not c.startswith("sh"):
            c = ("sz" + c) if c[0] in "03" else ("sh" + c)
        full.append(c)
    try:
        r = requests.get(f"http://qt.gtimg.cn/q={','.join(full)}", timeout=10)
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
            name   = parts[1]
            price  = float(parts[3])  if parts[3]  else 0
            prev   = float(parts[4])  if parts[4]  else 0
            open_  = float(parts[5])  if parts[5]  else 0
            high   = float(parts[33]) if parts[33] else 0
            low    = float(parts[34]) if parts[34] else 0
            amount = float(parts[37]) if parts[37] else 0
            if prev > 0:
                result[code] = {
                    "name":   name,
                    "price":  price,
                    "prev":   prev,
                    "pct":    (price - prev) / prev * 100,
                    "open":   open_,
                    "high":   high,
                    "low":    low,
                    "amount": amount,
                }
        except Exception:
            continue
    return result

def _norm_c(code: str) -> str:
    return code.replace("sz", "").replace("sh", "")

# ─── 连板分析 ────────────────────────────────────────────────────────────────
class LianbanAnalyzer:
    """连板晋级分析器"""

    @staticmethod
    def classify(stock: dict, data: dict) -> str:
        """分类：lianban_3plus / lianban_2 / first / zhaban / faded / weak"""
        code = stock["code"]
        if code not in data:
            return "nodata"
        d    = data[code]
        pct  = d["pct"]
        high = d["high"]
        prev = d["prev"]
        y_pct = stock.get("yesterday_pct", 0)

        ever_zt = (high >= prev * 1.099) if prev > 0 else False
        is_zt   = pct >= 9.85

        if is_zt and y_pct >= 9.5:
            return "lianban_3plus"  # 继续连板
        if is_zt and y_pct < 9.5:
            return "first"          # 首板（今天涨停但昨天没涨停）
        if ever_zt and not is_zt and pct < 9.5:
            return "zhaban"         # 炸板
        if 5 <= pct < 9.5:
            return "faded"          # 冲高回落
        return "weak"

    @staticmethod
    def format_board_count(y_pct: float) -> int:
        """根据昨日涨幅估算连板数"""
        if y_pct >= 9.5:
            return 2  # 至少2板
        return 1

# ─── 核心分析函数 ────────────────────────────────────────────────────────────
def analyze_day(target_date: str = None) -> dict:
    """分析指定日期（实际是分析"昨天涨停今天的表现"）"""
    if target_date is None:
        target_date = get_prev_trading_day()

    print(f"\n{'='*60}")
    print(f"🔗 连板晋级追踪 v2.0 | 分析日期: {target_date}")
    print(f"{'='*60}")

    # 加载昨日涨停股
    yesterday_stocks = load_candidates(target_date)
    print(f"📂 昨日涨停股池: {len(yesterday_stocks)}只 ({target_date})")

    if not yesterday_stocks:
        print("❌ 无昨日涨停数据，请先运行 tomorrow_picker.py 生成候选池")
        return {}

    # 获取实时数据
    codes = [_norm_c(s["code"]) for s in yesterday_stocks]
    data  = get_realtime_batch(codes)
    print(f"📡 实时数据: {len(data)}只")

    if not data:
        print("❌ 无法获取实时数据")
        return {}

    # 分类
    buckets = {
        "lianban_3plus": [],
        "lianban_2":     [],
        "first":         [],
        "zhaban":        [],
        "faded":         [],
        "weak":          [],
    }

    for stock in yesterday_stocks:
        tag = LianbanAnalyzer.classify(stock, data)
        if tag in buckets:
            d = data.get(stock["code"], {})
            buckets[tag].append({
                "name":         stock["name"],
                "code":         stock["code"],
                "pct":          d.get("pct", 0),
                "price":        d.get("price", 0),
                "high_pct":     (d["high"]/d["prev"]-1)*100 if d.get("prev",0) > 0 else 0,
                "amount":       d.get("amount", 0) / 1e8,
                "yesterday_pct": stock.get("yesterday_pct", 0),
            })

    return buckets

def save_result(buckets: dict, target_date: str):
    """保存分析结果"""
    path = HIST_DIR / f"{datetime.now().strftime('%Y%m%d')}.json"
    result = {
        "date":    datetime.now().strftime("%Y%m%d"),
        "target":  target_date,
        "buckets": buckets,
        "saved_at": datetime.now().isoformat(),
    }
    with open(path, "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return path

def print_report(buckets: dict):
    """打印分析报告"""
    def sort_key(lst):
        return sorted(lst, key=lambda x: x["amount"], reverse=True)

    print(f"\n{'─'*60}")
    if buckets.get("lianban_3plus"):
        print(f"🏆 3板+龙头 ({len(buckets['lianban_3plus'])}只):")
        for s in sort_key(buckets["lianban_3plus"])[:5]:
            print(f"  👑 {s['name']}({s['code']}) +{s['pct']:.1f}% "
                  f"成交{s['amount']:.0f}亿")
    else:
        print("🏆 3板+龙头: 无")

    if buckets.get("lianban_2"):
        print(f"\n🔗 2板确认 ({len(buckets['lianban_2'])}只):")
        for s in sort_key(buckets["lianban_2"])[:8]:
            print(f"  ✅ {s['name']}({s['code']}) +{s['pct']:.1f}% "
                  f"成交{s['amount']:.0f}亿")

    if buckets.get("first"):
        print(f"\n📈 首板延续 ({len(buckets['first'])}只):")
        for s in sort_key(buckets["first"])[:8]:
            print(f"  ➡️ {s['name']}({s['code']}) +{s['pct']:.1f}% "
                  f"成交{s['amount']:.0f}亿")

    if buckets.get("zhaban"):
        print(f"\n💥 炸板预警 ({len(buckets['zhaban'])}只):")
        for s in sorted(buckets["zhaban"], key=lambda x: x["pct"], reverse=True)[:5]:
            print(f"  🚨 {s['name']}({s['code']}) {s['pct']:+.1f}% "
                  f"(最高{s['high_pct']:.1f}%)")

    if buckets.get("faded"):
        print(f"\n📉 冲高回落 ({len(buckets['faded'])}只):")
        for s in sort_key(buckets["faded"])[:5]:
            print(f"  ⚠️ {s['name']}({s['code']}) +{s['pct']:.1f}%")

    if buckets.get("weak"):
        print(f"\n❄️ 走弱 ({len(buckets['weak'])}只):")
        for s in sorted(buckets["weak"], key=lambda x: x["pct"])[:5]:
            print(f"  🔵 {s['name']}({s['code']}) {s['pct']:+.1f}%")

    # 养家心法提示
    total_zt = sum(len(v) for v in buckets.values())
    print(f"\n{'─'*60}")
    print(f"💡 养家心法提示:")
    if buckets["lianban_3plus"]:
        print(f"  龙头已现！{len(buckets['lianban_3plus'])}只3板+股票 → 死磕龙头")
    elif buckets["lianban_2"]:
        print(f"  2板确认！{len(buckets['lianban_2'])}只 → 明日关注3板晋级")
    elif buckets["first"]:
        print(f"  首板延续({len(buckets['first'])}只)，等待晋级确认")
    if buckets["zhaban"]:
        print(f"  炸板{len(buckets['zhaban'])}只！注意退潮风险")
    if not any([buckets["lianban_3plus"], buckets["lianban_2"], buckets["first"]]):
        print(f"  昨日涨停股整体走弱，市场情绪偏谨慎")

    # 关键信号
    print(f"\n🎯 关键信号:")
    if buckets.get("lianban_2"):
        best = sort_key(buckets["lianban_2"])[0]
        print(f"  重点关注: {best['name']} 2板，成交{best['amount']:.0f}亿")
        print(f"  明日竞价若高开3-7%，可参与3板")
    if buckets.get("zhaban"):
        worst = sorted(buckets["zhaban"], key=lambda x: x["pct"])[0]
        print(f"  注意: {worst['name']} 炸板，明日不能反包则回避")

def print_history(days: int = 5):
    """打印历史连板统计"""
    print(f"\n{'='*50}")
    print(f"📜 最近{days}天连板历史")
    print(f"{'='*50}")
    files = sorted(HIST_DIR.glob("*.json"), reverse=True)[:days]
    for f in files:
        try:
            data = json.loads(f.read_text())
            b    = data.get("buckets", {})
            l3   = len(b.get("lianban_3plus", []))
            l2   = len(b.get("lianban_2", []))
            zb   = len(b.get("zhaban", []))
            date_str = data.get("target", f.stem)
            print(f"  {date_str}: 3板+{l3} 2板+{l2} 炸板{zb}")
        except Exception:
            continue

# ─── 主函数 ──────────────────────────────────────────────────────────────────
def main():
    if "--history" in sys.argv:
        idx  = sys.argv.index("--history")
        days = int(sys.argv[idx+1]) if idx+1 < len(sys.argv) else 5
        print_history(days)
        return

    target = None
    if "--date" in sys.argv:
        idx = sys.argv.index("--date")
        target = sys.argv[idx+1]

    buckets = analyze_day(target)
    if not buckets:
        return

    print_report(buckets)
    save_result(buckets, target or get_prev_trading_day())

if __name__ == "__main__":
    main()
