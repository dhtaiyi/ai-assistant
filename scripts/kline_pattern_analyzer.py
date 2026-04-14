#!/usr/bin/env python3
"""
个股K线形态深度分析
基于mootdx实时数据
"""

import pandas as pd
import numpy as np
from mootdx.quotes import Quotes


def get_kline_data(code, offset=30):
    """获取K线数据"""
    client = Quotes.factory(market='std')
    market = 0 if code.startswith(('0', '3')) else 1
    bars = client.bars(symbol=code, frequency=9, market=market, offset=offset)
    client.close()
    return bars


def analyze_pattern(bars):
    """深度分析K线形态"""
    close = bars['close']
    high = bars['high']
    low = bars['low']
    open_price = bars['open']
    vol = bars['volume']
    
    # 技术指标
    ma5 = close.rolling(5).mean()
    ma10 = close.rolling(10).mean()
    ma20 = close.rolling(20).mean()
    ma30 = close.rolling(30).mean()
    
    change = close.pct_change() * 100
    vol_ma5 = vol.rolling(5).mean()
    vol_ma10 = vol.rolling(10).mean()
    
    # MACD
    ema12 = close.ewm(span=12).mean()
    ema26 = close.ewm(span=26).mean()
    dif = ema12 - ema26
    dea = dif.ewm(span=9).mean()
    macd_hist = (dif - dea) * 2
    
    result = {
        'bars': bars,
        'ma': {
            'ma5': ma5, 'ma10': ma10, 'ma20': ma20, 'ma30': ma30,
            'dif': dif, 'dea': dea, 'macd_hist': macd_hist
        },
        'vol': {'ma5': vol_ma5, 'ma10': vol_ma10},
        'change': change
    }
    return result


