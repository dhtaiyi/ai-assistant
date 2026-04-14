#!/usr/bin/env python3
"""
突破形态监控扫描器 v2
优化版：单次连接批量获取，快速扫描
"""

import pandas as pd
import numpy as np
from mootdx.quotes import Quotes
import sys
from datetime import datetime


def get_bars_batch(client, codes, offset=60):
    """批量获取历史K线"""
    results = {}
    # 分批处理，每批50只
    batch_size = 50
    for i in range(0, len(codes), batch_size):
        batch = codes[i:i+batch_size]
        for code in batch:
            try:
                market = 0 if code.startswith(('0', '3')) else 1
                bars = client.bars(symbol=code, frequency=9, market=market, offset=offset)
                if bars is not None and len(bars) >= 30:
                    results[code] = bars
            except:
                pass
    return results


def detect_breakout(bars):
    """检测突破形态"""
    if bars is None or len(bars) < 30:
        return None
    
    close = bars['close']
    high = bars['high']
    low = bars['low']
    vol = bars['volume']
    
    ma5 = close.rolling(5).mean()
    ma10 = close.rolling(10).mean()
    ma20 = close.rolling(20).mean()
    ma60 = close.rolling(60).mean()
    vol_ma20 = vol.rolling(20).mean()
    
    last_close = close.iloc[-1]
    last_vol = vol.iloc[-1]
    vol_ratio = last_vol / vol_ma20.iloc[-1] if vol_ma20.iloc[-1] > 0 else 1
    
    # 近20日高低点
    high20 = high.iloc[-20:].max()
    low20 = low.iloc[-20:].min()
    range_ratio = (high20 - low20) / low20 * 100 if low20 > 0 else 100
    
    patterns_found = []
    
    # 1. 横盘突破
    if range_ratio < 15 and last_close > high20 * 0.97:
        strength = 0
        if last_close > high20: strength += 30
        if vol_ratio > 1.5: strength += 20
        if last_close > ma20.iloc[-1]: strength += 15
        if last_close > ma60.iloc[-1] if not pd.isna(ma60.iloc[-1]) else False: strength += 10
        if vol.iloc[-1] > vol.iloc[-2]: strength += 15
        if close.iloc[-1] > close.iloc[-3]: strength += 10
        
        patterns_found.append({
            'type': '横盘突破',
            'strength': min(strength, 100),
            'pattern': f'横盘突破({range_ratio:.1f}%)',
            'resistance': round(high20, 2),
            'volume_surge': round(vol_ratio, 2),
            'breakout': True,
            'current': round(last_close, 2),
            'distance': round((last_close - high20) / high20 * 100, 2) if high20 > 0 else 0,
        })
    
    # 2. 旗型突破
    pole_high = high.iloc[-15:-5].max()
    pole_low = low.iloc[-15:-5].min()
    pole_range = (pole_high - pole_low) / pole_low * 100 if pole_low > 0 else 0
    flag_high = high.iloc[-5:].max()
    flag_low = low.iloc[-5:].min()
    flag_range = (flag_high - flag_low) / flag_low * 100 if flag_low > 0 else 0
    
    if pole_range > 10 and flag_range < 5 and last_close > flag_high:
        strength = 0
        if last_close > high.iloc[:-5].max(): strength += 35
        if vol_ratio > 1.3: strength += 25
        if last_close > ma20.iloc[-1]: strength += 15
        if vol.iloc[-1] > vol.iloc[-2]: strength += 15
        
        patterns_found.append({
            'type': '旗型突破',
            'strength': min(strength, 100),
            'pattern': f'旗型突破(杆{pole_range:.0f}%)',
            'resistance': round(flag_high, 2),
            'volume_surge': round(vol_ratio, 2),
            'breakout': True,
            'current': round(last_close, 2),
            'distance': round((last_close - flag_high) / flag_high * 100, 2),
        })
    
    # 3. 收敛三角突破
    if 5 < range_ratio < 25:
        recent_highs = high.iloc[-15:].values
        recent_lows = low.iloc[-15:].values
        high_slope = np.polyfit(range(len(recent_highs)), recent_highs - recent_highs[0], 1)[0] if len(recent_highs) > 5 else 0
        low_slope = np.polyfit(range(len(recent_lows)), recent_lows - recent_lows[0], 1)[0] if len(recent_lows) > 5 else 0
        
        if high_slope < 0 and low_slope > 0 and last_close > high.iloc[-10:].max() * 0.97:
            strength = 0
            if last_close > high.iloc[-10:].max(): strength += 35
            if vol_ratio > 1.5: strength += 25
            if last_close > ma20.iloc[-1]: strength += 20
            if vol.iloc[-1] > vol.iloc[-2]: strength += 20
            
            patterns_found.append({
                'type': '三角突破',
                'strength': min(strength, 100),
                'pattern': '收敛三角突破',
                'resistance': round(high.iloc[-10:].max(), 2),
                'volume_surge': round(vol_ratio, 2),
                'breakout': True,
                'current': round(last_close, 2),
                'distance': 0,
            })
    
    # 4. 均线粘合突破
    if len(close) >= 60:
        ma5v, ma10v, ma20v, ma60v = ma5.iloc[-1], ma10.iloc[-1], ma20.iloc[-1], ma60.iloc[-1]
        if all(not pd.isna(x) for x in [ma5v, ma10v, ma20v, ma60v]):
            spread = abs(ma5v - ma10v) / ma10v * 100
            if spread < 3 and last_close > ma5v > ma10v > ma20v > ma60v:
                strength = 0
                if last_close > high.iloc[-20:].max() * 0.98: strength += 35
                if vol_ratio > 1.3: strength += 25
                if close.iloc[-1] > close.iloc[-3]: strength += 20
                if vol.iloc[-1] > vol_ma20.iloc[-1]: strength += 20
                
                patterns_found.append({
                    'type': '均线突破',
                    'strength': min(strength, 100),
                    'pattern': f'均线粘合({spread:.1f}%)',
                    'resistance': round(high.iloc[-20:].max(), 2),
                    'volume_surge': round(vol_ratio, 2),
                    'breakout': True,
                    'current': round(last_close, 2),
                    'distance': 0,
                })
    
    # 返回最强的形态
    if patterns_found:
        best = max(patterns_found, key=lambda x: x['strength'])
        return best
    return None


