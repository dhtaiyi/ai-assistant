#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
浏览器控制客户端
通过HTTP API控制嵌入式浏览器

使用方法:
    python client.py --status      # 查看状态
    python client.py -u URL        # 打开网页
    python client.py --stock      # 获取股票数据
    python client.py -c SELECTOR  # 点击元素
    python client.py -s down      # 滚动页面
"""

import requests
import json
import argparse
import asyncio
from typing import Dict, Any, Optional


class BrowserClient:
    """浏览器客户端"""
    
    def __init__(self, base_url: str = 'http://localhost:8080'):
        self.base_url = base_url.rstrip('/')
    
    def _request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """发送请求"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, timeout=10)
            else:
                response = requests.request(method, url, json=data, timeout=30)
            
            return response.json()
        except requests.exceptions.ConnectionError:
            return {'success': False, 'error': f'无法连接到 {url}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_status(self) -> Dict:
        """获取状态"""
        return self._request('GET', '/')
    
    def navigate(self, url: str) -> Dict:
        """导航"""
        return self._request('POST', '/', {'command': {'type': 'navigate', 'url': url}})
    
    def click(self, selector: str) -> Dict:
        """点击"""
        return self._request('POST', '/', {'command': {'type': 'click', 'selector': selector}})
    
    def scroll(self, direction: str = 'down', amount: int = 500) -> Dict:
        """滚动"""
        return self._request('POST', '/', {'command': {'type': 'scroll', 'direction': direction, 'amount': amount}})
    
    def get_stock_data(self) -> Dict:
        """获取股票数据"""
        return self._request('POST', '/', {'command': {'type': 'getStockData'}})
    
    def get_page_info(self) -> Dict:
        """获取页面信息"""
        return self._request('POST', '/', {'command': {'type': 'getPageInfo'}})
    
    def evaluate(self, code: str) -> Dict:
        """执行JavaScript"""
        return self._request('POST', '/', {'command': {'type': 'evaluate', 'code': code}})


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description='浏览器控制客户端',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python client.py --status           # 查看状态
  python client.py -u URL            # 打开网页
  python client.py --stock           # 获取股票数据
  python client.py -c SELECTOR       # 点击元素
  python client.py -s down           # 滚动页面
  python client.py -e "document.title"  # 执行JS
        '''
    )
    
    parser.add_argument('--url', '-u', help='打开的URL')
    parser.add_argument('--stock', action='store_true', help='获取股票数据')
    parser.add_argument('--info', action='store_true', help='获取页面信息')
    parser.add_argument('--status', action='store_true', help='查看状态')
    parser.add_argument('--click', '-c', help='点击元素选择器')
    parser.add_argument('--scroll', '-s', choices=['up', 'down', 'top', 'bottom'], help='滚动方向')
    parser.add_argument('--execute', '-e', help='执行JavaScript代码')
    parser.add_argument('--server', '-S', default='http://localhost:8080', help='服务器地址')
    
    args = parser.parse_args()
    
    client = BrowserClient(args.server)
    
    print("=" * 60)
    print("  浏览器控制客户端")
    print("=" * 60)
    print()
    
    # 查看状态
    if args.status:
        status = client.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return
    
    # 检查连接
    status = client.get_status()
    if not status.get('success'):
        print("❌ 浏览器未运行！")
        print("   请先运行: run.bat")
        print()
        print("   然后再运行此命令")
        return
    
    # 打开URL
    if args.url:
        print(f"🌐 打开 {args.url}...")
        result = client.navigate(args.url)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print()
    
    # 点击
    if args.click:
        print(f"👆 点击 {args.click}...")
        result = client.click(args.click)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print()
    
    # 滚动
    if args.scroll:
        print(f"📜 滚动 {args.scroll}...")
        result = client.scroll(args.scroll)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print()
    
    # 股票数据
    if args.stock:
        print("📊 获取股票数据...")
        result = client.get_stock_data()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print()
    
    # 页面信息
    if args.info:
        print("📄 页面信息...")
        result = client.get_page_info()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print()
    
    # 执行JavaScript
    if args.execute:
        print(f"💻 执行: {args.execute}...")
        result = client.evaluate(args.execute)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print()
    
    # 无参数时显示帮助
    if not any([args.url, args.stock, args.info, args.status, args.click, args.scroll, args.execute]):
        parser.print_help()


if __name__ == '__main__':
    main()
