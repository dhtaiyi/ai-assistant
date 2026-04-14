#!/usr/bin/env python3
"""
股票实时数据获取脚本
数据来源: 腾讯财经 API
"""

import requests
import json
import sys
from datetime import datetime

def get_stock_data(codes_dict):
    """
    codes_dict: {股票名: "sh/sz+代码", ...}
    返回: {股票名: {数据字典}, ...}
    """
    if not codes_dict:
        return {}
    
    codes = ",".join(codes_dict.values())
    url = f"https://qt.gtimg.cn/q={codes}"
    
    try:
        r = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        r.encoding = 'gbk'
        lines = r.text.strip().split('\n')
        
        results = {}
        for line in lines:
            if '=' not in line:
                continue
            key_part = line.split('=')[0].replace('v_', '')
            
            # Find the stock name from codes_dict by value
            stock_name = None
            for name, code in codes_dict.items():
                if code.replace('sz', '').replace('sh', '') in key_part:
                    stock_name = name
                    break
            
            if not stock_name:
                continue
                
            data = line.split('="')[1].rstrip('";')
            fields = data.split('~')
            
            if len(fields) < 40:
                continue
                
            try:
                current = float(fields[3]) if fields[3] else 0
                close = float(fields[4]) if fields[4] else 0
                open_p = float(fields[5]) if fields[5] else 0
                vol = float(fields[6]) if fields[6] else 0  # 成交量(手)
                buy1 = float(fields[9]) if fields[9] else 0   # 买一价
                sell1 = float(fields[19]) if fields[19] else 0 # 卖一价
                high = float(fields[33]) if fields[33] else 0
                low = float(fields[34]) if fields[34] else 0
                price_time = fields[30] if len(fields) > 30 else ""
                
                # 计算涨跌
                if close > 0:
                    change = (current - close) / close * 100
                    change_amount = current - close
                else:
                    change = 0
                    change_amount = 0
                
                # 成交额(万)
                amount = float(fields[37]) if len(fields) > 37 and fields[37] else 0
                
                results[stock_name] = {
                    'code': codes_dict[stock_name],
                    'current': current,
                    'close': close,
                    'open': open_p,
                    'high': high,
                    'low': low,
                    'change_pct': change,
                    'change_amount': change_amount,
                    'vol': vol,  # 手
                    'amount': amount,  # 万
                    'buy1': buy1,
                    'sell1': sell1,
                    'time': price_time,
                }
            except (ValueError, IndexError):
                continue
                
        return results
        
    except Exception as e:
        print(f"Error fetching stock data: {e}", file=sys.stderr)
        return {}


def get_market_index():
    """获取主要指数数据"""
    return get_stock_data({
        "上证指数": "sh000001",
        "深证成指": "sz399001", 
        "创业板指": "sz399006",
        "科创50": "sh000688",
    })


def get_board_leaders():
    """获取连板龙头股数据"""
    return get_stock_data({
        "汇源通信": "sz000586",
        "通鼎互联": "sz002491",
        "金陵药业": "sz000919",
        "中安科": "sh600654",
        "美诺华": "sh603538",
        "津药药业": "sh600488",
        "新能泰山": "sz000720",
        "大胜达": "sh603687",
    })


if __name__ == "__main__":
    import json
    
    # Test
    indices = get_market_index()
    print("=== 主要指数 ===")
    for name, data in indices.items():
        print(f"{name}: {data['current']} ({data['change_pct']:+.2f}%)")
    
    print("\n=== 连板龙头 ===")
    leaders = get_board_leaders()
    for name, data in leaders.items():
        print(f"{name}: {data['current']} ({data['change_pct']:+.2f}%) 最高{data['high']} 最低{data['low']}")
