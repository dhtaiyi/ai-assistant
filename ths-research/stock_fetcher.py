#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同花顺/东方财富股票数据采集器
使用东方财富免费API获取A股数据
"""

import asyncio
from playwright.async_api import async_playwright
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
import aiohttp


class StockDataFetcher:
    """股票数据采集器（使用东方财富API）"""
    
    # 东方财富API地址
    BASE_URL = "https://push2.eastmoney.com/api/qt/stock/get"
    
    # 字段映射
    FIELD_NAMES = {
        'f43': '当前价',
        'f44': '最高价',
        'f45': '最低价',
        'f46': '涨跌额',
        'f57': '股票代码',
        'f58': '股票名称',
        'f169': '涨跌值',
        'f170': '涨跌幅',
        'f47': '成交量',
        'f48': '成交额',
        'f71': '市场',
        'f113': '委比',
        'f117': '总市值',
        'f115': '流通市值',
    }
    
    def __init__(self):
        self.data = {}
    
    async def fetch_stock(self, code: str) -> Optional[Dict]:
        """
        获取单只股票数据
        
        Args:
            code: 股票代码，如 '600519' 或 '000001'
        
        Returns:
            股票数据字典，或None（如果获取失败）
        """
        # 判断市场（上海以6开头，深圳以0或3开头）
        if code.startswith('6'):
            secid = f"1.{code}"
        else:
            secid = f"0.{code}"
        
        url = f"{self.BASE_URL}?fields=f43,f44,f45,f46,f57,f58,f169,f170,f47,f48,f71,f113,f117,f115&secid={secid}&cb=cb"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    text = await resp.text()
                    
                    # 清理JSONP回调
                    if text.startswith("cb("):
                        text = text[3:-1]
                    
                    data = json.loads(text)
                    
                    if data.get('rc') != 0:
                        return None
                    
                    stock_data = data.get('data', {})
                    if not stock_data:
                        return None
                    
                    # 解析数据
                    result = {
                        'code': stock_data.get('f57', ''),
                        'name': stock_data.get('f58', ''),
                        'price': stock_data.get('f43', 0) / 100,  # 转换为元
                        'high': stock_data.get('f44', 0) / 100,
                        'low': stock_data.get('f45', 0) / 100,
                        'change_value': stock_data.get('f169', 0) / 100,
                        'change_percent': stock_data.get('f170', 0) / 100,
                        'volume': stock_data.get('f47', 0),
                        'amount': stock_data.get('f48', 0),
                        'market_cap': stock_data.get('f117', 0),
                        'circulating_cap': stock_data.get('f115', 0),
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    return result
                    
        except Exception as e:
            print(f"获取 {code} 数据失败: {e}")
            return None
    
    async def fetch_batch(self, codes: List[str]) -> List[Dict]:
        """
        批量获取多只股票数据
        
        Args:
            codes: 股票代码列表
        
        Returns:
            股票数据列表
        """
        results = []
        
        for code in codes:
            data = await self.fetch_stock(code)
            if data:
                results.append(data)
        
        return results
    
    async def fetch_index(self, index_code: str = "000001") -> Optional[Dict]:
        """
        获取大盘指数
        
        Args:
            index_code: 指数代码
                000001 - 上证指数
                399001 - 深证成指
                399006 - 创业板指
                000300 - 沪深300
        """
        # 指数使用特殊的市场代码
        if index_code == "000001":
            secid = "1.000001"
        elif index_code in ["399001", "399006", "000300"]:
            secid = f"0.{index_code}"
        else:
            secid = f"0.{index_code}"
        
        url = f"{self.BASE_URL}?fields=f43,f44,f45,f57,f58,f169,f170&secid={secid}&cb=cb"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    text = await resp.text()
                    
                    if text.startswith("cb("):
                        text = text[3:-1]
                    
                    data = json.loads(text)
                    
                    if data.get('rc') != 0:
                        return None
                    
                    stock_data = data.get('data', {})
                    
                    return {
                        'code': stock_data.get('f57', ''),
                        'name': stock_data.get('f58', ''),
                        'price': stock_data.get('f43', 0) / 100,
                        'high': stock_data.get('f44', 0) / 100,
                        'low': stock_data.get('f45', 0) / 100,
                        'change_value': stock_data.get('f169', 0) / 100,
                        'change_percent': stock_data.get('f170', 0) / 100,
                        'timestamp': datetime.now().isoformat()
                    }
                    
        except Exception as e:
            print(f"获取指数 {index_code} 数据失败: {e}")
            return None


async def main():
    """测试"""
    fetcher = StockDataFetcher()
    
    print("=" * 60)
    print("  股票数据采集测试")
    print("=" * 60)
    
    # 测试获取单只股票
    print("\n[1] 获取贵州茅台...")
    stock = await fetcher.fetch_stock("600519")
    if stock:
        print(f"  名称: {stock['name']}")
        print(f"  代码: {stock['code']}")
        print(f"  价格: ¥{stock['price']:.2f}")
        print(f"  涨跌: {stock['change_percent']:+.2f}%")
    
    # 测试获取大盘指数
    print("\n[2] 获取上证指数...")
    index = await fetcher.fetch_index("000001")
    if index:
        print(f"  名称: {index['name']}")
        print(f"  价格: ¥{index['price']:.2f}")
        print(f"  涨跌: {index['change_percent']:+.2f}%")
    
    # 测试批量获取
    print("\n[3] 批量获取...")
    stocks = await fetcher.fetch_batch(["600519", "000001", "600036"])
    print(f"  获取 {len(stocks)} 只股票")
    
    print("\n" + "=" * 60)
    print("  测试完成!")
    print("=" * 60)


if __name__ == '__main__':
    asyncio.run(main())
