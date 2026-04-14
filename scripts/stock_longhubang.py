#!/usr/bin/env python3
"""
龙虎榜数据获取
数据来源: 东方财富数据中心
API: datacenter-web.eastmoney.com
Report: RPT_DAILYBILLBOARD_PROFILE (每日龙虎榜个股)
"""

import requests
import json
import sys
from datetime import datetime, timedelta

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://data.eastmoney.com/stock/lhb.html',
}

BASE_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"


def get_daily_billboard(date=None, limit=100):
    """
    获取每日龙虎榜个股数据
    date: 日期字符串，如 '2026-04-08'，默认今日
    limit: 返回数量
    """
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    url = f"{BASE_URL}?reportName=RPT_DAILYBILLBOARD_PROFILE&columns=ALL&pageSize={limit}&pageNumber=1&sortColumns=TRADE_DATE&sortTypes=-1"
    
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        data = r.json()
        result = data.get('result', {})
        
        items = result.get('data', [])
        
        # 筛选指定日期
        filtered = [item for item in items if item.get('TRADE_DATE', '')[:10] == date]
        
        return filtered
    except Exception as e:
        print(f"龙虎榜获取失败: {e}", file=sys.stderr)
        return []


def get_billboard_by_stock(code, limit=10):
    """获取个股的龙虎榜历史"""
    url = f"{BASE_URL}?reportName=RPT_DAILYBILLBOARD_PROFILE&columns=ALL&pageSize={limit}&pageNumber=1&sortColumns=TRADE_DATE&sortTypes=-1&filter=SECURITY_CODE={code}"
    
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        data = r.json()
        result = data.get('result', {})
        return result.get('data', [])
    except Exception as e:
        print(f"个股龙虎榜获取失败: {e}", file=sys.stderr)
        return []


def format_billboard(date=None, our_stocks=None):
    """格式化龙虎榜报告"""
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    items = get_daily_billboard(date, 100)
    
    if our_stocks is None:
        our_stocks = {}
    
    lines = []
    lines.append("=" * 60)
    lines.append(f"📊 龙虎榜 - {date}")
    lines.append(f"获取时间: {datetime.now().strftime('%H:%M:%S')}")
    lines.append("=" * 60)
    
    # 过滤今日数据
    today_items = [item for item in items if item.get('TRADE_DATE', '')[:10] == date]
    
    if not today_items:
        lines.append("\n⚠️ 今日暂无龙虎榜数据（可能收盘后才更新）")
        lines.append("\n显示最新可用的龙虎榜数据：")
        today_items = items[:30]
    
    # 按净买入排序
    buy_items = sorted(today_items, key=lambda x: x.get('BILLBOARD_NET_AMT', 0) or 0, reverse=True)
    
    lines.append(f"\n🟢 资金净买入TOP10:")
    count = 0
    for item in buy_items:
        if count >= 10:
            break
        net = item.get('BILLBOARD_NET_AMT', 0) or 0
        if net > 0:
            count += 1
            name = item.get('SECURITY_NAME_ABBR', '')
            code = item.get('SECURITY_CODE', '')
            change = item.get('CHANGE_RATE', 0)
            emoji = "⭐" if code in our_stocks else "🟢"
            marker = " ← 重点关注" if code in our_stocks else ""
            lines.append(f"  {emoji} {name}({code}): 涨跌{change:+.2f}% 净买入{net/1e8:+.2f}亿{marker}")
    
    lines.append(f"\n🔴 资金净卖出TOP10:")
    count = 0
    sell_items = sorted(today_items, key=lambda x: x.get('BILLBOARD_NET_AMT', 0) or 0)
    for item in sell_items:
        if count >= 10:
            break
        net = item.get('BILLBOARD_NET_AMT', 0) or 0
        if net < 0:
            count += 1
            name = item.get('SECURITY_NAME_ABBR', '')
            code = item.get('SECURITY_CODE', '')
            change = item.get('CHANGE_RATE', 0)
            emoji = "⭐" if code in our_stocks else "🔴"
            marker = " ← 重点关注" if code in our_stocks else ""
            lines.append(f"  {emoji} {name}({code}): 涨跌{change:+.2f}% 净卖出{abs(net)/1e8:.2f}亿{marker}")
    
    lines.append(f"\n📈 今日龙虎榜共 {len(today_items)} 只个股上榜")
    
    # 重点股票分析
    if our_stocks:
        lines.append("\n" + "=" * 60)
        lines.append("🎯 重点股票龙虎榜分析:")
        for code, name in our_stocks.items():
            stock_items = [item for item in today_items if item.get('SECURITY_CODE', '') == code]
            if stock_items:
                for item in stock_items:
                    change = item.get('CHANGE_RATE', 0)
                    net = item.get('BILLBOARD_NET_AMT', 0) or 0
                    emoji = "🟢" if net > 0 else "🔴"
                    direction = "净买入" if net > 0 else "净卖出"
                    if net > 0:
                        lines.append(f"\n  ⭐ {name}({code}):")
                        lines.append(f"     龙虎榜今日{direction}{abs(net)/1e8:.2f}亿")
                        lines.append(f"     → 主力资金在买入！")
                    else:
                        lines.append(f"\n  ⚠️ {name}({code}):")
                        lines.append(f"     龙虎榜今日{direction}{abs(net)/1e8:.2f}亿")
                        lines.append(f"     → 主力资金在卖出，注意风险！")
            else:
                lines.append(f"\n  ➡️ {name}({code}): 今日未上龙虎榜")
    
    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


if __name__ == "__main__":
    # 默认重点股票
    our_stocks = {
        '000586': '汇源通信',
        '002491': '通鼎互联',
        '000919': '金陵药业',
        '600654': '中安科',
        '603538': '美诺华',
        '600488': '津药药业',
    }
    
    if len(sys.argv) > 1:
        date = sys.argv[1]
    else:
        date = None
    
    print(format_billboard(date, our_stocks))
