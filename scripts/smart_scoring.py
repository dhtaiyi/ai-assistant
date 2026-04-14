#!/usr/bin/env python3
"""
智能选股评分系统 V1 - 结合股票课程核心知识
==============================================
核心理论：
1. 举重理论：扩散=危险，收敛=安全
2. 主升浪三要素：低位起（<10元）、有故事、股性活跃
3. 涨停前图形：上影线突破、缩量回调、旗型整理
4. 威科夫：Spring=买入机会，Upthrust=卖出机会
5. 跟风原理：跟庄/跟机构，不抄底
6. 买点：首板（高开3-7%超预期）、一进二（分歧转一致）
==============================================
"""
import requests
import json
import re
import os
from datetime import datetime

LOG_FILE = "/tmp/smart_scoring.log"

# ========== 工具函数 ==========
def get_kline(code, days=5):
    """获取近N日K线数据"""
    try:
        # 转换代码格式
        c = code.replace('sz', '').replace('sh', '')
        prefix = 'sz' if code.startswith('sz') else 'sh'
        url = f'https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_day&param={prefix}{c},day,,,{days},qfq'
        r = requests.get(url, timeout=5)
        text = r.text
        # 解析JSON: kline_day={...}
        json_str = text[text.index('=')+1:]
        data = json.loads(json_str)
        klines = data.get('data', {}).get(f'{prefix}{c}', {}).get('qfqday', [])
        return klines[-days:]  # 返回最近的N天
    except Exception as e:
        return []

def calc_3day_gain(klines):
    """计算3日累计涨幅"""
    if len(klines) < 3:
        return 0
    try:
        close3 = float(klines[-3][1])  # 3天前收盘
        close0 = float(klines[-1][1])   # 今日收盘
        return (close0 - close3) / close3 * 100
    except:
        return 0

def calc_amplitude(klines):
    """计算近期振幅"""
    if not klines:
        return 0
    try:
        highs = [float(k[3]) for k in klines[-3:]]  # 最高价
        lows = [float(k[4]) for k in klines[-3:]]   # 最低价
        max_high = max(highs)
        min_low = min(lows)
        return (max_high - min_low) / min_low * 100
    except:
        return 0

def calc_volume_ratio(klines):
    """计算量比（今日量/近期均量）"""
    if len(klines) < 5:
        return 0
    try:
        volumes = [float(k[5]) for k in klines[-5:]]
        avg_vol = sum(volumes[:-1]) / len(volumes[:-1])
        today_vol = volumes[-1]
        return today_vol / avg_vol if avg_vol > 0 else 0
    except:
        return 0

def get_realtime_single(code):
    """获取单只股票实时数据"""
    try:
        c = code.replace('sz', '').replace('sh', '')
        prefix = 'sz' if code.startswith('sz') else 'sh'
        r = requests.get(f'http://qt.gtimg.cn/q={prefix}{c}', timeout=3)
        line = r.text.strip()
        if '"~' not in line:
            return None
        m = re.search(r'"([^"]+)"', line)
        if not m:
            return None
        parts = m.group(1).split('~')
        if len(parts) < 33:
            return None
        return {
            'name': parts[1],
            'price': float(parts[3]) if parts[3] else 0,
            'close_y': float(parts[4]) if parts[4] else 0,
            'open': float(parts[5]) if parts[5] else 0,
            'vol': float(parts[6]) if parts[6] else 0,
            'pct': float(parts[32]) if parts[32] else 0,
            'high': float(parts[33]) if parts[33] else 0,
            'low': float(parts[34]) if parts[34] else 0,
        }
    except:
        return None

def score_stock(code, info, klines, market_sh_pct=0):
    """
    综合评分（满分100）
    课程知识：
    - 成交额因子（30分）：越大越好，说明主力参与
    - 图形因子（25分）：收敛=好（举重理论）
    - 位置因子（20分）：低位起=安全，高位=危险
    - 跟风因子（15分）：成交额大+趋势强
    - 环境因子（10分）：指数配合=加分
    """
    score = 0
    details = []
    
    amount_yi = info.get('amount_yi', 0)
    pct = info.get('pct', 0)
    stock_type = info.get('type', 'unknown')
    
    # 1. 成交额因子（30分）
    if amount_yi >= 100:
        score += 30
        details.append("成交额爆棚(+30)")
    elif amount_yi >= 50:
        score += 20
        details.append("成交额大(+20)")
    elif amount_yi >= 20:
        score += 10
        details.append("成交额中等(+10)")
    else:
        details.append("成交额偏小(+0)")
    
    # 2. 图形因子（收敛=好）（25分）
    # 近3日振幅收敛=主力控盘=安全
    amplitude = calc_amplitude(klines)
    if klines and len(klines) >= 3:
        if amplitude <= 10:
            score += 25
            details.append(f"高度收敛(+25)")
        elif amplitude <= 15:
            score += 15
            details.append(f"中度收敛(+15)")
        elif amplitude <= 25:
            score += 5
            details.append(f"扩散警戒(+5)")
        else:
            details.append(f"扩散危险(+0)")
    
    # 3. 位置因子（20分）
    # 股价<10元=低位起（课程核心）
    price = info.get('price', 0)
    if price > 0 and price < 10:
        score += 20
        details.append("低位起(+20)")
    elif price < 20:
        score += 10
        details.append("中价安全(+10)")
    elif price >= 100:
        score -= 10  # 高价股风险加分
        details.append("高价股(-10)")
    
    # 4. 跟风/机构因子（15分）
    # 成交额大+不是涨停的强势股=机构参与
    vr = calc_volume_ratio(klines)
    if stock_type == '机构信号':
        score += 15
        details.append("机构跟风(+15)")
    elif pct >= 5 and pct < 9.9:
        score += 10
        details.append("强势跟风(+10)")
    elif vr >= 2:
        score += 8
        details.append(f"量比适中(+8)")
    elif vr >= 1.5:
        score += 4
        details.append(f"量比较好(+4)")
    
    # 5. 环境因子（10分）：指数配合
    if market_sh_pct > 0.5:
        score += 10
        details.append(f"指数配合(+10)")
    elif market_sh_pct > 0:
        score += 5
        details.append(f"指数中性(+5)")
    else:
        details.append(f"指数背离(+0)")
    
    # ========== 课程核心过滤器 ==========
    # 超过9%不好追（高空加油，风险大）
    if pct > 9.9 and pct < 20:
        score -= 5
        details.append("涨停谨慎(-5)")
    
    # 3日累计涨幅过大=短线超买
    gain3d = calc_3day_gain(klines)
    if gain3d > 25:
        score -= 10
        details.append(f"3日+{gain3d:.0f}%超买(-10)")
    elif gain3d > 15:
        score -= 5
        details.append(f"3日+{gain3d:.0f}%偏热(-5)")
    
    return {
        'code': code,
        'name': info.get('name', ''),
        'total_score': round(score, 1),
        'details': details,
        'amplitude': round(amplitude, 1),
        'gain3d': round(gain3d, 1),
        'vol_ratio': round(vr, 2),
        'price': price,
        'pct': pct,
        'amount_yi': amount_yi,
    }

