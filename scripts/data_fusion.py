#!/usr/bin/env python3
"""
涨停成交额补全模块 V2
新浪涨幅榜 amount字段是主数据源
"""
import requests

_CACHE = {}
_CACHE_TIME = {}
CACHE_TTL = 30

def fetch_sina_top200():
    cache_key = 'sina_top200'
    import time
    now = time.time()
    if cache_key in _CACHE and now - _CACHE_TIME.get(cache_key, 0) < CACHE_TTL:
        return _CACHE[cache_key]
    
    url = 'https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeDataSimple'
    try:
        r = requests.get(url, params={
            'page': 1, 'num': 200,
            'sort': 'changepercent', 'asc': 0,
            'node': 'hs_a'
        }, timeout=10)
        data = r.json()
        result = {}
        for s in data:
            sym = s.get('symbol', '')
            amt = float(s.get('amount', 0))
            result[sym] = amt
        _CACHE[cache_key] = result
        _CACHE_TIME[cache_key] = now
        return result
    except:
        return {}

def enrich_stocks(stocks):
    sina_data = fetch_sina_top200()
    for s in stocks:
        sym = s.get('symbol', '')
        # 标准化代码
        if not (sym.startswith('sh') or sym.startswith('sz')):
            c = sym[0] if sym else ''
            prefix = 'sh' if c in '689' else 'sz'
            sym = prefix + sym
        
        # 新浪涨幅榜amount字段优先
        amt = sina_data.get(sym, 0)
        if s.get('amount', 0) <= 0 and amt > 0:
            s['amount'] = amt
            s['amount_source'] = 'sina'
            s['amount_known'] = True
        elif s.get('amount', 0) > 0:
            s['amount_source'] = 'sina'
            s['amount_known'] = True
        else:
            s['amount_known'] = False
            s['amount_source'] = 'none'
    return stocks

if __name__ == '__main__':
    stocks = [
        {'symbol': 'sh688805', 'name': '健信超导', 'amount': 0},
        {'symbol': 'sh688166', 'name': '博瑞医药', 'amount': 0},
        {'symbol': 'sz300857', 'name': '协创数据', 'amount': 0},
        {'symbol': 'sh688287', 'name': '*ST观典', 'amount': 0},
    ]
    enriched = enrich_stocks(stocks)
    print("成交额补全结果:")
    for s in enriched:
        known = s.get('amount_known', True)
        amt_yi = s.get('amount', 0) / 1e8
        status = f"{amt_yi:.1f}亿" if known else "无数据"
        print(f"  {s['name']}: {status} ({s.get('amount_source')})")