def format_pattern_report(code, name=None):
    """生成完整形态报告"""
    bars = get_kline_data(code)
    if bars is None or bars.empty:
        return f"❌ {code} 数据获取失败"
    
    close = bars['close']
    high = bars['high']
    low = bars['low']
    open_price = bars['open']
    vol = bars['volume']
    
    a = analyze_pattern(bars)
    ma5 = a['ma']['ma5']
    ma10 = a['ma']['ma10']
    ma20 = a['ma']['ma20']
    dif = a['ma']['dif']
    dea = a['ma']['dea']
    macd_hist = a['ma']['macd_hist']
    change = a['change']
    vol_ma5 = a['vol']['ma5']
    
    last_close = close.iloc[-1]
    last_ch = change.iloc[-1]
    last_vol = vol.iloc[-1]
    vol_ratio = last_vol / vol_ma5.iloc[-1] if vol_ma5.iloc[-1] > 0 else 1
    
    name = name or code
    
    lines = []
    lines.append("=" * 65)
    lines.append(f"📊 {name}({code}) K线形态深度分析")
    lines.append("=" * 65)
    
    # 最新价格
    emoji = "🌟" if last_ch > 9 else "🟢" if last_ch > 0 else "🔴"
    lines.append(f"\n{emoji} 最新: {last_close:.2f} ({last_ch:+.2f}%)")
    
    # 最近5日K线
    lines.append(f"\n📅 最近5日K线:")
    lines.append(f"{'日期':<12} {'开':<7} {'收':<7} {'高':<7} {'低':<7} {'涨跌':<8} {'形态'}")
    lines.append("-" * 60)
    
    for i in range(-5, 0):
        dt = bars.index[i].strftime('%Y-%m-%d')[:10]
        o = open_price.iloc[i]
        c = close.iloc[i]
        h = high.iloc[i]
        l = low.iloc[i]
        ch = change.iloc[i]
        
        body = abs(c - o)
        upper = h - max(c, o)
        lower = min(c, o) - l
        body_ratio = body / (h - l) if (h - l) > 0 else 0
        
        if ch > 9.5:
            if h == l: p = "🌟一字涨停"
            elif h == c and l == o: p = "🌟T字涨停"
            elif h == c: p = "🌟上影涨停"
            elif l == o: p = "🌟下影涨停"
            else: p = "🌟实体涨停"
        elif ch > 5: p = "🌟大阳线"
        elif ch > 2: p = "🟢中阳线"
        elif ch > 0:
            if lower > body * 2: p = "📈锤子线"
            elif upper < body * 0.3: p = "🟢光头阳"
            else: p = "🟢小阳线"
        elif ch == 0: p = "⚪十字星"
        elif ch > -2: p = "🔴小阴线"
        elif ch > -5: p = "🔴中阴线"
        elif ch > -10: p = "⚠️大阴线"
        else:
            if h == l: p = "⚠️一字跌停"
            elif upper > body * 2: p = "⚠️射击之星"
            else: p = "⚠️实体跌停"
        
        e = "🟢" if ch > 0 else "🔴" if ch < 0 else "⚪"
        lines.append(f"{e}{dt:<10} {o:<7.2f} {c:<7.2f} {h:<7.2f} {l:<7.2f} {ch:+7.2f}% {p}")
    
    # 均线分析
    lines.append(f"\n📈 均线位置:")
    lc = last_close
    for ma_name, ma_val in [('MA5', ma5.iloc[-1]), ('MA10', ma10.iloc[-1]), ('MA20', ma20.iloc[-1])]:
        if pd.isna(ma_val):
            continue
        if lc > ma_val * 1.02:
            lines.append(f"  ✅ {ma_name}: {ma_val:.2f} (股价在{ma_name}上方 +{(lc/ma_val-1)*100:.1f}%)")
        elif lc < ma_val * 0.98:
            lines.append(f"  ❌ {ma_name}: {ma_val:.2f} (股价在{ma_name}下方 {(lc/ma_val-1)*100:.1f}%)")
        else:
            lines.append(f"  ⚠️ {ma_name}: {ma_val:.2f} (股价在{ma_name}附近)")
    
    # MACD
    lines.append(f"\n📉 MACD:")
    if dif.iloc[-1] > dea.iloc[-1] and dif.iloc[-1] > 0:
        lines.append(f"  ✅ DIF({dif.iloc[-1]:.4f}) > DEA({dea.iloc[-1]:.4f}) > 0  金叉")
    elif dif.iloc[-1] < dea.iloc[-1] and dif.iloc[-1] < 0:
        lines.append(f"  ❌ DIF({dif.iloc[-1]:.4f}) < DEA({dea.iloc[-1]:.4f}) < 0  死叉")
    elif dif.iloc[-1] > dea.iloc[-1]:
        lines.append(f"  ⚠️ DIF({dif.iloc[-1]:.4f}) > DEA({dea.iloc[-1]:.4f})  但<0")
    else:
        lines.append(f"  ⚠️ DIF({dif.iloc[-1]:.4f}) < DEA({dea.iloc[-1]:.4f})  但>0")
    
    if macd_hist.iloc[-1] > 0:
        lines.append(f"  ✅ 红柱放大(动量增强)")
    elif macd_hist.iloc[-1] < 0:
        lines.append(f"  ❌ 绿柱(动量减弱)")
    else:
        lines.append(f"  ⚠️ 红绿柱交替")
    
    # 量能
    lines.append(f"\n📊 量能分析:")
    if vol_ratio > 2:
        lines.append(f"  ⚠️ 巨量(是5日均量的{vol_ratio:.1f}倍) 警惕")
    elif vol_ratio > 1.3:
        lines.append(f"  🟢 温和放量(是5日均量的{vol_ratio:.1f}倍)")
    elif vol_ratio < 0.5:
        lines.append(f"  📉 缩量(是5日均量的{vol_ratio:.1f}倍)")
    else:
        lines.append(f"  ➡️ 量能正常")
    
    # 压力支撑
    recent_high = high.iloc[-10:].max()
    recent_low = low.iloc[-10:].min()
    lines.append(f"\n📍 关键价位:")
    lines.append(f"  压力位: {recent_high:.2f} (近期高点)")
    lines.append(f"  支撑位: {recent_low:.2f} (近期低点)")
    lines.append(f"  当前价: {last_close:.2f}")
    
    # 综合评分
    score = 0
    if last_close > ma5.iloc[-1]: score += 1
    if ma5.iloc[-1] > ma10.iloc[-1]: score += 1
    if ma10.iloc[-1] > ma20.iloc[-1]: score += 1
    if dif.iloc[-1] > dea.iloc[-1]: score += 1
    if last_ch > 0: score += 1
    
    lines.append(f"\n🏆 技术综合评分: {score}/5")
    
    if score >= 4:
        verdict = "🎯 强势形态，关注买入机会"
    elif score >= 3:
        verdict = "➡️ 中性形态，谨慎观望"
    else:
        verdict = "⚠️ 弱势形态，注意风险"
    lines.append(f"   {verdict}")
    
    lines.append("=" * 65)
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    codes = sys.argv[1:]
    if not codes:
        codes = ['000586', '002491']
    
    for code in codes:
        print(format_pattern_report(code))
        print()
