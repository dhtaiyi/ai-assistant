#!/usr/bin/env python3
"""
横盘突破形态选股器
从涨幅榜中筛选横盘突破形态的个股
"""

import requests

def get_klines(code, days=60):
    """获取K线数据"""
    if code.startswith('sh'):
        secid = f"1.{code[2:]}"
    else:
        secid = f"0.{code[2:]}"
    
    url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
    params = {
        'secid': secid,
        'fields1': 'f1,f2,f3,f4,f5,f6',
        'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
        'klt': 101,
        'fqt': 1,
        'beg': '20250101',
        'end': '20260222',
    }
    
    r = requests.get(url, params=params, timeout=10,
                     headers={'Referer': 'http://quote.eastmoney.com/'})
    data = r.json()
    
    if 'data' in data and data['data'] and 'klines' in data['data']:
        return data['data']['klines']
    return []

def parse_kline(kline):
    fields = kline.split(',')
    return {
        'date': fields[0],
        'close': float(fields[2]),
        'high': float(fields[3]),
        'low': float(fields[4]),
        'volume': int(fields[5]),
        'change': float(fields[8])
    }

def analyze_breakout(klines):
    """分析横盘突破形态"""
    if len(klines) < 30:
        return None, "数据不足"
    
    data = [parse_kline(k) for k in klines[-30:]]
    
    highs = [d['high'] for d in data]
    lows = [d['low'] for d in data]
    volumes = [d['volume'] for d in data]
    
    today = data[-1]
    vol_ma10 = sum(volumes[-10:]) / 10
    
    price_range = (max(highs[-10:]) - min(lows[-10:])) / max(highs[-10:]) * 100
    
    is_breakout = False
    reason = ""
    
    # 放量突破
    if today['change'] > 3 and today['volume'] > vol_ma10 * 1.5 and price_range < 15:
        is_breakout = True
        reason = "放量突破"
    
    # 横盘整理后放量
    vol_ma20 = sum(volumes[-20:-5]) / 15
    if today['volume'] > vol_ma20 * 1.8 and price_range < 12:
        avg_change = sum(d['change'] for d in data[-5:]) / 5
        if -2 < avg_change < 2:
            is_breakout = True
            reason = "横盘整理后放量"
    
    # 突破20日高点
    high_20 = max([d['close'] for d in data[:-5]])
    if today['close'] > high_20 and today['change'] > 2:
        if today['volume'] > vol_ma10 * 1.3:
            is_breakout = True
            reason = "突破20日高点"
    
    # 均线发散突破
    ma5 = sum([d['close'] for d in data[-5:]]) / 5
    ma10 = sum([d['close'] for d in data[-10:]]) / 10
    ma20 = sum([d['close'] for d in data[-20:]]) / 20
    
    ma_spread = abs(ma5 - ma10) + abs(ma10 - ma20)
    avg_spread = sum(abs(sum([d['close'] for d in data[i:i+5]])/5 - sum([d['close'] for d in data[i:i+10]])/10) 
                     for i in range(10, 20)) / 10
    
    if ma_spread < avg_spread * 0.3 and today['change'] > 2:
        if today['volume'] > vol_ma10:
            is_breakout = True
            reason = "均线发散突破"
    
    if is_breakout:
        return {'change': today['change'], 'reason': reason}, ""
    return None, "不符合形态"

def find_breakout_stocks(limit=10):
    """查找横盘突破形态个股"""
    # 获取涨幅榜
    url = "http://push2.eastmoney.com/api/qt/clist/get"
    params = {
        'pn': 1,
        'pz': 100,
        'po': 1,
        'np': 1,
        'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
        'fltt': 2,
        'invt': 2,
        'fid': 'f4',
        'fs': 'm:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23',
        'fields': 'f2,f3,f4,f6,f12,f14',
    }
    
    r = requests.get(url, params=params, timeout=10,
                     headers={'Referer': 'http://quote.eastmoney.com/'})
    stocks = r.json().get('data', {}).get('diff', [])
    
    breakout_stocks = []
    
    for s in stocks[:50]:
        code = f"sh{s['f12']}" if str(s['f12']).startswith('6') else f"sz{s['f12']}"
        name = s['f14']
        change = s['f4']
        
        if float(change) < 3:
            continue
        
        klines = get_klines(code)
        if not klines:
            continue
        
        result, msg = analyze_breakout(klines)
        if result:
            breakout_stocks.append({
                'name': name,
                'code': code,
                'change': change,
                'reason': result['reason']
            })
        
        if len(breakout_stocks) >= limit:
            break
    
    return breakout_stocks

def print_breakout():
    """打印横盘突破个股"""
    stocks = find_breakout_stocks(10)
    
    print("=" * 60)
    print("🚀 横盘突破形态个股")
    print("=" * 60)
    
    if stocks:
        for i, s in enumerate(stocks, 1):
            print(f"{i}. 🟢 {s['name']} ({s['code']})")
            print(f"   涨幅: {s['change']}%  |  形态: {s['reason']}")
            print()
    else:
        print("暂无符合条件的股票")
    
    print("=" * 60)

if __name__ == "__main__":
    print_breakout()
