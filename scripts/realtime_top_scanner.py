#!/usr/bin/env python3
"""
午盘实时扫描器 V1 - 弥补早盘候选池的滞后性
==============================================
功能：
1. 实时获取当前涨幅榜TOP30
2. 结合成交额、振幅、封单强度综合评分
3. 识别"正在形成中的妖股"（早盘不在候选池但盘中爆发）
4. 输出增强版候选建议
==============================================
"""
import requests
import json
import re
import os
from datetime import datetime, time

LOG_FILE = "/tmp/realtime_top_scan.log"

def is_trading():
    """检查是否在交易时段（支持午休扫描）"""
    now = datetime.now().time()
    morning = time(9, 30) <= now <= time(11, 30)
    afternoon = time(13, 0) <= now <= time(15, 0)
    lunch = time(11, 30) < now < time(13, 0)
    return morning or afternoon or lunch  # 午休也允许扫描（有上午数据）

def is_clean_stock(s):
    name = s.get('name', '')
    if any(x in name for x in ['ST', '*ST', 'N ', '退', 'S ']):
        return False
    code = s.get('symbol', '')
    if code.startswith('bj'):
        return False
    return True

def get_full_code(symbol):
    code = symbol.replace('sz', '').replace('sh', '')
    prefix = 'sz' if symbol.startswith('sz') else 'sh'
    return prefix + code

def get_realtime_indices():
    """获取实时指数"""
    indices = {}
    try:
        r = requests.get('http://qt.gtimg.cn/q=s_sh000001,s_sz399001,s_sz399006', timeout=5)
        for line in r.text.strip().split('\n'):
            if '"' not in line:
                continue
            m = re.search(r'="([^"]+)"', line)
            if not m:
                continue
            parts = m.group(1).split('~')
            try:
                if len(parts) > 5 and parts[1]:
                    name = parts[1]
                    price = float(parts[3]) if parts[3] else 0
                    # 批量接口：len<20时parts[5]=涨跌幅
                    pct = float(parts[5]) if len(parts) > 5 and parts[5] else 0
                    indices[name] = {'price': price, 'pct': pct}
            except (ValueError, IndexError):
                continue
    except:
        pass
    return indices


