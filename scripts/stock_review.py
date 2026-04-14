#!/usr/bin/env python3
"""
A股短线复盘工具 v1.0
基于：超短情绪周期 + 退学炒股 + 龙头战法 + 蜡烛图技术

使用方法：
  python3 stock_review.py              # 完整复盘
  python3 stock_review.py --help      # 帮助

数据来源：腾讯 qt.gtimg.cn + 新浪 vip.stock.finance.sina.com.cn
"""
import requests
import sys
import json
import os
from datetime import datetime

os.environ['NO_PROXY'] = '*'
os.environ['no_proxy'] = '*'

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
        indices.append({
            'name': f[1],
            'price': float(f[3]),
            'pct': float(f[32]),
            'date': f[30][:8] if len(f[30]) >= 8 else '',
            'time': f[30][8:] if len(f[30]) > 8 else '',
        })
    return indices

def get_market_data(num=5000):
    """获取全市场数据"""
    url = "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeDataSimple"
    params = {'page': 1, 'num': num, 'sort': 'changepercent', 'asc': 0, 'node': 'hs_a'}
    headers = {'Referer': 'https://finance.sina.com.cn'}
    r = requests.get(url, params=params, headers=headers, timeout=20)
    return r.json() if r.text else []

# ========== 情绪周期判断 ==========

def judge_cycle(stocks):
    """判断超短情绪周期：上升期/混沌期/退潮期"""
    zt = sum(1 for s in stocks if float(s.get('changepercent', 0)) >= 9.9)
    zd = sum(1 for s in stocks if float(s.get('changepercent', 0)) <= -9.9)
    total = len(stocks)
    up = sum(1 for s in stocks if float(s.get('changepercent', 0)) > 0)
    down = sum(1 for s in stocks if float(s.get('changepercent', 0)) < 0)
    up5 = sum(1 for s in stocks if 5 <= float(s.get('changepercent', 0)) < 9.9)

    # 涨停家数判断
    # 上升期：涨停 > 50，且没有批量跌停
    # 混沌期：涨停 20-50，轮动快
    # 退潮期：涨停 < 20，跌停增加

    cycle = None
    if zt >= 50 and zd <= 5:
        cycle = ("🟢 上升期", "情绪高涨，题材持续，可积极做多")
    elif zt >= 20 and zt < 50:
        cycle = ("🟡 混沌期", "轮动较快，高低切换，精选个股")
    elif zt < 20 or zd >= 20:
        cycle = ("🔴 退潮期", "情绪低迷，控制仓位，空仓等待")
    else:
        cycle = ("🟡 混沌期", "情绪一般，谨慎操作")

    return {
        'cycle': cycle[0],
        'advice': cycle[1],
        'zt': zt,
        'zd': zd,
        'up': up,
        'down': down,
        'total': total,
        'up5': up5,
        'zt_ratio': zt / total * 100 if total > 0 else 0,
        'up_ratio': up / total * 100 if total > 0 else 0,
    }

# ========== 强势股分析 ==========

def analyze_top_stocks(stocks, limit=10):
    """分析最强/最弱个股"""
    sorted_by_pct = sorted(stocks, key=lambda x: float(x.get('changepercent', 0)), reverse=True)

    # 涨停股
    zt_stocks = [s for s in sorted_by_pct if float(s.get('changepercent', 0)) >= 9.9]

    # 强势股（涨幅5-10%，非涨停）
    strong = [s for s in sorted_by_pct if 5 <= float(s.get('changepercent', 0)) < 9.9]

    # 弱势股
    weak = sorted_by_pct[-5:]

    return {
        'zt': zt_stocks[:limit],
        'strong': strong[:5],
        'weak': weak,
    }

# ========== 指数联动分析 ==========

def analyze_indices(indices):
    """分析指数联动关系"""
    result = []
    for idx in indices:
        pct = idx['pct']
        emoji = "🟢" if pct >= 0 else "🔴"
        result.append(f"  {emoji} {idx['name']}: {idx['price']:.2f} ({pct:+.2f}%)")
    return "\n".join(result)

# ========== 主复盘函数 ==========

