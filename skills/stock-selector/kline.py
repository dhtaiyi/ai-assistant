#!/usr/bin/env python3
"""
K线形态分析
"""
import requests
import sys
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

def parse(kline):
    fields = kline.split(',')
    return {
        'date': fields[0],
        'open': float(fields[1]),
        'close': float(fields[2]),
        'high': float(fields[3]),
        'low': float(fields[4]),
        'volume': int(fields[5]),
        'change': float(fields[8])
    }

def analyze(klines):
    if len(klines) < 20:
        return "数据不足"
    
    data = [parse(k) for k in klines[-20:]]
    last = data[-1]
    
    patterns = []
    
    # 连续上涨/下跌
    changes = [d['change'] for d in data]
    if all(c > 0 for c in changes[-3:]):
        patterns.append("📈 连续3天上涨")
    if all(c < 0 for c in changes[-3:]):
        patterns.append("📉 连续3天下跌")
    
    # 成交量
    volumes = [d['volume'] for d in data]
    vol_ma5 = sum(volumes[-5:]) / 5
    
    if volumes[-1] > vol_ma5 * 1.5:
        patterns.append("📊 成交量放大")
    elif volumes[-1] < vol_ma5 * 0.5:
        patterns.append("📉 成交量萎缩")
    
    # 突破
    highs = [d['high'] for d in data[:-1]]
    if last['close'] > max(highs):
        patterns.append("🚀 突破新高")
    
    # K线形态
    body = abs(last['close'] - last['open'])
    shadow = last['high'] - last['low']
    
    if body > 0 and shadow > 0:
        upper = last['high'] - max(last['open'], last['close'])
        lower = min(last['open'], last['close']) - last['low']
        
        if body / shadow < 0.3:
            patterns.append("⭐ 十字星")
        if lower > body * 2 and upper < body * 0.5:
            patterns.append("🔨 锤子线")
        if upper > body * 2 and lower < body * 0.5:
            patterns.append("🔻 上吊线")
    
    # 均线
    closes = [d['close'] for d in data]
    ma5 = sum(closes[-5:]) / 5
    ma10 = sum(closes[-10:]) / 10
    ma20 = sum(closes[-20:]) / 20
    
    if last['close'] > ma5:
        patterns.append("✅ 站上5日均线")
    else:
        patterns.append("❌ 跌破5日均线")
    
    if ma5 > ma10:
        patterns.append("📈 5日金叉10日")
    else:
        patterns.append("📉 5日死叉10日")
    
    if ma5 > ma10 > ma20:
        patterns.append("🌟 均线多头排列")
    if ma5 < ma10 < ma20:
        patterns.append("💨 均线空头排列")
    
    return patterns if patterns else ["暂无明显形态"]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 kline.py <股票代码>")
        print("示例: python3 kline.py sh600519")
        sys.exit(1)
    
    code = sys.argv[1]
    klines = get_klines(code)
    
    if not klines:
        print(f"❌ 无法获取 {code} 的K线数据")
        sys.exit(1)
    
    last = parse(klines[-1])
    patterns = analyze(klines)
    
    print("=" * 55)
    print(f"📊 K线形态分析 ({code})")
    print("=" * 55)
    print(f"\n当前价格: {last['close']:.2f}  涨跌: {last['change']:+.2f}%\n")
    
    print("形态信号:")
    for p in patterns:
        print(f"  {p}")
    
    print("\n" + "=" * 55)
