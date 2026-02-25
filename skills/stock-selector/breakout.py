#!/usr/bin/env python3
"""
横盘突破选股
"""
import requests
import os
os.environ['NO_PROXY'] = '*'

def get_klines(code):
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
        'close': float(fields[2]),
        'high': float(fields[3]),
        'volume': int(fields[5]),
        'change': float(fields[8])
    }

def analyze_breakout(klines):
    if len(klines) < 30:
        return None
    
    data = [parse_kline(k) for k in klines[-30:]]
    
    today = data[-1]
    vol_ma10 = sum(d['volume'] for d in data[-10:]) / 10
    
    # 突破20日高点
    high_20 = max(d['close'] for d in data[:-5])
    
    if today['close'] > high_20 and today['change'] > 2 and today['volume'] > vol_ma10 * 1.3:
        return {'reason': '突破20日高点', 'change': today['change']}
    
    # 放量突破
    if today['change'] > 3 and today['volume'] > vol_ma10 * 1.5:
        return {'reason': '放量突破', 'change': today['change']}
    
    return None

def find_breakout(limit=10):
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
    
    results = []
    for s in stocks[:50]:
        code = f"sh{s['f12']}" if str(s['f12']).startswith('6') else f"sz{s['f12']}"
        name = s['f14']
        
        if float(s['f4']) < 3:
            continue
        
        klines = get_klines(code)
        if not klines:
            continue
        
        result = analyze_breakout(klines)
        if result:
            results.append({'name': name, 'code': code, 'change': s['f4'], **result})
        
        if len(results) >= limit:
            break
    
    return results

if __name__ == "__main__":
    results = find_breakout(10)
    
    print("=" * 60)
    print("🚀 横盘突破选股")
    print("=" * 60)
    
    for i, r in enumerate(results, 1):
        print(f"\n{i}. 🟢 {r['name']} ({r['code']})")
        print(f"   涨幅: {r['change']}%  形态: {r['reason']}")
    
    print("\n" + "=" * 60)
