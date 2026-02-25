#!/usr/bin/env python3
"""
放量上影线选股
筛选条件：昨日放量(量比≥1.2) + 上影线>实体80% + 今日高开
"""
import requests
import os
os.environ['NO_PROXY'] = '*'

def get_klines(code, days=15):
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
        return data['data']['klines'][-days:]
    return []

def parse_kline(kline):
    fields = kline.split(',')
    return {
        'open': float(fields[1]),
        'close': float(fields[2]),
        'high': float(fields[3]),
        'volume': int(fields[5]),
    }

def analyze(klines):
    if len(klines) < 8:
        return None
    
    data = [parse_kline(k) for k in klines]
    
    prev = data[-2]
    today = data[-1]
    
    # 昨日上影线
    prev_body = abs(prev['close'] - prev['open'])
    prev_upper = prev['high'] - max(prev['open'], prev['close'])
    has_upper = prev_upper > prev_body * 0.8
    
    # 昨日放量
    vol_ma5 = sum(d['volume'] for d in data[-7:-2]) / 5
    vol_ratio = prev['volume'] / vol_ma5 if vol_ma5 > 0 else 0
    is_fangliang = vol_ratio >= 1.2
    
    # 今日高开
    is_gaokai = today['open'] > prev['close']
    
    if has_upper and is_fangliang and is_gaokai:
        return {
            'prev_upper': prev_upper,
            'vol_ratio': vol_ratio,
            'today_open': today['open'],
            'today_change': (today['close'] - today['open']) / today['open'] * 100,
        }
    return None

def find_stocks(limit=20):
    url = "http://push2.eastmoney.com/api/qt/clist/get"
    params = {
        'pn': 1,
        'pz': 200,
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
    for s in stocks:
        if float(s['f4']) < 0.5:
            continue
        
        code = f"sh{s['f12']}" if str(s['f12']).startswith('6') else f"sz{s['f12']}"
        klines = get_klines(code)
        
        if not klines or len(klines) < 8:
            continue
        
        result = analyze(klines)
        if result:
            results.append({
                'name': s['f14'],
                'code': code,
                'change': s['f4'],
                **result
            })
        
        if len(results) >= limit:
            break
    
    return results

if __name__ == "__main__":
    results = find_stocks(20)
    
    print("=" * 65)
    print("📊 放量上影线 + 高开选股")
    print("=" * 65)
    
    if results:
        for i, r in enumerate(results, 1):
            print(f"\n{i}. 🟢 {r['name']} ({r['code']})")
            print(f"   今日涨幅: {r['change']}%")
            print(f"   昨日上影: {r['prev_upper']:.2f} | 量比: {r['vol_ratio']:.1f}x")
            print(f"   今日高开: {r['today_open']:.2f} | 走势: {r['today_change']:+.2f}%")
    else:
        print("\n暂无符合条件的股票")
    
    print("\n" + "=" * 65)
