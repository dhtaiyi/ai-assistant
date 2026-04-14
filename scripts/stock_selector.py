#!/usr/bin/env python3
"""
A股短线选股模型 v1.0
基于：龙之精髓 + 课程体系 + 情绪周期 + 龙头战法

核心框架：
  情绪周期 → 选股标准 → 买点信号 → 仓位管理 → 止损纪律

使用方法：
  python3 stock_selector.py              # 完整选股
  python3 stock_selector.py --cycle     # 判断情绪周期
  python3 stock_selector.py --help      # 帮助

数据来源：腾讯 qt.gtimg.cn + 新浪 vip.stock.finance.sina.com.cn
"""
import requests
import sys
import json
import os
from datetime import datetime

os.environ['NO_PROXY'] = '*'
os.environ['no_proxy'] = '*'

# ========== MX API（东方财富妙想）==========
MX_APIKEY = "mkt_vu-pj52--GcXTwXkYR5reA8DX0Vq3E2y_fyygU2aB4g"
MX_URL = "https://mkapi2.dfcfs.com/finskillshub/api/claw/query"

def mx_query(tool_query):
    """查询MX API"""
    try:
        r = requests.post(MX_URL,
            headers={"Content-Type": "application/json", "apikey": MX_APIKEY},
            json={"toolQuery": tool_query},
            timeout=15)
        return r.json()
    except:
        return {}

def mx_get_table(result):
    """从MX API结果中提取表格数据"""
    try:
        tables = result.get('data', {}).get('data', {}).get('searchDataResultDTO', {}).get('dataTableDTOList', [])
        return tables
    except:
        return []

def get_mx_market_stats():
    """用MX API获取市场统计数据"""
    stats = {}
    
    # 涨停家数
    r1 = mx_query("今日涨停家数")
    for t in mx_get_table(r1):
        raw = t.get('rawTable', {})
        for k in raw:
            if k != 'headName':
                try:
                    stats['zt'] = int(raw[k][0])
                    stats['date'] = raw['headName'][0] if raw.get('headName') else ''
                except:
                    pass
    
    # 跌停家数
    r2 = mx_query("今日跌停家数")
    for t in mx_get_table(r2):
        raw = t.get('rawTable', {})
        for k in raw:
            if k != 'headName':
                try:
                    stats['zd'] = int(raw[k][0])
                except:
                    pass
    
    # 上涨家数
    r3 = mx_query("今日上涨家数")
    for t in mx_get_table(r3):
        raw = t.get('rawTable', {})
        for k in raw:
            if k != 'headName':
                try:
                    stats['up'] = int(raw[k][0])
                except:
                    pass
    
    # 下跌家数
    r4 = mx_query("今日下跌家数")
    for t in mx_get_table(r4):
        raw = t.get('rawTable', {})
        for k in raw:
            if k != 'headName':
                try:
                    stats['down'] = int(raw[k][0])
                except:
                    pass
    
    return stats

def get_mx_index():
    """用MX API获取指数数据"""
    indices = []
    
    for name, code in [("上证指数", "000001.SH"), ("深证成指", "399001.SZ"), ("创业板指", "399006.SZ")]:
        r = mx_query(f"{name} 最新收盘点位")
        for t in mx_get_table(r):
            raw = t.get('rawTable', {})
            for k in raw:
                if k != 'headName' and len(raw[k]) > 0:
                    try:
                        price = float(str(raw[k][0]).replace(',', ''))
                        indices.append({'name': name, 'price': price})
                    except:
                        pass
    return indices

# ========== 额外选股维度（来自用户脚本）==========

def get_rising_speed(limit=30):
    """
    涨速榜 - fid='f3' 按涨速排序
    来源：zhangsu.py
    """
    url = "http://push2.eastmoney.com/api/qt/clist/get"
    params = {
        'pn': 1, 'pz': limit, 'po': 1, 'np': 1,
        'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
        'fltt': 2, 'invt': 2,
        'fid': 'f3',  # 涨速
        'fs': 'm:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23',  # 全A股+科创
        'fields': 'f2,f3,f4,f12,f14',
    }
    headers = {'Referer': 'http://quote.eastmoney.com/'}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        return r.json().get('data', {}).get('diff', [])
    except:
        return []

