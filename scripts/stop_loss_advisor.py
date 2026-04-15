#!/usr/bin/env python3
"""动态止损顾问 v1.0

功能：
1. 买前计算止损价（ATR / 固定比例 / 支撑位）
2. 买后跟踪止损提示（移动止损 + 预警）
3. 配合 signal_priority.py 使用

用法：
  # 买前：计算止损
  python3 stop_loss_advisor.py --calc --price 10.5 --name "某股票"

  # 买后：跟踪止损
  python3 stop_loss_advisor.py --track --code 000586 --cost 9.8 --shares 10000

  # 自动模式（从持仓文件读取）
  python3 stop_loss_advisor.py --auto
"""

import json
import os
import sys
import re
import requests
from datetime import datetime
from pathlib import Path

STATE_DIR  = "/home/dhtaiyi/.openclaw/workspace/stock-data/positions"
HIST_DIR   = "/home/dhtaiyi/.openclaw/workspace/stock-data/hist"
os.makedirs(STATE_DIR, exist_ok=True)
os.makedirs(HIST_DIR,  exist_ok=True)

POS_FILE = f"{STATE_DIR}/positions.json"
HIST_FILE = f"{STATE_DIR}/stop_loss_history.json"

# ─── 止损方法 ────────────────────────────────────────────────────────────────
class StopLossAdvisor:
    """动态止损计算器"""

    @staticmethod
    def calc_atr(price: float, atr_pct: float = 0.06) -> dict:
        """
        ATR百分比止损
        atr_pct: ATR占成本的百分比，默认6%（激进3-5%，保守7-10%）
        返回止损价、止盈价、风险额
        """
        stop   = round(price * (1 - atr_pct), 2)
        target = round(price * (1 + atr_pct * 2), 2)  # 1:2盈亏比
        risk   = round(price - stop, 2)
        return {
            "method":     "ATR",
            "buy_price":  price,
            "stop_price": stop,
            "target_1":   round(price * (1 + atr_pct), 2),
            "target_2":   target,
            "riskAmt":    risk,
            "rewardAmt":  round(target - price, 2),
            "ratio":      "1:2",
            "pct":        f"-{atr_pct*100:.0f}%",
        }

    @staticmethod
    def calc_fixed(price: float, loss_pct: float = 0.07) -> dict:
        """固定比例止损"""
        stop = round(price * (1 - loss_pct), 2)
        return {
            "method":     "固定比例",
            "buy_price":  price,
            "stop_price": stop,
            "target_1":   round(price * (1 + loss_pct), 2),
            "target_2":   round(price * (1 + loss_pct * 2), 2),
            "riskAmt":    round(price * loss_pct, 2),
            "rewardAmt":  round(price * loss_pct * 2, 2),
            "ratio":      "1:2",
            "pct":        f"-{loss_pct*100:.0f}%",
        }

    @staticmethod
    def calc_support(price: float, support: float, risk_pct: float = 0.05) -> dict:
        """支撑位止损（更保守）"""
        stop = round(support, 2)
        riskAmt = round(price - stop, 2)
        return {
            "method":     "支撑位",
            "buy_price":  price,
            "stop_price": stop,
            "support":    support,
            "target_1":   round(support * (1 + risk_pct), 2),
            "target_2":   round(price * (1 + risk_pct * 2), 2),
            "riskAmt":    riskAmt,
            "rewardAmt":  round(support * risk_pct * 2, 2),
            "ratio":      "1:2",
            "pct":        f"-{riskAmt/price*100:.1f}%",
        }

    @staticmethod
    def calc_trailing(stop_price: float, current: float,
                      peak_price: float, mode: str = "hard") -> dict:
        """
        移动止损计算
        mode: hard(固定) / soft(跟随)
        - 股价创新高，上移止损
        - 股价回落触及止损，触发
        """
        if mode == "hard":
            # 经典移动止损：止损价随最高价上移，保持固定距离
            trail_pct = 0.07
            new_stop = round(peak_price * (1 - trail_pct), 2)
        else:
            # 软止损：只上移不下降
            new_stop = max(stop_price, round(peak_price * 0.93, 2))

        triggered = current <= stop_price
        return {
            "mode":       mode,
            "current":    current,
            "peak_price": peak_price,
            "stop_price": stop_price,
            "new_stop":   new_stop,
            "triggered":  triggered,
            "safe":       current >= stop_price * 1.02,  # 距离止损2%以上安全
        }

    @staticmethod
    def print_analysis(result: dict, name: str = "", code: str = ""):
        """打印分析结果"""
        m = result["method"]
        print(f"\n{'='*50}")
        print(f"止损分析 | {name}({code})")
        print(f"{'='*50}")
        print(f"  方法:       {m}")
        print(f"  买入价:     {result['buy_price']:.3f}")
        print(f"  止损价:     {result['stop_price']:.2f}  {result['pct']}")
        print(f"  一档目标:   {result['target_1']:.2f}  (+{result['riskAmt']:.2f})")
        print(f"  二档目标:   {result['target_2']:.2f}  (+{result['rewardAmt']:.2f})")
        print(f"  每手风险:  {result['riskAmt']:.2f}元  盈亏比 {result['ratio']}")
        if "support" in result:
            print(f"  参考支撑:   {result['support']:.2f}")

