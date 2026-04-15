#!/usr/bin/env python3
"""
竞价实时追踪器 V1 - 9:15-9:25核心窗口
==============================================
9:15-9:25 是超短最重要的时段，但当前系统没有在这个窗口内实时分析

功能：
1. 9:15/9:20/9:25 分三次扫描
2. 追踪昨日强势股今早竞价表现
3. 首板战法买点A信号实时检测
4. 竞价异动预警（大幅高开/低开）

核心指标：
- 竞价涨幅：从昨收到今竞价的涨幅
- 竞价量：竞价时段成交额（越大越强）
- 竞价结构：高开/低开/平开

买点A量化：
- 昨日涨停股 + 今竞价高开3-7% + 竞价量 > 1亿 = 最佳买点
- 高开>9% = 危险（容易炸板）
- 高开<0 = 弱势（不符合首板战法）
"""
import requests
import json
import re
import os
from datetime import datetime, time

LOG_FILE = "/tmp/auction_premarket.log"

# ====== 数据源 ======

SINA_AUCTION_URL = 'https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeDataSimple'

def get_tencent_realtime(codes):
    """腾讯实时行情（批量）"""
    if not codes:
        return {}
    code_str = ','.join(codes)
    try:
        r = requests.get(f'http://qt.gtimg.cn/q={code_str}', timeout=10)
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
                sym = line.split('=')[0].replace('v_', '')
                result[sym] = {
                    'name': parts[1],
                    'price': float(parts[3]) if parts[3] else 0,
                    'prev_close': float(parts[4]) if parts[4] else 0,
                    'open': float(parts[5]) if parts[5] else 0,
                    'high': float(parts[33]) if len(parts) > 33 and parts[33] else 0,
                    'low': float(parts[34]) if len(parts) > 34 and parts[34] else 0,
                    'amount': float(parts[37]) if len(parts) > 37 and parts[37] else 0,  # 万元
                    'pct': float(parts[32]) if len(parts) > 32 and parts[32] else 0,
                }
            except:
                continue
        return result
    except:
        return {}

def get_sina_limitup():
    """新浪涨幅榜获取昨日涨停股池（简化版）"""
    try:
        r = requests.get(SINA_AUCTION_URL, params={
            'page': 1, 'num': 100,
            'sort': 'changepercent', 'asc': 0,
            'node': 'hs_a'
        }, timeout=10)
        data = r.json()
        return [s for s in data if float(s.get('changepercent', 0)) >= 9.5]
    except:
        return []

# ====== 核心分析 ======

