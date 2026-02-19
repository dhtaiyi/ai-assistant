#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
浏览器控制命令行工具
"""

import asyncio
import argparse
import json
import sys
from browser import BrowserController


async def main():
    parser = argparse.ArgumentParser(description='浏览器控制工具')
    parser.add_argument('--url', '-u', help='打开的URL')
    parser.add_argument('--click', '-c', help='点击元素选择器')
    parser.add_argument('--type', '-t', nargs=2, metavar=('SELECTOR', 'TEXT'), help='输入文本')
    parser.add_argument('--scroll', '-s', choices=['up', 'down', 'top', 'bottom'], help='滚动')
    parser.add_argument('--stock', action='store_true', help='获取股票数据')
    parser.add_argument('--info', action='store_true', help='获取页面信息')
    parser.add_argument('--wait', '-w', type=float, default=0, help='等待秒数')
    parser.add_argument('--headless', action='store_true', default=False, help='后台运行')
    parser.add_argument('--execute', '-e', help='执行JavaScript')
    
    args = parser.parse_args()
    
    async with BrowserController(headless=args.headless) as controller:
        # 打开URL
        if args.url:
            print(f"🌐 打开 {args.url}...")
            result = await controller.navigate(args.url)
            print(f"标题: {result['title']}")
        
        # 点击
        if args.click:
            print(f"👆 点击 {args.click}...")
            result = await controller.click(args.click)
            print(json.dumps(result, ensure_ascii=False))
        
        # 输入
        if args.type:
            selector, text = args.type
            print(f"⌨️ 输入 {selector} = {text}...")
            result = await controller.type(selector, text)
            print(json.dumps(result, ensure_ascii=False))
        
        # 滚动
        if args.scroll:
            print(f"📜 滚动 {args.scroll}...")
            result = await controller.scroll(args.scroll)
            print(json.dumps(result, ensure_ascii=False))
        
        # 等待
        if args.wait > 0:
            print(f"⏳ 等待 {args.wait} 秒...")
            await controller.wait(args.wait)
        
        # 获取股票数据
        if args.stock:
            print("📊 获取股票数据...")
            data = await controller.get_stock_data()
            print(json.dumps(data, ensure_ascii=False, indent=2))
        
        # 获取页面信息
        if args.info:
            print("📄 页面信息...")
            data = await controller.get_page_info()
            print(json.dumps(data, ensure_ascii=False, indent=2))
        
        # 执行JavaScript
        if args.execute:
            print(f"💻 执行: {args.execute}...")
            result = await controller.execute_js(args.execute)
            print(result)


if __name__ == '__main__':
    asyncio.run(main())