# ─── 持仓管理 ────────────────────────────────────────────────────────────────
def load_positions() -> list:
    if os.path.exists(POS_FILE):
        try:
            with open(POS_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_positions(positions: list):
    with open(POS_FILE, "w") as f:
        json.dump(positions, f, ensure_ascii=False, indent=2)

def add_position(code: str, name: str, cost: float, shares: int, buy_date: str = None):
    """添加持仓"""
    positions = load_positions()
    # 去除重复
    positions = [p for p in positions if p["code"] != code]
    positions.append({
        "code":      code,
        "name":      name,
        "cost":      cost,
        "shares":    shares,
        "buy_date":  buy_date or datetime.now().strftime("%Y-%m-%d"),
        "added_at":  datetime.now().isoformat(),
    })
    save_positions(positions)
    print(f"✅ 已添加持仓: {name}({code}) 成本{cost} x {shares}股")

def remove_position(code: str):
    positions = [p for p in load_positions() if p["code"] != code]
    save_positions(positions)
    print(f"🗑️ 已移除持仓: {code}")

# ─── 历史记录 ────────────────────────────────────────────────────────────────
def log_stop_event(code: str, name: str, action: str, price: float, reason: str):
    """记录止损事件"""
    if not os.path.exists(HIST_FILE):
        data = []
    else:
        try:
            with open(HIST_FILE) as f:
                data = json.load(f)
        except Exception:
            data = []
    data.append({
        "ts":     datetime.now().isoformat(),
        "code":   code,
        "name":   name,
        "action": action,  # buy/stop/trarget1/target2/sell
        "price":  price,
        "reason": reason,
    })
    with open(HIST_FILE, "w") as f:
        json.dump(data[-200:], f, ensure_ascii=False, indent=2)

# ─── 实时数据 ────────────────────────────────────────────────────────────────
def get_realtime(code: str) -> dict:
    """获取单只股票实时数据"""
    if not code.startswith("sz") and not code.startswith("sh"):
        code = ("sz" + code) if code[0] in "03" else ("sh" + code)
    try:
        r = requests.get(f"http://qt.gtimg.cn/q={code}", timeout=8)
        r.encoding = "gbk"
        parts = re.search(r'"([^"]+)"', r.text)
        if not parts:
            return {}
        p = parts.group(1).split("~")
        if len(p) < 10:
            return {}
        price = float(p[3])  if p[3]  else 0
        prev  = float(p[4])  if p[4]  else 0
        high  = float(p[33]) if p[33] else 0
        low   = float(p[34]) if p[34] else 0
        return {
            "name":   p[1],
            "price":  price,
            "prev":   prev,
            "high":   high,
            "low":    low,
            "pct":    (price - prev) / prev * 100 if prev > 0 else 0,
        }
    except Exception:
        return {}

# ─── 跟踪模式 ────────────────────────────────────────────────────────────────
def track_position(pos: dict, force: bool = False):
    """跟踪单只持仓，输出止损建议"""
    code  = pos["code"]
    name  = pos.get("name", code)
    cost  = pos["cost"]
    shares = pos["shares"]
    data  = get_realtime(code)
    price = data.get("price", 0)
    high  = data.get("high", price)
    pct   = data.get("pct", 0)
    peak  = pos.get("peak_price", cost)  # 持仓期最高价

    if price == 0:
        print(f"[{name}] 无法获取实时数据")
        return

    # 更新持仓期峰值
    if high > peak:
        peak = high

    # 计算当前浮动盈亏
    profit_pct  = (price - cost) / cost * 100
    profit_amt  = (price - cost) * shares
    riskAmt     = (cost * 0.07) * shares  # 默认7%止损

    # 移动止损
    trail = StopLossAdvisor.calc_trailing(
        stop_price=pos.get("stop_price", round(cost * 0.93, 2)),
        current=price,
        peak_price=peak,
        mode="soft",
    )
    new_stop = trail["new_stop"]

    # 判断是否触发止损
    status = "🟢 正常"
    urgency = 0
    if trail["triggered"]:
        status = "🔴 触发止损！"
        urgency = 2
    elif price < cost * 0.95:
        status = "🟡 预警"
        urgency = 1
    elif price < cost * 0.93:
        status = "🟠 危险！"
        urgency = 2
    elif profit_pct > 15:
        status = "💰 大幅盈利，上移止损"

    print(f"\n{'─'*45}")
    print(f"📊 {name}({code}) 持仓跟踪")
    print(f"{'─'*45}")
    print(f"  成本:     {cost:.3f}  当前: {price:.3f}  {pct:+.2f}%")
    print(f"  持仓盈亏: {profit_pct:+.2f}%  {profit_amt:+,.0f}元")
    print(f"  持仓峰值: {peak:.3f}")
    print(f"  ─────────────────────")
    print(f"  移动止损: {trail['stop_price']:.2f} → {new_stop:.2f}")
    print(f"  状态: {status}")
    print(f"  安全边际: {'✅ 安全' if trail['safe'] else '⚠️ 接近止损'}")

    # 记录止损更新
    if new_stop != trail["stop_price"]:
        log_stop_event(code, name, "trailing_update", new_stop, f"peak={peak}")

    return {
        "code": code, "name": name,
        "price": price, "pct": pct,
        "profit_pct": profit_pct, "profit_amt": profit_amt,
        "stop_price": new_stop,
        "triggered": trail["triggered"],
        "urgency": urgency,
        "status": status,
    }

# ─── 批量跟踪 ────────────────────────────────────────────────────────────────
def track_all(force: bool = False):
    """跟踪所有持仓"""
    positions = load_positions()
    if not positions:
        print("📭 当前无持仓记录")
        print("   添加持仓: python3 stop_loss_advisor.py --add 000586 汇源通信 9.8 10000")
        return

    print(f"\n{'='*55}")
    print(f"📊 持仓跟踪 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*55}")

    alerts = []
    for pos in positions:
        r = track_position(pos, force=force)
        if r and r["urgency"] >= 1:
            alerts.append(r)

    if alerts:
        print(f"\n{'='*55}")
        print(f"🚨 需要关注的持仓 ({len(alerts)}只):")
        for a in alerts:
            print(f"  {a['status']} {a['name']} {a['profit_pct']:+.1f}% → 建议止损{a['stop_price']:.2f}")

        # 飞书通知
        _notify_alerts(alerts)

def _notify_alerts(alerts: list):
    """发送飞书预警"""
    lines = [f"🚨 持仓预警 {datetime.now().strftime('%H:%M')}\n"]
    for a in alerts:
        lines.append(f"{a['status']} {a['name']}\n"
                     f"  盈亏: {a['profit_pct']:+.1f}%  建议止损: {a['stop_price']:.2f}\n")
    try:
        from signal_priority import send_feishu
        send_feishu("\n".join(lines))
    except Exception:
        pass

# ─── CLI ─────────────────────────────────────────────────────────────────────
def main():
    args = sys.argv[1:]

    if "--calc" in args or "-c" in args:
        # 买前计算
        price = float(sys.argv[sys.argv.index("--calc")+1]) if "--calc" in args \
            else float(sys.argv[sys.argv.index("-c")+1])
        name  = "股票"
        code  = "?"
        for i, a in enumerate(args):
            if a in ("--name", "-n"):
                name = args[i+1]
            if a in ("--code", "--"):
                code = args[i+1]

        print(f"\n📊 买前止损计算 | {name} 买入价 {price}")
        r1 = StopLossAdvisor.calc_fixed(price, 0.07)
        r2 = StopLossAdvisor.calc_atr(price, 0.06)
        StopLossAdvisor.print_analysis(r1, name, code)
        StopLossAdvisor.print_analysis(r2, name, code)
        print(f"\n💡 建议: 激进型用ATR({price*0.94:.2f})，保守型用固定7%({price*0.93:.2f})")

    elif "--track" in args:
        idx  = args.index("--track")
        code = args[idx+1]
        cost = float(args[idx+2])
        shares = int(args[idx+3])
        data = get_realtime(code)
        name = data.get("name", code)
        pos  = {"code": code, "name": name, "cost": cost, "shares": shares,
                "stop_price": round(cost * 0.93, 2), "peak_price": cost}
        track_position(pos)

    elif "--add" in args:
        idx    = args.index("--add")
        code   = args[idx+1]
        name   = args[idx+2]
        cost   = float(args[idx+3])
        shares = int(args[idx+4])
        add_position(code, name, cost, shares)

    elif "--remove" in args:
        code = args[args.index("--remove")+1]
        remove_position(code)

    elif "--auto" in args or "--all" in args:
        track_all(force="--force" in args)

    elif "--list" in args:
        positions = load_positions()
        if not positions:
            print("📭 无持仓记录")
        for p in positions:
            print(f"  {p['name']}({p['code']}) 成本{p['cost']} x {p['shares']}股")

    else:
        print(__doc__)
        print("\n用法示例:")
        print("  python3 stop_loss_advisor.py --calc 10.5 --name 某股")
        print("  python3 stop_loss_advisor.py --add  000586 汇源通信 9.8 10000")
        print("  python3 stop_loss_advisor.py --track 000586 9.8 10000")
        print("  python3 stop_loss_advisor.py --auto")
        print("  python3 stop_loss_advisor.py --list")

if __name__ == "__main__":
    main()
