#!/usr/bin/env python3
"""
板块题材检测器 V1 - 识别主线主题
==============================================
核心功能：
1. 统计涨停股所属板块分布
2. 识别"主题效应"（多股联动=主线确认）
3. 计算板块强度和市场主线

理论依据（养家心法）：
- "跟龙头"：只做主线，不做杂毛
- 主题效应：同一板块多股涨停 = 资金认可
- 跟风原理：主线内的跟风股也有机会

数据来源：涨停股所属板块（手动标注行业映射）
"""
import requests
import json
import re
import os
from datetime import datetime
from collections import defaultdict

LOG_FILE = "/tmp/sector_theme.log"

# 股票→板块映射（常见标的，持续完善）
SECTOR_MAP = {
    # AI/科技
    '寒武纪': 'AI芯片', '协创数据': 'AI算力', '剑桥科技': '光模块',
    '光迅科技': '光模块', '中际旭创': '光模块', '新易盛': '光模块',
    '天孚通信': '光模块', '华工科技': '光模块',
    '中国西电': '电力设备', '许继电气': '电力设备', '平高电气': '电力设备',
    '西部材料': '军工材料', '神剑股份': '军工材料',
    '沐曦股份': 'AI芯片', '壁仞科技': 'AI芯片',
    
    # 医药/大健康
    '博瑞医药': '医药', '华人健康': '医药', '健信超导': '医药',
    '瑞康医药': '医药流通', '金陵药业': '中药',
    
    # 新能源
    '宁德时代': '新能源车', '阳光电源': '储能', '亿纬锂能': '电池',
    '神剑股份': '军工', '圣阳股份': '储能',
    
    # 消费/零售
    '天邦食品': '消费', '居然智家': '消费',
    
    # 机器人/AI应用
    '柯力传感': '传感器', '长芯博创': 'AI应用',
    '巨力索具': '通用设备', '利通电子': '电子',
    
    # 科技硬件
    '长信科技': '电子', '大族激光': '激光设备',
    '佰维存储': '存储', '兆易创新': '存储', '江波龙': '存储',
    '沪电股份': 'PCB', '东山精密': '精密制造',
    '立讯精密': '消费电子', '鹏鼎控股': 'PCB',
    '工业富联': 'AI服务器', '胜宏科技': 'PCB',
    
    # 连板强势股
    '华远控股': '地产', '来伊份': '食品', '睿能科技': '科技',
    '汇源通信': '通信', '通鼎互联': '通信',
}

# 板块分组（用于识别板块内部联动）
SECTOR_GROUPS = {
    'AI算力': ['寒武纪', '协创数据', '工业富联', '沐曦股份', '壁仞科技'],
    '光模块': ['剑桥科技', '光迅科技', '中际旭创', '新易盛', '天孚通信', '华工科技'],
    '存储': ['佰维存储', '兆易创新', '江波龙'],
    'PCB': ['沪电股份', '鹏鼎控股', '胜宏科技'],
    '军工': ['神剑股份', '西部材料'],
    '医药': ['博瑞医药', '华人健康', '健信超导', '瑞康医药'],
    '新能源车': ['宁德时代', '亿纬锂能'],
    '储能': ['阳光电源', '圣阳股份'],
}


def get_limitup_stocks(n=100):
    """获取涨停股列表"""
    url = 'https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeDataSimple'
    try:
        r = requests.get(url, params={
            'page': 1, 'num': n,
            'sort': 'changepercent', 'asc': 0,
            'node': 'hs_a'
        }, timeout=10)
        all_stocks = r.json()
        return [s for s in all_stocks if float(s.get('changepercent', 0)) >= 9.5]
    except:
        return []


def get_sector(name):
    """获取股票所属板块"""
    if name in SECTOR_MAP:
        return SECTOR_MAP[name]
    
    # 关键词匹配
    keywords = {
        '医药': ['医药', '制药', '健康', '医疗'],
        '科技': ['科技', '智能', 'AI', '算力'],
        '光模块': ['光模块', '光通信', '光器件'],
        '新能源': ['能源', '储能', '电池', '锂电'],
        '电子': ['电子', '半导体', '芯片'],
        '通信': ['通信', '5G', '光纤'],
        '军工': ['军工', '国防'],
        '消费': ['消费', '零售', '食品'],
    }
    
    for sector, kws in keywords.items():
        for kw in kws:
            if kw in name:
                return sector
    return '其他'


