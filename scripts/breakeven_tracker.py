#!/usr/bin/env python3
"""连板晋级追踪器 v3.0 - 问财增强版

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
import time
import subprocess
import requests
from datetime import datetime, timedelta, date
from pathlib import Path

# ─── 配置 ────────────────────────────────────────────────────────────────────
HIST_DIR  = Path("/home/dhtaiyi/.openclaw/workspace/stock-data/lianban")
os.makedirs(HIST_DIR, exist_ok=True)

# 问财配置
IWENCAI_SKILL = os.path.expanduser("~/.openclaw/workspace/skills/问财选A股/scripts/cli.py")
IWENCAI_API_KEY = os.environ.get(
    "IWENCAI_API_KEY",
    "sk-proj-01-NAItJumXGkKAe1Ha8v-rPenhNjrfud7CDgoY0DEAymigKrbbZSIwxhjOQG5RrqWytp8AZApOyf4RsS-q5d2FbyTbPZAYJC262Vbgthv9IizhxH3W-5a2kNpR3ifa0nAobbl6NQ"
)

# ─── 工具函数 ────────────────────────────────────────────────────────────────
def is_clean(name: str) -> bool:
    return not any(x in name for x in ["ST", "*ST", "N ", "退", "S "])

def norm_code(sym: str) -> str:
    """标准化股票代码，保留前导零"""
    sym = sym.upper().replace(".SZ","").replace(".SH","").replace("SZ","").replace("SH","")
    return sym  # 如 002361.SZ → 002361

def get_prev_trading_day(dt: datetime = None) -> str:
    """获取前一交易日"""
    dt = dt or datetime.now()
    days = 1 if dt.weekday() != 0 else 3
    prev = dt - timedelta(days=days)
    return prev.strftime("%Y%m%d")

def iwencai_query(query: str, limit: int = 20) -> list[dict]:
    """调用问财选A股CLI"""
    try:
        cmd = [
            "python3", IWENCAI_SKILL,
            "--query", query,
            "--limit", str(limit),
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
        print(f"[问财] 查询失败: {e}")
    return []

# ─── 问财数据获取 ────────────────────────────────────────────────────────────
def get_zt_stocks_today() -> list[dict]:
    """获取今日涨停股（含丰富字段）"""
    return iwencai_query("今日涨停股票，按成交额排序", 100)

def get_zt_stocks_by_date(date_str: str) -> list[dict]:
    """获取指定日期的历史涨停股"""
    # 问财支持日期查询
    return iwencai_query(f"{date_str}日涨停股票，按成交额排序", 100)

def get_yesterday_zt() -> list[dict]:
    """获取昨日涨停股"""
    prev = get_prev_trading_day()
    return get_zt_stocks_by_date(prev)

# ─── 腾讯实时行情 ────────────────────────────────────────────────────────────
def get_realtime_batch(codes: list[str]) -> dict:
    """批量获取实时行情（腾讯接口）"""
    if not codes:
        return {}
    normalized = [c.replace("sz", "sz").replace("sh", "sh") for c in codes]
    batch = ",".join([f"{'sz' if c.startswith(('0','3','8')) else 'sh'}{c}" for c in normalized])
    try:
        r = requests.get(f"http://qt.gtimg.cn/q={batch}", timeout=5)
        result = {}
        for line in r.text.split("\n"):
            m = re.search(r'="([^"]+)"', line)
            if m:
                parts = m.group(1).split("~")
                if len(parts) > 6:
                    sym = parts[0].replace("sz","").replace("sh","")
                    try:
                        today_pct = float(parts[5])
                    except:
                        today_pct = 0
                    result[sym] = {
                        "price": float(parts[3]) if parts[3] else 0,
                        "yesterday_close": float(parts[4]) if parts[4] else 0,
                        "today_open": float(parts[6]) if parts[6] else 0,
                        "pct": today_pct,
                    }
        return result
    except Exception as e:
        print(f"[腾讯] 批量查询失败: {e}")
        return {}

# ─── 连板分析 ────────────────────────────────────────────────────────────────
def analyze_lianban():
    """分析今日连板晋级情况"""
    today = datetime.now().strftime("%Y%m%d")

    print(f"============================================================")
    print(f"🔗 连板晋级追踪 v3.0 (问财增强版) | {today}")
    print(f"============================================================")

    # 获取昨日涨停股（候选池）
    print("\n⏳ 获取昨日涨停股...")
    yesterday_zt = get_yesterday_zt()
    if not yesterday_zt:
        print("   → 问财无数据，尝试加载历史...")
        prev = get_prev_trading_day()
        cand = load_candidates(prev)
        if cand:
            yesterday_zt = [{"股票代码": c["code"], "股票简称": c["name"]} for c in cand]

    print(f"   昨日涨停: {len(yesterday_zt)}只")

    # 获取今日涨停股
    print("⏳ 获取今日涨停股...")
    today_zt = get_zt_stocks_today()
    today_codes = {norm_code(s.get("股票代码","")): s for s in today_zt}
    print(f"   今日涨停: {len(today_zt)}只")

    if not yesterday_zt:
        print("❌ 无昨日数据，无法追踪连板")
        return

    # 分析晋级
    lianban_3plus = []  # 4板+
    lianban_2 = []      # 2板
    lianban_1 = []      # 首板（昨日涨停今日也涨停）
    fallen = []         # 掉队（昨日涨停今日未涨停）
    chonggao = []       # 冲高回落

    # 从历史找昨日连板数
    prev = get_prev_trading_day()
    history = load_lianban_history(prev)
    yesterday_lianban = {}
    for cat in ["lianban_3plus", "lianban_2", "lianban_1"]:
        for s in history.get(cat, []):
            yesterday_lianban[s["code"]] = history["lianban_map"].get(s["code"], 1)

    for s in yesterday_zt:
        code = norm_code(s.get("股票代码",""))
        name = s.get("股票简称", s.get("name", ""))
        if not is_clean(name):
            continue

        today_info = today_codes.get(code)
        if today_info:
            # 动态获取今日日期后缀
            date_key = None
            for k in today_info:
                if "涨停原因[" in k:
                    date_key = k
                    break
            reason = today_info.get(date_key or "", "")
            amount = 0
            hs_rate = 0
            for k, v in today_info.items():
                if "成交额[" in k:
                    amount = v or 0
                if "换手率[" in k:
                    hs_rate = v or 0

            prev_lianban = yesterday_lianban.get(code, 0)

            if prev_lianban >= 2:
                lianban_3plus.append({
                    "code": code, "name": name, "board": prev_lianban + 1,
                    "reason": reason, "amount": amount, "换手率": hs_rate,
                })
            elif prev_lianban == 1:
                lianban_2.append({
                    "code": code, "name": name, "board": 2,
                    "reason": reason, "amount": amount, "换手率": hs_rate,
                })
            else:
                # 昨日首板今日继续涨停
                lianban_1.append({
                    "code": code, "name": name, "board": 1,
                    "reason": reason, "amount": amount, "换手率": hs_rate,
                })
        else:
            # 掉队
            fallen.append({"code": code, "name": name})

    # 今日首板（今日新涨停，不在昨日候选里的）
    today_new = []
    yesterday_codes = {norm_code(s.get("股票代码","")) for s in yesterday_zt}
    for s in today_zt:
        code = norm_code(s.get("股票代码",""))
        if code not in yesterday_codes:
            # 动态取日期后缀
            reason, amount, hs = "", 0, 0
            for k, v in s.items():
                if "涨停原因[" in k: reason = v or ""
                if "成交额[" in k: amount = v or 0
                if "换手率[" in k: hs = v or 0
            today_new.append({
                "code": code,
                "name": s.get("股票简称",""),
                "reason": reason,
                "amount": amount,
                "换手率": hs,
            })

    # 输出
    print(f"\n【连板晋级】（{len(lianban_3plus)}只 4板+）")
    for s in sorted(lianban_3plus, key=lambda x: x["board"], reverse=True):
        print(f"  🏆 {s['name']}({s['code']}) {s['board']}板")
        if s.get("reason"):
            print(f"     {s['reason']}")

    print(f"\n【二板】（{len(lianban_2)}只）")
    for s in sorted(lianban_2, key=lambda x: x["amount"], reverse=True):
        print(f"  📈 {s['name']}({s['code']}) 2板 {s['amount']/1e8:.0f}亿")
        if s.get("reason"):
            print(f"     {s['reason']}")

    print(f"\n【首板】（{len(lianban_1)}只）")
    for s in sorted(lianban_1, key=lambda x: x["amount"], reverse=True)[:10]:
        print(f"  ➕ {s['name']}({s['code']}) {s['amount']/1e8:.0f}亿")

    print(f"\n【掉队】（{len(fallen)}只）")
    for s in fallen[:10]:
        print(f"  ❌ {s['name']}({s['code']})")

    print(f"\n【今日新首板】（{len(today_new)}只，成交额排序）")
    for s in sorted(today_new, key=lambda x: x["amount"], reverse=True)[:10]:
        print(f"  ⭐ {s['name']}({s['code']}) {s['amount']/1e8:.0f}亿")
        if s.get("reason"):
            print(f"     {s['reason']}")

    # 养家心法提示
    if len(lianban_3plus) >= 3:
        print(f"\n💡 养家心法：连板股{len(lianban_3plus)}只，情绪高涨，死磕龙头！")
    elif len(lianban_3plus) >= 1:
        print(f"\n💡 养家心法：市场有赚钱效应，关注龙头晋级")
    elif len(fallen) > len(yesterday_zt) * 0.5:
        print(f"\n⚠️ 养家心法：掉队率过高，谨慎追板")
    else:
        print(f"\n💡 养家心法：情绪混沌，等待主线明确")

    print(f"\n⚠️ 以上仅为小小雨的分析，不构成投资建议！")
    print(f"============================================================")

    # 保存
    report = {
        "date": today,
        "lianban_3plus": lianban_3plus,
        "lianban_2": lianban_2,
        "lianban_1": lianban_1,
        "fallen": fallen[:30],
        "today_new": today_new[:30],
        "lianban_map": {s["code"]: s["board"] for s in lianban_3plus + lianban_2 + lianban_1},
    }
    out_path = HIST_DIR / f"{today}.json"
    with open(out_path, "w") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n📁 报告已保存: {out_path}")

# ─── 历史数据加载 ────────────────────────────────────────────────────────────
def load_candidates(day_str: str) -> list[dict]:
    """加载指定日期的候选池"""
    cand_path = Path(f"/home/dhtaiyi/.openclaw/workspace/stock-data/candidates/{day_str}.json")
    if cand_path.exists():
        try:
            data = json.loads(cand_path.read_text())
            return [
                {"code": norm_code(c), "name": v.get("name", ""),
                 "yesterday_pct": v.get("pct", 10)}
                for c, v in data.items()
                if is_clean(v.get("name", ""))
            ]
        except Exception:
            pass
    return []

def load_lianban_history(day_str: str) -> dict:
    """加载指定日期的连板记录"""
    path = HIST_DIR / f"{day_str}.json"
    if path.exists():
        try:
            data = json.loads(path.read_text())
            return data
        except Exception:
            pass
    return {"lianban_3plus": [], "lianban_2": [], "lianban_1": [], "lianban_map": {}}

# ─── 主函数 ─────────────────────────────────────────────────────────────────
def main():
    today_str = datetime.now().strftime("%Y%m%d")

    if "--history" in sys.argv:
        idx = sys.argv.index("--history")
        n = int(sys.argv[idx+1]) if idx+1 < len(sys.argv) else 5
        show_history(n)
    else:
        analyze_lianban()

def show_history(n: int):
    """显示最近N天连板历史"""
    print(f"【最近{n}天连板历史】")
    today = datetime.now()
    for i in range(1, n+1):
        day = today - timedelta(days=i)
        day_str = day.strftime("%Y%m%d")
        data = load_lianban_history(day_str)
        if data.get("lianban_3plus") or data.get("lianban_2"):
            l3 = len(data.get("lianban_3plus", []))
            l2 = len(data.get("lianban_2", []))
            l1 = len(data.get("lianban_1", []))
            print(f"  {day_str}: 4板+{l3}只 | 2板{l2}只 | 首板{l1}只")
            if l3 > 0:
                names = ",".join(s["name"] for s in data["lianban_3plus"])
                print(f"    龙头: {names}")

if __name__ == "__main__":
    main()