def realtime_scan():
    """实时扫描TOP强势股"""
    url = 'https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeDataSimple'
    
    # 获取涨幅TOP200
    try:
        r1 = requests.get(url, params={
            'page': 1, 'num': 200,
            'sort': 'changepercent', 'asc': 0,
            'node': 'hs_a'
        }, timeout=10)
        all_stocks = r1.json()
    except Exception as e:
        print(f"❌ 获取涨幅榜失败: {e}")
        return

    # 获取成交额TOP100
    try:
        r2 = requests.get(url, params={
            'page': 1, 'num': 100,
            'sort': 'amount', 'asc': 0,
            'node': 'hs_a'
        }, timeout=10)
        by_amount = r2.json()
    except:
        by_amount = []

    # 成交额字典
    amount_dict = {}
    for s in (by_amount or []):
        sym = s.get('symbol', '')
        try:
            amount_dict[sym] = float(s.get('amount', 0)) / 1e8  # 亿
        except:
            pass

    # 指数
    indices = get_realtime_indices()

    # ===== 分类 =====
    limit_up = [s for s in all_stocks if float(s.get('changepercent', 0)) >= 9.5 and is_clean_stock(s)]
    strong = [s for s in all_stocks if 5 <= float(s.get('changepercent', 0)) < 9.5 and is_clean_stock(s)]

    print(f"\n{'='*60}")
    print(f"📊 午盘实时扫描 {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}")
    
    sh_pct = indices.get('上证指数', {}).get('pct', 0)
    print(f"指数: 上证 {indices.get('上证指数',{}).get('price','?')} ({sh_pct:+.2f}%)")
    print(f"      深证 {indices.get('深证成指',{}).get('price','?')} ({indices.get('深证成指',{}).get('pct',0):+.2f}%)")
    print(f"      创业板 {indices.get('创业板指',{}).get('price','?')} ({indices.get('创业板指',{}).get('pct',0):+.2f}%)")
    print(f"\n涨停: {len(limit_up)}只 | 强势(5-9%): {len(strong)}只")

    # ===== 妖股潜力评分 =====
    print(f"\n🔥 妖股潜力 TOP15（成交额+涨幅综合）:")
    candidates = []
    
    for s in (limit_up + strong):
        sym = s.get('symbol', '')
        try:
            pct = float(s.get('changepercent', 0))
            trade = float(s.get('trade', 0))
            high = float(s.get('high', 0))
            open_p = float(s.get('open', 0))
            amount = amount_dict.get(sym, 0)  # 亿
            close_y = float(s.get('settlement', 0))
            
            if not trade or not close_y:
                continue
            
            # 计算振幅
            amplitude = (high - close_y) / close_y * 100 if close_y > 0 else 0
            
            # 妖股评分（满分100）
            # 成交额得分（40分上限）：成交额越大越强
            amount_score = min(40, amount * 0.8)
            
            # 涨幅得分（30分）：越高越好
            pct_score = min(30, pct * 2)
            
            # 振幅得分（20分）：振幅大说明波动强，有主力
            amp_score = min(20, amplitude * 2)
            
            # 开板检测（10分）：从涨停打开到现在的，说明有分歧
            if pct >= 9.5 and open_p < trade:
                open_board_score = 10  # 开板过，有分歧但还能回封
            elif pct >= 9.5 and open_p == trade:
                open_board_score = 5   # 一直封着，没机会
            else:
                open_board_score = 5   # 强势股
            
            total_score = amount_score + pct_score + amp_score + open_board_score
            
            candidates.append({
                'name': s['name'],
                'code': get_full_code(sym),
                'pct': pct,
                'amount': amount,
                'amplitude': round(amplitude, 1),
                'score': round(total_score, 1),
                'type': '涨停' if pct >= 9.5 else '强势',
                'high': high,
                'open': open_p,
                'trade': trade
            })
        except (ValueError, TypeError, KeyError):
            continue

    # 按妖股评分排序
    candidates.sort(key=lambda x: x['score'], reverse=True)
    
    top15 = candidates[:15]
    for i, c in enumerate(top15, 1):
        amp_marker = "⚡" if c['amplitude'] > 5 else "  "
        board_marker = "🔓" if c['open'] < c['high'] and c['pct'] >= 9.5 else "  "
        print(f"  {i:2d}. {board_marker}{amp_marker}{c['name']}({c['code']}) "
              f"+{c['pct']:.1f}% 成交{c['amount']:.0f}亿 振幅{c['amplitude']:.1f}% "
              f"评分:{c['score']:.0f}")

    # ===== 成交额TOP10（机构信号）=====
    print(f"\n💰 成交额TOP10（机构信号）:")
    amt_sorted = sorted(
        [s for s in all_stocks if is_clean_stock(s) and float(s.get('changepercent', 0)) >= 3],
        key=lambda x: amount_dict.get(x.get('symbol',''), 0),
        reverse=True
    )[:10]
    
    for i, s in enumerate(amt_sorted, 1):
        sym = s.get('symbol', '')
        amt = amount_dict.get(sym, 0)
        pct = float(s.get('changepercent', 0))
        print(f"  {i:2d}. {s['name']}({get_full_code(sym)}) +{pct:.1f}% 成交{amt:.0f}亿")

    # ===== 买入机会检测 =====
    print(f"\n🎯 买点机会扫描:")
    opportunities = []
    
    for c in candidates:
        # 买点A：涨停板打开后回封（从高位回落但仍涨9%+）
        if 9.0 <= c['pct'] < 9.9 and c['amplitude'] > 3:
            opportunities.append(f"  🔔 {c['name']}({c['code']}) 买点A:首板战法(+{c['pct']:.1f}%,振幅{c['amplitude']:.1f}%)")
        
        # 买点B：一字板后开板（机构分歧）
        if c['pct'] >= 9.5 and c['open'] < c['high'] and c['amplitude'] > 4:
            opportunities.append(f"  🔓 {c['name']}({c['code']}) 开板分歧:关注回封(+{c['pct']:.1f}%,成交{c['amount']:.0f}亿)")
    
    if opportunities:
        for op in opportunities[:5]:
            print(op)
    else:
        print("  (暂无明显买点信号，等回落或回封确认)")

    # ===== 保存 ======
    today_str = datetime.now().strftime('%Y%m%d')
    save_dir = "/home/dhtaiyi/.openclaw/workspace/stock-data/realtime"
    os.makedirs(save_dir, exist_ok=True)
    save_path = f"{save_dir}/{today_str}_{datetime.now().strftime('%H%M')}.json"
    
    with open(save_path, 'w') as f:
        json.dump({
            'time': datetime.now().isoformat(),
            'indices': indices,
            'limit_up_count': len(limit_up),
            'strong_count': len(strong),
            'top15': top15,
            'amount_top10': [{'name': s['name'], 'code': get_full_code(s.get('symbol','')), 
                             'pct': float(s.get('changepercent',0)), 
                             'amount': amount_dict.get(s.get('symbol',''),0)} 
                            for s in amt_sorted]
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 实时扫描已保存: {save_path}")
    return top15, amt_sorted[:5]


if __name__ == "__main__":
    print(f"={'='*60}")
    print(f"🔥 午盘实时妖股扫描器 V1")
    print(f"={'='*60}")
    
    if not is_trading():
        print("⏰ 当前非交易时段（9:30-11:30 / 13:00-15:00）")
        print("   指数数据仅供参考，不进行完整扫描")
        
        # 仍获取指数数据
        indices = get_realtime_indices()
        if indices:
            print(f"\n当前指数:")
            for name, info in indices.items():
                print(f"  {name}: {info['price']} ({info['pct']:+.2f}%)")
        exit(0)
    
    top15, top_amt = realtime_scan()
    
    print(f"\n{'='*60}")
    print("💡 提示：午盘实时扫描弥补早盘候选池的滞后性")
    print("   早盘候选池基于昨日数据，本扫描基于实时强势股")
    print("   两者结合使用效果更佳！")
    print(f"{'='*60}")
