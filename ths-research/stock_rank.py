#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据采集器 - 完整版
使用东方财富免费API
"""
import json
import urllib.request
from datetime import datetime
from typing import Dict, List, Optional


class StockFetcher:
    """股票数据采集器"""
    
    # API地址
    STOCK_URL = "https://push2.eastmoney.com/api/qt/stock/get"
    LIST_URL = "https://push2.eastmoney.com/api/qt/clist/get"
    
    def get_stock(self, code: str) -> Optional[Dict]:
        """获取单只股票数据"""
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
                start = text.find('{')
                data = json.loads(text[start:])
                
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
            secid = "1.000001"
        else:
            secid = f"0.{code}"
        
        url = f"{self.STOCK_URL}?fields=f43,f44,f45,f57,f58,f169,f170&secid={secid}"
        
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            with urllib.request.urlopen(req, timeout=10) as response:
                text = response.read().decode('utf-8')
                start = text.find('{')
                data = json.loads(text[start:])
                
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
    
    def get_top_stocks(self, limit: int = 10) -> List[Dict]:
        """涨幅榜"""
        url = f"{self.LIST_URL}?pn=1&ps={limit}&fs=m:0+f:!50&fields=f2,f3,f4,f5,f6,f12,f13,f14,f62&sort=f3"
        
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            with urllib.request.urlopen(req, timeout=10) as response:
                text = response.read().decode('utf-8')
                start = text.find('{')
                data = json.loads(text[start:])
                
                stocks = []
                if data.get('data') and data['data'].get('diff'):
                    for k, v in data['data']['diff'].items():
                        stocks.append({
                            'code': v.get('f12', ''),
                            'name': v.get('f14', '').strip(),
                            'price': v.get('f2', 0) / 100,
                            'change_pct': v.get('f3', 0),
                        })
                stocks.sort(key=lambda x: x['change_pct'], reverse=True)
                return stocks[:limit]
        except Exception as e:
            print(f"错误: {e}")
            return []
    
    def get_bottom_stocks(self, limit: int = 10) -> List[Dict]:
        """跌幅榜"""
        url = f"{self.LIST_URL}?pn=1&ps={limit}&fs=m:0+f:!50&fields=f2,f3,f4,f5,f6,f12,f13,f14,f62&sort=f3"
        
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            with urllib.request.urlopen(req, timeout=10) as response:
                text = response.read().decode('utf-8')
                start = text.find('{')
                data = json.loads(text[start:])
                
                stocks = []
                if data.get('data') and data['data'].get('diff'):
                    for k, v in data['data']['diff'].items():
                        stocks.append({
                            'code': v.get('f12', ''),
                            'name': v.get('f14', '').strip(),
                            'price': v.get('f2', 0) / 100,
                            'change_pct': v.get('f3', 0),
                        })
                stocks.sort(key=lambda x: x['change_pct'])
                return stocks[:limit]
        except Exception as e:
            print(f"错误: {e}")
            return []
    
    def get_volume_stocks(self, limit: int = 10) -> List[Dict]:
        """成交量榜"""
        url = f"{self.LIST_URL}?pn=1&ps={limit}&fs=m:0+f:!50&fields=f2,f3,f5,f6,f12,f13,f14,f62&sort=f6"
        
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            with urllib.request.urlopen(req, timeout=10) as response:
                text = response.read().decode('utf-8')
                start = text.find('{')
                data = json.loads(text[start:])
                
                stocks = []
                if data.get('data') and data['data'].get('diff'):
                    for k, v in data['data']['diff'].items():
                        stocks.append({
                            'code': v.get('f12', ''),
                            'name': v.get('f14', '').strip(),
                            'price': v.get('f2', 0) / 100,
                            'change_pct': v.get('f3', 0),
                            'volume': v.get('f5', 0),
                        })
                stocks.sort(key=lambda x: x['volume'], reverse=True)
                return stocks[:limit]
        except Exception as e:
            print(f"错误: {e}")
            return []


def main():
    """测试"""
    fetcher = StockFetcher()
    
    print("="*60)
    print("  📊 股票数据采集")
    print("="*60)
    
    # 个股
    print("\n[1] 贵州茅台(600519)")
    stock = fetcher.get_stock("600519")
    if stock:
        print(f"    {stock['name']}: ¥{stock['price']:.2f} ({stock['change']})")
    
    # 大盘
    print("\n[2] 上证指数")
    index = fetcher.get_index("000001")
    if index:
        print(f"    {index['name']}: ¥{index['price']:.2f} ({index['change']})")
    
    # 涨幅榜
    print("\n[3] 📈 涨幅榜 TOP10")
    up_stocks = fetcher.get_top_stocks(10)
    for i, s in enumerate(up_stocks, 1):
        print(f"    {i:2}. {s['name']:8} {s['code']:6} ¥{s['price']:6.2f}  {s['change_pct']:+6.2f}%")
    
    # 跌幅榜
    print("\n[4] 📉 跌幅榜 TOP10")
    down_stocks = fetcher.get_bottom_stocks(10)
    for i, s in enumerate(down_stocks, 1):
        print(f"    {i:2}. {s['name']:8} {s['code']:6} ¥{s['price']:6.2f}  {s['change_pct']:+6.2f}%")
    
    # 成交量榜
    print("\n[5] 🔥 成交量榜 TOP10")
    vol_stocks = fetcher.get_volume_stocks(10)
    for i, s in enumerate(vol_stocks, 1):
        vol = s['volume']
        if vol > 100000000:
            vol_str = f"{vol/100000000:.1f}亿"
        elif vol > 10000:
            vol_str = f"{vol/10000:.1f}万"
        else:
            vol_str = str(vol)
        print(f"    {i:2}. {s['name']:8} {s['code']:6} ¥{s['price']:6.2f}  成交量:{vol_str}")
    
    print("\n"+"="*60)
    print(f"  时间: {datetime.now().strftime('%H:%M:%S')}")
    print("="*60)


if __name__ == '__main__':
    main()
