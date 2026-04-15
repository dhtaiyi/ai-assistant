#!/usr/bin/env python3
"""
午盘实时扫描器 V2.0 - 问财增强版
======================================
功能：
1. 实时获取当前涨幅榜TOP30 + 成交额数据
2. 结合问财涨停原因（同花顺官方）
3. 妖股评分（成交额+涨幅+振幅+开板检测）
4. 识别买点机会（买点A/B/C）
5. 识别板块跟风机会
======================================
"""

import json
import os
import re
import sys
import time
import requests
import subprocess
from datetime import datetime, time as dtime

LOG_FILE = "/tmp/realtime_top_scan.log"

# 问财配置
IWENCAI_SKILL = os.path.expanduser("~/.openclaw/workspace/skills/问财选A股/scripts/cli.py")
IWENCAI_API_KEY = os.environ.get(
    "IWENCAI_API_KEY",
    "sk-proj-01-NAItJumXGkKAe1Ha8v-rPenhNjrfud7CDgoY0DEAymigKrbbZSIwxhjOQG5RrqWytp8AZApOyf4RsS-q5d2FbyTbPZAYJC262Vbgthv9IizhxH3W-5a2kNpR3ifa0nAobbl6NQ"
)

# ─── 问财涨停原因缓存 ──────────────────────────────────────────────────────
_reason_cache = {}
_reason_cache_time = 0
_REASON_CACHE_TTL = 300  # 5分钟

def get_zt_reasons() -> dict:
    """获取今日涨停股的涨停原因（带缓存）"""
    global _reason_cache, _reason_cache_time
    now = time.time()
    if _reason_cache and (now - _reason_cache_time) < _REASON_CACHE_TTL:
        return _reason_cache

    try:
        cmd = [
            "python3", IWENCAI_SKILL,
            "--query", "今日涨停股票，按成交额排序",
            "--limit", "100",
            "--api-key", IWENCAI_API_KEY
        ]
        env = os.environ.copy()
        env["IWENCAI_BASE_URL"] = "https://openapi.iwencai.com"
        env["IWENCAI_API_KEY"] = IWENCAI_API_KEY
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, env=env)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if data.get("success"):
                _reason_cache = {}
                for s in data.get("datas", []):
                    code_raw = s.get("股票代码", "")
                    # 标准化: 002361.SZ → sz002361
                    code = code_raw.upper().replace(".SZ", "").replace(".SH", "")
                    prefix = "sz" if "SZ" in code_raw else "sh"
                    norm = prefix + code
                    _reason_cache[norm] = {
                        "reason": s.get("涨停原因[20260415]", ""),
                        "换手率": s.get("换手率[20260415]", 0),
                        "振幅": s.get("振幅[20260415]", 0),
                        "首次涨停": s.get("首次涨停时间[20260415]", ""),
                        "成交额": s.get("成交额[20260415]", 0),
                    }
                _reason_cache_time = now
                print(f"   [问财] 缓存更新: {len(_reason_cache)}只涨停股")
    except Exception as e:
        print(f"   [问财] 涨停原因获取失败: {e}")
    return _reason_cache

# ─── 工具函数 ──────────────────────────────────────────────────────────────
def is_trading():
    now = datetime.now().time()
    morning = dtime(9, 30) <= now <= dtime(11, 30)
    afternoon = dtime(13, 0) <= now <= dtime(15, 0)
    return morning or afternoon

def is_clean_stock(s):
    name = s.get('name', '')
    if any(x in name for x in ['ST', '*ST', 'N ', '退', 'S ']):
        return False
    code = s.get('symbol', '')
    if code.startswith('bj'):
        return False
    return True

def get_full_code(symbol):
    code = symbol.replace('sz', '').replace('sh', '')
    prefix = 'sz' if symbol.startswith('sz') else 'sh'
    return prefix + code

def get_realtime_indices():
    indices = {}
    try:
        r = requests.get('http://qt.gtimg.cn/q=s_sh000001,s_sz399001,s_sz399006', timeout=5)
        for line in r.text.strip().split('\n'):
            if '"' not in line:
                continue
            m = re.search(r'="([^"]+)"', line)
            if not m:
                continue
            parts = m.group(1).split('~')
            try:
                if len(parts) > 5 and parts[1]:
                    name = parts[1]
                    price = float(parts[3]) if parts[3] else 0
                    pct = float(parts[5]) if len(parts) > 5 and parts[5] else 0
                    indices[name] = {'price': price, 'pct': pct}
            except (ValueError, IndexError):
                continue
    except:
        pass
    return indices

