#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同花顺数据采集器
让OpenClaw通过浏览器读取同花顺数据
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any


class THSCrawler:
    """同花顺数据采集器"""
    
    def __init__(self, browser_controller):
        self.browser = browser_controller
        self.data_dir = '/root/.openclaw/workspace/ths-crawler/data'
        
        # 同花顺常用URL
        self.urls = {
            'home': 'https://www.10jqka.com.cn/',
            'stock_list': 'https://stock.10jqka.com.cn/',
            'quotes': 'https://quote.10jqka.com.cn/',
            'futures': 'https://futures.10jqka.com.cn/',
            'data_center': 'https://data.10jqka.com.cn/',
            'trade': 'https://trade.10jqka.com.cn/',
        }
    
    def open_ths(self):
        """打开同花顺首页"""
        return self.browser.go_to(self.urls['home'])
    
    def open_stock(self, code):
        """
        打开指定股票页面
        同花顺股票URL格式: https://stock.10jqka.com.cn/stockcode/600519.html
        """
        url = f"https://stock.10jqka.com.cn/stockcode/{code}.html"
        return self.browser.go_to(url)
    
    def open_stock_quote(self, code):
        """
        打开股票行情页（同花顺免费）
        """
        url = f"https://quote.10jqka.com.cn/{code}.shtml"
        return self.browser.go_to(url)
    
    def get_stock_price(self, code) -> Dict:
        """
        获取股票实时价格
        """
        # 打开行情页
        self.open_stock_quote(code)
        time.sleep(2)
        
        # 执行JavaScript提取数据
        result = self.browser.run_js('''
            const data = {};
            
            // 价格
            const priceEl = document.querySelector('.stock-price .price, #quotation-entry .price');
            data.price = priceEl?.innerText || '';
            
            // 涨跌幅
            const changeEl = document.querySelector('.stock-price .change, #quotation-entry .change');
            data.change = changeEl?.innerText || '';
            
            // 成交量
            const volEl = document.querySelector('.volume, .deal-num');
            data.volume = volEl?.innerText || '';
            
            // 成交额
            const amountEl = document.querySelector('.amount, .deal-amount');
            data.amount = amountEl?.innerText || '';
            
            // 最高/最低
            const highEl = document.querySelector('.high, .high-price');
            const lowEl = document.querySelector('.low, .low-price');
            data.high = highEl?.innerText || '';
            data.low = lowEl?.innerText || '';
            
            // 开盘价
            const openEl = document.querySelector('.open, .open-price');
            data.open = openEl?.innerText || '';
            
            // 昨收
            const closeEl = document.querySelector('.close, .pre-close');
            data.pre_close = closeEl?.innerText || '';
            
            return data;
        ''')
        
        if result.get('success'):
            return {
                'success': True,
                'code': code,
                'data': result.get('result'),
                'time': datetime.now().isoformat()
            }
        return result
    
    def get_stock_info(self, code) -> Dict:
        """
        获取股票基本信息
        """
        self.open_stock(code)
        time.sleep(2)
        
        result = self.browser.run_js('''
            const info = {};
            
            // 股票名称
            const nameEl = document.querySelector('h1.stock-name, .stockname a, #stockname');
            info.name = nameEl?.innerText || '';
            
            // 股票代码
            const codeEl = document.querySelector('.stock-code, #stockcode');
            info.code = codeEl?.innerText || '';
            
            // 公司简介
            const descEl = document.querySelector('.company-desc, .intro, .about');
            info.description = descEl?.innerText?.substring(0, 500) || '';
            
            // 行业
            const industryEl = document.querySelector('.industry a, .hangye a');
            info.industry = industryEl?.innerText || '';
            
            return info;
        ''')
        
        if result.get('success'):
            return {
                'success': True,
                'code': code,
                'info': result.get('result'),
                'time': datetime.now().isoformat()
            }
        return result
    
    def get_fund_flow(self, code) -> Dict:
        """
        获取资金流向
        """
        self.open_stock(code)
        time.sleep(2)
        
        # 尝试查找资金流向数据
        result = self.browser.run_js('''
            const flow = {};
            
            // 主力净流入
            const mainFlow = document.querySelector('.main-flow, .zjlx, [id*="flow"]');
            flow.main_inflow = mainFlow?.innerText || '';
            
            // 买卖盘
            const buyVol = document.querySelector('.buy-volume, .ma-in');
            const sellVol = document.querySelector('.sell-volume, .ma-out');
            flow.buy_volume = buyVol?.innerText || '';
            flow.sell_volume = sellVol?.innerText || '';
            
            return flow;
        ''')
        
        if result.get('success'):
            return {
                'success': True,
                'code': code,
                'fund_flow': result.get('result'),
                'time': datetime.now().isoformat()
            }
        return result
    
    def get_realtime_quotes(self, codes: List[str]) -> List[Dict]:
        """
        批量获取多只股票实时行情
        codes: 股票代码列表，如 ['600519', '000001']
        """
        results = []
        
        for code in codes:
            try:
                data = self.get_stock_price(code)
                results.append(data)
                time.sleep(1)  # 避免请求过快
            except Exception as e:
                results.append({
                    'code': code,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def get_market_summary(self) -> Dict:
        """
        获取大盘行情摘要
        """
        result = self.browser.run_js('''
            const summary = {};
            
            // 上证指数
            const shEl = document.querySelector('[data-index="000001"] .index-price, .sh-index .price');
            const shChange = document.querySelector('[data-index="000001"] .index-change, .sh-index .change');
            summary.shanghai = {
                price: shEl?.innerText || '',
                change: shChange?.innerText || ''
            };
            
            // 深证成指
            const szEl = document.querySelector('[data-index="399001"] .index-price, .sz-index .price');
            const szChange = document.querySelector('[data-index="399001"] .index-change, .sz-index .change');
            summary.shenzhen = {
                price: szEl?.innerText || '',
                change: szChange?.innerText || ''
            };
            
            // 创业板
            const cyEl = document.querySelector('[data-index="399006"] .index-price, .cy-index .price');
            const cyChange = document.querySelector('[data-index="399006"] .index-change, .cy-index .change');
            summary.chuangye = {
                price: cyEl?.innerText || '',
                change: cyChange?.innerText || ''
            };
            
            return summary;
        ''')
        
        if result.get('success'):
            return {
                'success': True,
                'market': result.get('result'),
                'time': datetime.now().isoformat()
            }
        return result
    
    def get_stock_holders(self, code) -> Dict:
        """
        获取股东信息
        """
        # 东方财富等网站股东数据更准确，这里尝试同花顺
        self.open_stock(code)
        time.sleep(2)
        
        result = self.browser.run_js('''
            const holders = {};
            
            // 十大股东
            const mainHolders = document.querySelector('.holder-list, .top-holders, #holder');
            holders.top_holders = mainHolders?.innerText?.substring(0, 2000) || '';
            
            return holders;
        ''')
        
        if result.get('success'):
            return {
                'success': True,
                'code': code,
                'holders': result.get('result'),
                'time': datetime.now().isoformat()
            }
        return result
    
    def save_data(self, data: Dict, filename: str):
        """
        保存采集数据到文件
        """
        import os
        os.makedirs(self.data_dir, exist_ok=True)
        
        filepath = f"{self.data_dir}/{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def export_csv(self, data: List[Dict], filename: str):
        """
        导出数据到CSV
        """
        import os
        os.makedirs(self.data_dir, exist_ok=True)
        
        filepath = f"{self.data_dir}/{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        if not data:
            return None
        
        # 获取所有键
        keys = set()
        for item in data:
            if isinstance(item, dict):
                keys.update(item.keys())
        
        # 写入CSV
        with open(filepath, 'w', encoding='utf-8-sig') as f:
            f.write(','.join(keys) + '\n')
            for item in data:
                row = []
                for key in keys:
                    val = item.get(key, '')
                    if isinstance(val, dict):
                        val = json.dumps(val, ensure_ascii=False)
                    val = str(val).replace(',', '，').replace('\n', ' ')
                    row.append(val)
                f.write(','.join(row) + '\n')
        
        return filepath


# 便捷函数
def get_realtime_price(crawler, code):
    """获取单只股票实时价格"""
    return crawler.get_stock_price(code)


def get_batch_quotes(crawler, codes):
    """批量获取多只股票行情"""
    return crawler.get_realtime_quotes(codes)


def get_market_overview(crawler):
    """获取大盘整体情况"""
    return crawler.get_market_summary()


if __name__ == '__main__':
    # 测试
    from openclaw_integration import OpenClawBrowser
    
    print("=" * 60)
    print("  同花顺数据采集测试")
    print("=" * 60)
    print()
    
    browser = OpenClawBrowser()
    crawler = THSCrawler(browser)
    
    # 测试大盘
    print("📊 获取大盘行情...")
    result = crawler.get_market_summary()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print()
    print("=" * 60)
