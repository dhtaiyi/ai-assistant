#!/usr/bin/env python3
"""明日预选工具 v2.0

基于今日数据生成明日重点标的：
- 今日涨停股池分析（按板块/成交额）
- 首板筛选（明日二板机会）
- 连板股处理（晋级/掉队判断）
- 主线板块识别
- 操作计划输出

用法：
  python3 tomorrow_picker.py
  python3 tomorrow_picker.py --date 20260415
"""

import json
import os
import re
import sys
import requests
from datetime import datetime, timedelta, date
from pathlib import Path

# ─── 配置 ────────────────────────────────────────────────────────────────────
HEADERS    = {"User-Agent": "Mozilla/5.0", "Referer": "https://finance.sina.com.cn"}
HIST_DIR   = Path("/home/dhtaiyi/.openclaw/workspace/stock-data/candidates")
os.makedirs(HIST_DIR, exist_ok=True)

# ─── 数据获取 ────────────────────────────────────────────────────────────────
def get_zt_stocks(n: int = 100) -> list[dict]:
    """获取今日涨停股（非ST非新股）"""
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
        print(f"[tomorrow_picker] 涨停数据获取失败: {e}")
        return []

def get_market_stats() -> dict:
    """获取市场整体数据"""
    stats = {"total": 0, "zt_count": 0, "up_count": 0,
             "pct_change": 0, "amount": 0}
    try:
        url = "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeDataSimple"
        params = {"page": 1, "num": 5, "sort": "changepercent", "asc": 0,
                  "node": "hs_a", "_s_r_a": "page"}
        r = requests.get(url, params=params, headers=HEADERS, timeout=10)
        data = r.json()
        if data:
            stats["pct_change"] = float(data[0].get("changepercent", 0))
    except Exception:
        pass
    # 从涨停数据推断
    zt = get_zt_stocks()
    stats["zt_count"] = len(zt)
    stats["up_count"] = len([s for s in zt if float(s.get("changepercent", 0)) > 0])
    total_amount = sum(float(s.get("amount", 0)) for s in zt)
    stats["amount"] = total_amount / 1e8
    return stats

def load_yesterday_zt(date_str: str) -> list[dict]:
    """加载昨日涨停股"""
    path = HIST_DIR / f"{date_str}.json"
    if path.exists():
        try:
            with open(path) as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_today_zt(stocks: list[dict], date_str: str):
    path = HIST_DIR / f"{date_str}.json"
    with open(path, "w") as f:
        json.dump(stocks, f, ensure_ascii=False, indent=2)

# ─── 板块映射 ────────────────────────────────────────────────────────────────
# 动态识别：基于涨停股名称关键词 + 成交额排序
SECTOR_KEYWORDS = {
    "光纤光通信": ["光迅", "长飞", "特发", "光智", "汇源", "通鼎", "长江通信", "永鼎", "中际旭创", "天孚", "新易盛", "博创"],
    "AI算力":    ["算力", "浪潮", "寒武纪", "光模块", "CPO", "IDC", "铜缆", "华为"],
    "机器人":    ["机器人", "减速器", "伺服", "电机", "灵巧", "工业母机"],
    "创新药":    ["医药", "制药", "生物", "疫苗", "中药", "创新药", "AACR"],
    "汽车零部件":["汽车", "零部件", "新能源车", "锂电", "固态电池"],
    "化工":      ["化工", "染料", "钛白粉", "氟化工", "磷化工"],
    "并购重组":  ["重组", "并购", "收购", "借壳"],
    "消费电子":  ["苹果", "果链", "折叠屏", "OLED", "PCB"],
    "军工":      ["军工", "卫星", "航天", "航空", "船舶"],
}

def guess_sector(name: str) -> str:
    for sector, kws in SECTOR_KEYWORDS.items():
        for kw in kws:
            if kw in name:
                return sector
    return "其他"