# ─── 板块统计 ──────────────────────────────────────────────────────────────
def sector_stats(reasons: dict) -> dict:
    """按涨停原因分组"""
    sectors = {}
    for norm, info in reasons.items():
        reason = info.get("reason", "其他")
        if not reason:
            reason = "其他"
        # 取第一个标签
        primary = reason.split("+")[0].split("(")[0].strip()
        if primary not in sectors:
            sectors[primary] = []
        sectors[primary].append({"norm": norm, **info})
    return sectors

# ─── 主扫描 ──────────────────────────────────────────────────────────────
def realtime_scan():
    print(f"\n{'='*60}")
    print(f"📊 午盘实时扫描 V2.0 (问财增强版) {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}")

    # 问财涨停原因（一次获取，全局使用）
    print("⏳ 获取涨停原因数据...")
    reasons = get_zt_reasons()

    # 获取实时数据
    url = 'https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeDataSimple'
    try:
        r1 = requests.get(url, params={
            'page': 1, 'num': 200,
            'sort': 'changepercent', 'asc': 0,
            'node': 'hs_a'
        }, timeout=10)
        all_stocks = r1.json()
    except Exception as e:
        print(f"❌ 涨幅榜获取失败: {e}")
        return

    try:
        r2 = requests.get(url, params={
            'page': 1, 'num': 100,
            'sort': 'amount', 'asc': 0,
            'node': 'hs_a'
        }, timeout=10)
        by_amount = r2.json()
    except:
        by_amount = []

    amount_dict = {}
    for s in (by_amount or []):
        sym = s.get('symbol', '')
        try:
            amount_dict[sym] = float(s.get('amount', 0)) / 1e8
        except:
            pass

    indices = get_realtime_indices()

    # 指数
    sh_pct = indices.get('上证指数', {}).get('pct', 0)
    print(f"\n指数: 上证 {indices.get('上证指数',{}).get('price','?')} ({sh_pct:+.2f}%)")
    print(f"      深证 {indices.get('深证成指',{}).get('price','?')} ({indices.get('深证成指',{}).get('pct',0):+.2f}%)")
    print(f"      创业板 {indices.get('创业板指',{}).get('price','?')} ({indices.get('创业板指',{}).get('pct',0):+.2f}%)")

    limit_up = [s for s in all_stocks if float(s.get('changepercent', 0)) >= 9.5 and is_clean_stock(s)]
    strong = [s for s in all_stocks if 5 <= float(s.get('changepercent', 0)) < 9.5 and is_clean_stock(s)]
    print(f"\n涨停: {len(limit_up)}只 | 强势(5-9%): {len(strong)}只")

    # 板块主线
    if reasons:
        secs = sector_stats(reasons)
        print(f"\n【主线板块】(官方涨停原因)")
        sorted_secs = sorted(secs.items(), key=lambda x: sum(s.get("成交额",0) for s in x[1]), reverse=True)
        for i, (sec, members) in enumerate(sorted_secs[:5], 1):
            total_amt = sum(s.get("成交额", 0) for s in members) / 1e8
            names = ",".join(m["norm"].replace("sz","").replace("sh","")[:6] for m in members[:3])
            print(f"  {i}. {sec} {total_amt:.0f}亿 ({len(members)}只) {names}")

    # 妖股潜力评分
    print(f"\n🔥 妖股潜力 TOP15（成交额+涨幅+振幅综合）:")
    candidates = []

    for s in (limit_up + strong):
        sym = s.get('symbol', '')
        try:
            pct = float(s.get('changepercent', 0))
            trade = float(s.get('trade', 0))
            high = float(s.get('high', 0))
            open_p = float(s.get('open', 0))
            amount = amount_dict.get(sym, 0)
            close_y = float(s.get('settlement', 0))

            if not trade or not close_y:
                continue

            amplitude = (high - close_y) / close_y * 100 if close_y > 0 else 0

            # 妖股评分
            amount_score = min(40, amount * 0.8)
            pct_score = min(30, pct * 2)
            amp_score = min(20, amplitude * 2)
            if pct >= 9.5 and open_p < trade:
                open_board_score = 10
            elif pct >= 9.5 and open_p == trade:
                open_board_score = 5
            else:
                open_board_score = 5

            total_score = amount_score + pct_score + amp_score + open_board_score

            # 问财增强数据
            reason_info = reasons.get(sym, {})
            reason = reason_info.get("reason", "")
            hs_rate = reason_info.get("换手率", 0)
            zt_time = reason_info.get("首次涨停", "")[11:16] if reason_info.get("首次涨停") else ""

            candidates.append({
                'name': s['name'],
                'code': get_full_code(sym),
                'pct': pct,
                'amount': amount,
                'amplitude': round(amplitude, 1),
                'score': round(total_score, 1),
                'type': '涨停' if pct >= 9.5 else '强势',
                'high': high,
                'open': open_p,
                'trade': trade,
                'reason': reason,
                '换手率': hs_rate,
                'zt_time': zt_time,
            })
        except (ValueError, TypeError, KeyError):
            continue

    candidates.sort(key=lambda x: x['score'], reverse=True)
    top15 = candidates[:15]

    for i, c in enumerate(top15, 1):
        amp_marker = "⚡" if c['amplitude'] > 5 else "  "
        board_marker = "🔓" if c['open'] < c['high'] and c['pct'] >= 9.5 else "  "
        zt = f"[{c['zt_time']}]" if c['zt_time'] else ""
        print(f"  {i:2d}. {board_marker}{amp_marker}{c['name']}({c['code']}) "
              f"+{c['pct']:.1f}% 成交{c['amount']:.0f}亿 振幅{c['amplitude']:.1f}% "
              f"评分:{c['score']:.0f} {zt}")
        if c.get('reason'):
            print(f"       原因: {c['reason']}")

    # 成交额TOP10
    print(f"\n💰 成交额TOP10（机构信号）:")
    amt_sorted = sorted(
        [s for s in all_stocks if is_clean_stock(s) and float(s.get('changepercent', 0)) >= 3],
        key=lambda x: amount_dict.get(x.get('symbol', ''), 0),
        reverse=True
    )[:10]

    for i, s in enumerate(amt_sorted, 1):
        sym = s.get('symbol', '')
        amt = amount_dict.get(sym, 0)
        pct = float(s.get('changepercent', 0))
        print(f"  {i:2d}. {s['name']}({get_full_code(sym)}) +{pct:.1f}% 成交{amt:.0f}亿")

    # 买点机会
    print(f"\n🎯 买点机会扫描:")
    opportunities = []
    for c in candidates:
        if 9.0 <= c['pct'] < 9.9 and c['amplitude'] > 3:
            opportunities.append(f"  🔔 {c['name']}({c['code']}) 买点A:首板(+{c['pct']:.1f}%,振幅{c['amplitude']:.1f}%)")
        if c['pct'] >= 9.5 and c['open'] < c['high'] and c['amplitude'] > 4:
            opportunities.append(f"  🔓 {c['name']}({c['code']}) 开板分歧:关注回封(+{c['pct']:.1f}%,成交{c['amount']:.0f}亿)")

    if opportunities:
        for op in opportunities[:5]:
            print(op)
    else:
        print("  (暂无明显买点，等回落或回封确认)")

    # 养家心法提示
    if len(limit_up) >= 50:
        print(f"\n💡 养家心法：情绪上升期，涨停{len(limit_up)}只，积极参与主线龙头")
    elif len(limit_up) >= 20:
        print(f"\n💡 养家心法：情绪一般，{len(limit_up)}只涨停，轻仓试探")
    else:
        print(f"\n💡 养家心法：情绪低迷，{len(limit_up)}只涨停，空仓休息")

    print(f"\n{'='*60}")

# ─── 主函数 ──────────────────────────────────────────────────────────────
def main():
    if not is_trading():
        print("⏰ 非交易时段，退出")
        return
    realtime_scan()

if __name__ == "__main__":
    main()
