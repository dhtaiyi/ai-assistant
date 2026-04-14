#!/usr/bin/env python3
"""
每日收盘后选股器 v2.1
自动从新浪财经获取全市场数据，选出明日监控标的，更新 breakthrough_alert.py

选股标准（参考课程战法）：
1. 涨幅 > 5%（今日强势）
2. 成交额 > 20亿（资金认可）
3. 流通市值 20-500亿（适中，易拉升）
4. 非ST、非新股开板

使用方法：
  python3 daily_candidate_picker.py
"""

import requests
import json
import os
from datetime import datetime

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0'}
BREAKTHROUGH_FILE = os.path.expanduser("~/.openclaw/workspace/scripts/breakthrough_alert.py")
PATTERNS_DIR = os.path.expanduser("~/.openclaw/workspace/stock-patterns/candidates")

def get_sina_data(sort='changepercent', n=80):
    """从新浪获取市场数据（涨幅榜或成交额榜）"""
    node_map = {
        'changepercent': 'hs_a',  # 涨幅榜
        'amount': 'hs_a',         # 成交额榜
    }
    url = f'https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=1&num={n}&sort={sort}&asc=0&node={node_map[sort]}&symbol=&_s_r_a=page'
    r = requests.get(url, timeout=10, headers=HEADERS)
    return json.loads(r.text)

def is_valid_stock(s):
    """过滤条件"""
    name = s.get('name', '')
    code = s.get('code', '')
    
    # 过滤ST、退市、新股
    if any(x in name for x in ['ST', 'N ', '*', '退']):
        return False
    
    # 成交额(元)转亿
    amount_亿 = float(s.get('amount', 0)) / 1e8
    if amount_亿 < 20:
        return False
    
    # 流通市值(万元)转亿
    circ_亿 = float(s.get('nmc', 0)) / 1e4
    if circ_亿 < 15 or circ_亿 > 500:
        return False
    
    return True

def score_stock(s):
    """综合评分"""
    pct = float(s.get('changepercent', 0))
    amount_亿 = float(s.get('amount', 0)) / 1e8
    circ_亿 = float(s.get('nmc', 0)) / 1e4
    
    # 涨幅权重40% + 成交额权重30% + 市值适中权重30%
    score = pct * 0.4 + min(amount_亿 / 10, 10) * 0.3 + min(circ_亿 / 50, 10) * 0.3
    return round(score, 2)

def select_candidates():
    """选股核心逻辑"""
    today_str = datetime.now().strftime('%Y%m%d')
    print(f"=== 每日选股 {today_str} ===\n")
    
    # 1. 获取涨幅榜80 + 成交额榜50
    gainers = get_sina_data('changepercent', 80)
    vol_top = get_sina_data('amount', 50)
    
    print(f"涨幅榜: {len(gainers)} 只, 成交额榜: {len(vol_top)} 只")
    
    # 合并去重
    pool = {}
    for s in gainers:
        code = s['code']
        pool[code] = s
    for s in vol_top:
        code = s['code']
        if code not in pool:
            pool[code] = s
    
    print(f"合并后候选池: {len(pool)} 只\n")
    
    # 2. 过滤 + 评分
    candidates = []
    for code, s in pool.items():
        if not is_valid_stock(s):
            continue
        
        score = score_stock(s)
        amount_亿 = float(s.get('amount', 0)) / 1e8
        circ_亿 = float(s.get('nmc', 0)) / 1e4
        
        candidates.append({
            'code': code,
            'name': s.get('name', ''),
            'price': float(s.get('trade', 0)),
            'pct': float(s.get('changepercent', 0)),
            'amount': round(amount_亿, 1),
            'circ_mv': round(circ_亿, 0),
            'high': float(s.get('high', 0)),
            'score': score,
        })
    
    # 3. 排序取前5
    candidates.sort(key=lambda x: x['score'], reverse=True)
    top5 = candidates[:5]
    
    print(f"=== 入选标的 ({len(top5)} 只) ===")
    for i, c in enumerate(top5, 1):
        print(f"  {i}. {c['name']}({c['code']}) {c['price']}元 +{c['pct']:.1f}% 成交{c['amount']:.0f}亿 流通{c['circ_mv']:.0f}亿 评分{c['score']}")
    
    return top5, today_str

def update_breakthrough_script(candidates, date_str):
    """更新 breakthrough_alert.py 的 WATCH_STOCKS"""
    
    stocks_lines = []
    for c in candidates:
        code = c['code']
        # 判断交易所前缀
        if code.startswith('6') or code.startswith('9'):
            prefix = 'sh'
        else:
            prefix = 'sz'
        
        full_code = f"{prefix}{code}"
        stocks_lines.append(
            f'    "{full_code}": {{"name": "{c["name"]}", "resist": {c["high"]}, "reason": "强势+{c["pct"]:.0f}%成交{c["amount"]:.0f}亿"}}'
        )
    
    stocks_str = ',\n'.join(stocks_lines)
    
    with open(BREAKTHROUGH_FILE, 'r') as f:
        content = f.read()
    
    start_marker = '# 重点监控的股票和关键价位'
    end_marker = '}\n\nSTATE_FILE'
    
    new_block = f'''# 重点监控的股票和关键价位 ({date_str} 自动更新)
WATCH_STOCKS = {{
{stocks_str}
}}

STATE_FILE'''
    
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    
    if start_idx == -1 or end_idx == -1:
        print(f"❌ 找不到替换位置!")
        return False
    
    end_idx += len(end_marker)
    
    new_content = content[:start_idx] + new_block + content[end_idx:]
    
    with open(BREAKTHROUGH_FILE, 'w') as f:
        f.write(new_content)
    
    print(f"\n✅ breakthrough_alert.py 已更新 {len(candidates)} 只标的")
    return True

def save_candidates_report(candidates, date_str):
    """保存候选股报告（两种格式）"""
    os.makedirs(PATTERNS_DIR, exist_ok=True)
    
    # 格式1: 带date元信息的完整报告
    report_path = f"{PATTERNS_DIR}/{date_str}_candidates.json"
    with open(report_path, 'w') as f:
        json.dump({
            'date': date_str,
            'candidates': candidates,
            'generated': datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)
    
    # 格式2: pattern_scan.py 所需的直接dict格式
    scan_fmt = {}
    for c in candidates:
        code = c['code']
        # 判断交易所前缀
        if code.startswith('6') or code.startswith('9'):
            prefix = 'sh'
        else:
            prefix = 'sz'
        full_code = f"{prefix}{code}"
        scan_fmt[full_code] = {
            'name': c['name'],
            'price': c['price'],
            'pct': c['pct'],
            'high': c['high'],
            'amount': c['amount'],
            'circ_mv': c['circ_mv'],
            'score': c['score']
        }
    
    scan_path = f"{PATTERNS_DIR}/{date_str}.json"
    with open(scan_path, 'w') as f:
        json.dump(scan_fmt, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 报告已保存: {report_path}")
    print(f"✅ 图形扫描数据: {scan_path}")

def main():
    candidates, date_str = select_candidates()
    
    if not candidates:
        print("❌ 未找到符合条件的标的!")
        return
    
    update_breakthrough_script(candidates, date_str)
    save_candidates_report(candidates, date_str)

if __name__ == '__main__':
    main()