# ========== 数据获取 ==========

def get_indices():
    """获取主要指数"""
    codes = "sh000001,sz399001,sz399006,sh000300,sz399005"
    r = requests.get(f"http://qt.gtimg.cn/q={codes}", timeout=10)
    r.encoding = 'gbk'
    indices = []
    for line in r.text.split(';'):
        if 'v_' not in line: continue
        data = line.split('"')[1] if '"' in line else ''
        f = data.split('~')
        if len(f) < 33 or not f[1]: continue
        indices.append({'name': f[1], 'price': float(f[3]), 'pct': float(f[32])})
    return indices

def get_market_data(num=5000):
    """获取全市场数据"""
    url = "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeDataSimple"
    params = {'page': 1, 'num': num, 'sort': 'changepercent', 'asc': 0, 'node': 'hs_a'}
    headers = {'Referer': 'https://finance.sina.com.cn'}
    r = requests.get(url, params=params, headers=headers, timeout=20)
    return r.json() if r.text else []

def get_realtime(code):
    """获取单只股票实时数据"""
    r = requests.get(f"http://qt.gtimg.cn/q={code}", timeout=10)
    r.encoding = 'gbk'
    data = r.text.split('"')[1] if '"' in r.text else ''
    f = data.split('~')
    if len(f) < 33 or not f[1]: return None
    return {
        'name': f[1], 'code': code,
        'price': float(f[3]), 'prev': float(f[4]),
        'open': float(f[5]), 'high': f[33], 'low': f[34],
        'pct': float(f[32]), 'date': f[30]
    }

# ========== 情绪周期判断 ==========

def judge_cycle(stocks):
    """判断超短情绪周期"""
    zt = sum(1 for s in stocks if float(s.get('changepercent', 0)) >= 9.9)
    zd = sum(1 for s in stocks if float(s.get('changepercent', 0)) <= -9.9)
    total = len(stocks)
    up = sum(1 for s in stocks if float(s.get('changepercent', 0)) > 0)
    down = sum(1 for s in stocks if float(s.get('changepercent', 0)) < 0)
    
    up_ratio = up / total * 100 if total > 0 else 0
    
    # 周期判断（综合涨停数 + 上涨比例 + 跌停数）
    # 上升期：涨停多(>=30) + 上涨比例高(>=40%) + 跌停少(<=10)
    # 混沌期：涨停一般(15-30) 或 上涨比例一般(20-40%)
    # 退潮期：涨停少(<15) 或 上涨比例低(<20%) 或 跌停多(>=20)
    
    if zt >= 50 and zd <= 5 and up_ratio >= 40:
        cycle = ("🟢 上升期", "积极做多，满仓干龙头", 8)
        cycle_level = "主升期"
    elif zt >= 30 and zd <= 10 and up_ratio >= 30:
        cycle = ("🟢 上升期(初期)", "试探性做多，精选龙头", 6)
        cycle_level = "启动确认期"
    elif zt >= 20 and up_ratio >= 20:
        cycle = ("🟡 混沌期", "谨慎操作，高低切换", 4)
        cycle_level = "混沌期"
    elif zt >= 10 or (up_ratio >= 15 and zd < 20):
        cycle = ("🟡 退潮期(初期)", "控仓试错，不追高位", 2)
        cycle_level = "退潮初期"
    else:
        cycle = ("🔴 退潮期", "空仓等待，不做接力", 0)
        cycle_level = "主跌期"
    
    return {
        'cycle': cycle[0],
        'advice': cycle[1],
        'zt': zt, 'zd': zd,
        'up': up, 'down': down, 'total': total,
        'up_ratio': up / total * 100 if total > 0 else 0,
        'zt_ratio': zt / total * 100 if total > 0 else 0,
        'level': cycle_level,
        'risk_level': cycle[2],  # 0-10 风险等级
    }

# ========== 选股标准（低、先、量、识、活） ==========

