#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取财务指标
"""

import tushare as ts
import os
import sys

def get_financial(stock_code):
    """获取财务指标"""
    token = os.getenv('TUSHARE_TOKEN')
    if not token:
        print("❌ 请先配置 TUSHARE_TOKEN")
        return
    
    pro = ts.pro_api(token)
    
    # 添加市场后缀
    if '.' not in stock_code:
        if stock_code.startswith('6'):
            stock_code = f"{stock_code}.SH"
        else:
            stock_code = f"{stock_code}.SZ"
    
    print(f"📊 获取 {stock_code} 财务指标...")
    
    df = pro.fina_indicator(
        ts_code=stock_code,
        start_date='20230101',
        end_date='20241231'
    )
    
    if df is not None and len(df) > 0:
        # 显示关键指标
        print(f"\n最近 {min(3, len(df))} 期财务数据:\n")
        
        display_cols = ['end_date', 'roe', 'net_profit_ratio', 'gross_profit_margin', 'revenue_growth', 'profit_growth']
        available_cols = [c for c in display_cols if c in df.columns]
        
        print(df[available_cols].head(3).to_string())
        
        # 最新指标
        latest = df.iloc[0]
        print(f"\n📈 最新指标:")
        print(f"  ROE: {latest.get('roe', 'N/A')}%")
        print(f"  净利润率: {latest.get('net_profit_ratio', 'N/A')}%")
        print(f"  毛利率: {latest.get('gross_profit_margin', 'N/A')}%")
        print(f"  营收增长: {latest.get('revenue_growth', 'N/A')}%")
    else:
        print("❌ 未获取到数据")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        get_financial(sys.argv[1])
    else:
        print("用法: python get_financial.py <股票代码>")
        print("示例: python get_financial.py 600519")
