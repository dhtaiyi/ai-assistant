#!/usr/bin/env python3
"""
连板晋级追踪器 V2 - 捕捉1板→2板→3板的关键时刻
==============================================
核心功能：
1. 追踪昨日涨停股今日的连板情况
2. 识别"1板→2板"的晋级时刻（关键信号！）
3. 识别"2板→3板"的妖股确认信号
4. 识别炸板风险（从涨停打开）

理论依据：
- 养家心法："上升期死磕周期龙"
- 1板→2板是最关键的晋级（确认不是"一日游"）
- 2板成妖，3板封神，4板以上是龙头
- 炸板次日不能反包 = 退潮信号

连板阶段定义：
- 首板（1板）：昨日涨停，今天继续涨停
- 二板（2板）：连续2天涨停
- 三板（3板）：连续3天涨停
- 高板（4板+）：妖股/龙头
"""
import requests
import json
import re
import os
from datetime import datetime, time
from collections import defaultdict

LOG_FILE = "/tmp/lianban_tracker.log"

def is_trading():
    now = datetime.now().time()
    return (time(9, 30) <= now <= time(15, 0))

def is_clean_stock(name):
    if any(x in name for x in ['ST', '*ST', 'N ', '退', 'S ']):
        return False
    return True

def get_full_code(symbol):
    code = symbol.replace('sz', '').replace('sh', '')
    prefix = 'sz' if symbol.startswith('sz') else 'sh'
    return prefix + code

def get_yesterday_limitup_codes():
    """加载昨日涨停股"""
    today = datetime.now()
    wd = today.weekday()
    if wd == 0:
        y = today - timedelta(days=3)
    else:
        y = today - timedelta(days=1)
    y_str = y.strftime('%Y%m%d')
    
    candidates_path = f"/home/dhtaiyi/.openclaw/workspace/stock-patterns/candidates/{y_str}.json"
    
    # 尝试找最近的有效候选池
    if not os.path.exists(candidates_path):
        from datetime import timedelta
        for i in range(1, 7):
            d = today - timedelta(days=i)
            if d.weekday() >= 5:
                continue
            path = f"/home/dhtaiyi/.openclaw/workspace/stock-patterns/candidates/{d.strftime('%Y%m%d')}.json"
            if os.path.exists(path):
                candidates_path = path
                break
    
    stocks = []
    if os.path.exists(candidates_path):
        with open(candidates_path) as f:
            data = json.load(f)
        for code, info in data.items():
            name = info.get('name', '')
            if is_clean_stock(name) and info.get('type') in ['涨停', '首板']:
                stocks.append({'code': code, 'name': name, 'yesterday_pct': info.get('pct', 10)})
    
    return stocks


def get_realtime(codes_list):
    """批量获取实时数据"""
    if not codes_list:
        return {}
    
    full_codes = []
    for item in codes_list:
        code = item['code']
        if not code.startswith('sz') and not code.startswith('sh'):
            code = ('sz' + code) if code[0] in '03' else ('sh' + code)
        full_codes.append(code)
    
    codes_str = ','.join(full_codes)
    try:
        r = requests.get(f'http://qt.gtimg.cn/q={codes_str}', timeout=10)
        result = {}
        for line in r.text.strip().split('\n'):
            if '"' not in line:
                continue
            m = re.search(r'=\s*"([^"]+)"', line)
            if not m:
                continue
            parts = m.group(1).split('~')
            if len(parts) < 10:
                continue
            try:
                name = parts[1]
                price = float(parts[3]) if parts[3] else 0
                prev_close = float(parts[4]) if parts[4] else 0
                open_p = float(parts[5]) if parts[5] else 0
                high = float(parts[33]) if len(parts) > 33 and parts[33] else 0
                amount = float(parts[37]) if len(parts) > 37 and parts[37] else 0
                
                if prev_close > 0:
                    pct = (price - prev_close) / prev_close * 100
                    auction_pct = (open_p - prev_close) / prev_close * 100 if open_p > 0 else 0
                    result[name] = {
                        'price': price,
                        'prev_close': prev_close,
                        'pct': pct,
                        'auction_pct': auction_pct,
                        'open': open_p,
                        'high': high,
                        'amount': amount,
                    }
            except:
                continue
        return result
    except:
        return {}


