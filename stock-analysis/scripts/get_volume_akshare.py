#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
成交量查询脚本 - 使用 akshare
"""

import akshare as ak
import pandas as pd

def get_volume_top10():
    """获取成交量 TOP10"""
    print("📊 正在获取实时行情...")
    
    try:
        df = ak.stock_zh_a_spot_em()
        print(f"✅ 获取到 {len(df)} 只股票")
        
        # 按成交量排序
        df_sorted = df.sort_values('成交量', ascending=False)
        
        print(f"\n📈 成交量 TOP10 ({pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}):")
        print("="*90)
        
        for i, (_, row) in enumerate(df_sorted.head(10).iterrows(), 1):
            code = row['代码']
            name = row['名称']
            price = row['最新价']
            pct = row['涨跌幅']
            vol = row['成交量'] / 10000  # 万手
            amount = row['成交额'] / 100000000  # 亿元
            
            trend = "📈" if pct > 0 else "📉" if pct < 0 else "➡️"
            
            print(f"{i:2}. {code} | {name:>8} | {price:>8.2f}元 | {pct:>+6.2f}% | {vol:>8.1f}万 | {amount:>6.1f}亿 {trend}")
        
        print("="*90)
        
        return df_sorted
        
    except Exception as e:
        print(f"❌ 获取失败: {e}")
        return None

if __name__ == '__main__':
    get_volume_top10()
