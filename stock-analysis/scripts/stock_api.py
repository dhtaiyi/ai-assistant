#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据服务 - 提供HTTP API接口
功能：获取板块、个股、联动分析数据
"""

import akshare as ak
import pandas as pd
from flask import Flask, jsonify
from datetime import datetime
import threading
import time

app = Flask(__name__)

# ============= 缓存配置 =============
CACHE = {
    'market': None,
    'industry': None,
    'concept': None,
    'last_update': None
}
CACHE_INTERVAL = 60  # 缓存更新间隔（秒）

# ============= 板块数据 =============
@app.route('/')
def index():
    """主页 - 服务状态"""
    return jsonify({
        'status': 'ok',
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'endpoints': [
            '/',
            '/market',           # 大盘行情
            '/industry',          # 行业板块
            '/concept',           # 概念板块
            '/stock/<code>',      # 个股详情
            '/industry/stocks/<industry>',  # 板块个股
            '/analysis',         # 联动分析
            '/sync/<industry>',  # 板块同步率
            '/health'            # 健康检查
        ]
    })

@app.route('/market')
def market():
    """大盘行情"""
    try:
        df = ak.stock_zh_index_spot()
        CACHE['market'] = df
        return jsonify({
            'status': 'ok',
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data': df.to_dict(orient='records')
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/industry')
def industry():
    """行业板块"""
    try:
        df = ak.stock_board_industry_name_em()
        CACHE['industry'] = df
        return jsonify({
            'status': 'ok',
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data': df.to_dict(orient='records')
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/concept')
def concept():
    """概念板块"""
    try:
        df = ak.stock_board_concept_name_em()
        CACHE['concept'] = df
        return jsonify({
            'status': 'ok',
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data': df.to_dict(orient='records')
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/stock/<code>')
def stock_detail(code):
    """个股详情"""
    try:
        # 获取实时行情
        df = ak.stock_zh_a_spot_em()
        stock = df[df['代码'] == code]
        
        if len(stock) == 0:
            return jsonify({'status': 'error', 'message': '股票不存在'})
        
        data = stock.iloc[0].to_dict()
        
        return jsonify({
            'status': 'ok',
            'data': data
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/industry/stocks/<industry>')
def industry_stocks(industry):
    """获取板块内所有个股"""
    try:
        # 获取板块数据
        df = ak.stock_board_industry_cons_ths(symbol=industry)
        
        return jsonify({
            'status': 'ok',
            'industry': industry,
            'count': len(df),
            'data': df.to_dict(orient='records')
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/analysis')
def analysis():
    """板块-个股联动分析"""
    try:
        # 获取实时行情
        df = ak.stock_zh_a_spot_em()
        
        # 计算涨跌分布
        up = len(df[df['涨跌幅'] > 0])
        down = len(df[df['涨跌幅'] < 0])
        flat = len(df[df['涨跌幅'] == 0])
        
        # 找出涨幅最大的板块
        industry_df = ak.stock_board_industry_name_em()
        industry_df = industry_df.sort_values('涨跌幅', ascending=False)
        
        # 找出跌幅最大的板块
        industry_df_down = ak.stock_board_industry_name_em()
        industry_df_down = industry_df_down.sort_values('涨跌幅')
        
        return jsonify({
            'status': 'ok',
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'market': {
                'up': up,
                'down': down,
                'flat': flat,
                'total': len(df)
            },
            'top_industry_up': industry_df.head(5)[['板块名称', '涨跌幅', '涨停数']].to_dict(orient='records'),
            'top_industry_down': industry_df_down.head(5)[['板块名称', '涨跌幅', '跌停数']].to_dict(orient='records')
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/sync/<industry>')
def sync_analysis(industry):
    """板块同步率分析"""
    try:
        # 获取板块内个股
        stocks_df = ak.stock_board_industry_cons_ths(symbol=industry)
        stock_codes = stocks_df['代码'].tolist()[:50]  # 最多取50只
        
        # 获取实时行情
        market_df = ak.stock_zh_a_spot_em()
        market_df = market_df[market_df['代码'].isin(stock_codes)]
        
        if len(market_df) == 0:
            return jsonify({'status': 'error', 'message': '无法获取数据'})
        
        # 计算同步率
        df = market_df.copy()
        
        # 分类
        up_stocks = df[df['涨跌幅'] > 2]
        down_stocks = df[df['涨跌幅'] < -2]
        flat_stocks = df[(df['涨跌幅'] >= -2) & (df['涨跌幅'] <= 2)]
        
        # 计算平均涨跌幅
        avg_pct = df['涨跌幅'].mean()
        std_pct = df['涨跌幅'].std()  # 标准差
        
        # 同步率（涨跌幅方向一致的比例）
        if avg_pct > 1:
            sync_rate = len(up_stocks) / len(df) * 100
            direction = '上涨'
        elif avg_pct < -1:
            sync_rate = len(down_stocks) / len(df) * 100
            direction = '下跌'
        else:
            sync_rate = len(flat_stocks) / len(df) * 100
            direction = '震荡'
        
        return jsonify({
            'status': 'ok',
            'industry': industry,
            'total_stocks': len(df),
            'sync_rate': round(sync_rate, 2),
            'direction': direction,
            'avg_pct': round(avg_pct, 2),
            'std_pct': round(std_pct, 2),
            'statistics': {
                'up_more_2': len(up_stocks),
                'down_more_2': len(down_stocks),
                'flat': len(flat_stocks)
            },
            'top_up': df.nlargest(5, '涨跌幅')[['代码', '名称', '最新价', '涨跌幅']].to_dict(orient='records'),
            'top_down': df.nsmallest(5, '涨跌幅')[['代码', '名称', '最新价', '涨跌幅']].to_dict(orient='records')
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/health')
def health():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'time': datetime.now().isoformat()
    })

# ============= 主程序 =============
def main():
    print("=" * 60)
    print("    股票数据服务 v1.0")
    print("=" * 60)
    print()
    print("📡 服务启动中...")
    print("🔗 访问地址: http://localhost:8080")
    print()
    print("📋 API 接口:")
    print("  - /                       服务状态")
    print("  - /market                 大盘行情")
    print("  - /industry               行业板块")
    print("  - /concept                概念板块")
    print("  - /stock/<code>          个股详情")
    print("  - /industry/stocks/<板块> 板块个股")
    print("  - /analysis               联动分析")
    print("  - /sync/<板块>            同步率分析")
    print("  - /health                 健康检查")
    print()
    print("=" * 60)
    print()
    
    app.run(host='0.0.0.0', port=8080, debug=False)

if __name__ == '__main__':
    main()
