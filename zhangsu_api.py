#!/usr/bin/env python3
"""
涨速榜API - 东方财富
获取涨速最快的股票
"""

import requests
import json

class ZhangSuBang:
    """东方财富涨速榜API"""
    
    BASE_URL = "http://push2.eastmoney.com/api/qt/clist/get"
    
    @staticmethod
    def get_rise_speed(limit=50):
        """
        获取涨速榜
        
        参数:
            limit: 获取数量，默认50
            
        返回:
            list: 股票列表
        """
        params = {
            'pn': 1,
            'pz': limit,
            'po': 1,  # 降序
            'np': 1,
            'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
            'fltt': 2,
            'invt': 2,
            'fid': 'f3',  # 涨速
            'fs': 'm:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23',  # 沪深A股
            'fields': 'f1,f2,f3,f4,f5,f6,f12,f13,f14,f100',
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'http://quote.eastmoney.com/'
        }
        
        try:
            r = requests.get(ZhangSuBang.BASE_URL, params=params, headers=headers, timeout=10)
            data = r.json()
            
            if 'data' in data and data['data'] and 'diff' in data['data']:
                return data['data']['diff']
            return []
        except Exception as e:
            print(f"获取涨速榜失败: {e}")
            return []
    
    @staticmethod
    def get_rise_top(limit=20):
        """获取涨幅榜"""
        params = {
            'pn': 1,
            'pz': limit,
            'po': 1,
            'np': 1,
            'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
            'fltt': 2,
            'invt': 2,
            'fid': 'f4',  # 涨幅
            'fs': 'm:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23',
            'fields': 'f1,f2,f3,f4,f5,f6,f12,f13,f14,f100',
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'http://quote.eastmoney.com/'
        }
        
        try:
            r = requests.get(ZhangSuBang.BASE_URL, params=params, headers=headers, timeout=10)
            data = r.json()
            
            if 'data' in data and data['data'] and 'diff' in data['data']:
                return data['data']['diff']
            return []
        except Exception as e:
            print(f"获取涨幅榜失败: {e}")
            return []


def print_zhangsu(limit=20):
    """打印涨速榜"""
    stocks = ZhangSuBang.get_rise_speed(limit)
    
    print("=" * 60)
    print("🚀 涨速榜 - 东方财富")
    print("=" * 60)
    
    for i, s in enumerate(stocks[:limit], 1):
        name = s.get('f14', '')
        code = s.get('f12', '')
        price = s.get('f2', '-')
        change_pct = s.get('f4', '0')
        speed = s.get('f3', '0')
        
        if price != '-':
            emoji = "🟢" if float(change_pct) > 0 else "🔴"
            print(f"{i:2d}. {emoji} {name} ({code})")
            print(f"     价格: {price}  涨跌: {change_pct}%  涨速: {speed}%")
    
    print("=" * 60)


if __name__ == "__main__":
    print_zhangsu(20)