# ─── 核心分析 ────────────────────────────────────────────────────────────────
def analyze_today() -> dict:
    """分析今日数据，返回结构化结果"""
    zt = get_zt_stocks()

    # 基本统计
    total_amount = sum(float(s.get("amount", 0)) for s in zt) / 1e8
    market_stats = get_market_stats()

    # 板块分析
    sector_map: dict[str, list] = {}
    for s in zt:
        name = s["name"]
        code = s["symbol"]
        pct  = float(s.get("changepercent", 0))
        amt  = float(s.get("amount", 0)) / 1e8
        sec  = guess_sector(name)
        if sec not in sector_map:
            sector_map[sec] = []
        sector_map[sec].append({
            "name": name, "code": _norm_code(code),
            "pct": pct, "amount": amt,
        })

    # 按成交额排序板块
    sectors = sorted(
        sector_map.items(),
        key=lambda x: sum(st["amount"] for st in x[1]),
        reverse=True,
    )

    # 强势首板（成交额大、位置低）
    first_board = []
    high_board  = []  # 4板+
    candidates  = []  # 明日重点

    for s in zt:
        code = _norm_code(s["symbol"])
        name = s["name"]
        amt  = float(s.get("amount", 0)) / 1e8
        pct  = float(s.get("changepercent", 0))
        # 首板条件：成交>5000万，涨幅接近10%（非高位）
        if amt > 0.5 and pct > 9.5 and pct < 10.2:
            first_board.append({"name": name, "code": code,
                                 "pct": pct, "amount": amt})
        elif pct > 9.5:
            candidates.append({"name": name, "code": code,
                                 "pct": pct, "amount": amt})

    first_board.sort(key=lambda x: x["amount"], reverse=True)
    candidates.sort(key=lambda x: x["amount"], reverse=True)

    return {
        "zt_count":   len(zt),
        "total_amount": total_amount,
        "sectors":    sectors,
        "first_board": first_board,
        "candidates":  candidates,
        "market":      market_stats,
    }

def _norm_code(symbol: str) -> str:
    """统一代码格式为6位"""
    return symbol.replace("sz", "").replace("sh", "")

# ─── 昨日连板追踪 ────────────────────────────────────────────────────────────
def get_lianban_evolution() -> dict:
    """获取昨日涨停股今日表现（连板晋级/掉队）"""
    today     = datetime.now()
    yesterday = today - timedelta(days=1 if today.weekday() != 0 else 3)
    y_str     = yesterday.strftime("%Y%m%d")
    y_zt      = load_yesterday_zt(y_str)

    if not y_zt:
        return {}

    codes = [s["code"] for s in y_zt if _norm_code(s.get("symbol", s.get("code", "")))]
    full_codes = ",".join(
        ("sz" + c) if not c.startswith("sz") and not c.startswith("sh")
        else c
        for c in codes
    )

    try:
        r = requests.get(f"http://qt.gtimg.cn/q={full_codes}", timeout=10)
        r.encoding = "gbk"
    except Exception:
        return {}

    # 解析
    lianban_2, lianban_3plus, broke, faded = [], [], [], []
    for line in r.text.strip().split("\n"):
        if '"' not in line:
            continue
        m = re.search(r'=\s*"([^"]+)"', line)
        if not m:
            continue
        parts = m.group(1).split("~")
        if len(parts) < 34:
            continue
        try:
            name  = parts[1]
            price = float(parts[3])  if parts[3]  else 0
            prev  = float(parts[4])  if parts[4]  else 0
            high  = float(parts[33]) if parts[33] else 0
            pct   = (price - prev) / prev * 100 if prev > 0 else 0
            code  = _norm_code(line.split("=")[0].replace("v_", ""))

            ever_limitup = (high >= prev * 1.099) if prev > 0 else False

            # 找昨日涨停信息
            y_info = next((s for s in y_zt
                           if _norm_code(s.get("symbol", s.get("code", ""))) == code), {})
            y_pct  = y_info.get("pct", 0) if y_info else 0

            if pct >= 9.5:
                if y_pct >= 9.5:
                    lianban_3plus.append({"name": name, "code": code, "pct": pct})
                else:
                    lianban_2.append({"name": name, "code": code, "pct": pct})
            elif ever_limitup and pct < 9.5:
                broke.append({"name": name, "code": code, "pct": pct,
                              "high_pct": (high/prev-1)*100 if prev > 0 else 0})
            elif 5 <= pct < 9.5:
                faded.append({"name": name, "code": code, "pct": pct})
        except Exception:
            continue

    return {
        "lianban_3plus": lianban_3plus,
        "lianban_2":     lianban_2,
        "broke":         broke,
        "faded":         faded,
    }