def filter_stocks(stocks, cycle_info):
    """
    选股五字诀：
    低：低位1-2板
    先：板块内率先上板
    量：量价齐升，换手充分
    识：有辨识度，题材正宗
    活：流动性好（流通市值20-50亿）
    
    额外维度（来自用户脚本）：
    - 涨速榜：短期强势信号
    - 放量突破：资金关注
    """
    level = cycle_info['level']
    risk = cycle_info['risk_level']
    
    candidates = []
    
    for s in stocks:
        try:
            pct = float(s.get('changepercent', 0))
            symbol = s.get('symbol', '')
            name = s.get('name', '')
            
            # ===== 涨停股筛选 =====
            if pct >= 9.9:
                if 'ST' in name or '*' in name:
                    continue
                
                candidates.append({
                    'name': name,
                    'symbol': symbol,
                    'pct': pct,
                    'type': '涨停',
                    'reason': '涨停封板',
                })
            
            # ===== 强势股（涨幅5-9.9%）=====
            elif 5 <= pct < 9.9 and risk >= 4:
                if 'ST' in name or '*' in name:
                    continue
                candidates.append({
                    'name': name,
                    'symbol': symbol,
                    'pct': pct,
                    'type': '强势',
                    'reason': '涨幅5-10%强势',
                })
            
            # ===== 放量突破（来自breakout.py逻辑）=====
            # 放量突破：涨幅>3% + 成交量放大
            elif 3 <= pct < 5 and risk >= 6:
                if 'ST' in name or '*' in name:
                    continue
                candidates.append({
                    'name': name,
                    'symbol': symbol,
                    'pct': pct,
                    'type': '放量突破',
                    'reason': '放量突破3%+（突破候选）',
                })
                
        except (ValueError, TypeError):
            continue
    
    # 按涨幅排序
    candidates.sort(key=lambda x: x['pct'], reverse=True)
    
    return candidates[:30]

# ========== 买点信号判断（整合课程+用户脚本）==========

def check_buy_signals(stock, realtime_data):
    """
    买点信号检查（整合课程体系 + breakout.py + upper_shadow.py）
    
    ✅ 买点信号：
    1. 涨停封板（缩量 > 烂板）
    2. 突破20日高点（breakout.py逻辑）
    3. 放量突破（量比 > 1.3）
    4. 涨速快（短期资金关注）
    5. 分歧转一致（烂板回封）
    
    ❌ 卖点/规避信号：
    1. 涨停炸板（出货）
    2. 尾盘急拉（操纵 - upper_shadow.py）
    3. 高位利空（该涨不涨）
    4. 钓鱼线（主力出货）
    5. 上影线过长 > 实体80%（upper_shadow.py）
    """
    signals = []
    warnings = []
    
    if not realtime_data:
        return signals, warnings
    
    pct = realtime_data.get('pct', 0)
    price = realtime_data.get('price', 0)
    high = float(realtime_data.get('high', 0)) if realtime_data.get('high') else 0
    open_price = realtime_data.get('open', 0)
    
    # ===== 涨停信号 =====
    if pct >= 9.9:
        if high > price * 1.005:
            signals.append("⚠️ 烂板（曾经开板）")
        else:
            signals.append("✅ 缩量涨停（强势）")
        
        # 上影线判断（来自upper_shadow.py）
        if open_price > 0:
            upper_shadow = high - max(open_price, price)
            body = abs(price - open_price)
            if body > 0 and upper_shadow > body * 0.8:
                warnings.append("⚠️ 上影线过长（>实体80%），警惕诱多")
    
    # ===== 强势信号 =====
    elif 5 <= pct < 9.9:
        signals.append(f"🟢 强势上涨 {pct:.2f}%")
    
    # ===== 放量突破信号（来自breakout.py）=====
    elif 3 <= pct < 5:
        signals.append(f"🟡 放量突破候选 {pct:.2f}%")
        warnings.append("💡 需确认成交量是否持续放大")
    
    # ===== 高位警告 =====
    if high > 0 and price >= high * 0.98:
        warnings.append("⚠️ 接近历史高位，小心见顶")
    
    return signals, warnings

# ========== 主选股函数 ==========

