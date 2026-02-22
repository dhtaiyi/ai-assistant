#!/usr/bin/env python3
"""
K线形态分析工具
获取K线数据并分析各种技术形态
"""

import requests

def get_klines(code, days=60):
    """获取K线数据"""
    # 判断市场: sh=上海(1), sz=深圳(0)
    if code.startswith('sh'):
        secid = f"1.{code[2:]}"
    else:
        secid = f"0.{code[2:]}"
    
    url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
    params = {
        'secid': secid,
        'fields1': 'f1,f2,f3,f4,f5,f6',
        'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
        'klt': 101,  # 日K
        'fqt': 1,    # 前复权
        'beg': '20250101',
        'end': '20260222',
    }
    
    headers = {'Referer': 'http://quote.eastmoney.com/'}
    
    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        data = r.json()
        
        if 'data' in data and data['data'] and 'klines' in data['data']:
            return data['data']['klines']
    except:
        pass
    return []

def parse_kline(kline):
    """解析单根K线"""
    fields = kline.split(',')
    return {
        'date': fields[0],
        'open': float(fields[1]),
        'close': float(fields[2]),
        'high': float(fields[3]),
        'low': float(fields[4]),
        'volume': int(fields[5]),
        'amount': float(fields[6]),
        'amplitude': float(fields[7]),  # 振幅
        'change': float(fields[8]),     # 涨跌幅
        'change_amt': float(fields[9]), # 涨跌额
        'turnover': float(fields[10]),   # 换手率
    }

def analyze_pattern(klines):
    """分析K线形态"""
    if len(klines) < 5:
        return ["数据不足"]
    
    # 解析K线
    data = [parse_kline(k) for k in klines[-20:]]  # 取最近20根
    
    patterns = []
    
    # ===== 趋势分析 =====
    changes = [d['change'] for d in data]
    
    # 连续上涨/下跌
    if all(c > 0 for c in changes[-3:]):
        patterns.append("📈 连续3天上涨")
    if all(c > 0 for c in changes[-5:]):
        patterns.append("📈 连续5天上涨")
    if all(c < 0 for c in changes[-3:]):
        patterns.append("📉 连续3天下跌")
    if all(c < 0 for c in changes[-5:]):
        patterns.append("📉 连续5天下跌")
    
    # ===== 成交量分析 =====
    volumes = [d['volume'] for d in data]
    vol_ma5 = sum(volumes[-5:]) / 5
    vol_ma10 = sum(volumes[-10:]) / 10
    
    if volumes[-1] > vol_ma5 * 1.5:
        patterns.append("📊 成交量大幅放大 (放量)")
    elif volumes[-1] < vol_ma5 * 0.5:
        patterns.append("📉 成交量大幅萎缩 (缩量)")
    
    if volumes[-1] > volumes[-2] > volumes[-3]:
        patterns.append("📊 成交量连续3天放大")
    
    # ===== 突破分析 =====
    highs = [d['high'] for d in data[:-1]]
    lows = [d['low'] for d in data[:-1]]
    
    if data[-1]['close'] > max(highs):
        patterns.append("🚀 突破近期新高")
    if data[-1]['close'] < min(lows):
        patterns.append("💔 跌破近期新低")
    
    # ===== 单根K线形态 =====
    last = data[-1]
    body = abs(last['close'] - last['open'])
    shadow = last['high'] - last['low']
    
    if body > 0 and shadow > 0:
        body_ratio = body / shadow
        
        # 十字星
        if body_ratio < 0.3:
            patterns.append("⭐ 十字星 (方向不明)")
        
        # 锤子线/上吊线
        upper_shadow = last['high'] - max(last['open'], last['close'])
        lower_shadow = min(last['open'], last['close']) - last['low']
        
        if lower_shadow > body * 2 and upper_shadow < body * 0.3:
            patterns.append("🔨 锤子线 (看涨信号)")
        if upper_shadow > body * 2 and lower_shadow < body * 0.3:
            patterns.append("🔻 上吊线 (看跌信号)")
        
        # 大阳线/大阴线
        if last['change'] > 7:
            patterns.append("🔥 大阳线 (强势上涨)")
        if last['change'] < -7:
            patterns.append("💥 大阴线 (强势下跌)")
        
        # 乌云盖顶/曙光初现
        if len(data) >= 2:
            prev = data[-2]
            # 乌云盖顶
            if prev['close'] > prev['open'] and last['close'] < prev['close'] and last['open'] > prev['close']:
                patterns.append("☁️ 乌云盖顶 (看跌)")
            # 曙光初现
            if prev['close'] < prev['open'] and last['close'] > prev['close'] and last['open'] < prev['close']:
                patterns.append("🌅 曙光初现 (看涨)")
    
    # ===== 均线分析 =====
    closes = [d['close'] for d in data]
    
    ma5 = sum(closes[-5:]) / 5
    ma10 = sum(closes[-10:]) / 10
    ma20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else ma10
    
    if closes[-1] > ma5:
        patterns.append("✅ 股价站上5日均线")
    else:
        patterns.append("❌ 股价跌破5日均线")
    
    if closes[-1] > ma10:
        patterns.append("✅ 股价站上10日均线")
    else:
        patterns.append("❌ 股价跌破10日均线")
    
    # 均线金叉/死叉
    if ma5 > ma10:
        patterns.append("📈 5日均线金叉10日均线 (多头)")
    else:
        patterns.append("📉 5日均线死叉10日均线 (空头)")
    
    # 均线多头/空头排列
    if ma5 > ma10 > ma20:
        patterns.append("🌟 均线多头排列 (强烈看涨)")
    if ma5 < ma10 < ma20:
        patterns.append("💨 均线空头排列 (强烈看跌)")
    
    return patterns if patterns else ["暂无明显形态"]

def analyze_stock(code, name):
    """分析单只股票"""
    klines = get_klines(code)
    
    if not klines:
        print(f"❌ {name} ({code}) - 获取数据失败")
        return
    
    patterns = analyze_pattern(klines)
    last = parse_kline(klines[-1])
    
    print(f"\n{'='*55}")
    print(f"📊 {name} ({code})")
    print(f"   价格: {last['close']:.2f}  涨跌: {last['change']:+.2f}%")
    print('='*55)
    
    for p in patterns:
        print(f"  {p}")

# 主程序
if __name__ == "__main__":
    stocks = {
        'sh600519': '贵州茅台',
        'sh601318': '中国平安',
        'sh000858': '五粮液',
        'sz000001': '平安银行',
        'sh600036': '招商银行',
        'sh300750': '宁德时代',
    }
    
    print("🕵️ K线形态分析 - 东方财富")
    
    for code, name in stocks.items():
        analyze_stock(code, name)
