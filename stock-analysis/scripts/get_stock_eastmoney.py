#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
东方财富股票数据获取
"""

import requests
import json
import sys

def get_stock_price(stock_code):
    """获取股票价格"""
    
    # 判断市场
    if stock_code.startswith('6'):
        symbol = f"1.{stock_code}"
    else:
        symbol = f"0.{stock_code}"
    
    # 东方财富API
    url = f"https://push2.eastmoney.com/api/qt/stock/get"
    params = {
        "ut": "fa5fd1943c7b386f172d6893dbfba10b",
        "invt": "2",
        "fltt": "2",
        "fields": "f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f55,f57,f58,f59,f60,f116,f117,f162,f167,f168,f169,f170,f171,f173,f177",
        "secid": symbol,
        "_": "1626074955867"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        
        if data.get('data'):
            stock_data = data['data']
            
            print(f"📈 股票: {stock_code}")
            print("="*40)
            
            # 安全获取数值
            def get_val(key, divisor=1):
                val = stock_data.get(key)
                if val is None:
                    return 0
                try:
                    return float(val) / divisor
                except:
                    return 0
            
            # 价格信息
            price = get_val('f43', 1000)
            change = get_val('f46', 1000)
            pct_chg = get_val('f170', 1000)
            
            print(f"💰 最新价: {price:.2f}元")
            print(f"📊 涨跌幅: {change:+.2f} ({pct_chg:+.2f}%)")
            
            # 开盘收盘
            open_price = get_val('f45', 1000)
            high = get_val('f44', 1000)
            low = get_val('f45', 1000)  # 用f45是最低
            prev_close = get_val('f58', 1000)
            
            print(f"\n📉 开盘: {open_price:.2f}")
            print(f"📈 最高: {high:.2f}")
            print(f"📊 最低: {low:.2f}")
            print(f"📌 昨收: {prev_close:.2f}")
            
            # 成交量
            volume = get_val('f47', 1)  # 成交量(手)
            amount = get_val('f48', 100000000)  # 成交额(亿元)
            
            print(f"\n📦 成交量: {volume/10000:.2f}万手")
            print(f"💵 成交额: {amount:.2f}亿元")
            
            # 市值
            total_mv = get_val('f116', 100000000)  # 总市值(亿)
            circ_mv = get_val('f117', 100000000)  # 流通市值(亿)
            
            print(f"\n🏢 总市值: {total_mv:.2f}亿元")
            print(f"💼 流通市值: {circ_mv:.2f}亿元")
            
            print("="*40)
            return True
        else:
            print(f"❌ 未找到股票 {stock_code}")
            return False
            
    except Exception as e:
        print(f"❌ 获取失败: {e}")
        return False

if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else "600519"
    get_stock_price(code)
