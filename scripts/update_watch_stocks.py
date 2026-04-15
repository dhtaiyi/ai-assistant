#!/usr/bin/env python3
"""
盘中实时更新观察标的 v1
==============================
功能：
1. 实时扫描当前最强妖股
2. 更新 breakthrough_alert.py 的 WATCH_STOCKS
3. 在盘中定时运行，保持标的新鲜度
运行时间：
  - 13:00（下午开盘）
  - 13:30 / 14:00 / 14:30（盘中30分钟更新）
"""
import requests
import json
import re
import os
import sys
from datetime import datetime, time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ALERT_FILE = os.path.join(SCRIPT_DIR, 'breakthrough_alert.py')
LOG_FILE = "/tmp/update_watch_stocks.log"

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')


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


def scan_top_candidates(n=10):
    """扫描当前最强N只股票"""
    url = 'https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeDataSimple'
    
    # 获取涨幅TOP200
    try:
        r1 = requests.get(url, params={
            'page': 1, 'num': 200,
            'sort': 'changepercent', 'asc': 0,
            'node': 'hs_a'
        }, timeout=10)
        all_stocks = r1.json()
    except Exception as e:
        log(f"❌ 获取涨幅榜失败: {e}")
        return []

    # 获取成交额TOP100
    try:
        r2 = requests.get(url, params={
            'page': 1, 'num': 100,
            'sort': 'amount', 'asc': 0,
            'node': 'hs_a'
        }, timeout=10)
        by_amount = r2.json()
    except:
        by_amount = []

    # 成交额字典
    amount_dict = {}
    for s in (by_amount or []):
        sym = s.get('symbol', '')
        try:
            amount_dict[sym] = float(s.get('amount', 0)) / 1e8
        except:
            pass

    # 分类
    limit_up = [s for s in all_stocks if float(s.get('changepercent', 0)) >= 9.5 and is_clean_stock(s)]
    strong = [s for s in all_stocks if 5 <= float(s.get('changepercent', 0)) < 9.5 and is_clean_stock(s)]

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

            # 妖股评分
            amount_score = min(40, amount * 0.8)
            pct_score = min(30, pct * 2)
            amplitude = (high - close_y) / close_y * 100 if close_y > 0 else 0
            amp_score = min(20, amplitude * 2)
            
            if pct >= 9.5 and open_p < trade:
                open_board_score = 10
            elif pct >= 9.5 and open_p == trade:
                open_board_score = 5
            else:
                open_board_score = 5

            total_score = amount_score + pct_score + amp_score + open_board_score

            candidates.append({
                'name': s['name'],
                'code': get_full_code(sym),
                'pct': pct,
                'amount': amount,
                'amplitude': round(amplitude, 1),
                'score': round(total_score, 1),
                'type': '涨停' if pct >= 9.5 else '强势',
                'price': trade,
                'high': high,
            })
        except:
            continue

    candidates.sort(key=lambda x: x['score'], reverse=True)
    return candidates[:n]


def update_watch_stocks(candidates):
    """更新 breakthrough_alert.py 的 WATCH_STOCKS"""
    if not candidates:
        log("⚠️ 无候选股，跳过更新")
        return False

    watch = {}
    for c in candidates:
        # 关键价位：涨停价的1.03（+3%空间）
        resist = round(c['price'] * 1.03, 2) if c['price'] > 0 else 0
        watch[c['code']] = {
            "name": c['name'],
            "resist": resist,
            "reason": f"{c['type']}+{c['pct']:.0f}%|{c['score']}分|成交{c['amount']:.0f}亿"
        }

    # 读取当前文件
    if not os.path.exists(ALERT_FILE):
        log(f"❌ {ALERT_FILE} 不存在")
        return False

    with open(ALERT_FILE) as f:
        content = f.read()

    # 生成新的WATCH_STOCKS代码块
    watch_json = json.dumps(watch, ensure_ascii=False, indent=4)
    new_block = f"WATCH_STOCKS = {watch_json}"
    
    # 找到现有的 WATCH_STOCKS 块并替换
    # 匹配模式：WATCH_STOCKS = { ... }
    pattern = r'(WATCH_STOCKS = \{[\s\S]*?\n\})'
    match = re.search(pattern, content)
    
    if match:
        old_block = match.group(1)
        new_content = content.replace(old_block, new_block + '\n')
        
        with open(ALERT_FILE, 'w') as f:
            f.write(new_content)
        
        log(f"✅ 已更新 {len(watch)} 只观察标的")
        for c in candidates[:5]:
            log(f"   {c['name']}({c['code']}) {c['type']}+{c['pct']:.1f}% 评分{c['score']:.0f}")
        return True
    else:
        log(f"⚠️ 未找到WATCH_STOCKS块，手动替换注释行")
        # 备选：找到 "# 重点监控" 注释后的行，插入
        lines = content.split('\n')
        new_lines = []
        inserted = False
        for i, line in enumerate(lines):
            new_lines.append(line)
            if '# 重点监控的股票和关键价位' in line and not inserted:
                inserted = True
                new_lines.append(new_block)
        
        if inserted:
            with open(ALERT_FILE, 'w') as f:
                f.write('\n'.join(new_lines))
            log(f"✅ 插入模式更新了 {len(watch)} 只")
            return True
        else:
            log("❌ 无法定位WATCH_STOCKS，替换失败")
            return False


def main():
    log("=" * 50)
    log(f"📡 盘中观察标的更新 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    log("=" * 50)

    # 检查交易时段（13:00-15:00）
    now = datetime.now().time()
    if not (time(13, 0) <= now <= time(15, 0)):
        log(f"⏰ 非盘中时段（{now}），跳过")
        return

    candidates = scan_top_candidates(n=10)
    if not candidates:
        log("❌ 扫描无结果")
        return

    success = update_watch_stocks(candidates)
    if success:
        log(f"🎯 下一轮更新：30分钟后")
    else:
        log(f"❌ 更新失败")


if __name__ == "__main__":
    main()