def analyze_lianban():
    """分析连板情况"""
    from datetime import timedelta
    
    today = datetime.now()
    wd = today.weekday()
    if wd == 0:
        y = today - timedelta(days=3)
    else:
        y = today - timedelta(days=1)
    y_str = y.strftime('%Y%m%d')
    
    print(f"\n{'='*60}")
    print(f"🔗 连板晋级追踪 V2 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")
    
    # 加载昨日涨停股
    candidates_path = f"/home/dhtaiyi/.openclaw/workspace/stock-patterns/candidates/{y_str}.json"
    stocks = []
    if os.path.exists(candidates_path):
        with open(candidates_path) as f:
            data = json.load(f)
        for code, info in data.items():
            name = info.get('name', '')
            if is_clean_stock(name):
                stocks.append({'code': code, 'name': name, 'yesterday_pct': info.get('pct', 10)})
    
    print(f"📂 昨日涨停股池: {len(stocks)}只 ({y_str})")
    
    if not stocks:
        print("❌ 无昨日涨停数据")
        return
    
    # 获取实时数据
    data = get_realtime(stocks)
    print(f"📡 实时数据: {len(data)}只")
    
    if not data:
        print("❌ 无法获取实时数据")
        return
    
    # 分类
    lianban_3plus = []   # 3板+
    lianban_2 = []       # 2板
    lianban_1 = []       # 首板(今天继续涨停)
    zhaban = []          # 炸板(开板后回落)
    faded = []           # 冲高回落(未涨停)
    weak = []            # 走弱
    
    for item in stocks:
        name = item['name']
        if name not in data:
            continue
        
        d = data[name]
        pct = d['pct']
        high = d['high']
        prev = d['prev_close']
        amount_yi = d['amount'] / 1e8
        
        # 判断是否曾涨停（今日最高>=9.9%）
        ever_limitup = (high >= prev * 1.099) if prev > 0 else False
        
        # 判断是否炸板（曾经涨停但现在打开）
        zhaban_now = ever_limitup and pct < 9.5
        
        if pct >= 9.5:
            if item['yesterday_pct'] >= 9.5:
                lianban_3plus.append({'name': name, 'code': item['code'], 'pct': pct, 'amount': amount_yi, 'yesterday_pct': item['yesterday_pct']})
            else:
                lianban_1.append({'name': name, 'code': item['code'], 'pct': pct, 'amount': amount_yi})
        elif zhaban_now:
            zhaban.append({'name': name, 'code': item['code'], 'pct': pct, 'amount': amount_yi, 'high_pct': (high/prev-1)*100 if prev > 0 else 0})
        elif 5 <= pct < 9.5:
            faded.append({'name': name, 'code': item['code'], 'pct': pct, 'amount': amount_yi})
        else:
            weak.append({'name': name, 'code': item['code'], 'pct': pct, 'amount': amount_yi})
    
    # ===== 输出 =====
    if lianban_3plus:
        print(f"\n🏆 3板+龙头 ({len(lianban_3plus)}只):")
        for s in sorted(lianban_3plus, key=lambda x: x['amount'], reverse=True):
            board_count = "超预期" if s['yesterday_pct'] >= 9.5 else ""
            print(f"  👑 {s['name']}({s['code']}) {s['pct']:+.1f}% 成交{s['amount']:.0f}亿 {board_count}")
    
    if lianban_2:
        print(f"\n🔗 2板确认 ({len(lianban_2)}只):")
        for s in sorted(lianban_2, key=lambda x: x['amount'], reverse=True):
            print(f"  ✅ {s['name']}({s['code']}) +{s['pct']:.1f}% 成交{s['amount']:.0f}亿")
    
    if lianban_1:
        print(f"\n📈 首板延续 ({len(lianban_1)}只):")
        for s in sorted(lianban_1, key=lambda x: x['amount'], reverse=True)[:8]:
            print(f"  ➡️ {s['name']}({s['code']}) +{s['pct']:.1f}% 成交{s['amount']:.0f}亿")
    
    if zhaban:
        print(f"\n💥 炸板预警 ({len(zhaban)}只):")
        for s in sorted(zhaban, key=lambda x: x['pct'], reverse=True)[:5]:
            print(f"  🚨 {s['name']}({s['code']}) {s['pct']:+.1f}%（最高{s['high_pct']:.1f}%）")
    
    if faded:
        print(f"\n📉 冲高回落 ({len(faded)}只):")
        for s in sorted(faded, key=lambda x: x['pct'], reverse=True)[:5]:
            print(f"  ⚠️ {s['name']}({s['code']}) +{s['pct']:.1f}%")
    
    if weak:
        print(f"\n❄️ 走弱 ({len(weak)}只):")
        for s in sorted(weak, key=lambda x: x['pct'])[:5]:
            print(f"  🔵 {s['name']}({s['code']}) {s['pct']:+.1f}%")
    
    # ===== 养家心法提示 =====
    print(f"\n{'─'*60}")
    print(f"💡 养家心法提示:")
    
    if lianban_3plus:
        print(f"  ✅ 龙头已现！{len(lianban_3plus)}只3板+股票")
        print(f"  → 死磕龙头！")
    elif lianban_2:
        print(f"  ✅ 2板确认！{len(lianban_2)}只股票晋级2板")
        print(f"  → 重点关注，明日可能3板")
    elif lianban_1:
        print(f"  ➡️ 首板延续中({len(lianban_1)}只)，等待晋级确认")
    
    if zhaban:
        print(f"  🚨 {len(zhaban)}只炸板！注意退潮风险")
    
    if not lianban_3plus and not lianban_2 and not lianban_1:
        print(f"  ⚠️ 昨日涨停股整体走弱，市场情绪偏谨慎")
    
    # ===== 关键信号 =====
    print(f"\n{'─'*60}")
    print(f"🎯 关键信号:")
    
    if lianban_2:
        best = lianban_2[0]
        print(f"  🔔 重点关注: {best['name']} 2板中，成交{best['amount']:.0f}亿")
        print(f"     明日竞价若高开3-7%，可参与3板")
    
    if lianban_1 and not lianban_2:
        print(f"  🔔 昨日涨停今首板({len(lianban_1)}只)，观察是否能晋级2板")
    
    # ===== 保存 =====
    save_dir = "/home/dhtaiyi/.openclaw/workspace/stock-data/lianban"
    os.makedirs(save_dir, exist_ok=True)
    save_path = f"{save_dir}/{datetime.now().strftime('%Y%m%d')}.json"
    
    with open(save_path, 'w') as f:
        json.dump({
            'time': datetime.now().isoformat(),
            'lianban_3plus': lianban_3plus,
            'lianban_2': lianban_2,
            'lianban_1': lianban_1,
            'zhaban': zhaban,
            'faded': faded,
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 连板数据已保存: {save_path}")


if __name__ == "__main__":
    print(f"连板晋级追踪 V2 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    analyze_lianban()
