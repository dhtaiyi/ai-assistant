#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同花顺快速数据采集脚本
命令行工具，快速获取数据
"""

import sys
import json
import argparse
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(
        description='同花顺数据采集工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python quick_crawl.py --code 600519           # 获取茅台实时价格
  python quick_crawl.py --codes 600519 000001   # 获取多只股票
  python quick_crawl.py --index                 # 获取大盘指数
  python quick_crawl.py --monitor 600519        # 监控股票价格
  python quick_crawl.py --export 600519 600036  # 导出CSV
        '''
    )
    
    # 基本参数
    parser.add_argument('--code', '-c', help='股票代码')
    parser.add_argument('--codes', '-C', nargs='+', help='多个股票代码')
    parser.add_argument('--index', '-i', action='store_true', help='获取大盘指数')
    parser.add_argument('--monitor', '-m', nargs='+', help='监控股票')
    parser.add_argument('--export', '-e', nargs='+', help='导出CSV')
    parser.add_argument('--output', '-o', default='json', choices=['json', 'csv'], help='输出格式')
    parser.add_argument('--interval', '-t', type=int, default=60, help='监控间隔(秒)')
    parser.add_argument('--count', '-n', type=int, default=10, help='采集次数')
    
    args = parser.parse_args()
    
    # 导入浏览器控制
    from openclaw_integration import OpenClawBrowser
    from ths_crawler import THSCrawler
    from advanced_crawler import THSAdvancedCrawler
    
    print("=" * 60)
    print("  同花顺数据采集工具")
    print("=" * 60)
    print()
    
    # 初始化
    browser = OpenClawBrowser()
    simple_crawler = THSCrawler(browser)
    advanced_crawler = THSAdvancedCrawler(browser)
    
    # 检查连接
    status = browser.status()
    if not status.get('success'):
        print("❌ 无法连接到浏览器控制服务器")
        print("   请确保: 1) Chrome扩展已安装 2) server.py已启动")
        sys.exit(1)
    
    print(f"✅ 已连接到浏览器控制服务器")
    print()
    
    # 执行任务
    if args.monitor:
        # 监控模式
        print(f"🔄 开始监控 {len(args.monitor)} 只股票...")
        advanced_crawler.monitor_prices(
            args.monitor,
            interval=args.interval,
            max_iterations=args.count
        )
    
    elif args.codes:
        # 批量查询
        print(f"📊 查询 {len(args.codes)} 只股票...")
        results = advanced_crawler.compare_stocks(args.codes)
        
        for result in results:
            code = result.get('code', result.get('data', {}).get('code', 'Unknown'))
            price = result.get('data', {}).get('price', 'N/A')
            change = result.get('data', {}).get('change_percent', 'N/A')
            print(f"  {code}: {price} ({change})")
        
        # 导出
        if args.output == 'csv':
            filepath = advanced_crawler.save_to_csv(results, 'stock_comparison')
            print(f"\n📁 数据已导出到: {filepath}")
    
    elif args.code:
        # 单只查询
        print(f"📈 获取 {args.code} 实时数据...")
        result = advanced_crawler.get_stock_realtime_data(args.code)
        
        if result.get('success'):
            data = result.get('data', {})
            print(f"""
  代码: {data.get('code')}
  价格: {data.get('price')}
  涨跌: {data.get('change')} ({data.get('change_percent')})
  开盘: {data.get('open')}
  最高: {data.get('high')}
  最低: {data.get('low')}
  昨收: {data.get('pre_close')}
  成交量: {data.get('volume')}
  成交额: {data.get('amount')}
            """)
            
            # 导出
            if args.output == 'csv':
                filepath = advanced_crawler.save_to_csv([result], 'stock_price')
                print(f"📁 数据已导出到: {filepath}")
        else:
            print(f"❌ 获取失败: {result.get('error', '未知错误')}")
    
    elif args.index:
        # 大盘指数
        print("📊 获取大盘指数...")
        result = advanced_crawler.get_market_index()
        
        if result.get('success'):
            indices = result.get('market', {})
            for key, data in indices.items():
                print(f"  {data.get('name', key)}: {data.get('price', 'N/A')} ({data.get('change', 'N/A')})")
        else:
            print("❌ 获取失败")
    
    elif args.export:
        # 导出CSV
        print(f"📁 导出 {len(args.export)} 只股票数据到CSV...")
        results = advanced_crawler.compare_stocks(args.export)
        filepath = advanced_crawler.save_to_csv(results, 'export')
        print(f"✅ 已导出到: {filepath}")
    
    else:
        parser.print_help()
    
    print()
    print("=" * 60)


if __name__ == '__main__':
    main()