def select_stocks():
    """完整选股流程"""
    print("=" * 60)
    print("🎯 A股短线选股模型 v1.0")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    # Step 1: 获取指数
    print("\n📊 【第一步：指数环境】")
    indices = get_indices()
    if indices:
        for idx in indices:
            emoji = "🟢" if idx['pct'] >= 0 else "🔴"
            print(f"  {emoji} {idx['name']}: {idx['price']:.2f} ({idx['pct']:+.2f}%)")
    
    # Step 2: 获取市场数据（优先MX API，备用新浪）
    print("\n📈 【第二步：市场情绪】")
    
    mx_stats = get_mx_market_stats()
    if mx_stats.get('zt'):
        print(f"  （数据来源：MX API）")
        print(f"  涨停: {mx_stats.get('zt', '-')} 只  跌停: {mx_stats.get('zd', '-')} 只")
        print(f"  上涨: {mx_stats.get('up', '-')} 只  下跌: {mx_stats.get('down', '-')} 只")
        if mx_stats.get('date'):
            print(f"  数据日期: {mx_stats['date']}")
        
        # 用MX数据手动判断周期
        zt = mx_stats.get('zt', 0)
        zd = mx_stats.get('zd', 0)
        up = mx_stats.get('up', 0)
        down = mx_stats.get('down', 0)
        total = up + down
        up_ratio = up / total * 100 if total > 0 else 0
        
        if zt >= 50 and zd <= 5 and up_ratio >= 40:
            cycle = ("🟢 上升期", "积极做多，满仓干龙头", 8, "主升期")
        elif zt >= 30 and zd <= 10 and up_ratio >= 30:
            cycle = ("🟢 上升期(初期)", "试探性做多，精选龙头", 6, "启动确认期")
        elif zt >= 20 and up_ratio >= 20:
            cycle = ("🟡 混沌期", "谨慎操作，高低切换", 4, "混沌期")
        elif zt >= 10 or (up_ratio >= 15 and zd < 20):
            cycle = ("🟡 退潮期(初期)", "控仓试错，不追高位", 2, "退潮初期")
        else:
            cycle = ("🔴 退潮期", "空仓等待，不做接力", 0, "主跌期")
        
        print(f"  📍 情绪周期: {cycle[0]}")
        print(f"  📍 周期阶段: {cycle[3]}")
        print(f"  📍 操作建议: {cycle[1]}")
        print(f"  📍 风险等级: {'⚠️ ' + str(cycle[2]) + '/10' if cycle[2] < 5 else '✅ ' + str(cycle[2]) + '/10'}")
        risk_level = cycle[2]
        cycle_level = cycle[3]
        stocks = get_market_data() if risk_level > 0 else []
    else:
        print("  （数据来源：新浪API）")
        stocks = get_market_data()
        if not stocks:
            print("  ❌ 无法获取市场数据")
            return
        
        cycle = judge_cycle(stocks)
        print(f"  上涨: {cycle['up']} 只  下跌: {cycle['down']} 只")
        print(f"  涨停: {cycle['zt']} 只  跌停: {cycle['zd']} 只")
        print(f"  ")
        print(f"  📍 情绪周期: {cycle['cycle']}")
        print(f"  📍 周期阶段: {cycle['level']}")
        print(f"  📍 操作建议: {cycle['advice']}")
        print(f"  📍 风险等级: {'⚠️ ' + str(cycle['risk_level']) + '/10' if cycle['risk_level'] < 5 else '✅ ' + str(cycle['risk_level']) + '/10'}")
        risk_level = cycle['risk_level']
        cycle_level = cycle['level']
    
    # Step 3: 选股
    print("\n🔍 【第三步：筛选标的】")
    if risk_level == 0:
        print("  🔴 退潮期，全市场空仓，不进行选股")
        return
    
    candidates = filter_stocks(stocks, {'risk_level': risk_level, 'level': cycle_level})
    print(f"  初步筛选: {len(candidates)} 只候选")
    
    if not candidates:
        print("  ⚠️ 没有符合条件的标的")
        return
    
    # Step 4: 买点信号检查
    print("\n✅ 【第四步：买点信号】")
    for i, cand in enumerate(candidates[:10], 1):
        symbol = cand['symbol']
        rt = get_realtime(symbol)
        signals, warnings = check_buy_signals(cand, rt)
        
        print(f"\n  {i}. {cand['name']} ({symbol})")
        print(f"     涨幅: {cand['pct']:+.2f}%  类型: {cand['type']}")
        
        if rt:
            print(f"     现价: {rt['price']:.2f}  最高: {rt['high']}")
        
        for sig in signals:
            print(f"     {sig}")
        for warn in warnings:
            print(f"     {warn}")
        
        if cand['pct'] >= 9.9 and cycle['risk_level'] >= 6:
            print(f"     💡 建议: {'重点关注' if '烂板' not in str(signals) else '谨慎观察'}")
        elif cand['pct'] >= 9.9:
            print(f"     💡 建议: 观察为主，不追高")
    
    # Step 5: 仓位建议
    print("\n💼 【第五步：仓位建议】")
    risk = cycle['risk_level']
    if risk >= 8:
        print("  🟢 上升期：仓位 8-10层")
        print("  策略：满仓干龙头，不犹豫")
    elif risk >= 6:
        print("  🟢 初期上升：仓位 6-7层")
        print("  策略：精选龙头，重仓博弈")
    elif risk >= 4:
        print("  🟡 混沌期：仓位 3-5层")
        print("  策略：高低切换，快进快出")
    elif risk >= 2:
        print("  🟡 退潮初期：仓位 1-2层")
        print("  策略：小仓试错，不追高位")
    else:
        print("  🔴 退潮期：仓位 0层")
        print("  策略：空仓等待，宁可错过")
    
    # Step 6: 风险提示
    print("\n⚠️ 【第六步：风险提示】")
    print("  1. 止损纪律：-7%无条件止损")
    print("  2. 仓位控制：不重仓单只超过3层")
    print("  3. 买点原则：分歧转一致时买入")
    print("  4. 卖点原则：不幻想，不格局，该走就走")
    print("  5. 退潮期：空仓就是最大的赢家")
    
    print("\n" + "=" * 60)
    print("📋 选股模型核心口诀")
    print("=" * 60)
    print("""
  🎯 选股五字诀：低、先、量、识、活
  📈 周期判断：上升期重仓，退潮期空仓
  💡 买点信号：分歧转一致，烂板回封
  ⚠️ 卖点纪律：不幻想，该走就走
  🔴 退潮期：空仓就是赢
    """)
    print("=" * 60)

