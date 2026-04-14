#!/usr/bin/env python3
"""
股票综合分析系统 v2.0 (基于 mootdx 通达信协议)
数据来源: mootdx (通达信行情协议，自动选择最优服务器)
"""

import requests
import json
import re
import os
import sys
from datetime import datetime, timedelta
from mootdx.quotes import Quotes

# ===== mootdx 行情获取 =====

def get_tdx_client():
    """获取通达信行情客户端"""
    try:
        client = Quotes.factory(market='std')
        return client
    except Exception as e:
        print(f"通达信连接失败: {e}")
        return None


def get_realtime_by_tdx(codes):
    """
    通过mootdx获取实时行情
    codes: list of str, e.g. ['000586', '600000']
    """
    client = get_tdx_client()
    if not client:
        return None
    
    try:
        # mootdx quotes() takes list of stock codes directly
        df = client.quotes(codes)
        client.close()
        
        if df is not None and not df.empty:
            # Calculate pct_change
            df['pct_change'] = (df['price'] - df['last_close']) / df['last_close'] * 100
            # Map market to name
            market_map = {0: '深', 1: '沪'}
            df['market_name'] = df['market'].map(market_map)
            return df
        return None
    except Exception as e:
        print(f"实时行情获取失败: {e}")
        try:
            client.close()
        except:
            pass
        return None


def get_stock_bars_tdx(code, frequency=9, offset=20):
    """
    获取K线数据
    frequency: 9=日K, 0=5分钟, 1=15分钟, 4=60分钟
    """
    client = get_tdx_client()
    if not client:
        return None
    
    try:
        # Determine market
        if code.startswith('0') or code.startswith('3'):
            market = 0
        else:
            market = 1
        
        if frequency == 9:  # daily
            df = client.bars(symbol=code, frequency=frequency, market=market, offset=offset)
        else:
            df = client.bars(symbol=code, frequency=frequency, market=market, offset=offset)
        
        client.close()
        return df
    except Exception as e:
        print(f"K线获取失败: {e}")
        try:
            client.close()
        except:
            pass
        return None


def get_index_tdx(symbol='000001', offset=10):
    """获取指数数据"""
    client = get_tdx_client()
    if not client:
        return None
    
    try:
        if symbol == '000001':
            df = client.index(symbol='000001', frequency=9, market=1, offset=offset)
        elif symbol == '399006':
            df = client.index(symbol='399006', frequency=9, market=0, offset=offset)
        else:
            market = 0 if symbol.startswith('0') else 1
            df = client.index(symbol=symbol, frequency=9, market=market, offset=offset)
        
        client.close()
        return df
    except Exception as e:
        print(f"指数获取失败: {e}")
        try:
            client.close()
        except:
            pass
        return None


# ===== 技术分析 =====

def calculate_ma(series, period):
    """计算移动平均"""
    return series.rolling(period).mean()


def calculate_ema(series, period):
    """计算指数移动平均"""
    return series.ewm(span=period).mean()


def analyze_technique(bars_df):
    """技术分析"""
    if bars_df is None or bars_df.empty:
        return {}
    
    close = bars_df['close']
    high = bars_df['high']
    low = bars_df['low']
    vol = bars_df['volume']
    open_price = bars_df['open']
    
    result = {}
    
    # MA
    if len(close) >= 5:
        result['ma5'] = round(close.iloc[-5:].mean(), 2)
    if len(close) >= 10:
        result['ma10'] = round(close.iloc[-10:].mean(), 2)
    if len(close) >= 20:
        result['ma20'] = round(close.iloc[-20:].mean(), 2)
    
    # Price position
    current = close.iloc[-1]
    if 'ma5' in result:
        result['price_vs_ma5'] = "✅ MA5上方" if current > result['ma5'] else "⚠️ MA5下方"
    if 'ma10' in result:
        result['price_vs_ma10'] = "✅ MA10上方" if current > result['ma10'] else "⚠️ MA10下方"
    if 'ma20' in result:
        result['price_vs_ma20'] = "✅ MA20上方" if current > result['ma20'] else "⚠️ MA20下方"
    
    # Volume analysis
    vol_ma5 = vol.iloc[-5:].mean() if len(vol) >= 5 else vol.mean()
    current_vol = vol.iloc[-1]
    if current_vol > vol_ma5 * 1.5:
        result['volume'] = "⚠️ 巨量（警惕）"
    elif current_vol > vol_ma5:
        result['volume'] = "✅ 温和放量"
    elif current_vol < vol_ma5 * 0.5:
        result['volume'] = "📉 缩量"
    else:
        result['volume'] = "➡️ 正常"
    
    # K-line pattern
    today = bars_df.iloc[-1]
    change_pct = (today['close'] - today['open']) / today['open'] * 100 if today['open'] > 0 else 0
    
    if abs(change_pct - 9.9) < 0.3:
        if today['high'] == today['low'] == today['close']:
            result['pattern'] = "🌟🌟🌟 一字涨停（最强）"
        else:
            result['pattern'] = "🌟🌟 实体涨停"
    elif change_pct > 5:
        result['pattern'] = "🌟 大阳线"
    elif change_pct < -5:
        result['pattern'] = "⚠️ 大阴线"
    else:
        body = abs(today['close'] - today['open'])
        upper = today['high'] - max(today['close'], today['open'])
        lower = min(today['close'], today['open']) - today['low']
        
        if upper > body * 2 and lower < body:
            result['pattern'] = "📉 射击之星（偏空）"
        elif lower > body * 2 and upper < body:
            result['pattern'] = "📈 锤子线（偏多）"
        else:
            result['pattern'] = "➡️ 普通K线"
    
    # Trend direction
    if len(close) >= 5:
        recent_trend = close.iloc[-1] - close.iloc[-5]
        result['5d_trend'] = f"🟢 +{recent_trend:.2f}" if recent_trend > 0 else f"🔴 {recent_trend:.2f}"
    
    return result