def full_review():
    """完整复盘"""
    print("=" * 60)
    print("📊 A股短线复盘")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 1. 获取指数
    print("\n🌏 【一、指数表现】")
    indices = get_indices()
    if indices:
        date = indices[0].get('date', '')
        print(f"   数据时间: {date[:4]}-{date[4:6]}-{date[6:8]} {indices[0].get('time','')}")
        print(analyze_indices(indices))
    else:
        print("   ❌ 无法获取指数数据")

    # 2. 获取市场数据
    print("\n📈 【二、市场情绪】")
    stocks = get_market_data()
    if not stocks:
        print("   ❌ 无法获取市场数据")
        return

    cycle = judge_cycle(stocks)
    print(f"   数据量: {cycle['total']} 只")
    print(f"   上涨: {cycle['up']} 只 🟢  下跌: {cycle['down']} 只 🔴")
    print(f"   涨停: {cycle['zt']} 只 ⭐  跌停: {cycle['zd']} 只 💥")
    print(f"   涨幅5-10%: {cycle['up5']} 只")
    print(f"   ")
    print(f"   📍 情绪周期: {cycle['cycle']}")
    print(f"   💡 操作建议: {cycle['advice']}")

    # 3. 强势股分析
    print("\n🔥 【三、强势股】")
    top = analyze_top_stocks(stocks)
    print(f"   涨停股 ({len(top['zt'])}只):")
    for i, s in enumerate(top['zt'][:5], 1):
        pct = float(s.get('changepercent', 0))
        print(f"     {i}. ⭐ {s.get('name')} ({s.get('symbol')}) +{pct:.2f}%")

    if top['strong']:
        print(f"\n   强势股 (涨幅5-10%):")
        for i, s in enumerate(top['strong'][:3], 1):
            pct = float(s.get('changepercent', 0))
            print(f"     {i}. 🟢 {s.get('name')} ({s.get('symbol')}) +{pct:.2f}%")

    # 4. 弱势股
    print("\n❄️ 【四、弱势股】")
    for i, s in enumerate(top['weak'], 1):
        pct = float(s.get('changepercent', 0))
        emoji = "💥" if pct <= -9 else "🔴"
        print(f"     {i}. {emoji} {s.get('name')} ({s.get('symbol')}) {pct:.2f}%")

    # 5. 短线操作要点
    print("\n📋 【五、复盘要点】")
    print(f"   1. 今日涨停 {cycle['zt']} 只 → {'情绪较好，可积极' if cycle['zt']>=30 else '情绪一般，谨慎'}")
    print(f"   2. 跌停 {cycle['zd']} 只 → {'有亏钱效应，注意回避' if cycle['zd']>=10 else '亏钱效应可控'}")
    print(f"   3. 上涨比例 {cycle['up_ratio']:.1f}% → {'多方占优' if cycle['up_ratio']>50 else '空方占优'}")
    print(f"   4. 情绪周期: {cycle['cycle'].split()[1]}")

    # 6. 明日预判
    print("\n🔮 【六、明日预判】")
    if cycle['zt'] >= 50 and cycle['zd'] <= 5:
        print("   → 情绪上升期延续，关注龙头股继续表现")
        print("   → 关注方向：今日涨停股是否有二波机会")
    elif cycle['zt'] >= 20:
        print("   → 混沌期，高低切换，快速轮动")
        print("   → 策略：低吸不追高，聚焦主线龙头")
    else:
        print("   → 退潮期，管住手，等情绪回暖")
        print("   → 关注：是否有新题材启动信号")

    print("\n" + "=" * 60)

# ========== CLI ==========

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ('-h', '--help'):
        print("""
📊 A股短线复盘工具

用法:
  python3 stock_review.py              # 完整复盘
  python3 stock_review.py sh600519    # 查询个股
  python3 stock_review.py --help       # 帮助

复盘框架:
  一、指数表现      - 主要指数涨跌
  二、市场情绪      - 涨停/跌停家数 → 判断周期
  三、强势股        - 涨停股/强势股
  四、弱势股        - 跌停/大跌股
  五、复盘要点      - 情绪/亏钱效应/多方占比
  六、明日预判      - 周期判断 → 操作策略

情绪周期判断:
  上升期: 涨停>=50 且 跌停<=5  → 积极做多
  混沌期: 涨停20-50           → 精选个股
  退潮期: 涨停<20 或 跌停>=20  → 空仓等待
""")
    elif len(sys.argv) > 1 and sys.argv[1].startswith(('sh', 'sz', 'bj')):
        code = sys.argv[1]
        r = requests.get(f"http://qt.gtimg.cn/q={code}", timeout=10)
        r.encoding = 'gbk'
        data = r.text.split('"')[1] if '"' in r.text else ''
        f = data.split('~')
        if len(f) > 32 and f[1]:
            pct = float(f[32])
            emoji = "🟢" if pct >= 0 else "🔴"
            print(f"\n{emoji} {f[1]} ({code})")
            print(f"   当前: {float(f[3]):.2f}")
            print(f"   昨收: {float(f[4]):.2f}")
            print(f"   涨跌: {float(f[31]):+.2f} ({pct:+.2f}%)")
            print(f"   最高: {f[33]}  最低: {f[34]}")
            print(f"   时间: {f[30]}")
        else:
            print(f"❌ 无法获取 {code}")
    else:
        full_review()
