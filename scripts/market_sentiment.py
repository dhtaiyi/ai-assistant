#!/usr/bin/env python3
"""
每日市场情绪判断 V2 - 区分机构主导 vs 连板情绪
"""
import requests
import json
import re
from datetime import datetime

def get_sentiment():
    log = []

    url = 'https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeDataSimple'
    r1 = requests.get(url, params={'page': 1, 'num': 200, 'sort': 'changepercent', 'asc': 0, 'node': 'hs_a'}, timeout=10)
    by_pct = r1.json()
    r2 = requests.get(url, params={'page': 1, 'num': 100, 'sort': 'amount', 'asc': 0, 'node': 'hs_a'}, timeout=10)
    by_amt = r2.json()
    r_idx = requests.get('http://qt.gtimg.cn/q=s_sh000001,s_sz399001,s_sz399006', timeout=5)
    
    indices = {}
    for line in r_idx.text.strip().split('\n'):
        m = re.search(r'"([^"]+)"', line)
        if not m:
            continue
        parts = m.group(1).split('~')
        if len(parts) > 5:
            name = parts[1]
            indices[name] = {'price': float(parts[3] or 0), 'pct': float(parts[5] or 0)}

    sh_pct = indices.get('上证指数', {}).get('pct', 0)
    limit_up = [s for s in by_pct if float(s.get('changepercent', 0)) >= 9.9]
    big_up = [s for s in by_pct if 5 <= float(s.get('changepercent', 0)) < 9.9]
    lu = len(limit_up)
    total_amount = sum(float(s.get('amount', 0)) for s in by_amt[:50]) / 1e8

    log.append(f"📊 市场概况")
    log.append(f"  涨停: {lu} | 大涨5-9%: {len(big_up)}")
    for name, info in indices.items():
        log.append(f"  {name}: {info['price']} {info['pct']:+.2f}%")

    log.append(f"\n💰 成交额TOP5:")
    top5_non_lu = []
    for s in by_amt[:5]:
        amount_yi = float(s.get('amount', 0)) / 1e8
        pct = float(s.get('changepercent', 0))
        tag = "🔵" if pct < 9.9 else "🔴"
        log.append(f"  {tag} {s['name']} {pct:+.1f}% 成交{amount_yi:.0f}亿")
        if pct < 9.9 and pct >= 3:
            top5_non_lu.append(s)

    # ========== 核心判断 ==========
    # 机构主导信号：成交额TOP5中至少2只不是涨停(涨幅2%+)，且总成交额大
    # (宽松条件：只要成交额前5有2只以上是非涨停的强势股，就可能是机构行情)
    is_institutional = (len(top5_non_lu) >= 2 and total_amount > 200)

    if is_institutional:
        top5_names = [s['name'] for s in top5_non_lu[:5]]
        inst_list = [f"{s['name']}({float(s.get('changepercent',0)):+.0f}%)" for s in top5_non_lu[:5]]
        sentiment = "🔵 机构主导行情"
        strategy = "不追连板！跟机构抱团趋势股；重点关注成交额前5"
        action = "趋势股持有+轻仓首板"
        hot_stocks = top5_names
    elif lu >= 80:
        sentiment = "🟢 主升浪(连板情绪)"
        strategy = "满仓干龙头！"
        action = "重仓连板"
        hot_stocks = [s['name'] for s in limit_up[:5]]
        inst_list = []
    elif lu >= 50:
        sentiment = "🔥 上升期(连板情绪)"
        strategy = "积极参与龙头连板"
        action = "仓位7-8成"
        hot_stocks = [s['name'] for s in limit_up[:5]]
        inst_list = []
    elif lu >= 30:
        sentiment = "⚡ 混沌期"
        strategy = "轻仓参与，情绪好时出击"
        action = "仓位3-5成"
        hot_stocks = [s['name'] for s in limit_up[:5]] if limit_up else [s['name'] for s in big_up[:5]]
        inst_list = []
    else:
        sentiment = "❄️ 退潮期"
        strategy = "空仓或极轻仓，只做首板"
        action = "仓位1成"
        hot_stocks = []
        inst_list = []

    log.append(f"\n{'='*55}")
    log.append(f"{sentiment}")
    log.append(f"📋 策略: {strategy}")
    log.append(f"🎯 建议: {action}")
    if hot_stocks and not is_institutional:
        log.append(f"🏆 情绪龙头: {', '.join(hot_stocks)}")
    if is_institutional and inst_list:
        log.append(f"🔵 机构抱团: {', '.join(inst_list)}")
    log.append(f"{'='*55}")

    result = {
        'date': datetime.now().strftime('%Y%m%d'),
        'time': datetime.now().strftime('%H:%M'),
        'sentiment': sentiment,
        'strategy': strategy,
        'action': action,
        'limit_up': lu,
        'institutional': is_institutional,
        'sh_pct': sh_pct,
        'top_amt': [{'name': s['name'], 'pct': float(s.get('changepercent',0)), 'amount_yi': round(float(s.get('amount',0))/1e8,1)} for s in by_amt[:10]],
        'hot_stocks': hot_stocks,
        'inst_stocks': [s['name'] for s in top5_non_lu[:5]] if is_institutional else []
    }
    with open('/tmp/sentiment_result.json', 'w') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return log

if __name__ == '__main__':
    print(f"市场情绪判断 V2 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()
    for line in get_sentiment():
        print(line)
