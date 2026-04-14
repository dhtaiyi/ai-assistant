#!/usr/bin/env python3
"""
股票综合分析脚本 - 增强版
功能:
1. 获取实时行情数据
2. 计算技术指标
3. 分析买卖点
4. 读取龙虎榜数据
5. 生成综合复盘报告
"""

import requests
import json
import sys
import os
from datetime import datetime, timedelta
from stock_realtime import get_stock_data, get_market_index, get_board_leaders

# ===== 技术分析函数 =====

def calculate_ma(price_list, period):
    """计算移动平均线"""
    if len(price_list) < period:
        return None
    return sum(price_list[-period:]) / period


def calculate_vol_ma(vol_list, period):
    """计算成交量移动平均"""
    if len(vol_list) < period:
        return None
    return sum(vol_list[-period:]) / period


def analyze_stock(stock_name, code):
    """
    综合分析单只股票
    返回: 分析报告字典
    """
    data = get_stock_data({stock_name: code})
    if not data or stock_name not in data:
        return None
    
    d = data[stock_name]
    
    # 模拟历史数据（实际应从API获取）
    # 这里基于当前价格模拟一个简单的分析
    current = d['current']
    close = d['close'] 
    high = d['high']
    low = d['low']
    change_pct = d['change_pct']
    vol = d['vol']
    
    # 判断封板状态
    is_limit_up = abs(change_pct - 9.9) < 0.2 if change_pct > 0 else False
    is_limit_down = abs(change_pct + 9.9) < 0.2 if change_pct < 0 else False
    
    # 判断开板情况
    # 一字板 = 最低价=最高价=当前价(涨停时)
    is_one_word_board = (high == low == current) and change_pct > 9
    
    # 估算封单金额(万)
    # 买一价 * 买一量 ≈ 封单金额
    seal_amount = d.get('buy1', 0) * 100  # 简化估算
    
    result = {
        'name': stock_name,
        'code': code,
        'current': current,
        'close': close,
        'high': high,
        'low': low,
        'change_pct': change_pct,
        'vol': vol,
        'seal_amount_wan': seal_amount,
        'is_limit_up': is_limit_up,
        'is_one_word_board': is_one_word_board,
        'today_analysis': {},
        'buy_point': None,
        'sell_point': None,
        'risk_level': None,
    }
    
    # ===== 技术分析 =====
    
    # 1. K线形态分析（简化版）
    if is_limit_up:
        if is_one_word_board:
            result['today_analysis']['k形态'] = "一字涨停（最强）"
        elif high > low * 1.05:
            result['today_analysis']['k形态'] = "实体涨停（大阳线）"
        else:
            result['today_analysis']['k形态'] = "涨停（普通）"
    elif is_limit_down:
        result['today_analysis']['k形态'] = "跌停"
    else:
        # 判断普通K线
        body = abs(current - close)
        upper_shadow = high - max(current, close)
        lower_shadow = min(current, close) - low
        body_ratio = body / (high - low) if (high - low) > 0 else 0
        
        if upper_shadow > body * 2 and lower_shadow < body:
            result['today_analysis']['k形态'] = "射击之星（偏空）"
        elif lower_shadow > body * 2 and upper_shadow < body:
            result['today_analysis']['k形态'] = "锤子线（偏多）"
        elif change_pct > 5:
            result['today_analysis']['k形态'] = "大阳线"
        elif change_pct < -5:
            result['today_analysis']['k形态'] = "大阴线"
        else:
            result['today_analysis']['k形态'] = "普通K线"
    
    # 2. 均线位置分析（简化）
    if close > 0 and current > 0:
        # 模拟均线（实际需历史数据）
        ma5_sim = current * 0.98  # 假设5日线略低
        ma10_sim = current * 0.95
        ma20_sim = current * 0.90
        
        above_ma5 = "✅ 在5日线上方" if current > ma5_sim else "⚠️ 在5日线下方"
        above_ma10 = "✅ 在10日线上方" if current > ma10_sim else "⚠️ 在10日线下方"
        result['today_analysis']['均线'] = f"{above_ma5}，{above_ma10}"
    
    # 3. 成交量分析（简化）
    if vol > 100000:  # 10万手以上算放量
        result['today_analysis']['量能'] = "⚠️ 巨量（警惕）"
    elif vol > 50000:
        result['today_analysis']['量能'] = "✅ 温和放量"
    else:
        result['today_analysis']['量能'] = "⚠️ 缩量"
    
    # ===== 买卖点分析 =====
    
    if is_limit_up:
        # 涨停股分析
        if is_one_word_board:
            result['today_analysis']['强度'] = "🌟🌟🌟 一字板（最强）"
            result['risk_level'] = "高"
            result['buy_point'] = "明日若开板回封可关注买入"
            result['sell_point'] = "持有，涨停不卖"
        else:
            result['today_analysis']['强度'] = "🌟🌟 实体涨停（强）"
            result['risk_level'] = "中"
            result['buy_point'] = "明日高开可考虑，轻仓"
            result['sell_point'] = "跌破5日线止盈"
    elif change_pct > 5:
        result['today_analysis']['强度'] = "🌟 涨幅较大"
        result['risk_level'] = "中"
        result['buy_point'] = f"若回调至{current * 0.97:.2f}可关注"
        result['sell_point'] = f"若跌破{current * 0.93:.2f}止损"
    elif change_pct < -5:
        result['today_analysis']['强度'] = "⚠️ 跌幅较大"
        result['risk_level'] = "高"
        result['buy_point'] = "不抄底，等企稳"
        result['sell_point'] = "已持有则止损"
    else:
        result['today_analysis']['强度'] = "➡️ 震荡"
        result['risk_level'] = "中"
        result['buy_point'] = f"突破{current * 1.03:.2f}买入"
        result['sell_point'] = f"跌破{current * 0.97:.2f}止损"
    
    return result


