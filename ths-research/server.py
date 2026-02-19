#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据采集API服务器
提供HTTP API获取股票数据
"""

import asyncio
from aiohttp import web
import json
from datetime import datetime
from stock_fetcher import StockDataFetcher

app = web.Application()
fetcher = StockDataFetcher()


async def get_stock(request):
    """获取单只股票数据"""
    code = request.query.get('code', '')
    
    if not code:
        return web.json_response({
            'success': False,
            'error': '缺少参数: code'
        })
    
    stock = await fetcher.fetch_stock(code)
    
    if stock:
        return web.json_response({
            'success': True,
            'data': stock
        })
    else:
        return web.json_response({
            'success': False,
            'error': f'获取 {code} 数据失败'
        })


async def get_index(request):
    """获取大盘指数"""
    code = request.query.get('code', '000001')
    
    index = await fetcher.fetch_index(code)
    
    if index:
        return web.json_response({
            'success': True,
            'data': index
        })
    else:
        return web.json_response({
            'success': False,
            'error': f'获取指数 {code} 数据失败'
        })


async def get_batch(request):
    """批量获取股票数据"""
    codes = request.query.get('codes', '')
    if not codes:
        return web.json_response({
            'success': False,
            'error': '缺少参数: codes'
        })
    
    code_list = codes.split(',')
    stocks = await fetcher.fetch_batch(code_list)
    
    return web.json_response({
        'success': True,
        'data': stocks,
        'count': len(stocks)
    })


async def get_all(request):
    """获取所有预设股票数据"""
    default_stocks = [
        '600519',  # 贵州茅台
        '000001',  # 平安银行
        '600036',  # 招商银行
        '300750',  # 宁德时代
        '000651',  # 格力电器
        '600276',  # 恒瑞医药
        '000858',  # 五粮液
        '002594',  # 比亚迪
    ]
    
    stocks = await fetcher.fetch_batch(default_stocks)
    
    # 获取大盘指数
    index = await fetcher.fetch_index("000001")
    
    return web.json_response({
        'success': True,
        'timestamp': datetime.now().isoformat(),
        'market': index,
        'stocks': stocks,
        'count': len(stocks)
    })


async def index(request):
    """首页"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>股票数据API</title>
        <style>
            body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
            h1 { color: #333; }
            .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 8px; }
            code { background: #e0e0e0; padding: 2px 6px; border-radius: 4px; }
            pre { background: #1e1e1e; color: #00ff00; padding: 15px; border-radius: 8px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <h1>📊 股票数据API</h1>
        
        <h2>接口列表</h2>
        
        <div class="endpoint">
            <h3>获取单只股票</h3>
            <p>GET /stock?code=600519</p>
        </div>
        
        <div class="endpoint">
            <h3>获取大盘指数</h3>
            <p>GET /index?code=000001</p>
        </div>
        
        <div class="endpoint">
            <h3>批量获取</h3>
            <p>GET /batch?codes=600519,000001,600036</p>
        </div>
        
        <div class="endpoint">
            <h3>获取所有预设股票</h3>
            <p>GET /all</p>
        </div>
        
        <h2>示例响应</h2>
        <pre>{
    "success": true,
    "data": {
        "code": "600519",
        "name": "贵州茅台",
        "price": 1485.30,
        "change_percent": -0.09,
        ...
    }
}</pre>
    </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')


# 注册路由
app.router.add_get('/', index)
app.router.add_get('/stock', get_stock)
app.router.add_get('/index', get_index)
app.router.add_get('/batch', get_batch)
app.router.add_get('/all', get_all)


if __name__ == '__main__':
    print("=" * 60)
    print("  股票数据API服务器")
    print("=" * 60)
    print()
    print("  启动中...")
    print()
    print("  接口:")
    print("    GET /           - API首页")
    print("    GET /stock      - 获取单只股票 (?code=600519)")
    print("    GET /index      - 获取大盘指数 (?code=000001)")
    print("    GET /batch      - 批量获取 (?codes=600519,000001)")
    print("    GET /all        - 获取所有预设股票")
    print()
    print("  运行: python server.py")
    print("  端口: 8080")
    print()
    print("=" * 60)
    
    web.run_app(app, host='0.0.0.0', port=8080)
