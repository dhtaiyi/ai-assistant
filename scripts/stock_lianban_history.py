#!/usr/bin/env python3
"""
连板梯队历史查询
查看近N天的连板数据
"""

import os
import json
from datetime import datetime, timedelta

DATA_DIR = os.path.expanduser("~/.openclaw/workspace/stock-data")

def get_files(days=7):
    """获取近N天的数据文件"""
    files = []
    for i in range(days):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y%m%d")
        filepath = os.path.join(DATA_DIR, f"limitup_{date}.json")
        if os.path.exists(filepath):
            files.append(filepath)
    return files

def load_data(filepath):
    """加载单日数据"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def show_history(days=7):
    """显示历史记录"""
    files = get_files(days)
    
    if not files:
        print("暂无历史数据")
        return
    
    print("\n" + "=" * 70)
    print(f"  📊 连板梯队历史（近{days}天）")
    print("=" * 70)
    
    for filepath in files:
        data = load_data(filepath)
        date = data.get('date', '')
        weekday = data.get('weekday', '')
        total = data.get('total_zt', 0)
        space = data.get('space_board', {})
        
        # 连板股票
        lianban = [s for s in data.get('stocks', []) if s.get('lianban', 0) > 0]
        
        print(f"\n📅 {date} ({weekday}) | 涨停{total}只 | 连板{len(lianban)}只")
        
        if space and space.get('lianban', 0) > 0:
            print(f"   🐉 空间板: {space['name']} {space['lianban']}板 [{space.get('sector', '')}]")
        
        if lianban:
            for s in sorted(lianban, key=lambda x: x['lianban'], reverse=True)[:5]:
                print(f"   {'🐉' if s['lianban']>=3 else '🔺'} {s['name']}({s['code']}) {s['lianban']}板 {s['pct']:.1f}%")
        
        # 板块分布
        sectors = data.get('sectors', [])
        hot_sectors = [s for s in sectors if s['count'] >= 2][:3]
        if hot_sectors:
            sec_str = " | ".join([f"{s['sector']}({s['count']})" for s in hot_sectors])
            print(f"   🔥 热门: {sec_str}")
    
    print("\n" + "=" * 70)

def show_space_board_history(days=30):
    """显示空间板历史"""
    files = get_files(days)
    
    if not files:
        print("暂无历史数据")
        return
    
    print("\n" + "=" * 70)
    print(f"  🐉 空间板历史（近{days}天）")
    print("=" * 70)
    
    space_boards = []
    for filepath in files:
        data = load_data(filepath)
        space = data.get('space_board', {})
        if space and space.get('lianban', 0) >= 3:
            space_boards.append({
                'date': data.get('date', ''),
                **space
            })
    
    if space_boards:
        for sb in space_boards[:10]:
            print(f"  📅 {sb['date']} | 🐉 {sb['name']}({sb['code']}) {sb['lianban']}板 [{sb.get('sector', '')}]")
    else:
        print("  暂无3板以上的空间板记录")
    
    print("=" * 70)

if __name__ == "__main__":
    import sys
    
    days = 7
    if len(sys.argv) > 1:
        if sys.argv[1] == '--space':
            show_space_board_history(30)
        else:
            days = int(sys.argv[1])
    
    show_history(days)
