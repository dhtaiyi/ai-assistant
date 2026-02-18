#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
baostock 股票数据查询
"""

import baostock as bs
import pandas as pd
import sys

def get_stock_daily(code, days=10):
    """获取股票日线数据"""
    # 登录
    lg = bs.login()
    if lg.error_code != '0':
        print(f"❌ 登录失败: {lg.error_msg}")
        return
    
    # 股票代码
    if code.startswith('6'):
        bs_code = f"sh.{code}"
    else:
        bs_code = f"sz.{code}"
    
    # 计算日期
    from datetime import datetime, timedelta
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days*2)).strftime('%Y-%m-%d')
    
    # 查询数据
    rs = bs.query_history_k_data_plus(
        bs_code,
        "date,code,open,high,low,close,volume,amount,pct_chg",
        start_date=start_date,
        end_date=end_date,
        frequency="d",
        adjustflag="2"  # 前复权
    )
    
    # 转换为 DataFrame
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    
    df = pd.DataFrame(data_list, columns=rs.fields)
    
    # 登出
    bs.logout()
    
    # 显示结果
    print(f"\n📈 {code} 最近{len(df)}个交易日:")
    print("="*80)
    
    # 只显示最近5天
    recent = df.tail(5).iloc[::-1]  # 反转，最新在前面
    
    for _, row in recent.iterrows():
        date = row['date']
        close = float(row['close'])
        pct = float(row['pct_chg'])
        volume = int(row['volume']) / 10000  # 转换为万手
        
        trend = "📈" if pct > 0 else "📉" if pct < 0 else "➡️"
        
        print(f"{date} | {close:>8.2f} | {pct:>+7.2f}% | {volume:>8.1f}万 {trend}")
    
    print("="*80)
    
    # 统计
    if len(df) > 0:
        closes = df['close'].astype(float)
        pct_chgs = df['pct_chg'].astype(float)
        
        print(f"\n📊 统计:")
        print(f"  最高价: {closes.max():.2f}")
        print(f"  最低价: {closes.min():.2f}")
        print(f"  区间涨幅: {pct_chgs.sum():+.2f}%")
    
    return df

if __name__ == '__main__':
    code = sys.argv[1] if len(sys.argv) > 1 else '600519'
    get_stock_daily(code)
