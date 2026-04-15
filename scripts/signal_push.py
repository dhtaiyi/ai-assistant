#!/usr/bin/env python3
"""信号推送调度器 v1.0

统一管理所有推送逻辑：
1. 定时任务调度（每分钟检查信号）
2. 协调 signal_priority / breakeven_tracker / stop_loss_advisor
3. 调用飞书发送消息
4. 防重复推送（cooldown 机制）

用法（通常由 cron 调用）：
  python3 signal_push.py --mode monitor       # 实时监控模式（守护进程）
  python3 signal_push.py --mode morning       # 早盘推送（9:25/9:30/9:35）
  python3 signal_push.py --mode midday         # 午盘推送（11:25/11:30）
  python3 signal_push.py --mode afternoon      # 尾盘推送（14:50/14:55）
  python3 signal_push.py --mode evening        # 收盘总结（15:30）
  python3 signal_push.py --mode p0             # 立即P0推送（紧急信号）
  python3 signal_push.py --mode p2             # 手动P2汇总
  python3 signal_push.py --mode full           # 全套分析推送
"""

import json
import os
import re
import sys
import time
import signal
import requests
import threading
from datetime import datetime, time as dtime
from pathlib import Path

# ─── 配置 ────────────────────────────────────────────────────────────────────
WORKSPACE   = Path("/home/dhtaiyi/.openclaw/workspace")
SCRIPTS_DIR = WORKSPACE / "scripts"
STATE_DIR   = WORKSPACE / "stock-data"
os.makedirs(STATE_DIR, exist_ok=True)

FEISHU_APP_ID     = "cli_a92923c6a2f99bc0"
FEISHU_APP_SECRET = "H4CdLHf1NwM1iv3JWzBsfdFFUY8bO4At"
FEISHU_USER_ID    = "ou_04add8ebe219f09799570c70e3cdc732"

# 推送时间表
PUSH_SCHEDULE = {
    "morning":    ["09:25", "09:30", "09:35", "09:40", "09:50"],
    "midday":     ["11:25", "11:28"],
    "afternoon":   ["14:50", "14:55"],
    "evening":    ["15:30"],
}

# Cooldown：同一标的同一类型推送的最小间隔（秒）
COOLDOWN_FILE = f"{STATE_DIR}/push_cooldown.json"

# ─── 飞书 API ────────────────────────────────────────────────────────────────
_token_cache = None
_token_expire = 0

def get_feishu_token() -> str:
    global _token_cache, _token_expire
    now = time.time()
    if _token_cache and now < _token_expire - 60:
        return _token_cache
    try:
        r = requests.post(
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET},
            timeout=5
        )
        data = r.json()
        _token_cache = data.get("tenant_access_token", "")
        _token_expire = now + data.get("expire", 7200)
        return _token_cache
    except Exception as e:
        print(f"[feishu] token获取失败: {e}")
        return ""

def send_feishu_text(text: str, user_id: str = None) -> bool:
    token = get_feishu_token()
    if not token:
        return False
    try:
        r = requests.post(
            "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={
                "receive_id": user_id or FEISHU_USER_ID,
                "msg_type": "text",
                "content": json.dumps({"text": text})
            },
            timeout=10
        )
        return r.status_code in (200, 201)
    except Exception as e:
        print(f"[feishu] 发送失败: {e}")
        return False

def send_feishu_card(title: str, fields: list, user_id: str = None) -> bool:
    """发送卡片消息"""
    token = get_feishu_token()
    if not token:
        return False
    elements = [{"tag": "markdown", "content": f"**{title}**\n"}]
    for f in fields:
        elements.append({"tag": "markdown", "content": f"- **{f['label']}**: {f['value']}"})

    payload = {
        "receive_id": user_id or FEISHU_USER_ID,
        "msg_type": "interactive",
        "content": json.dumps({
            "elements": elements,
            "header": {"title": {"tag": "plain_text", "content": title}, "template": "red"}
        })
    }
    try:
        r = requests.post(
            "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json=payload, timeout=10
        )
        return r.status_code in (200, 201)
    except Exception as e:
        print(f"[feishu] 卡片发送失败: {e}")
        return False