# ─── 明日预选 ────────────────────────────────────────────────────────────────
def generate_picks(today_data: dict, lianban: dict) -> dict:
    """生成明日操作计划"""
    zt_count  = today_data["zt_count"]
    sectors   = today_data["sectors"]
    first_bd  = today_data["first_board"]

    # 情绪判断
    if zt_count >= 80:
        emotion = "🔥 上升期（高潮）"
        position = "40-60%"
        strategy = "聚焦龙头，不恐高"
    elif zt_count >= 50:
        emotion = "📈 上升期"
        position = "30-50%"
        strategy = "主线首板二板，稳健操作"
    elif zt_count >= 30:
        emotion = "⚠️ 混沌期"
        position = "20-30%"
        strategy = "控制仓位，聚焦主线最强首板"
    else:
        emotion = "❄️ 退潮期"
        position = "10-20%"
        strategy = "多看少动，等待情绪修复"

    # 风险标（高位连板，明日回避）
    risk_stocks = []
    if lianban.get("lianban_3plus"):
        risk_stocks.extend(lianban["lianban_3plus"])

    # 重点关注（首板二板）
    watch_stocks = []
    for s in first_bd[:8]:
        if s not in risk_stocks:
            watch_stocks.append(s)
    if lianban.get("lianban_2"):
        watch_stocks.extend(lianban["lianban_2"][:3])

    return {
        "emotion":      emotion,
        "zt_count":     zt_count,
        "position":     position,
        "strategy":     strategy,
        "main_sectors": [s[0] for s in sectors[:3]],
        "watch_stocks": watch_stocks,
        "risk_stocks":  risk_stocks,
    }

# ─── 输出格式化 ──────────────────────────────────────────────────────────────
def print_report(today_data: dict, picks: dict, lianban: dict):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"\n{'='*60}")
    print(f"📋 明日预选报告 v2.0 | {now}")
    print(f"{'='*60}")

    # ── 今日概况 ──────────────────────────────────────────────────────────
    print(f"\n【今日概况】")
    print(f"  涨停: {picks['zt_count']}只  总成交: {today_data['total_amount']:.0f}亿")
    print(f"  情绪: {picks['emotion']}")

    # ── 主线板块 ──────────────────────────────────────────────────────────
    print(f"\n【主线板块】(按成交额排序)")
    for i, (sec, stocks) in enumerate(today_data["sectors"][:4], 1):
        total = sum(s["amount"] for s in stocks)
        names = ",".join(s["name"] for s in stocks[:3])
        print(f"  {i}. {sec}  {total:.0f}亿 ({len(stocks)}只)")
        print(f"     {names}")

    # ── 昨日连板追踪 ─────────────────────────────────────────────────────
    if lianban:
        if lianban.get("lianban_3plus"):
            print(f"\n【3板+龙头】")
            for s in lianban["lianban_3plus"]:
                print(f"  👑 {s['name']}({s['code']}) +{s['pct']:.1f}%")
        if lianban.get("lianban_2"):
            print(f"\n【2板确认】明日关注3板机会")
            for s in lianban["lianban_2"]:
                print(f"  ✅ {s['name']}({s['code']}) +{s['pct']:.1f}%")
        if lianban.get("broke"):
            print(f"\n【炸板预警】")
            for s in lianban["broke"]:
                print(f"  💥 {s['name']}({s['code']}) {s['pct']:+.1f}%")

    # ── 明日首板关注 ──────────────────────────────────────────────────────
    print(f"\n【明日首板关注】(成交额排序)")
    for s in today_data["first_board"][:8]:
        print(f"  📈 {s['name']}({s['code']}) 成交{s['amount']:.1f}亿")

    # ── 操作计划 ──────────────────────────────────────────────────────────
    print(f"\n{'─'*60}")
    print(f"【操作计划】")
    print(f"  仓位:   {picks['position']}")
    print(f"  策略:   {picks['strategy']}")
    print(f"  买入:   10:30前成交>5000万的率先涨停股")
    print(f"  止损:   -7%无条件出")
    print(f"  禁止:   涨停<30家时不追连板")

    if picks["risk_stocks"]:
        print(f"\n【明日回避】")
        for s in picks["risk_stocks"]:
            print(f"  🚫 {s.get('name','?')}({s.get('code','?')}) 3板+高位风险")

    print(f"\n{'='*60}")
    print("⚠️ 以上仅为小小雨的分析，不构成投资建议，股市有风险！")
    print(f"{'='*60}\n")

# ─── 主函数 ──────────────────────────────────────────────────────────────────
def main():
    target_date = None
    if "--date" in sys.argv:
        idx = sys.argv.index("--date")
        target_date = sys.argv[idx + 1]
    else:
        target_date = datetime.now().strftime("%Y%m%d")

    # 分析今日
    today_data = analyze_today()
    # 保存今日涨停股
    save_today_zt(today_data["candidates"], target_date)

    # 昨日连板追踪
    lianban = get_lianban_evolution()

    # 生成明日预选
    picks = generate_picks(today_data, lianban)

    # 输出报告
    print_report(today_data, picks, lianban)

    # 保存结果
    result = {
        "date":     target_date,
        "analyzed": datetime.now().isoformat(),
        "today":    today_data,
        "lianban":  lianban,
        "picks":    picks,
    }
    out_path = HIST_DIR / f"tomorrow_{target_date}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"📁 报告已保存: {out_path}")

if __name__ == "__main__":
    main()
