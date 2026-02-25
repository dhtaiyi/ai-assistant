#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票实时监控脚本 - 使用 baostock
"""

import baostock as bs
import pandas as pd
import time
import sys
from datetime import datetime

def get_latest_price(code):
    """获取最新价格"""
    # 登录
    lg = bs.login()
    if lg.error_code != '0':
        print(f"❌ 登录失败")
        return None
    
    # 股票代码
    if code.startswith('6'):
        bs_code = f"sh.{code}"
    else:
        bs_code = f"sz.{code}"
    
    # 查询最近5天
    rs = bs.query_history_k_data_plus(
        bs_code,
        "date,open,high,low,close,volume,pct_chg",
        start_date='2026-02-01',
        end_date='2026-02-18',
        frequency="d",
        adjustflag="3"
    )
    
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    
    bs.logout()
    
    if len(data_list) > 0:
        # 取最新一条
        row = data_list[-1]
        return {
            'date': row[0],
            'open': float(row[1]),
            'high': float(row[2]),
            'low': float(row[3]),
            'close': float(row[4]),
            'volume': int(row[5]),
            'pct': float(row[6])
        }
    
    return None

def monitor(code, interval=60):
    """监控股票"""
    print(f"\n🚀 启动 {code} 实时监控...")
    print(f"⏰ 检查间隔: {interval}秒")
    print("-" * 50)
    
    last_close = None
    
    while True:
        data = get_latest_price(code)
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        if data:
            close = data['close']
            pct = data['pct']
            volume = data['volume'] / 10000
            
            trend = "📈" if pct > 0 else "📉" if pct < 0 else "➡️"
            
            print(f"[{timestamp}] {code} | {close:.2f} ({pct:+.2f}%) | {volume:.1f}万 {trend}")
            
            # 检测涨跌
            if last_close and abs(close - last_close) > last_close * 0.02:
                print(f"  🚨 价格波动超过2%!")
            
            last_close = close
        
        time.sleep(interval)

if __name__ == '__main__':
    code = sys.argv[1] if len(sys.argv) > 1 else '600519'
    interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    
    try:
        monitor(code, interval)
    except KeyboardInterrupt:
        print("\n\n👋 监控已停止")
