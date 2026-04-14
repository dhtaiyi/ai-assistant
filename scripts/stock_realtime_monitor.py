#!/usr/bin/env python3
"""
盘前预警 + 盘中监控脚本
功能：
1. 盘前扫描：找出即将突破的股票（贴近压力位、缩量整理、异动前兆）
2. 盘中监控：实时盯住这些股票，触发突破/跌破/异动时提醒
"""

import time
import sys
from datetime import datetime
from mootdx.quotes import Quotes


def get_realtime_quote(codes):
    """获取实时行情（腾讯API备用）"""
    import requests
    stocks_str = ",".join([f"sh{c}" if c.'66') else f"sz{c}" for c in codes])
    url = f"https://qt.gtimg.cn/q={stocks_str}"
    try:
        r = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        lines = r.text.strip().split('\n')
        results = {}
        for line in lines:
            if '=' not in line:
                continue
            code_part = line.split('=')[0].replace('v_', '')
            data = line.split('=")[1].rstrip('";').split('~')
            if len(data) > 37:
                try:
                    code = data[37] if len(data) > 37 else code_part
                    current = float(data[3]) if data[3] else 0
                    close = float(data[4]) if data[4] else 0
                    open_p = float(data[5]) if data[5] else 0
                    high = float(data[33]) if data[33] else 0
                    low = float(data[34]) if data[34] else 0
                    vol = float(data[36]) if data[36] else 0
                    amount = float(data[37]) if len(data) > 37 and data[37] else 0
                    pct = (current - close) / close * 100 if close > 0 else 0
                    results[code] = {
                        'current': current, 'close': close, 'open': open_p,
                        'high': high, 'low': low, 'vol': vol, 'amount': amount, 'pct': pct
                    }
                except:
                    pass
        return results
    except:
        return {}


def get_mootdx_quotes_tdx(codes):
    """通过mootdx批量获取实时行情"""
    client = Quotes.factory(market='std')
    try:
        quotes = client.quotes(codes)
        client.close()
        if quotes is None or quotes.empty:
            return {}
        result = {}
        for _, row in quotes.iterrows():
            code = row.get('code', '')
            price = row.get('price', 0)
            last_close = row.get('last_close', 0)
            high = row.get('high', 0)
            low = row.get('low', 0)
            vol = row.get('vol', 0)
            pct = row.get('pct_change', 0)
            result[code] = {
                'current': price, 'close': last_close, 'high': high, 'low': low, 'vol': vol, 'pct': pct
            }
        return result
    except:
        try:
            client.close()
        except:
            pass
        return {}


def get_bars_premarket(code, offset=40):
    """盘前获取历史K线"""
    client = Quotes.factory(market='std')
    try:
        market = 0 if code.'60', '3') else 1
        bars = client.bars(symbol=code, frequency=9, market=market, offset=offset)
        client.close()
        return bars
    except:
        try:
            client.close()
        except:
            pass
        return None


