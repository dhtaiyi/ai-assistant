#!/usr/bin/env python3
"""信号分级推送系统 v1.0

优先级定义：
- P0_紧急：标的涨停/炸板 → 立即推送
- P1_重要：突破关键价位 → 当次检查推送
- P2_常规：每30分钟汇总 → 批量
- P3_静默：无变化 → 不推送

STATE_FILE = "/tmp/signal_state.json"
状态文件格式：
{"stocks": {"code": {"last_price": 0, "last_pct": 0, "last_status": ""}}}
"""

import json
import os
import time
import sys
from datetime import datetime, time as dtime
from pathlib import Path

# ─── 配置 ────────────────────────────────────────────────────────────────────
STATE_FILE = "/tmp/signal_state.json"
P0_IMMEDIATE  = True   # P0立即推送，否则合并到P2
P2_INTERVAL   = 1800  # P2批量汇总间隔(秒)
PUSH_COOLDOWN = 300    # 同一标的同一状态最小推送间隔(秒)

# 飞书推送（由 signal_push.py 统一调用，此处只返回消息结构）
FEISHU_APP_ID    = "cli_a92923c6a2f99bc0"
FEISHU_APP_SECRET = "H4CdLHf1NwM1iv3JWzBsfdFFUY8bO4At"
FEISHU_USER_ID    = "ou_04add8ebe219f09799570c70e3cdc732"

# ─── 状态读写 ────────────────────────────────────────────────────────────────
def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {"stocks": {}, "_meta": {"last_push": {}}}

def save_state(state: dict):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[signal_priority] 状态保存失败: {e}")

# ─── 信号判断 ────────────────────────────────────────────────────────────────
class SignalPriority:
    """信号优先级判断器"""

    @staticmethod
    def judge(code: str, curr: dict, prev: dict) -> tuple[str, str]:
        """
        判断信号优先级和描述
        返回: (priority, description)
        priority: P0/P1/P2/P3
        """
        price    = curr.get("price", 0)
        pct      = curr.get("pct", 0)
        high     = curr.get("high", 0)
        prev_p   = prev.get("last_price", 0)
        prev_pct = prev.get("last_pct", 0)
        prev_st  = prev.get("last_status", "")

        if price == 0 or prev_p == 0:
            return "P3", "数据异常"

        # ── P0: 涨停/炸板 ──────────────────────────────────────────────
        is_limitup     = pct >= 9.85
        was_limitup    = prev_pct >= 9.85
        high_limitup   = (high >= prev_p * 1.099) if prev_p > 0 else False

        # 涨停瞬间
        if is_limitup and not was_limitup:
            return "P0", f"🚀 涨停！+{pct:.1f}%"

        # 炸板（曾经涨停但打开）
        if high_limitup and not is_limitup and pct < 9.5:
            zhaban_pct = pct
            return "P0", f"💥 炸板！{zhaban_pct:+.1f}%（最高+{(high/prev_p-1)*100:.1f}%）"

        # ── P1: 突破关键价位 ───────────────────────────────────────────
        # 突破日内高点 +3%+
        if price > high * 0.997 and prev_pct < 3 < pct and high_limitup:
            return "P1", f"📈 突破前高 {high:.2f}，涨幅{pct:.1f}%"

        # 涨幅骤降预警（从+5%以上快速回落至+2%以下）
        if prev_pct > 5 and pct < 2 and pct > 0:
            return "P1", f"⚠️ 冲高回落预警！{prev_pct:.1f}%→{pct:.1f}%"

        # ── P2: 有变化 ─────────────────────────────────────────────────
        if abs(pct - prev_pct) > 0.5 or abs(price - prev_p) / prev_p > 0.005:
            return "P2", f"波动 {pct:+.1f}% 现价{price:.2f}"

        # ── P3: 无变化 ─────────────────────────────────────────────────
        return "P3", "无变化"