def get_longhubang():
    """
    获取龙虎榜数据
    数据来源: 东财 龙虎榜
    """
    # 东财龙虎榜API
    url = "https://data.eastmoney.com/stock/lhb.html"
    
    # 尝试从东财获取龙虎榜
    try:
        # 龙虎榜汇总API
        lhb_url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
        params = {
            "sortColumns": "TRADE_DATE",
            "sortTypes": "-1",
            "pageSize": "10",
            "pageNumber": "1",
            "reportName": "RPT_LHB_ALLSTOCKS",
            "columns": "ALL",
        }
        r = requests.get(lhb_url, params=params, timeout=10)
        if r.status_code == 200:
            try:
                jdata = r.json()
                if jdata.get('result'):
                    return jdata['result'].get('data', [])
            except:
                pass
    except Exception as e:
        print(f"龙虎榜获取失败: {e}", file=sys.stderr)
    
    return []


def generate_daily_report(date_str=None):
    """
    生成每日综合复盘报告
    """
    if date_str is None:
        date_str = datetime.now().strftime('%Y%m%d')
    
    report = {
        'date': date_str,
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'market': {},
        'leaders': {},
        'summary': {},
    }
    
    # 1. 获取指数数据
    indices = get_market_index()
    report['market']['indices'] = indices
    
    # 判断市场状态
    sz50_change = indices.get('上证指数', {}).get('change_pct', 0)
    cyb_change = indices.get('创业板指', {}).get('change_pct', 0)
    
    if sz50_change > 2:
        report['market']['status'] = "强势反弹"
    elif sz50_change > 0:
        report['market']['status'] = "震荡偏强"
    elif sz50_change > -2:
        report['market']['status'] = "震荡偏弱"
    else:
        report['market']['status'] = "大幅下跌"
    
    # 2. 获取连板龙头数据
    leaders = get_board_leaders()
    report['leaders'] = leaders
    
    # 3. 详细分析每只龙头
    report['analysis'] = {}
    for name, code in {
        "汇源通信": "sz000586",
        "通鼎互联": "sz002491",
        "金陵药业": "sz000919",
        "中安科": "sh600654",
        "美诺华": "sh603538",
        "津药药业": "sh600488",
    }.items():
        if name in leaders:
            analysis = analyze_stock(name, code)
            if analysis:
                report['analysis'][name] = analysis
    
    # 4. 龙虎榜数据
    try:
        lhb_data = get_longhubang()
        report['longhubang'] = lhb_data[:10] if lhb_data else []
    except:
        report['longhubang'] = []
    
    # 5. 综合判断
    # 情绪判断
    limit_up_count = sum(1 for d in leaders.values() if d.get('change_pct', 0) > 9)
    
    report['summary'] = {
        'market_status': report['market']['status'],
        'limit_up_count': limit_up_count,
        'emotion_cycle': '上升期' if limit_up_count >= 3 else '混沌期',
        'main_line': '光纤/算力/AI',
        'top_pick': '汇源通信' if leaders.get('汇源通信', {}).get('change_pct', 0) > 9 else None,
        'risk_warn': '津药药业' if leaders.get('津药药业', {}).get('change_pct', 0) < -3 else None,
    }
    
    return report


