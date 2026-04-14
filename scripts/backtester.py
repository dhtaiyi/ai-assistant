#!/usr/bin/env python3
"""
K线历史回测工具 v1.0
验证买点A/B/C/D的历史胜率
使用方法：python3 backtester.py
"""

import pandas as pd
from mootdx.quotes import Quotes
from datetime import datetime, timedelta

def get_kline(symbol, market, days=60):
    """获取日K线数据"""
    c = Quotes.factory(market='std')
    df = c.bars(symbol=symbol, frequency=9, market=market, offset=days)
    c.close()
    if df is None or df.empty:
        return None
    df = df.tail(days).copy()
    # 计算指标
    df['pct_chg'] = df['close'].pct_change() * 100
    df['vol_ratio'] = df['vol'] / df['vol'].rolling(5).mean()
    df['ma5'] = df['close'].rolling(5).mean()
    df['ma10'] = df['close'].rolling(10).mean()
    df['ma20'] = df['close'].rolling(20).mean()
    # 涨停信号
    df['zt'] = df['pct_chg'] >= 9.9
    return df

def backtest_pattern_a(codes, name="买点A首板战法"):
    """
    买点A：首板战法
    买入信号：放量涨停突破
    卖出：次日收盘/止损-7%
    """
    print("\n" + "=" * 60)
    print("[BACKTEST] 买点A：首板战法")
    print("=" * 60)
    
    total = 0
    win = 0
    loss = 0
    results = []
    
    for name_code, symbol in codes.items():
        market = 0 if symbol.startswith('sz') else 1
        code = symbol[2:] if symbol[:2] in ('sz', 'sh') else symbol
        df = get_kline(code, market, days=120)
        if df is None:
            continue
        
        zt_days = df[df['zt']].index.tolist()
        
        for i, dt in enumerate(zt_days[:-1], 0):
            pos = df.index.get_loc(dt)
            if pos == 0:
                continue
            prev = df.iloc[pos]
            nxt = df.iloc[pos + 1] if pos + 1 < len(df) else None
            
            # 买入条件：放量突破
            if nxt is None:
                continue
            
            buy_price = nxt['open']  # 次日开盘买
            stop_loss = buy_price * 0.93  # -7%止损
            sell_price = nxt['close']  # 次日收盘卖（简化）
            
            if pd.isna(buy_price) or pd.isna(sell_price):
                continue
            
            sell_close = df.iloc[pos + 1]['close'] if pos + 2 < len(df) else None
            
            total += 1
            ret = (sell_close - buy_price) / buy_price * 100 if sell_close else 0
            
            if ret > 0:
                win += 1
            else:
                loss += 1
            
            results.append({"股票": name_code, "日期": str(dt)[:10],
                         "买入价": round(buy_price, 2),
                         "次日卖价": round(sell_close, 2) if sell_close else "N/A",
                         "收益": round(ret, 1)})
    
    if total > 0:
        print("测试样本: %d 笔" % total)
        print("胜率: %d/%d = %.1f%%" % (win, total, win / total * 100))
        print("最优3笔:")
        top3 = sorted(results, key=lambda x: x["收益"], reverse=True)[:3]
        for r in top3:
            print("  %s %s 收益:%+.1f%%" % (r["股票"], r["日期"], r["收益"]))
    else:
        print("数据不足")
    
    return total, win / total * 100 if total > 0 else 0

def run_backtest():
    print("[BACKTEST] K线历史回测 v1.0")
    print("时间: " + datetime.now().strftime("%Y-%m-%d %H:%M"))
    
    test_stocks = {
        "汇源通信": "sz000586",
        "东山精密": "sz002384",
        "光迅科技": "sz002281",
        "长飞光纤": "sh601869",
        "通鼎互联": "sz002491",
        "金陵药业": "sz000919",
    }
    
    # 买点A 回测
    backtest_pattern_a(test_stocks, "买点A首板战法")

if __name__ == "__main__":
    run_backtest()
