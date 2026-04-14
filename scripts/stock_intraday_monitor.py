#!/usr/bin/env python3
# coding: utf-8
from datetime import datetime
from mootdx.quotes import Quotes
import time
import sys

WATCH = {
    '000586': {'name': '汇源通信', 'pressure': 22.84, 'support': 14.55},
    '002491': {'name': '通鼎互联', 'pressure': 15.20, 'support': 10.50},
    '000919': {'name': '金陵药业', 'pressure': 8.91, 'support': 7.50},
    '600654': {'name': '中安科', 'pressure': 4.40, 'support': 3.50},
    '603538': {'name': '美诺华', 'pressure': 43.24, 'support': 35.00},
    '600488': {'name': '津药药业', 'pressure': 8.44, 'support': 6.00},
    '300308': {'name': '中际旭创', 'pressure': 688.26, 'support': 600.00},
}
CODES = list(WATCH.keys())

def get_realtime():
    try:
        client = Quotes.factory(market='std')
        df = client.quotes(CODES)
        client.close()
        if df is None or df.empty:
            return {}
        result = {}
        for i in range(len(df)):
            row = df.iloc[i]
            code = str(row.get('code', ''))
            result[code] = {
                'price': float(row.get('price', 0)),
                'close': float(row.get('last_close', 0)),
                'high': float(row.get('high', 0)),
                'low': float(row.get('low', 0)),
            }
        return result
    except Exception as e:
        print('realtime error:', e)
        try:
            client.close()
        except:
            pass
        return {}

def get_prev_close():
    prev = {}
    for code in CODES:
        try:
            client = Quotes.factory(market='std')
            market = 0 if code[0] in '03' else 1
            bars = client.bars(symbol=code, frequency=9, market=market, offset=5)
            client.close()
            if bars is not None and len(bars) >= 2:
                prev[code] = float(bars['close'].iloc[-2])
        except Exception as e:
            print('prev_kline error:', e)
            try:
                client.close()
            except:
                pass
    return prev

def main(interval=30):
    print('intraday monitor ready')
    print('codes:', CODES)
    print('interval:', interval, 's')
    print('Ctrl+C to stop')
    prev = get_prev_close()
    print('prev_close:', prev)
    alerts = {}

    while True:
        now = datetime.now()
        h, m = now.hour, now.minute
        if h < 9 or h >= 15:
            time.sleep(10)
            continue
        if h == 9 and m < 25:
            time.sleep(10)
            continue
        if h == 11 and m > 30:
            time.sleep(10)
            continue
        if h == 12:
            time.sleep(10)
            continue
        if h == 13 and m < 5:
            time.sleep(10)
            continue

        quotes = get_realtime()
        ts = now.strftime('%H:%M')

        for code in CODES:
            q = quotes.get(code, {})
            price = q.get('price', 0)
            if price <= 0:
                continue
            prev_c = prev.get(code, q.get('close', 0))
            if prev_c <= 0:
                prev_c = price
            pct = (price - prev_c) / prev_c * 100 if prev_c > 0 else 0
            info = WATCH[code]
            pressure = info['pressure']
            support = info['support']
            name = info['name']

            key = now.strftime('%Y%m%d') + '_' + code
            sent = alerts.get(key, set())

            # 突破压力
            if pressure > 0 and price > pressure and 'break' not in sent:
                txt = ts + ' 突破 ' + name + '(' + code + ') ' + str(round(price, 2)) + ' > ' + str(round(pressure, 2)) + ' ' + str(round(pct, 2)) + '%'
                print(txt)
                sent.add('break')
                alerts[key] = sent

            # 跌破支撑
            if support > 0 and price < support and 'breakdown' not in sent:
                txt = ts + ' 跌破 ' + name + '(' + code + ') ' + str(round(price, 2)) + ' < ' + str(round(support, 2)) + ' ' + str(round(pct, 2)) + '%'
                print(txt)
                sent.add('breakdown')
                alerts[key] = sent

            # 涨停
            if pct > 9 and 'limit' not in sent:
                txt = ts + ' 涨停 ' + name + '(' + code + ') ' + str(round(price, 2)) + ' ' + str(round(pct, 2)) + '%'
                print(txt)
                sent.add('limit')
                alerts[key] = sent

            # 炸板
            if 'limit' in sent and pct < 9:
                txt = ts + ' 炸板 ' + name + '(' + code + ') ' + str(round(pct, 2)) + '%'
                print(txt)
                sent.discard('limit')
                alerts[key] = sent

        time.sleep(interval)

if __name__ == '__main__':
    interval = 30
    if len(sys.argv) > 1:
        try:
            interval = int(sys.argv[1])
        except:
            pass
    main(interval)
