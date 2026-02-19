#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同花顺高级数据采集器
支持登录、数据导出、定时任务
"""

import json
import time
import csv
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path


class THSAdvancedCrawler:
    """同花顺高级数据采集器"""
    
    def __init__(self, browser_controller):
        self.browser = browser_controller
        self.data_dir = '/root/.openclaw/workspace/ths-crawler/data'
        self.report_dir = '/root/.openclaw/workspace/ths-crawler/reports'
        
        # 确保目录存在
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.report_dir, exist_ok=True)
        
        # 缓存
        self.price_cache = {}
        self.cache_timeout = 60  # 秒
        
        # 登录状态
        self.is_logged_in = False
        self.last_login_time = None
    
    # ==================== 登录管理 ====================
    
    def login(self, username: str, password: str) -> Dict:
        """
        同花顺登录
        注意：同花顺可能需要验证码
        """
        self.browser.go_to('https://www.10jqka.com.cn/user/login/')
        time.sleep(2)
        
        # 输入账号密码
        self.browser.type('#username', username)
        self.browser.type('#password', password)
        
        # 点击登录
        self.browser.click('#loginBtn')
        time.sleep(3)
        
        # 检查登录状态
        result = self.check_login_status()
        
        if result.get('success'):
            self.is_logged_in = True
            self.last_login_time = datetime.now()
        
        return result
    
    def check_login_status(self) -> Dict:
        """检查登录状态"""
        result = self.browser.run_js('''
            const userInfo = document.querySelector('.user-name, .nick-name, .user-info');
            const loginBtn = document.querySelector('#loginBtn, .login-btn');
            
            if (userInfo) {
                return { logged_in: true, message: '已登录' };
            } else if (loginBtn) {
                return { logged_in: false, message: '未登录' };
            } else {
                return { logged_in: false, message: '状态未知' };
            }
        ''')
        
        return result
    
    def logout(self):
        """退出登录"""
        self.browser.click('.logout-btn, #logout')
        self.is_logged_in = False
        self.last_login_time = None
    
    # ==================== 数据采集 ====================
    
    def get_stock_realtime_data(self, code: str, use_cache: bool = True) -> Dict:
        """
        获取股票实时数据（带缓存）
        """
        # 检查缓存
        if use_cache and code in self.price_cache:
            cached = self.price_cache[code]
            if (datetime.now() - cached['time']).seconds < self.cache_timeout:
                return cached['data']
        
        # 采集数据
        url = f"https://stock.10jqka.com.cn/quotes/{code}.html"
        self.browser.go_to(url)
        time.sleep(2)
        
        result = self.browser.run_js('''
            (function() {
                const data = {
                    code: ''' + f'"{code}"' + ''',
                    timestamp: new Date().toISOString(),
                    price: null,
                    change: null,
                    change_percent: null,
                    volume: null,
                    amount: null,
                    open: null,
                    high: null,
                    low: null,
                    pre_close: null,
                    turnover_rate: null,
                    pe: null,
                    market_cap: null
                };
                
                // 尝试多种选择器
                const priceSelectors = [
                    '.stock-price .price',
                    '#quotation-entry .price',
                    '.current-price',
                    '.price-current'
                ];
                
                for (const sel of priceSelectors) {
                    const el = document.querySelector(sel);
                    if (el) {
                        data.price = el.innerText;
                        break;
                    }
                }
                
                // 涨跌幅
                const changeSelectors = [
                    '.stock-change .change',
                    '#quotation-entry .change',
                    '.change-percent'
                ];
                
                for (const sel of changeSelectors) {
                    const el = document.querySelector(sel);
                    if (el) {
                        const text = el.innerText;
                        data.change = text.split('/')[0]?.trim();
                        data.change_percent = text.split('/')[1]?.trim() || text;
                        break;
                    }
                }
                
                // 成交量
                const volEl = document.querySelector('.volume-num, .deal-num, .volume');
                if (volEl) data.volume = volEl.innerText;
                
                // 成交额
                const amtEl = document.querySelector('.amount-num, .deal-amount, .amount');
                if (amtEl) data.amount = amtEl.innerText;
                
                // 盘口数据
                const openEl = document.querySelector('.open-price, .open');
                const highEl = document.querySelector('.high-price, .high');
                const lowEl = document.querySelector('.low-price, .low');
                const closeEl = document.querySelector('.pre-close, .previous-close');
                
                if (openEl) data.open = openEl.innerText;
                if (highEl) data.high = highEl.innerText;
                if (lowEl) data.low = lowEl.innerText;
                if (closeEl) data.pre_close = closeEl.innerText;
                
                return data;
            })();
        ''')
        
        if result.get('success'):
            # 更新缓存
            self.price_cache[code] = {
                'data': result,
                'time': datetime.now()
            }
        
        return result
    
    def get_market_index(self) -> Dict:
        """
        获取主要指数
        """
        self.browser.go_to('https://www.10jqka.com.cn/market/')
        time.sleep(2)
        
        result = self.browser.run_js('''
            (function() {
                const indices = {};
                
                // 上证指数
                const sh = document.querySelector('[data-code="000001"], .sh-index');
                if (sh) {
                    indices.shanghai = {
                        name: '上证指数',
                        price: sh.querySelector('.price, .current')?.innerText || '',
                        change: sh.querySelector('.change, .percent')?.innerText || ''
                    };
                }
                
                // 深证成指
                const sz = document.querySelector('[data-code="399001"], .sz-index');
                if (sz) {
                    indices.shenzhen = {
                        name: '深证成指',
                        price: sz.querySelector('.price, .current')?.innerText || '',
                        change: sz.querySelector('.change, .percent')?.innerText || ''
                    };
                }
                
                // 创业板
                const cy = document.querySelector('[data-code="399006"], .cy-index');
                if (cy) {
                    indices.chuangye = {
                        name: '创业板指',
                        price: cy.querySelector('.price, .current')?.innerText || '',
                        change: cy.querySelector('.change, .percent')?.innerText || ''
                    };
                }
                
                // 沪深300
                const hs = document.querySelector('[data-code="000300"], .hs300');
                if (hs) {
                    indices.hs300 = {
                        name: '沪深300',
                        price: hs.querySelector('.price, .current')?.innerText || '',
                        change: hs.querySelector('.change, .percent')?.innerText || ''
                    };
                }
                
                return indices;
            })();
        ''')
        
        return result
    
    def get_stock_list(self, market: str = 'a') -> List[Dict]:
        """
        获取股票列表
        market: 'a' - A股, 'hk' - 港股, 'us' - 美股
        """
        urls = {
            'a': 'https://stock.10jqka.com.cn/stocklist/',
            'hk': 'https://stock.10jqka.com.cn/hkstock/',
            'us': 'https://stock.10jqka.com.cn/usstock/'
        }
        
        self.browser.go_to(urls.get(market, urls['a']))
        time.sleep(3)
        
        result = self.browser.run_js('''
            (function() {
                const stocks = [];
                const rows = document.querySelectorAll('table tr, .stock-list li, .stock-item');
                
                rows.forEach((row, i) => {
                    if (i > 100) return; // 限制数量
                    
                    const cells = row.querySelectorAll('td, .stock-info');
                    if (cells.length >= 2) {
                        stocks.push({
                            code: cells[0]?.innerText?.trim() || '',
                            name: cells[1]?.innerText?.trim() || ''
                        });
                    }
                });
                
                return stocks;
            })();
        ''')
        
        return result.get('result', []) if result.get('success') else []
    
    # ==================== 数据导出 ====================
    
    def save_to_json(self, data: Any, filename: str) -> str:
        """保存到JSON文件"""
        filepath = os.path.join(self.data_dir, f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def save_to_csv(self, data: List[Dict], filename: str) -> str:
        """保存到CSV文件"""
        if not data:
            return None
        
        filepath = os.path.join(self.data_dir, f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        
        keys = set()
        for item in data:
            if isinstance(item, dict):
                keys.update(item.keys())
        
        with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(keys))
            writer.writeheader()
            writer.writerows(data)
        
        return filepath
    
    def generate_report(self, data: Dict, title: str = "数据报告") -> str:
        """生成HTML报告"""
        filepath = os.path.join(self.report_dir, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
        
        html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        h1 {{ color: #333; }}
        .data-card {{ background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        pre {{ background: #f8f8f8; padding: 10px; border-radius: 4px; overflow-x: auto; }}
        .timestamp {{ color: #999; font-size: 12px; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <p class="timestamp">生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <div class="data-card">
        <pre>{json.dumps(data, ensure_ascii=False, indent=2)}</pre>
    </div>
</body>
</html>
'''
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return filepath
    
    # ==================== 定时采集 ====================
    
    def monitor_prices(self, codes: List[str], interval: int = 60, max_iterations: int = 100):
        """
        监控股票价格
        codes: 股票代码列表
        interval: 采集间隔（秒）
        max_iterations: 最大采集次数
        """
        results = []
        
        print(f"开始监控 {len(codes)} 只股票，间隔 {interval} 秒")
        print("按 Ctrl+C 停止")
        print()
        
        for i in range(max_iterations):
            print(f"--- 第 {i+1}/{max_iterations} 次采集 ---")
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            for code in codes:
                try:
                    data = self.get_stock_realtime_data(code)
                    data['iteration'] = i + 1
                    data['timestamp'] = timestamp
                    results.append(data)
                    print(f"  {code}: {data.get('data', {}).get('price', 'N/A')}")
                except Exception as e:
                    print(f"  {code}: 采集失败 - {e}")
            
            print()
            
            if i < max_iterations - 1:
                time.sleep(interval)
        
        # 保存结果
        self.save_to_json(results, 'monitor_result')
        self.save_to_csv(results, 'monitor_result')
        
        print(f"监控完成，采集 {len(results)} 条数据")
        print(f"数据已保存到 {self.data_dir}")
        
        return results
    
    # ==================== 批量操作 ====================
    
    def compare_stocks(self, codes: List[str]) -> List[Dict]:
        """
        对比多只股票
        """
        results = []
        
        for code in codes:
            data = self.get_stock_realtime_data(code)
            results.append(data)
            time.sleep(1)
        
        return results
    
    def find_rising_stocks(self, codes: List[str], min_rise: float = 5.0) -> List[Dict]:
        """
        查找涨幅超过指定值的股票
        """
        rising = []
        
        for code in codes:
            data = self.get_stock_realtime_data(code)
            if data.get('success'):
                change = data.get('data', {}).get('change_percent', '0%')
                try:
                    change_val = float(change.replace('%', '').replace('+', ''))
                    if change_val >= min_rise:
                        rising.append(data)
                except:
                    pass
        
        return rising
    
    def find_falling_stocks(self, codes: List[str], max_fall: float = -5.0) -> List[Dict]:
        """
        查找跌幅超过指定值的股票
        """
        falling = []
        
        for code in codes:
            data = self.get_stock_realtime_data(code)
            if data.get('success'):
                change = data.get('data', {}).get('change_percent', '0%')
                try:
                    change_val = float(change.replace('%', '').replace('+', ''))
                    if change_val <= max_fall:
                        falling.append(data)
                except:
                    pass
        
        return falling


if __name__ == '__main__':
    # 测试
    from openclaw_integration import OpenClawBrowser
    
    print("=" * 60)
    print("  同花顺高级数据采集器")
    print("=" * 60)
    print()
    
    browser = OpenClawBrowser()
    crawler = THSAdvancedCrawler(browser)
    
    # 测试获取指数
    print("📊 获取大盘指数...")
    result = crawler.get_market_index()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print()
    print("=" * 60)
