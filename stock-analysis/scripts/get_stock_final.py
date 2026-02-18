#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终版股票数据获取
"""

import requests
import sys

def get_stock(stock_code):
    """获取股票数据"""
    
    # 判断市场
    if stock_code.startswith('6'):
        secid = f"1.{stock_code}"
        market = 'SH'
    else:
        secid = f"0.{stock_code}"
        market = 'SZ'
    
    # 新浪API
    url = f"https://hq.sinajs.cn/list={market}{stock_code}"
    
    headers = {
        "Referer": "https://finance.sina.com.cn",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    print(f"📈 股票: {stock_code} ({market})")
    print("="*40)
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        content = resp.text
        
        if content:
            # 解析返回数据
            data = content.split('=')[1].strip('"').split(',')
            
            if len(data) > 1:
                name = data[0]  # 名称
                open_price = float(data[1]) if data[1] else 0  # 开盘
                price = float(data[2]) if data[2] else 0  # 当前
                high = float(data[3]) if data[3] else 0  # 最高
                low = float(data[4]) if data[4] else 0  # 最低
                
                print(f"📊 名称: {name}")
                print(f"💰 当前: {price:.2f}")
                print(f"📈 最高: {high:.2f}")
                print(f"📉 最低: {low:.2f}")
                print(f"📊 开盘: {open_price:.2f}")
                print("="*40)
                return True
    
    except Exception as e:
        print(f"获取失败: {e}")
    
    print("❌ 获取失败")
    return False

if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else "600519"
    get_stock(code)