# ===== 主分析函数 =====

def analyze_stock_full(code):
    """综合分析单只股票"""
    result = {
        'code': code,
        'name': code,
        'realtime': {},
        'bars': None,
        'technique': {},
        'summary': {}
    }
    
    # 实时行情
    rt = get_realtime_by_tdx([code])
    if rt is not None and not rt.empty:
        row = rt.iloc[0]
        result['realtime'] = {
            'price': row['price'],
            'last_close': row['last_close'],
            'open': row['open'],
            'high': row['high'],
            'low': row['low'],
            'vol': row['vol'],
            'amount': row.get('amount', 0),
            'pct_change': row['pct_change'],
            'market': row.get('market_name', ''),
            'bid': row.get('bid1', 0),
            'bid_vol': row.get('bid_vol1', 0),
            'ask': row.get('ask1', 0),
            'ask_vol': row.get('ask_vol1', 0),
        }
    
    # K线数据
    bars = get_stock_bars_tdx(code, frequency=9, offset=30)
    result['bars'] = bars
    
    # 技术分析
    if bars is not None and not bars.empty:
        result['technique'] = analyze_technique(bars)
    
    # 综合判断
    if result['realtime']:
        pct = result['realtime'].get('pct_change', 0)
        if pct > 9:
            result['summary']['action'] = "⚠️ 涨停股，明日观察开板"
            result['summary']['risk'] = "高"
        elif pct > 5:
            result['summary']['action'] = "🌟 涨幅较大，轻仓关注"
            result['summary']['risk'] = "中"
        elif pct > 0:
            result['summary']['action'] = "➡️ 震荡偏强，观望"
            result['summary']['risk'] = "中"
        else:
            result['summary']['action'] = "⚠️ 下跌，注意风险"
            result['summary']['risk'] = "高"
    
    return result


def generate_tdx_report(codes=None):
    """生成综合报告"""
    if codes is None:
        codes = ['000586', '002491', '000919', '600654', '603538', '600488']
    
    lines = []
    lines.append("=" * 55)
    lines.append(f"📊 股票综合分析报告 (mootdx通达信协议)")
    lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 55)
    
    # 指数
    lines.append("\n📈 【大盘指数】")
    for sym, name in [('000001', '上证指数'), ('399006', '创业板指')]:
        idx = get_index_tdx(sym, offset=3)
        if idx is not None and not idx.empty:
            last = idx.iloc[-1]
            prev = idx.iloc[-2] if len(idx) > 1 else last
            pct = (last['close'] - prev['close']) / prev['close'] * 100
            emoji = "🟢" if pct > 0 else "🔴"
            lines.append(f"  {emoji} {name}: {last['close']:.2f} ({pct:+.2f}%)")
    
    # 股票
    lines.append("\n🔥 【个股分析】")
    for code in codes:
        analysis = analyze_stock_full(code)
        rt = analysis.get('realtime', {})
        tech = analysis.get('technique', {})
        summary = analysis.get('summary', {})
        
        if not rt:
            lines.append(f"\n  ❓ {code}: 数据获取失败")
            continue
        
        pct = rt.get('pct_change', 0)
        emoji = "🌟" if pct > 9 else "⬆️" if pct > 0 else "⬇️"
        
        lines.append(f"\n  {emoji} {code} ({rt.get('market', '')})")
        lines.append(f"     现价: {rt.get('price', 0):.2f} ({pct:+.2f}%)")
        lines.append(f"     今开: {rt.get('open', 0):.2f} 最高: {rt.get('high', 0):.2f} 最低: {rt.get('low', 0):.2f}")
        lines.append(f"     昨收: {rt.get('last_close', 0):.2f}")
        lines.append(f"     成交量: {rt.get('vol', 0):.0f}手 成交额: {rt.get('amount', 0)/1e8:.2f}亿")
        
        if tech:
            if 'pattern' in tech:
                lines.append(f"     形态: {tech['pattern']}")
            if 'volume' in tech:
                lines.append(f"     量能: {tech['volume']}")
            if 'price_vs_ma5' in tech:
                lines.append(f"     {tech.get('price_vs_ma5', '')}")
            if '5d_trend' in tech:
                lines.append(f"     5日趋势: {tech['5d_trend']}")
        
        if summary:
            lines.append(f"     📍 建议: {summary.get('action', '观望')}")
            lines.append(f"     ⚠️ 风险: {summary.get('risk', '中')}")
    
    lines.append("\n" + "=" * 55)
    return "\n".join(lines)


if __name__ == "__main__":
    codes = sys.argv[1:] if len(sys.argv) > 1 else None
    print(generate_tdx_report(codes))
