#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from mootdx.quotes import Quotes
from datetime import datetime
import time
import sys
import pandas as pd
import numpy as np

def get_bars(code, offset=40):
    client = Quotes.factory(market='std')
    try:
        market = 0 if code[0] in '03' else 1
        bars = client.bars(symbol=code, frequency=9, market=market, offset=offset)
        client.close()
        return bars
    except:
        try:
            client.close()
        except:
            pass
        return None

def get_quotes(codes):
    client = Quotes.factory(market='std')
    try:
        df = client.quotes(codes)
        client.close()
        if df is not None and not df.empty:
            result = {}
            for i in range(len(df)):
                row = df.iloc[i]
                code = str(row.get('code', '')
                result[code] = {
                    'price': float(row.get('price', 0),
                    'close': float(row.get('last_close', 0),
                    'high': float(row.get('high', 0)),
                    'low': float(row.get('low', 0)),
                    'vol': float(row.get('vol', 0)),
                    'pct': float(row.get('pct_change', 0)),
                }
            return result
    except:
        try:
            client.close()
        except:
            pass
    return {}

def scan():
    watch = [
        ('000586', 'huiyuan'),
        ('002491', 'tongdaohu'),
        ('000919', 'jinlingyaoye'),
        ('600654', 'zhonganke'),
        ('603538', 'mainuohua'),
        ('600488', 'jinyaoyaoye'),
        ('000720', 'xinnengtaishan'),
        ('300475', 'xiangnengxinchuang'),
        ('300058', 'lanseguangbiao'),
    ]
    
    names = dict(watch)
    results = []
    
    for code, _ in watch:
        bars = get_bars(code, offset=40)
        if bars is None or len(bars) < 5:
            continue
        
        close = bars['close']
        high20 = bars['high'].iloc[-20:].max()
        low20 = bars['low'].iloc[-20:].min()
        vol_ma5 = bars['volume'].iloc[-5:].mean()
        vol_now = bars['volume'].iloc[-1]
        pct = (close.iloc[-1] - close.iloc[-2]) / close.iloc[-2] * 100
        dist_high = (high20 - close.iloc[-1]) / close.iloc[-1] * 100
        vola20 = (high20 - low20) / low20 * 100
        
        signals = []
        alert = 'normal'
        
        if 0 < dist_high < 3:
            signals.append('near_high')
            alert = 'watch'
        if dist_high < 1.5:
            alert = 'strong_watch'
        if vola20 < 10:
            signals.append('consolidating')
        if vol_now < vol_ma5 * 0.7:
            signals.append('shrink_vol')
        if pct > 5:
            signals.append('surging')
        if pct > 9:
            alert = 'limitup'
        
        if alert != 'normal' or len(signals) > 0:
            results.append({
                'code': code,
                'name': names.get(code, code),
                'price': close.iloc[-1],
                'high20': high20,
                'low20': low20,
                'pct': pct,
                'dist': dist_high,
                'vola': vola20,
                'vol_r': vol_now / vol_ma5 if vol_ma5 > 0 else 1,
                'signals': signals,
                'alert': alert,
                'bars': bars,
            })
    
    results.sort(key=lambda x: x['dist'])
    return {r['code']: r for r in results}

def monitor(targets, interval=30):
    codes = list(targets.keys())
    baselines = {}
    for code in codes:
        bars = targets[code].get('bars')
        if bars is not None and len(bars) >= 2:
            baselines[code] = {
                'prev_close': float(bars['close'].iloc[-1]),
                'alert_sent': set()
            }
    
    print(f'\nMonitor {len(codes)} stocks, interval {interval}s. Ctrl+C to stop\n')
    try:
        while True:
            now = datetime.now()
            h, m = now.hour, now.minute
            if h < 9 or h >= 15 or (h == 9 and m < 25) or h == 12:
                time.sleep(10)
                continue
            
            quotes = get_quotes(codes)
            if not quotes:
                time.sleep(interval)
                continue
            
            for code in codes:
                if code not in quotes:
                    continue
                q = quotes[code]
                t = targets.get(code, {})
                base = baselines.get(code, {'alert_sent': set()})
                price = q['price']
                prev = base.get('prev_close', q['close'])
                if prev <= 0:
                    prev = q['close']
                pct = (price - prev) / prev * 100 if prev > 0 else 0
                high20 = t.get('high20', 0)
                sent = base['alert_sent']
                
                if high20 > 0 and price > high20 and 'break' not in sent:
                    print(f'BRKOUT {now.strftime("%H:%M")} {t["name"]}({code}) {price:.2f} > {high20:.2f}')
                    sent.add('break')
                
                if pct > 5 and 'surging' not in sent:
                    print(f'SURGE {now.strftime("%H:%M")} {t["name"]}({code}) {pct:.1f}%')
                    sent.add('surging')
                
                if pct > 9 and 'limit' not in sent:
                    print(f'LIMITUP {now.strftime("%H:%M")} {t["name"]}({code}) {pct:.1f}%')
                    sent.add('limit')
                
                baselines[code] = base
            
            time.sleep(interval)
    except KeyboardInterrupt:
        print('\nStopped')

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'scan'
    
    if mode == 'monitor':
        results = scan()
        if results:
            monitor(results)
    else:
        print('Scanning...')
        r = scan()
        print(f'Found {len(r)} stocks')
