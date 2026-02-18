#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取股票日线数据
"""

import tushare as ts
import os
import sys

def get_daily(stock_code, days=30):
    """获取日线数据"""
    token = os.getenv('TUSHARE_TOKEN')
    if not token:
        print("❌ 请先配置 TUSHARE_TOKEN")
        print("export TUSHARE_TOKEN='your_token'")
        return
    
    pro = ts.pro_api(token)
    
    # 添加市场后缀
    if '.' not in stock_code:
        if stock_code.startswith('6'):
            stock_code = f"{stock_code}.SH"
        else:
            stock_code = f"{stock_code}.SZ"
    
    # 计算日期
    import datetime
    end_date = datetime.datetime.now().strftime('%Y%m%d')
    start_date = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime('%Y%m%d')
    
    print(f"📈 获取 {stock_code} 日线数据...")
    
    df = pro.daily(
        ts_code=stock_code,
        start_date=start_date,
        end_date=end_date
    )
    
    if df is not None and len(df) > 0:
        print(f"\n最近 {min(5, len(df))} 天数据:\n")
        print(df.head(5)[['trade_date', 'open', 'high', 'low', 'close', 'vol']].to_string())
        
        # 计算涨跌幅
        first_close = df.iloc[-1]['close']
        last_close = df.iloc[0]['close']
        change = (last_close - first_close) / first_close * 100
        
        print(f"\n📊 月度涨跌: {change:.2f}%")
    else:
        print("❌ 未获取到数据")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        get_daily(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 30)
    else:
        print("用法: python get_stock_daily.py <股票代码> [天数]")
        print("示例: python get_stock_daily.py 600519 30")