def detect_themes():
    """检测板块主题"""
    stocks = get_limitup_stocks()
    if not stocks:
        return {}
    
    # 统计板块
    sector_count = defaultdict(list)
    for s in stocks:
        name = s.get('name', '')
        pct = float(s.get('changepercent', 0))
        amount = float(s.get('amount', 0)) / 1e8
        symbol = s.get('symbol', '')
        code = ('sz' if symbol.startswith('sz') else 'sh') + symbol.replace('sz','').replace('sh','')
        
        sector = get_sector(name)
        sector_count[sector].append({
            'name': name,
            'code': code,
            'pct': pct,
            'amount': amount
        })
    
    # 计算板块强度（涨停股数量+成交额）
    sector_strength = {}
    for sector, members in sector_count.items():
        total_amount = sum(m['amount'] for m in members)
        avg_pct = sum(m['pct'] for m in members) / len(members)
        strength = len(members) * 10 + total_amount * 0.1
        sector_strength[sector] = {
            'count': len(members),
            'total_amount': round(total_amount, 1),
            'avg_pct': round(avg_pct, 1),
            'strength': round(strength, 1),
            'members': members[:5]  # 最多显示5只
        }
    
    return sector_strength


def analyze():
    print(f"\n{'='*60}")
    print(f"🔥 板块题材检测 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")
    
    sector_strength = detect_themes()
    
    if not sector_strength:
        print("❌ 无数据")
        return
    
    # 按强度排序
    sorted_sectors = sorted(sector_strength.items(), key=lambda x: x[1]['strength'], reverse=True)
    
    print(f"\n📊 板块热度排行榜:")
    for sector, info in sorted_sectors[:10]:
        if info['count'] >= 2:
            marker = "🔥"
        elif info['count'] >= 1:
            marker = "⚡"
        else:
            marker = "  "
        
        print(f"  {marker}{sector}: {info['count']}只涨停 {info['avg_pct']:+.1f}% 均涨幅 {info['total_amount']:.0f}亿成交")
        for m in info['members'][:3]:
            print(f"      {m['name']}({m['code']}) +{m['pct']:.1f}%")
    
    # ===== 主线识别 =====
    main_themes = [(s, i) for s, i in sorted_sectors if i['count'] >= 2]
    
    print(f"\n{'─'*60}")
    print(f"💎 主线题材（涨停≥2只）:")
    if main_themes:
        for sector, info in main_themes[:5]:
            print(f"  👑 {sector}: {info['count']}只连动")
            for m in info['members'][:3]:
                print(f"      → {m['name']} +{m['pct']:.1f}%")
    else:
        print("  （暂无明确主线，混沌期特征）")
    
    # ===== 跟风机会 =====
    print(f"\n{'─'*60}")
    print(f"📈 跟风机会（主线内滞涨股）:")
    
    for sector, info in main_themes[:3]:
        members = sorted(info['members'], key=lambda x: x['pct'])
        # 找涨幅相对小的跟风股
        if len(members) >= 2:
            follower = members[0]  # 涨幅最小的
            leader = members[-1]    # 涨幅最大的
            if follower['pct'] < leader['pct'] - 3:
                print(f"  🔄 {sector}跟风: {follower['name']}(+{follower['pct']:.1f}%) 跟{leader['name']}(+{leader['pct']:.1f}%)")
    
    # ===== 养家心法提示 =====
    print(f"\n{'─'*60}")
    print(f"💡 养家心法提示:")
    
    if main_themes:
        top = main_themes[0]
        print(f"  ✅ 主线明确: {top[0]}（{top[1]['count']}只涨停）")
        print(f"  → 只做主线龙头，不做杂毛")
    else:
        print(f"  ⚠️ 无明确主线，混沌期，轻仓练习")
    
    if len(main_themes) >= 3:
        print(f"  ✅ 多主线并存，行情活跃，可以积极操作")
    
    # ===== 保存 =====
    today_str = datetime.now().strftime('%Y%m%d')
    save_dir = "/home/dhtaiyi/.openclaw/workspace/stock-data/sector"
    os.makedirs(save_dir, exist_ok=True)
    save_path = f"{save_dir}/{today_str}.json"
    
    save_data = {
        'time': datetime.now().isoformat(),
        'main_themes': [(s, i) for s, i in sorted_sectors if i['count'] >= 2],
        'all_sectors': sector_strength
    }
    
    with open(save_path, 'w') as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 板块数据已保存: {save_path}")


if __name__ == "__main__":
    print(f"板块题材检测 V1 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    analyze()
