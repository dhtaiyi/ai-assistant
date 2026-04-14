#!/usr/bin/env python3
"""
A股连板梯队记录系统
每天记录涨停股及其连板数、所属板块
用于追踪龙头梯队历史
"""

import requests
import json
import os
import time
from datetime import datetime, timedelta
from collections import defaultdict

os.environ['NO_PROXY'] = '*'
os.environ['no_proxy'] = '*'

DATA_DIR = os.path.expanduser("~/.openclaw/workspace/stock-data")
os.makedirs(DATA_DIR, exist_ok=True)

def get_today_file():
    """获取今天的记录文件"""
    today = datetime.now().strftime("%Y%m%d")
    return os.path.join(DATA_DIR, f"limitup_{today}.json")

def get_yesterday_file():
    """获取昨天的记录文件"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    return os.path.join(DATA_DIR, f"limitup_{yesterday}.json")

def get_limitup_stocks():
    """获取今日涨停股列表"""
    url = "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeDataSimple"
    all_zt = []
    
    for page in range(1, 6):
        params = {'page': page, 'num': 100, 'sort': 'changepercent', 'asc': 0, 'node': 'hs_a'}
        try:
            r = requests.get(url, params=params, headers={'Referer': 'https://finance.sina.com.cn'}, timeout=15)
            stocks = r.json() if r.text else []
            for s in stocks:
                pct = float(s.get('changepercent', 0))
                if pct >= 9.9:
                    all_zt.append(s)
        except:
            continue
    
    return all_zt

def identify_sector(name, code):
    """识别个股所属板块"""
    # 简化版：基于名称关键词识别
    sector_keywords = {
        '医药': ['医药', '制药', '生化', '健康', '医疗', '中药', '生物', '药业', '康', '仁'],
        '科技': ['科技', '电子', '软件', '互联', '芯片', '半导体', '光', '芯', '瑞', '微'],
        '军工': ['军工', '航空', '航天', '船舶', '特气', '兵', '雷', '导', '舰'],
        '新能源': ['能源', '电气', '电力', '光伏', '锂', '电池', '储能', '汽车', '新能'],
        '化工': ['化工', '化学', '材料', '树脂', '制药'],
        '基建': ['建', '路桥', '市政', '工程', '设计'],
        '消费': ['食品', '饮料', '纺织', '服装', '零售', '电商'],
        '金融': ['银行', '证券', '保险', '信托', '租赁'],
    }
    
    # 从代码推断板块
    code_prefix = code[:2] if code else ''
    # 沪市6开头，科创板688，深市00/002/003开头，创业板300
    
    for sector, keywords in sector_keywords.items():
        for kw in keywords:
            if kw in name:
                return sector
    
    # 根据代码推断
    if code.startswith('688'):
        return '科创'
    elif code.startswith('300'):
        return '创业板'
    elif code.startswith('002'):
        return '中小板'
    
    return '其他'

def load_yesterday_data():
    """加载昨日数据用于计算连板数"""
    yest_file = get_yesterday_file()
    if not os.path.exists(yest_file):
        return {}
    
    with open(yest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 返回股票代码集合
    yesterday_stocks = {}
    for item in data.get('stocks', []):
        code = item.get('code', '').replace('sh', '').replace('sz', '')
        yesterday_stocks[code] = item
    
    return yesterday_stocks

def calculate_lianban(zt_stocks, yesterday_stocks):
    """计算连板数"""
    result = []
    
    for s in zt_stocks:
        name = s.get('name', '')
        symbol = s.get('symbol', '')
        code = symbol.replace('sh', '').replace('sz', '')
        pct = float(s.get('changepercent', 0))
        price = s.get('trade', 0)
        
        # 检查是否昨日涨停（计算连板）
        lianban = 0
        if code in yesterday_stocks:
            lianban = yesterday_stocks[code].get('lianban', 0) + 1
        
        sector = identify_sector(name, code)
        
        result.append({
            'name': name,
            'code': code,
            'symbol': symbol,
            'pct': pct,
            'price': float(price) if price else 0,
            'lianban': lianban,
            'sector': sector,
        })
    
    # 按连板数和涨幅排序
    result.sort(key=lambda x: (x['lianban'], x['pct']), reverse=True)
    return result

def save_daily_record(zt_stocks, lianban_stocks):
    """保存今日记录"""
    today_file = get_today_file()
    
    today = datetime.now().strftime("%Y-%m-%d")
    today_weekday = datetime.now().strftime("%A")
    
    data = {
        'date': today,
        'weekday': today_weekday,
        'total_zt': len(zt_stocks),
        'stocks': lianban_stocks,
        'sectors': analyze_sectors(lianban_stocks),
        'space_board': get_space_board(lianban_stocks),
    }
    
    with open(today_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return data

def analyze_sectors(stocks):
    """分析今日涨停板块分布"""
    sector_count = defaultdict(list)
    
    for s in stocks:
        sector = s.get('sector', '其他')
        sector_count[sector].append(s)
    
    # 转换为排序后的列表
    result = []
    for sector, items in sorted(sector_count.items(), key=lambda x: len(x[1]), reverse=True):
        result.append({
            'sector': sector,
            'count': len(items),
            'stocks': [f"{i['name']}({i['lianban']}板)" for i in items]
        })
    
    return result

def get_space_board(stocks):
    """获取空间板（连板数最高的）"""
    if not stocks:
        return None
    
    max_lianban = max(s.get('lianban', 0) for s in stocks)
    space_boards = [s for s in stocks if s.get('lianban', 0) == max_lianban]
    
    return {
        'name': space_boards[0]['name'],
        'code': space_boards[0]['code'],
        'lianban': max_lianban,
        'pct': space_boards[0]['pct'],
        'sector': space_boards[0]['sector'],
    }

def print_report(data):
    """打印日报"""
    print("\n" + "=" * 60)
    print(f"  📊 A股涨停板日报 {data['date']} ({data['weekday']})")
    print("=" * 60)
    
    print(f"\n📈 涨停家数: {data['total_zt']}")
    
    # 空间板
    if data.get('space_board'):
        sb = data['space_board']
        print(f"\n🐉 空间板: {sb['name']}({sb['code']}) {sb['lianban']}连板 {sb['pct']:.1f}% [{sb['sector']}]")
    
    # 连板梯队
    lianban_stocks = [s for s in data['stocks'] if s.get('lianban', 0) >= 2]
    if lianban_stocks:
        print(f"\n📊 连板梯队 ({len(lianban_stocks)}只):")
        for s in lianban_stocks:
            board_emoji = "🐉" if s['lianban'] >= 3 else "🔺" if s['lianban'] == 2 else "📈"
            print(f"  {board_emoji} {s['name']}({s['code']}) {s['lianban']}板 {s['pct']:.1f}%")
    
    # 板块分布
    if data.get('sectors'):
        print(f"\n🏭 涨停板块分布:")
        for sec in data['sectors'][:5]:
            if sec['count'] >= 2:
                print(f"  {sec['sector']}: {sec['count']}只 - {', '.join(sec['stocks'][:3])}")
    
    print("\n" + "=" * 60)

def run():
    """主函数"""
    print("📡 获取今日涨停数据...")
    zt_stocks = get_limitup_stocks()
    print(f"今日涨停: {len(zt_stocks)}只")
    
    print("📊 加载昨日数据计算连板...")
    yesterday_stocks = load_yesterday_data()
    print(f"昨日涨停: {len(yesterday_stocks)}只")
    
    print("🔢 计算连板数据...")
    lianban_stocks = calculate_lianban(zt_stocks, yesterday_stocks)
    
    print("💾 保存记录...")
    data = save_daily_record(zt_stocks, lianban_stocks)
    
    print_report(data)
    
    return data

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--check':
        # 检查模式：只输出关键数据
        today_file = get_today_file()
        if os.path.exists(today_file):
            with open(today_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print_report(data)
        else:
            print("今日数据尚未记录，先运行完整命令")
    else:
        run()