def find_breakout_candidates():
    """盘前扫描：找出即将突破的个股"""
    import pandas as pd
    
    print("=" * 60)
    print(f"🔍 盘前预警扫描 - {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)
    
    # 白名单重点股票（今日热门）
    focus_stocks = {
        '000586': '汇源通信', '002491': '通鼎互联', '000919': '金陵药业',
        '600654': '中安科', '603538': '美诺华', '600488': '津药药业',
        '000720': '新能泰山', '300475': '香农芯创', '300058': '蓝色光标',
        '600126': '杭钢股份', '603067': '振华股份', '688655': '迅捷兴',
    }
    
    print(f"\n📋 重点关注 {len(focus_stocks)} 只股票...")
    
    candidates = []
    
    for code, name in focus_stocks.items():
        bars = get_bars_premarket(code, offset=40)
        if bars is None or bars.empty:
            continue
        
        close = bars['close']
        high = bars['high']
        low = bars['low']
        vol = bars['volume']
        
        last_close = close.iloc[-1]
        last_high = high.iloc[-1]
        last_low = low.iloc[-1]
        
        # 近期压力位
        high20 = high.iloc[-20:].max()
        low20 = low.iloc[-20:].min()
        ma5 = close.iloc[-5:].mean()
        ma10 = close.iloc[-10:].mean()
        vol_ma5 = vol.iloc[-5:].mean()
        vol_now = vol.iloc[-1]
        
        # 计算距离压力位的幅度
        distance_to_high = (high20 - last_close) / last_close * 100
        range20 = (high20 - low20) / low20 * 100
        
        # 信号检测
        signals = []
        
        # 信号1: 贴近压力位（<3%）
        if 0 < distance_to_high < 3:
            signals.append(f"⚠️贴近压力位({distance_to_high:.1f}%)")
        
        # 信号2: 横盘整理（振幅<10%）
        if range20 < 10:
            signals.append(f"📊横盘整理({range20:.1f}%)")
        
        # 信号3: 缩量
        if vol_now < vol_ma5 * 0.7:
            signals.append("📉缩量整理")
        
        # 信号4: 连续小阳线
        if len(close) >= 5:
            small_green = sum(1 for i in range(-5, 0) if 0 <= close.iloc[i] - close.iloc[i-1] < 1) >= 3
            if small_green:
                signals.append("🟢连蓄小阳线")
        
        # 信号5: 放量突破前高
        if len(vol) >= 2 and vol.iloc[-1] > vol_ma5 * 1.5:
            if last_close > high.iloc[-2]:
                signals.append("📈放量异动")
        
        # 综合预警等级
        alert = "⚠️关注" if signals else "➡️正常"
        if distance_to_high < 2 and range20 < 8:
            alert = "🔴重点关注"
        elif distance_to_high < 3:
            alert = "⚠️关注"
        
        if signals or alert != "➡️正常":
            candidates.append({
                'code': code, 'name': name,
                'last_close': last_close,
                'high20': high20,
                'low20': low20,
                'range20': range20,
                'distance': distance_to_high,
                'vol_ratio': vol_now / vol_ma5 if vol_ma5 > 0 else 1,
                'signals': signals,
                'alert': alert,
            })
    
    # 按距离排序
    candidates.sort(key=lambda x: x['distance'])
    
    print(f"\n📊 发现 {len(candidates)} 只预警股票:")
    
    for c in candidates[:20]:
        signals_str = " | ".join(c['signals']) if c['signals'] else "正常"
        alert_icon = c['alert'].split('关注')[0]
        print(f"\n{alert_icon} {c['name']}({c['code']}) | 现价:{c['last_close']:.2f}")
        print(f"   压力位:{c['high20']:.2f} | 距压:{c['distance']:.2f}% | 振幅:{c['range20']:.1f}%")
        print(f"   信号:{signals_str}")
    
    return candidates


def monitor_stocks(candidates, interval=60, duration=300):
    """
    盘中监控
    candidates: 预警股票列表
    interval: 检测间隔秒
    duration: 监控总时长
    """
    print(f"\n📡 开始盘中监控 ({len(candidates)}只 | 每{interval}秒检测 | 共{duration}秒)")
    start = time.time()
    
    # 昨日收盘基准
    import pandas as pd
    baseline = {}
    for c in candidates:
        bars = get_bars_premarket(c['code'], offset=2)
        if bars is not None and len(bars) >= 2:
            baseline[c['code']] = {
                'prev_close': bars['close'].iloc[-2],
                'prev_high': bars['high'].iloc[-2],
                'prev_low': bars['low'].iloc[-2],
            }
    
    alerts = []
    
    while time.time() - start < duration:
        now = datetime.now()
        hour = now.hour
        
        # 9:30-15:00 交易时间
        if hour < 9 or hour >= 15 or (hour == 9 and now.minute < 25):
            time.sleep(5)
            continue
        if hour == 11 or hour == 12:
            time.sleep(5)
            continue
        if hour == 13 and now.minute < 5:
            time.sleep(5)
            continue
        if hour >= 15 and now.minute > 5:
            print("已收盘，监控结束")
            break
        
        quotes = get_mootdx_quotes_tdx(list({c['code']: 1 for c in candidates}.keys()))
        if not quotes:
            time.sleep(interval)
            continue
        
        for c in candidates:
            code = c['code']
            if code not in quotes:
                continue
            
            q = quotes[code]
            price = q['current']
            prev = baseline.get(code, {})
            
            if not prev:
                continue
            
            pct_chg = (price - prev['prev_close']) / prev['prev_close'] * 100
            
            # 触发预警
            alert_type = None
            
            # 预警1: 突破压力位
            if price > c['high20']:
                alert_type = "🔥突破压力位"
            
            # 预警2: 快速上涨
            if pct_chg > 5:
                alert_type = f"🚀快速上涨{pct_chg:+.2f}%"
            
            # 预警3: 跌破支撑
            if price < c['low20']:
                alert_type = "💥跌破支撑"
            
            # 预警4: 异动（涨跌幅>9）
            if abs(pct_chg) > 9:
                alert_type = f"⚠️异动脉冲{pct_chg:+.2f}%"
            
            if alert_type:
                alerts.append({
                    'time': now.strftime('%H:%M:%S'),
                    'code': code,
                    'name': c['name'],
                    'price': price,
                    'type': alert_type,
                    'pct': pct_chg,
                })
        
        if alerts:
            print(f"\n🚨 预警时刻: {now.strftime('%H:%M:%S')}")
            for a in alerts[-5:]:
                print(f"  {a['time']} | {a['name']}({a['code']}) | {a['type']} | 现价:{a['price']}")
            alerts = []  # 清空已提示
        
        time.sleep(interval)


if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "scan"
    
    if mode == "monitor":
        candidates = find_breakout_candidates()
        if candidates:
            monitor_stocks(candidates, interval=30, duration=36000)  # 10小时
    else:
        find_breakout_candidates()