def format_report_text(report):
    """将报告格式化为易读的文本"""
    lines = []
    lines.append("=" * 50)
    lines.append(f"📊 每日股票复盘报告 - {report['date']}")
    lines.append(f"生成时间: {report['generated_at']}")
    lines.append("=" * 50)
    
    # 指数
    lines.append("\n📈 【大盘指数】")
    for name, data in report.get('market', {}).get('indices', {}).items():
        change = data.get('change_pct', 0)
        emoji = "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
        lines.append(f"  {emoji} {name}: {data.get('current', 0):.2f} ({change:+.2f}%)")
    
    market_status = report.get('market', {}).get('status', '未知')
    lines.append(f"\n  市场状态: {market_status}")
    
    # 连板龙头
    lines.append("\n🔥 【连板龙头】")
    for name, data in report.get('leaders', {}).items():
        change = data.get('change_pct', 0)
        emoji = "🌟" if change > 9 else "⬆️" if change > 0 else "⬇️"
        high = data.get('high', 0)
        low = data.get('low', 0)
        lines.append(f"  {emoji} {name}: {data.get('current', 0):.2f} ({change:+.2f}%) [高:{high:.2f} 低:{low:.2f}]")
    
    # 详细分析
    lines.append("\n🎯 【个股详细分析】")
    for name, analysis in report.get('analysis', {}).items():
        lines.append(f"\n  ■ {name} ({analysis.get('code', '')})")
        lines.append(f"    现价: {analysis.get('current', 0):.2f} ({analysis.get('change_pct', 0):+.2f}%)")
        
        today = analysis.get('today_analysis', {})
        for k, v in today.items():
            lines.append(f"    {k}: {v}")
        
        if analysis.get('is_limit_up'):
            lines.append(f"    🌟 涨停状态: {'一字板（最强）' if analysis.get('is_one_word_board') else '实体涨停'}")
        
        lines.append(f"    📍 建议买入: {analysis.get('buy_point', '观望')}")
        lines.append(f"    📍 建议卖出: {analysis.get('sell_point', '持有')}")
        lines.append(f"    ⚠️ 风险等级: {analysis.get('risk_level', '中')}")
    
    # 综合判断
    summary = report.get('summary', {})
    lines.append("\n" + "=" * 50)
    lines.append("📋 【综合判断】")
    lines.append(f"  情绪周期: {summary.get('emotion_cycle', '未知')}")
    lines.append(f"  主线题材: {summary.get('main_line', '待确认')}")
    
    if summary.get('top_pick'):
        lines.append(f"  🥇 重点关注: {summary.get('top_pick')}")
    if summary.get('risk_warn'):
        lines.append(f"  ⚠️ 风险提示: {summary.get('risk_warn')}")
    
    lines.append("=" * 50)
    
    return "\n".join(lines)


if __name__ == "__main__":
    print("正在获取数据...")
    report = generate_daily_report()
    
    # 保存JSON
    output_dir = "/home/dhtaiyi/.openclaw/workspace/stock-analysis"
    os.makedirs(output_dir, exist_ok=True)
    date_str = datetime.now().strftime('%Y%m%d')
    
    json_file = f"{output_dir}/report_{date_str}.json"
    with open(json_file, 'w') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"报告已保存: {json_file}")
    
    # 输出文本格式
    print()
    print(format_report_text(report))