def scan_breakout_fast(min_strength=55, limit=30):
    """快速扫描：先获取今日涨幅大的股票，再检测突破"""
    client = Quotes.factory(market='std')
    
    # 获取全市场股票列表
    print("获取股票列表...")
    all_stocks = client.stock_all()
    if all_stocks is None or all_stocks.empty:
        client.close()
        return []
    
    # 沪深股票
    codes = []
    for _, row in all_stocks.iterrows():
        code = str(row.get('code', ''))
        if len(code) == 6 and code[0] in '0369':
            codes.append(code)
    
    print(f"共 {len(codes)} 只股票，开始扫描...")
    
    breakouts = []
    scanned = 0
    
    # 分批处理
    batch_size = 100
    for i in range(0, len(codes), batch_size):
        batch = codes[i:i+batch_size]
        scanned += len(batch)
        
        print(f"  扫描进度: {scanned}/{len(codes)}...", end='\r')
        
        for code in batch:
            try:
                market = 0 if code.startswith(('0', '3')) else 1
                bars = client.bars(symbol=code, frequency=9, market=market, offset=60)
                if bars is not None and len(bars) >= 30:
                    result = detect_breakout(bars)
                    if result and result['strength'] >= min_strength:
                        result['code'] = code
                        breakouts.append(result)
            except:
                pass
        
        if len(breakouts) >= 100:  # 找到足够多了就停
            break
    
    client.close()
    
    # 排序
    breakouts.sort(key=lambda x: x['strength'], reverse=True)
    return breakouts[:limit]


if __name__ == "__main__":
    min_strength = 55
    if len(sys.argv) > 1:
        try:
            min_strength = int(sys.argv[1])
        except:
            pass
    
    print(f"🔍 突破形态扫描器 v2 (强度≥{min_strength})")
    print()
    results = scan_breakout_fast(min_strength=min_strength, limit=30)
    
    if not results:
        print("\n⚠️ 未发现强势突破形态")
        print("可能市场处于整理阶段，建议观望")
    else:
        print(f"\n\n🔥 发现 {len(results)} 只突破形态股票:")
        print("=" * 70)
        
        strong = [r for r in results if r['strength'] >= 75]
        medium = [r for r in results if 60 <= r['strength'] < 75]
        weak = [r for r in results if r['strength'] < 60]
        
        if strong:
            print(f"\n🌟 强烈突破 (≥75分) 共{len(strong)}只:")
            for r in strong[:15]:
                vol_ico = "📈" if r['volume_surge'] > 1.5 else "➡️" if r['volume_surge'] > 1.0 else "📉"
                print(f"  🌟 {r['code']} | {r['pattern']} | 现价{r['current']} | 量比{r['volume_surge']}x | {r['strength']}分")
        
        if medium:
            print(f"\n📈 中等突破 (60-74分) 共{len(medium)}只:")
            for r in medium[:10]:
                print(f"  ⬆️ {r['code']} | {r['pattern']} | {r['current']} | {r['strength']}分")
        
        if weak:
            print(f"\n➡️ 弱势突破 ({len(weak)}只):")
            for r in weak[:5]:
                print(f"  ➡️ {r['code']} | {r['pattern']} | {r['strength']}分")
        
        print("\n" + "=" * 70)
        print("💡 建议关注强势突破（75分以上）+ 放量 + 突破前高的股票")
