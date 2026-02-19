#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据采集器 - 简单版
使用东方财富免费API
"""
import json
import urllib.request
import urllib.parse
from datetime import datetime
from typing import Dict, List, Optional


class StockFetcher:
    """股票数据采集器"""
    
    # 东方财富API
    STOCK_URL = "https://push2.eastmoney.com/api/qt/stock/get"
    INDEX_URL = "https://push2.eastmoney.com/api/qt/stock/get"
    
    def get_stock(self, code: str) -> Optional[Dict]:
        """获取单只股票数据"""
        # 判断市场
        if code.startswith('6'):
            secid = f"1.{code}"
        else:
            secid = f"0.{code}"
        
        url = f"{self.STOCK_URL}?fields=f43,f44,f45,f46,f57,f58,f169,f170,f47,f48,f71,f113,f117,f115&secid={secid}"
        
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            with urllib.request.urlopen(req, timeout=10) as response:
                text = response.read().decode('utf-8')
                
                # 提取JSON
                start = text.find('{')
                end = text.rfind('}') + 1
                if start < 0 or end <= 0:
                    return None
                
                data = json.loads(text[start:end])
                
                if data.get('rc') != 0:
                    return None
                
                stock = data.get('data', {})
                if not stock:
                    return None
                
                return {
                    'code': stock.get('f57', ''),
                    'name': stock.get('f58', ''),
                    'price': stock.get('f43', 0) / 100,
                    'change': f"{stock.get('f170', 0) / 100:+.2f}%",
                    'high': stock.get('f44', 0) / 100,
                    'low': stock.get('f45', 0) / 100,
                    'volume': stock.get('f47', 0),
                    'amount': stock.get('f48', 0),
                    'time': datetime.now().strftime('%H:%M:%S')
                }
        except Exception as e:
            print(f"错误: {e}")
            return None
    
    def get_index(self, code: str = "000001") -> Optional[Dict]:
        """获取大盘指数"""
        if code == "000001":
            secid = "1.000001"  # 上证
        else:
            secid = f"0.{code}"
        
        url = f"{self.INDEX_URL}?fields=f43,f44,f45,f57,f58,f169,f170&secid={secid}"
        
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            with urllib.request.urlopen(req, timeout=10) as response:
                text = response.read().decode('utf-8')
                
                start = text.find('{')
                end = text.rfind('}') + 1
                if start < 0 or end <= 0:
                    return None
                
                data = json.loads(text[start:end])
                
                if data.get('rc') != 0:
                    return None
                
                index = data.get('data', {})
                
                return {
                    'code': index.get('f57', ''),
                    'name': index.get('f58', ''),
                    'price': index.get('f43', 0) / 100,
                    'change': f"{index.get('f170', 0) / 100:+.2f}%",
                    'high': index.get('f44', 0) / 100,
                    'low': index.get('f45', 0) / 100,
                    'time': datetime.now().strftime('%H:%M:%S')
                }
        except Exception as e:
            print(f"错误: {e}")
            return None
    
    def get_batch(self, codes: List[str]) -> List[Dict]:
        """批量获取"""
        results = []
        for code in codes:
            stock = self.get_stock(code)
            if stock:
                results.append(stock)
        return results


def main():
    """测试"""
    fetcher = StockFetcher()
    
    print("=" * 60)
    print("  股票数据采集测试")
    print("=" * 60)
    
    # 单只股票
    print("\n[1] 贵州茅台(600519)")
    stock = fetcher.get_stock("600519")
    if stock:
        print(f"  名称: {stock['name']}")
        print(f"  价格: ¥{stock['price']:.2f}")
        print(f"  涨跌: {stock['change']}")
    
    # 大盘指数
    print("\n[2] 上证指数")
    index = fetcher.get_index("000001")
    if index:
        print(f"  名称: {index['name']}")
        print(f"  价格: ¥{index['price']:.2f}")
        print(f"  涨跌: {index['change']}")
    
    # 批量获取
    print("\n[3] 批量获取")
    stocks = fetcher.get_batch(["600519", "000001", "600036"])
    print(f"  获取 {len(stocks)} 只股票")
    for s in stocks:
        print(f"    {s['name']}: ¥{s['price']:.2f} ({s['change']})")
    
    print("\n" + "=" * 60)
    print("  测试完成!")
    print("=" * 60)


if __name__ == '__main__':
    main()
