#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单股票数据获取 - 东方财富
"""

import requests
import sys

def get_stock(stock_code):
    """获取股票数据"""
    
    # 判断市场: 6开头=上海, 0/3开头=深圳
    if stock_code.startswith('6'):
        secid = f"1.{stock_code}"
    else:
        secid = f"0.{stock_code}"
    
    url = f"https://quote.eastmoney.com/api/{secid}.html"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    print(f"📈 股票: {stock_code}")
    print("="*40)
    
    # 方法1: 使用大盘指数API
    try:
        api_url = f"https://push2.eastmoney.com/api/qt/ulist.np/get"
        params = {
            "fltt": 2,
            "fields": "f1,f2,f3,f4,f12,f13,f14",
            "secids": secid,
            "_": "1234567890"
        }
        resp = requests.get(api_url, params=params, headers=headers, timeout=10)
        data = resp.json()
        
        if data.get('data') and len(data['data']) > 0:
            item = data['data'][0]
            name = item.get('f14', stock_code)
            price = item.get('f2', '-')
            change = item.get('f4', '-')
            pct = item.get('f3', '-')
            
            print(f"📊 名称: {name}")
            print(f"💰 价格: {price}")
            print(f"📈 涨跌: {change} ({pct}%)")
            return True
    except Exception as e:
        print(f"方法1失败: {e}")
    
    print("❌ 获取失败")
    return False

if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else "600519"
    get_stock(code)