def analyze_watchlist(candidates, market_sh_pct=0):
    """对候选股池进行智能评分"""
    results = []
    
    for code, info in candidates.items():
        # 跳过ST
        if 'ST' in info.get('name', ''):
            continue
        
        # 获取K线
        klines = get_kline(code, days=5)
        
        # 评分
        scored = score_stock(code, info, klines, market_sh_pct)
        results.append(scored)
        
        # 实时价格补充
        rt = get_realtime_single(code)
        if rt and rt.get('price', 0) > 0:
            scored['price'] = rt['price']
            scored['pct'] = rt['pct']
            scored['open_today'] = rt['open']
            # 竞价跳空计算
            if rt['close_y'] > 0:
                gap = (rt['open'] - rt['close_y']) / rt['close_y'] * 100
                scored['gap_open'] = round(gap, 2)
                # 竞价高开3-7%最佳
                if 3 <= gap <= 7:
                    scored['gap_score'] = '✅最佳'
                elif gap > 9:
                    scored['gap_score'] = '⚠️过高'
                elif gap < 0:
                    scored['gap_score'] = '🔴低开'
    
    # 按总分排序
    results.sort(key=lambda x: x['total_score'], reverse=True)
    return results

def get_market_sh_pct():
    """获取上证指数涨跌幅"""
    try:
        r = requests.get('http://qt.gtimg.cn/q=s_sh000001', timeout=3)
        m = re.search(r'"([^"]+)"', r.text)
        if m:
            parts = m.group(1).split('~')
            return float(parts[5]) if len(parts) > 5 else 0
    except:
        return 0

if __name__ == '__main__':
    import sys
    
    date_str = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime('%Y%m%d')
    cand_path = f'/home/dhtaiyi/.openclaw/workspace/stock-patterns/candidates/{date_str}.json'
    
    print(f"🧠 智能选股评分系统 V1 - {datetime.now().strftime('%H:%M')}")
    print(f"候选股池: {cand_path}")
    
    market_sh_pct = get_market_sh_pct()
    print(f"上证指数: {market_sh_pct:+.2f}%")
    print()
    
    if not os.path.exists(cand_path):
        print("❌ 候选股池不存在，请先运行早盘扫描")
        sys.exit(1)
    
    with open(cand_path) as f:
        candidates = json.load(f)
    
    print(f"📊 候选股池: {len(candidates)} 只")
    print("=" * 70)
    
    # 评分
    results = analyze_watchlist(candidates, market_sh_pct)
    
    # 输出TOP10
    for i, r in enumerate(results[:10], 1):
        print(f"\n{i}. **{r['name']}**({r['code']}) 总分:{r['total_score']}")
        print(f"   现价:{r['price']} 涨幅:{r['pct']:+.1f}% 成交:{r['amount_yi']:.0f}亿")
        print(f"   3日累计:{r['gain3d']:+.1f}% | 近3日振幅:{r['amplitude']:.1f}% | 量比:{r['vol_ratio']:.1f}x")
        if r.get('gap_open') is not None:
            print(f"   竞价跳空:{r['gap_open']:+.2f}% [{r.get('gap_score','?')}]")
        print(f"   加分项: {' | '.join(r['details'][:4])}")
    
    print("\n" + "=" * 70)
    print("💡 课程核心理念应用:")
    print("  • 举重理论：近3日振幅收敛→主力控盘→安全")
    print("  • 低位起：股价<10元→低位起→安全垫厚")
    print("  • 跟风原理：机构信号股+成交额大→主力参与")
    print("  • 竞价跳空：+3~7%超预期最佳，>9%风险大")
    print("  • 3日超买：累计涨幅>25%→短线回调风险")
    print("=" * 70)
    
    # 保存评分结果
    out_path = f'/home/dhtaiyi/.openclaw/workspace/stock-patterns/candidates/scored_{date_str}.json'
    with open(out_path, 'w') as f:
        json.dump(results[:10], f, ensure_ascii=False, indent=2)
    print(f"\n✅ 评分结果已保存: {out_path}")
