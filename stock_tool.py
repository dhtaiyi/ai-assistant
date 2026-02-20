#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据查询工具 - 基于akshare
"""

import akshare as ak
import json
from datetime import datetime

def get_stock_daily(stock_code):
    """获取个股日线数据"""
    try:
        # 判断沪市还是深市
        if stock_code.startswith('6'):
            symbol = f"sh{stock_code}"
        else:
            symbol = f"sz{stock_code}"
        
        df = ak.stock_zh_a_daily(symbol=symbol)
        df = df.tail(10)
        # 转换日期类型
        df['date'] = df['date'].astype(str)
        return df.to_dict('records')
    except Exception as e:
        return [{"error": str(e)}]

def get_index_daily(index_code):
    """获取指数日线数据"""
    try:
        if index_code.startswith('sh') or index_code.startswith('sz'):
            symbol = index_code
        else:
            symbol = f"sh{index_code}"
        
        df = ak.stock_zh_index_daily(symbol=symbol)
        return df.tail(10).to_dict('records')
    except Exception as e:
        return {"error": str(e)}

def get_stock_info(stock_code):
    """获取股票基本信息"""
    try:
        if stock_code.startswith('6'):
            symbol = f"sh{stock_code}"
        else:
            symbol = f"sz{stock_code}"
        
        df = ak.stock_zh_a_daily(symbol=symbol)
        if len(df) > 0:
            latest = df.iloc[-1]
            return {
                "code": stock_code,
                "date": str(latest['date']),
                "close": float(latest['close']),
                "open": float(latest['open']),
                "high": float(latest['high']),
                "low": float(latest['low']),
                "volume": float(latest['volume']),
                "amount": float(latest['amount'])
            }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python3 stock_tool.py <命令> [参数]")
        print("命令:")
        print("  daily <股票代码>    - 获取日线数据")
        print("  info <股票代码>      - 获取基本信息")
        print("  index <指数代码>     - 获取指数数据")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "daily" and len(sys.argv) > 2:
        data = get_stock_daily(sys.argv[2])
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif cmd == "info" and len(sys.argv) > 2:
        data = get_stock_info(sys.argv[2])
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif cmd == "index" and len(sys.argv) > 2:
        data = get_index_daily(sys.argv[2])
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print("无效命令")