def print_cycle():
    """仅打印情绪周期"""
    stocks = get_market_data()
    if not stocks:
        print("❌ 无法获取数据")
        return
    cycle = judge_cycle(stocks)
    print(f"\n📊 今日情绪周期：{cycle['cycle']}")
    print(f"📍 周期阶段：{cycle['level']}")
    print(f"💼 操作建议：{cycle['advice']}")
    print(f"⚠️ 风险等级：{cycle['risk_level']}/10")
    print(f"\n📈 涨停：{cycle['zt']} 只  跌停：{cycle['zd']} 只")
    print(f"📊 上涨：{cycle['up']} 只  下跌：{cycle['down']} 只")
    print(f"📊 上涨比例：{cycle['up_ratio']:.1f}%")

# ========== CLI ==========

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == '--cycle':
            print_cycle()
        elif sys.argv[1] == '--help':
            print("""
🎯 A股短线选股模型 v1.0

用法:
  python3 stock_selector.py         # 完整选股流程
  python3 stock_selector.py --cycle # 仅判断情绪周期
  python3 stock_selector.py --help  # 帮助

选股框架：
  1. 指数环境 → 判断市场整体
  2. 市场情绪 → 判断周期（上升/混沌/退潮）
  3. 筛选标的 → 五字诀（低先量识活）
  4. 买点信号 → 涨停/烂板回封/分歧转一致
  5. 仓位建议 → 根据周期调整
  6. 风险提示 → 止损纪律

周期仓位对照：
  上升期(8-10级风险) → 8-10层仓
  初期上升(6-8级风险) → 6-7层仓
  混沌期(4-6级风险) → 3-5层仓
  退潮初期(2-4级风险) → 1-2层仓
  退潮期(0-2级风险) → 0层仓
            """)
        else:
            print("未知参数，使用 --help 查看帮助")
    else:
        select_stocks()
