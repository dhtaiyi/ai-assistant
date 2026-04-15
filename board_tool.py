#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股板块查询工具 - 基于akshare
"""

import akshare as ak
import json
import sys

def get_board_change():
    """获取板块涨跌排行"""
    try:
        df = ak.stock_board_change_em()
        # 清理数据
        df = df[['板块名称', '涨跌幅', '主力净流入', '板块异动总次数']].head(20)
        return df.to_dict('records')
    except Exception as e:
        return [{"error": str(e)}]

def get_industry_fund_flow():
    """获取行业资金流向"""
    try:
        df = ak.stock_fund_flow_industry()
        df = df[['行业', '行业-涨跌幅', '流入资金', '流出资金']].head(20)
        # 转换numpy类型
        records = []
        for _, row in df.iterrows():
            records.append({
                '行业': str(row['行业']),
                '涨跌幅': float(row['行业-涨跌幅']),
                '流入资金': float(row['流入资金']),
                '流出资金': float(row['流出资金'])
            })
        return records
    except Exception as e:
        return [{"error": str(e)}]

def get_concept_fund_flow():
    """获取概念板块资金流向"""
    try:
        df = ak.stock_fund_flow_concept()
        df = df[['行业', '行业-涨跌幅', '流入资金', '流出资金']].head(20)
        # 转换numpy类型
        records = []
        for _, row in df.iterrows():
            records.append({
                '概念': str(row['行业']),
                '涨跌幅': float(row['行业-涨跌幅']),
                '流入资金': float(row['流入资金']),
                '流出资金': float(row['流出资金'])
            })
        return records
    except Exception as e:
        return [{"error": str(e)}]

def get_hot_boards(limit=10):
    """获取热门板块(涨跌幅排行)"""
    try:
        df = ak.stock_board_change_em()
        # 按涨跌幅排序
        df = df.sort_values('涨跌幅', ascending=False)
        df = df[['板块名称', '涨跌幅', '主力净流入']].head(limit)
        return df.to_dict('records')
    except Exception as e:
        return [{"error": str(e)}]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 board_tool.py <命令>")
        print("命令:")
        print("  change      - 板块涨跌排行")
        print("  industry    - 行业资金流向")
        print("  concept     - 概念板块资金流向")
        print("  hot [数量]  - 热门板块排行")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "change":
        data = get_board_change()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif cmd == "industry":
        data = get_industry_fund_flow()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif cmd == "concept":
        data = get_concept_fund_flow()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif cmd == "hot":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        data = get_hot_boards(limit)
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print("无效命令")
