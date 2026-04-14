#!/usr/bin/env python3
"""
盘中突破提醒 v1.0
监控关键价位的突破情况，有突破时推送飞书通知
使用方法：python3 breakthrough_alert.py
"""

import requests
import time
import json
import os
from datetime import datetime

# 重点监控的股票和关键价位 (20260413 自动更新)
WATCH_STOCKS = {
    "sz301696": {
        "name": "C三瑞",
        "resist": 132.21,
        "reason": ""
    },
    "sz301526": {
        "name": "国际复材",
        "resist": 16.35,
        "reason": ""
    },
    "sz002240": {
        "name": "盛新锂能",
        "resist": 53.33,
        "reason": ""
    },
    "sh603459": {
        "name": "C红板",
        "resist": 68.4,
        "reason": ""
    },
    "sh600166": {
        "name": "福田汽车",
        "resist": 3.83,
        "reason": ""
    }
}

STATE_FILE = "/tmp/breakthrough_state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def get_realtime(codes):
    url = "http://qt.gtimg.cn/q=" + ",".join(codes)
    r = requests.get(url, timeout=5)
    result = {}
    for line in r.text.strip().split("\n"):
        if "~" not in line:
            continue
        parts = line.split("~")
        if len(parts) < 33:
            continue
        code = line.split("=")[0].replace("v_", "")
        price = float(parts[3]) if parts[3] else 0
        pct = float(parts[32]) if parts[32] else 0
        # parts[44]=总市值(亿元), parts[45]=流通市值(亿元)
        total_mv = parts[44] if len(parts) > 44 and parts[44] else "0"
        circ_mv = parts[45] if len(parts) > 45 and parts[45] else "0"
        try:
            total_mv_yi = float(total_mv)
            total_mv_str = f"{total_mv_yi:.1f}亿"
        except:
            total_mv_str = total_mv
        try:
            circ_mv_yi = float(circ_mv)
            circ_mv_str = f"{circ_mv_yi:.1f}亿"
        except:
            circ_mv_str = circ_mv
        result[code] = {"price": price, "pct": pct, "total_mv": total_mv_str, "circ_mv": circ_mv_str}
    return result

def check_breakthrough():
    codes = list(WATCH_STOCKS.keys())
    data = get_realtime(codes)
    state = load_state()
    alerts = []

    for code, info in WATCH_STOCKS.items():
        name = info["name"]
        resist = info["resist"]
        reason = info["reason"]
        d = data.get(code, {})
        price = d.get("price", 0)
        pct = d.get("pct", 0)
        total_mv = d.get("total_mv", "-")
        circ_mv = d.get("circ_mv", "-")

        if price <= 0:
            continue

        # 检查是否突破
        key = code
        prev_price = state.get(key, {}).get("price", 0)
        already_alerted = state.get(key, {}).get("alerted", False)

        # 突破条件：价格超过关键价位且超过前一次记录
        if price > resist and (prev_price <= resist or not already_alerted):
            alerts.append({
                "name": name,
                "code": code,
                "price": price,
                "resist": resist,
                "pct": pct,
                "total_mv": total_mv,
                "circ_mv": circ_mv,
                "reason": reason,
                "type": "突破"
            })
            state[key] = {"price": price, "alerted": True}

        # 涨停预警
        elif pct >= 9.9 and not state.get(key, {}).get("zt_alerted"):
            alerts.append({
                "name": name,
                "code": code,
                "price": price,
                "pct": pct,
                "total_mv": total_mv,
                "circ_mv": circ_mv,
                "reason": reason,
                "type": "涨停"
            })
            state[key] = {"price": price, "alerted": True, "zt_alerted": True}

        # 更新状态
        else:
            if key not in state:
                state[key] = {}
            state[key]["price"] = price

    save_state(state)
    return alerts

def send_feishu(message):
    """发送飞书通知"""
    app_id = "cli_a92923c6a2f99bc0"
    app_secret = "H4CdLHf1NwM1iv3JWzBsfdFFUY8bO4At"
    
    token_r = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        headers={"Content-Type": "application/json"},
        json={"app_id": app_id, "app_secret": app_secret},
        timeout=10
    )
    try:
        token = token_r.json().get("tenant_access_token", "")
    except Exception:
        token = ""
        print(f"Token response text: {token_r.text[:200]}")
    
    if not token:
        print("获取token失败")
        return
    
    user_id = "ou_04add8ebe219f09799570c70e3cdc732"
    r = requests.post(
        "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={
            "receive_id": user_id,
            "msg_type": "text",
            "content": json.dumps({"text": message}, ensure_ascii=False)
        },
        timeout=10
    )

def main():
    now = datetime.now()
    
    # 检查是否在交易时间
    is_trading = False
    if now.weekday() < 5:  # 周一到周五
        hour = now.hour
        minute = now.minute
        total_min = hour * 60 + minute
        # 9:30-11:30, 13:00-15:00
        if (total_min >= 570 and total_min <= 690) or (total_min >= 780 and total_min <= 900):
            is_trading = True
    
    if not is_trading:
        return  # 午休时间，静默跳过，不发通知
    
    alerts = check_breakthrough()
    
    if alerts:
        for a in alerts:
            resist_str = f"突破价位: {a['resist']}" if a.get('resist') else ""
            reason_str = f"原因: {a.get('reason', '-')}"
            extra = "\n".join(x for x in [resist_str, reason_str] if x)
            msg = f"【{a['type']}提醒】\n{a['name']}({a['code'][-6:]})\n现价: {a['price']}  涨幅: {a['pct']:+.1f}%\n总市值: {a['total_mv']}  流通: {a['circ_mv']}" + (f"\n{extra}" if extra else "")
            print(msg)
            send_feishu(msg)
    else:
        print(f"[{now.strftime('%H:%M')}] 无突破信号")

if __name__ == "__main__":
    main()
