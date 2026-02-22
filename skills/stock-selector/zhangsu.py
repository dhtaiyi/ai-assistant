#!/usr/bin/env python3
"""
涨速榜查询
"""
import requests
import os
os.environ['NO_PROXY'] = '*'

def get_zhangsu(limit=20):
    url = "http://push2.eastmoney.com/api/qt/clist/get"
    params = {
        'pn': 1,
        'pz': limit,
        'po': 1,
        'np': 1,
        'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
        'fltt': 2,
        'invt': 2,
        'fid': 'f3',  # 涨速
        'fs': 'm:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23',
        'fields': 'f2,f3,f4,f12,f14',
    }
    
    r = requests.get(url, params=params, timeout=10,
                     headers={'Referer': 'http://quote.eastmoney.com/'})
    return r.json().get('data', {}).get('diff', [])

if __name__ == "__main__":
    import sys
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    
    stocks = get_zhangsu(limit)
    
    print("=" * 55)
    print("🚀 涨速榜 TOP" + str(limit))
    print("=" * 55)
    
    for i, s in enumerate(stocks, 1):
        name = s.get('f14', '')
        code = s.get('f12', '')
        change = s.get('f4', '0')
        speed = s.get('f3', '0')
        
        emoji = "🟢" if float(change) > 0 else "🔴"
        print(f"{i:2d}. {emoji} {name} ({code})")
        print(f"    涨跌: {change}%  涨速: {speed}%")
    
    print("\n" + "=" * 55)
