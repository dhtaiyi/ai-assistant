#!/usr/bin/env python3
"""
实时行情查询
"""
import requests
import os

# 不使用代理
os.environ['NO_PROXY'] = '*'
os.environ['no_proxy'] = '*'

STOCKS = {
    'sh600519': '贵州茅台',
    'sh601318': '中国平安',
    'sh000858': '五粮液',
    'sz000001': '平安银行',
    's_sh000001': '上证指数',
    's_sz399001': '深证成指',
    's_sh000300': '沪深300',
}

def get_stock(code):
    url = f"http://qt.gtimg.cn/q={code}"
    response = requests.get(url, timeout=10)
    response.encoding = 'gbk'
    return response.text

def parse(code, data):
    if code.startswith('s_'):
        fields = data.split('~')
        if len(fields) > 5:
            return {
                'name': fields[1],
                'current': float(fields[3]),
                'change': float(fields[4]),
                'change_pct': float(fields[5]),
                'type': 'index'
            }
    else:
        fields = data.split('~')
        if len(fields) > 4:
            return {
                'name': fields[1],
                'current': float(fields[3]),
                'yesterday': float(fields[4]),
                'change': float(fields[3]) - float(fields[4]),
                'change_pct': (float(fields[3]) - float(fields[4])) / float(fields[4]) * 100,
                'type': 'stock'
            }
    return None

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # 查询指定股票
        codes = [sys.argv[1]]
    else:
        # 查询默认股票
        codes = list(STOCKS.keys())
    
    print("=" * 55)
    print("📈 实时行情")
    print("=" * 55)
    
    for code in codes:
        data = get_stock(code)
        result = parse(code, data)
        if result:
            emoji = "🟢" if result['change'] >= 0 else "🔴"
            print(f"\n{emoji} {result['name']} ({code})")
            print(f"   当前: {result['current']:.2f}")
            if result['type'] == 'stock':
                print(f"   昨收: {result['yesterday']:.2f}")
            print(f"   涨跌: {result['change']:+.2f} ({result['change_pct']:+.2f}%)")
    
    print("\n" + "=" * 55)