# ─── Cooldown 管理 ────────────────────────────────────────────────────────────
def load_cooldown() -> dict:
    if os.path.exists(COOLDOWN_FILE):
        try:
            with open(COOLDOWN_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {"_last_cleanup": 0}

def save_cooldown(data: dict):
    try:
        with open(COOLDOWN_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        pass

def can_push(key: str, min_interval: int = 300) -> bool:
    """检查是否可以推送（防重复）"""
    data = load_cooldown()
    now  = time.time()
    # 每小时清理一次过期条目
    if now - data.get("_last_cleanup", 0) > 3600:
        cleaned = {k: v for k, v in data.items()
                   if k != "_last_cleanup" and now - v < min_interval}
        cleaned["_last_cleanup"] = now
        data = cleaned
        save_cooldown(data)

    last = data.get(key, 0)
    if now - last < min_interval:
        return False
    data[key] = now
    save_cooldown(data)
    return True

# ─── 子模块调用 ──────────────────────────────────────────────────────────────
def run_signal_priority(force_p2: bool = False) -> dict:
    """运行信号分级检查"""
    sys.path.insert(0, str(SCRIPTS_DIR))
    try:
        from signal_priority import check_signals
        # 从监控列表读取
        watch_path = STATE_DIR / "watch_stocks.json"
        stocks = []
        if watch_path.exists():
            stocks = json.loads(watch_path.read_text())
        if not stocks:
            # 默认监控池
            stocks = [
                {"code": "000586", "name": "汇源通信"},
                {"code": "002491", "name": "通鼎互联"},
                {"code": "600594", "name": "益佰制药"},
                {"code": "600654", "name": "中安科"},
            ]
        return check_signals(stocks, force_push_p2=force_p2)
    except Exception as e:
        print(f"[signal_priority] 运行失败: {e}")
        return {}

def run_stop_loss_check() -> list:
    """运行止损检查"""
    sys.path.insert(0, str(SCRIPTS_DIR))
    try:
        from stop_loss_advisor import track_all, load_positions
        positions = load_positions()
        if not positions:
            return []
        # 这里只收集预警信息，不重复打印
        alerts = []
        for pos in positions:
            try:
                from stop_loss_advisor import track_position
                r = track_position(pos, force=False)
                if r and r.get("urgency", 0) >= 1:
                    alerts.append(r)
            except Exception:
                pass
        return alerts
    except Exception as e:
        print(f"[stop_loss] 运行失败: {e}")
        return []

def run_tomorrow_picker() -> dict:
    """运行明日预选"""
    sys.path.insert(0, str(SCRIPTS_DIR))
    try:
        from tomorrow_picker import analyze_today, get_lianban_evolution, generate_picks
        today_data = analyze_today()
        lianban    = get_lianban_evolution()
        picks      = generate_picks(today_data, lianban)
        return {"today": today_data, "lianban": lianban, "picks": picks}
    except Exception as e:
        print(f"[tomorrow_picker] 运行失败: {e}")
        return {}

# ─── 各时段推送函数 ──────────────────────────────────────────────────────────
def push_morning():
    """早盘推送：竞价、开盘"""
    now = datetime.now()
    print(f"\n[{now.strftime('%H:%M:%S')}] === 早盘推送 ===")

    results = run_signal_priority(force_p2=True)
    p0_list = results.get("p0", [])
    p1_list = results.get("p1", [])
    p2_list = results.get("p2", [])

    # 飞书消息
    lines = [f"🌅 早盘 {now.strftime('%H:%M')} 信号\n"]

    if p0_list:
        lines.append("🚨 P0紧急:")
        for code, name, desc in p0_list:
            lines.append(f"  {name}({code}) {desc}")
    if p1_list:
        lines.append("⚠️ P1重要:")
        for code, name, desc in p1_list[:5]:
            lines.append(f"  {name}({code}) {desc}")
    if p2_list:
        lines.append(f"📊 P2波动({len(p2_list)}只):")
        for code, name, desc in p2_list[:5]:
            lines.append(f"  {name}({code}) {desc}")

    if len(lines) > 1:
        send_feishu_text("\n".join(lines))
        print(f"  ✅ 飞书已推送 ({len(lines)-1}行)")

def push_midday():
    """午盘推送"""
    now = datetime.now()
    print(f"\n[{now.strftime('%H:%M:%S')}] === 午盘推送 ===")

    alerts = run_stop_loss_check()
    lines  = [f"🌤 午盘 {now.strftime('%H:%M')} 持仓状态\n"]

    if alerts:
        lines.append("🚨 持仓预警:")
        for a in alerts:
            lines.append(f"  {a['name']} {a['profit_pct']:+.1f}% → 止损{a['stop_price']:.2f}")
    else:
        lines.append("  持仓暂无预警 ✅")

    if can_push("midday", 1800):
        send_feishu_text("\n".join(lines))
        print(f"  ✅ 飞书已推送")

def push_afternoon():
    """尾盘推送"""
    now = datetime.now()
    print(f"\n[{now.strftime('%H:%M:%S')}] === 尾盘推送 ===")

    # 检查持仓
    alerts = run_stop_loss_check()
    lines  = [f"🌆 尾盘 {now.strftime('%H:%M')} 操作提示\n"]

    if alerts:
        lines.append("🚨 持仓预警:")
        for a in alerts:
            lines.append(f"  {a['name']} {a['profit_pct']:+.1f}% → 止损{a['stop_price']:.2f}")
        lines.append("\n⚠️ 注意尾盘止损！")
    else:
        lines.append("  持仓暂无预警 ✅")

    if can_push("afternoon", 1800):
        send_feishu_text("\n".join(lines))
        print(f"  ✅ 飞书已推送")

def push_evening():
    """收盘总结"""
    now = datetime.now()
    print(f"\n[{now.strftime('%H:%M:%S')}] === 收盘总结 ===")

    data = run_tomorrow_picker()
    picks = data.get("picks", {})
    today = data.get("today", {})

    lines = [f"🌙 收盘总结 {now.strftime('%Y-%m-%d %H:%M')}\n"]
    lines.append(f"涨停: {picks.get('zt_count', '?')}只")
    lines.append(f"情绪: {picks.get('emotion', '?')}")
    lines.append(f"仓位: {picks.get('position', '?')}")
    lines.append(f"策略: {picks.get('strategy', '?')}")

    sectors = picks.get("main_sectors", [])
    if sectors:
        lines.append(f"主线: {', '.join(sectors)}")

    # 持仓状态
    alerts = run_stop_loss_check()
    if alerts:
        lines.append(f"\n🚨 持仓预警({len(alerts)}只):")
        for a in alerts:
            lines.append(f"  {a['name']} {a['profit_pct']:+.1f}%")

    send_feishu_text("\n".join(lines))
    print(f"  ✅ 收盘总结已推送")

def push_full():
    """全套分析推送"""
    now = datetime.now()
    print(f"\n[{now.strftime('%H:%M:%S')}] === 全套分析 ===")

    # 1. 信号检查
    sig_result = run_signal_priority(force_p2=True)
    # 2. 止损检查
    alerts = run_stop_loss_check()
    # 3. 明日预选
    picker = run_tomorrow_picker()

    lines = [f"📊 全套分析 {now.strftime('%H:%M')}\n"]

    # 紧急信号
    p0 = sig_result.get("p0", [])
    if p0:
        lines.append("🚨 P0紧急:")
        for code, name, desc in p0:
            lines.append(f"  {name} {desc}")

    # 持仓预警
    if alerts:
        lines.append("\n🚨 持仓预警:")
        for a in alerts:
            lines.append(f"  {a['name']} {a['profit_pct']:+.1f}% → {a['stop_price']:.2f}")

    # 市场情绪
    picks = picker.get("picks", {})
    lines.append(f"\n市场: {picks.get('emotion','?')} | {picks.get('zt_count','?')}只涨停")
    lines.append(f"主线: {', '.join(picks.get('main_sectors', [])[:3])}")

    send_feishu_text("\n".join(lines))

# ─── 实时监控模式（守护进程）─────────────────────────────────────────────────
_run = True

def signal_handler(sig, frame):
    global _run
    print("\n[signal_push] 收到停止信号，退出监控...")
    _run = False

def run_monitor(interval: int = 60):
    """实时监控模式：每 interval 秒检查一次信号"""
    global _run
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print(f"\n{'='*55}")
    print(f"📡 信号监控模式启动 | 间隔 {interval}秒")
    print(f"{'='*55}")
    last_market_check = 0
    last_p2_check     = 0

    while _run:
        now = datetime.now()
        now_ts = now.time()

        # 非交易时段（9:30-15:00 之外）降低频率
        market_open = dtime(9, 30) <= now_ts <= dtime(15, 0)
        check_interval = 30 if market_open else 300

        # P0 检查（每分钟）
        if market_open:
            if can_push("monitor_p0", 60):
                result = run_signal_priority(force_p2=False)
                p0 = result.get("p0", [])
                if p0:
                    msg = f"🚨 P0紧急信号 {now.strftime('%H:%M')}\n"
                    for code, name, desc in p0:
                        msg += f"{name}({code}) {desc}\n"
                    send_feishu_text(msg)
                    print(f"  🚨 P0推送: {[x[1] for x in p0]}")

        # P2 每30分钟汇总
        if market_open and time.time() - last_p2_check > 1800:
            if can_push("monitor_p2", 1800):
                result = run_signal_priority(force_p2=True)
                p2 = result.get("p2", [])
                if p2:
                    msg = f"📊 信号汇总 {now.strftime('%H:%M')}\n"
                    for code, name, desc in p2[:10]:
                        msg += f"{name} {desc}\n"
                    if len(p2) > 10:
                        msg += f"...共{len(p2)}只\n"
                    send_feishu_text(msg)
                last_p2_check = time.time()

        # 止损检查（每5分钟）
        if market_open and time.time() - last_market_check > 300:
            if can_push("monitor_stop", 300):
                alerts = run_stop_loss_check()
                if alerts:
                    msg = f"🚨 持仓预警 {now.strftime('%H:%M')}\n"
                    for a in alerts:
                        msg += f"{a['name']} {a['profit_pct']:+.1f}% → 止损{a['stop_price']:.2f}\n"
                    send_feishu_text(msg)
            last_market_check = time.time()

        time.sleep(interval)

    print("[signal_push] 监控已停止")

# ─── 主入口 ──────────────────────────────────────────────────────────────────
def main():
    mode = "monitor"
    if len(sys.argv) > 1:
        mode = sys.argv[1].replace("--", "").replace("-", "_")
        if mode not in dir():
            mode_map = {
                "monitor":   run_monitor,
                "morning":   push_morning,
                "midday":    push_midday,
                "afternoon": push_afternoon,
                "evening":   push_evening,
                "full":      push_full,
                "p0":        lambda: run_signal_priority(force_p2=False),
                "p2":        lambda: run_signal_priority(force_p2=True),
            }
            if mode in mode_map:
                mode = mode_map[mode]
            else:
                print(f"未知模式: {mode}")
                print(__doc__)
                return

    if callable(mode):
        mode()
    else:
        print(f"未知模式: {mode}")

if __name__ == "__main__":
    main()