# ─── 飞书推送 ───────────────────────────────────────────────────────────────
def get_feishu_token() -> str:
    """获取飞书 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    data = {"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}
    try:
        import requests
        r = requests.post(url, json=data, timeout=5)
        return r.json().get("tenant_access_token", "")
    except Exception:
        return ""

def send_feishu(text: str, user_id: str = None) -> bool:
    """发送飞书消息"""
    token = get_feishu_token()
    if not token:
        return False
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "receive_id": user_id or FEISHU_USER_ID,
        "msg_type": "text",
        "content": json.dumps({"text": text})
    }
    try:
        import requests
        r = requests.post(
            "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id",
            headers=headers, json=payload, timeout=5
        )
        return r.status_code == 200
    except Exception:
        return False

# ─── 主检查函数（被 signal_push.py 调用）──────────────────────────────────────
def check_signals(stocks: list[dict], force_push_p2: bool = False) -> dict:
    """
    检查一篮子股票的信号
    stocks: [{"code": "000586", "name": "汇源通信", ...}, ...]
    force_push_p2: True = 立即输出P2汇总（定时触发）

    返回:
    {
        "p0": [("code", "name", "desc"), ...],
        "p1": [...],
        "p2": [...],
        "p3_count": N,
    }
    """
    state     = load_state()
    now       = datetime.now()
    p0_list, p1_list, p2_list = [], [], []
    p3_count  = 0

    for st in stocks:
        code  = st.get("code", "")
        name  = st.get("name",  "未知")
        price = st.get("price", 0)
        pct   = st.get("pct",   0)
        high  = st.get("high",  price)

        curr = {"price": price, "pct": pct, "high": high}
        prev = state["stocks"].get(code, {})

        priority, desc = SignalPriority.judge(code, curr, prev)

        # 更新状态
        state["stocks"][code] = {
            "last_price":  price,
            "last_pct":    pct,
            "last_status": priority,
            "last_update": now.isoformat(),
        }

        if priority == "P0":
            p0_list.append((code, name, desc))
        elif priority == "P1":
            p1_list.append((code, name, desc))
        elif priority == "P2":
            p2_list.append((code, name, desc))
        else:
            p3_count += 1

    # 保存状态
    save_state(state)

    # ── 推送逻辑 ────────────────────────────────────────────────────────
    pushed = {"p0": 0, "p1": 0, "p2": 0}

    # P0: 立即推送
    if p0_list:
        for code, name, desc in p0_list:
            msg = f"【P0紧急】{name}({code}) {desc}"
            if send_feishu(msg):
                pushed["p0"] += 1
        print(f"[signal_priority] P0推送: {p0_list}")

    # P1: 当次检查推送
    if p1_list:
        for code, name, desc in p1_list:
            msg = f"【P1重要】{name}({code}) {desc}"
            if send_feishu(msg):
                pushed["p1"] += 1
        print(f"[signal_priority] P1推送: {p1_list}")

    # P2: 批量汇总
    if force_push_p2 and p2_list:
        lines = [f"【P2汇总 {now.strftime('%H:%M')}】"]
        for code, name, desc in p2_list[:15]:
            lines.append(f"{name}({code}) {desc}")
        if p2_list:
            lines.append(f"...共{len(p2_list)}只波动")
        if send_feishu("\n".join(lines)):
            pushed["p2"] = len(p2_list)
        print(f"[signal_priority] P2批量: {len(p2_list)}只")

    return {
        "p0": p0_list,
        "p1": p1_list,
        "p2": p2_list,
        "p3_count": p3_count,
        "pushed": pushed,
        "ts": now.isoformat(),
    }

# ─── CLI ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # 演示：直接运行检查自定义股票池
    import requests, re

    WATCH_CODES = ["sz000586", "sz002491", "sh600594", "sh600654"]

    codes_str = ",".join(WATCH_CODES)
    try:
        r = requests.get(f"http://qt.gtimg.cn/q={codes_str}", timeout=8)
        r.encoding = "gbk"
        stocks = []
        for line in r.text.strip().split("\n"):
            m = re.search(r'v_(\w+)=.*?"([^"]+)"', line)
            if not m:
                continue
            code = m.group(1)
            parts = m.group(2).split("~")
            if len(parts) < 33:
                continue
            try:
                name  = parts[1]
                price = float(parts[3])  if parts[3]  else 0
                prev  = float(parts[4])  if parts[4]  else 0
                high  = float(parts[33]) if parts[33] else 0
                pct   = (price - prev) / prev * 100 if prev > 0 else 0
                stocks.append({"code": code, "name": name, "price": price,
                                "pct": pct, "high": high})
            except Exception:
                continue
    except Exception as e:
        print(f"数据获取失败: {e}")
        sys.exit(1)

    force = "--force" in sys.argv
    result = check_signals(stocks, force_push_p2=force)

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 检查结果:")
    print(f"  P0紧急: {len(result['p0'])}只")
    print(f"  P1重要: {len(result['p1'])}只")
    print(f"  P2常规: {len(result['p2'])}只")
    print(f"  P3静默: {result['p3_count']}只")