def analyze_auction_wave():
    """竞价波浪分析 - 9:15/9:20/9:25分批扫描"""
    print(f"\n{'='*60}")
    print(f"📡 竞价实时追踪 {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}")
    
    # 获取昨日涨停股池（用于今日竞价参考）
    # 注意：新浪涨幅榜是今日数据，不是昨日
    # 所以我们用"今日涨幅>=9.5%且开盘价=昨收价"的股票来近似"昨日涨停今日继续"
    # 更准确的方式是读取昨日候选池文件
    
    # 读取昨日候选池
    today = datetime.now()
    wd = today.weekday()
    from datetime import timedelta
    if wd == 0:
        y = today - timedelta(days=3)
    else:
        y = today - timedelta(days=1)
    y_str = y.strftime('%Y%m%d')
    
    candidates_path = f"/home/dhtaiyi/.openclaw/workspace/stock-patterns/candidates/{y_str}.json"
    stocks_to_watch = []
    
    if os.path.exists(candidates_path):
        with open(candidates_path) as f:
            candidates = json.load(f)
        stocks_to_watch = [(code, info) for code, info in candidates.items() 
                          if info.get('type') in ['涨停', '首板']]
        print(f"从昨日候选池加载: {len(stocks_to_watch)}只")
    else:
        # 没有昨日数据，用今日涨幅榜前20作为观察
        print(f"无昨日候选池，使用今日涨幅前20")
        try:
            r = requests.get(SINA_AUCTION_URL, params={
                'page': 1, 'num': 20, 'sort': 'changepercent', 'asc': 0, 'node': 'hs_a'
            }, timeout=10)
            data = r.json()
            for s in data:
                sym = s.get('symbol', '')
                name = s.get('name', '')
                pct = float(s.get('changepercent', 0))
                amount = float(s.get('amount', 0))
                if pct >= 9.5:
                    prefix = 'sh' if sym.startswith('sh') else 'sz'
                    full = prefix + sym if prefix in sym else sym
                    stocks_to_watch.append((full, {'name': name, 'pct': pct, 'amount': amount}))
        except:
            pass
    
    if not stocks_to_watch:
        print("无观察股票，跳过")
        return []
    
    # 批量获取实时数据
    codes = [s[0] for s in stocks_to_watch]
    real_data = get_tencent_realtime(codes)
    
    # 分析
    results = []
    buy_a_signals = []
    danger_signals = []
    weak_signals = []
    
    for code, info in stocks_to_watch:
        name = info.get('name', '?')
        r = real_data.get(code, {})
        if not r or not r.get('prev_close'):
            continue
        
        prev_close = r['prev_close']
        open_p = r['open']
        price = r['price']
        amount_yi = r['amount'] / 1e8  # 万元->亿
        
        if prev_close <= 0:
            continue
        
        # 竞价涨幅
        auction_pct = (open_p - prev_close) / prev_close * 100
        # 当前涨幅
        current_pct = r.get('pct', 0)
        
        results.append({
            'name': name,
            'code': code,
            'auction_pct': round(auction_pct, 2),
            'current_pct': round(current_pct, 2),
            'amount_yi': round(amount_yi, 1),
            'prev_close': prev_close,
            'open': open_p,
            'price': price,
        })
        
        # 买点A检测：竞价高开3-7%
        if 3 <= auction_pct <= 7 and amount_yi >= 1:
            buy_a_signals.append(results[-1])
        # 高开>9%危险
        elif auction_pct > 9:
            danger_signals.append(results[-1])
        # 低开
        elif auction_pct < 0:
            weak_signals.append(results[-1])
    
    # 按竞价涨幅排序
    results.sort(key=lambda x: x['auction_pct'], reverse=True)
    
    # 输出
    now = datetime.now()
    hour = now.hour
    minute = now.minute
    
    wave = "9:15首波" if minute < 18 else ("9:20二波" if minute < 23 else "9:25终版")
    print(f"\n📡 {wave} 竞价追踪")
    print(f"观察标的: {len(results)}只")
    
    # 竞价排行
    print(f"\n竞价涨幅排行TOP10:")
    for r in results[:10]:
        auc = r['auction_pct']
        marker = "✅" if 3 <= auc <= 7 else ("🚨" if auc > 9 else ("⚠️" if auc < 0 else "  "))
        print(f"  {marker} {r['name']}({r['code']}) 竞价{auc:+.2f}% 现{float(r['current_pct']):+.2f}% 额{r['amount_yi']:.1f}亿")
    
    # 买点A信号
    if buy_a_signals:
        print(f"\n🎯 买点A信号（竞价高开3-7%）:")
        for r in buy_a_signals[:5]:
            print(f"  ✅ {r['name']}({r['code']}) 竞价{r['auction_pct']:+.1f}% 现{r['current_pct']:+.1f}% 额{r['amount_yi']:.1f}亿")
    
    # 危险信号
    if danger_signals:
        print(f"\n🚨 高开>9%危险信号:")
        for r in danger_signals[:5]:
            print(f"  🚫 {r['name']} 竞价{r['auction_pct']:+.1f}%（容易炸板！）")
    
    # 弱势信号
    if weak_signals:
        print(f"\n⚠️ 低开弱势:")
        for r in weak_signals[:5]:
            print(f"  ⚠️ {r['name']} 竞价{r['auction_pct']:+.1f}%")
    
    # 汇总
    total = len(results)
    buy_a = len(buy_a_signals)
    danger = len(danger_signals)
    weak = len(weak_signals)
    
    print(f"\n{'─'*40}")
    print(f"📊 竞价情绪汇总（{wave}）")
    print(f"  买点A候选: {buy_a}/{total}只")
    print(f"  高开危险: {danger}只")
    print(f"  低开弱势: {weak}只")
    
    if buy_a >= 2:
        print(f"  💡 买点A机会集中，积极关注！")
    elif buy_a == 1:
        print(f"  💡 1只买点A，保持关注")
    elif danger >= total * 0.5:
        print(f"  🚨 竞价过于亢奋，谨慎追高！")
    else:
        print(f"  ⏳ 等待竞价机会")
    
    # 保存
    save_path = f"/home/dhtaiyi/.openclaw/workspace/stock-data/auction/premarket_{now.strftime('%H%M')}.json"
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, 'w') as f:
        json.dump({
            'time': now.isoformat(),
            'wave': wave,
            'all': results,
            'buy_a': buy_a_signals,
            'danger': danger_signals,
            'weak': weak_signals,
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 数据已保存: {save_path}")
    
    return buy_a_signals

if __name__ == "__main__":
    from datetime import time
    now = datetime.now().time()
    
    if not (time(9, 14) <= now <= time(9, 26) or time(13, 0) <= now <= time(13, 5)):
        print(f"⏰ 当前时间 {now.strftime('%H:%M')} 不在竞价窗口（9:15-9:25 / 13:00-13:05）内")
        print("   但仍可分析昨日候选股的竞价表现（用于复盘）")
    
    signals = analyze_auction_wave()
    
    if signals:
        print(f"\n🎯 共发现 {len(signals)} 只买点A候选！")
