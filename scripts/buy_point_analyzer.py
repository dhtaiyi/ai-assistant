#!/usr/bin/env python3
"""
买点分析系统 - 结合退学炒股+养家心法
==============================================
退学炒股核心理念：
- 首板战法：昨日涨停，今高开3-7%超预期，介入
- 一进二：分歧转一致，缩量板最佳
- 弱转强：昨日冲高回落，今超预期高开
- 空间板5日线低吸：龙头首阴不破5日线

养家心法：
- 强势市场重仓，弱势市场轻仓
- 别人贪婪时我贪婪，别人恐惧时我恐惧
- 确定性第一位
==============================================
"""
import requests
import json
import re
from datetime import datetime

def get_kline(code, days=8):
    """获取近N日K线"""
    try:
        c = code.replace('sz', '').replace('sh', '')
        prefix = 'sz' if code.startswith('sz') else 'sh'
        url = f'https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_day&param={prefix}{c},day,,,{days},qfq'
        r = requests.get(url, timeout=5)
        json_str = r.text[r.text.index('=')+1:]
        data = json.loads(json_str)
        return data.get('data', {}).get(f'{prefix}{c}', {}).get('qfqday', [])
    except:
        return []

def get_realtime_info(code):
    """获取实时行情"""
    try:
        c = code.replace('sz', '').replace('sh', '')
        prefix = 'sz' if code.startswith('sz') else 'sh'
        r = requests.get(f'http://qt.gtimg.cn/q={prefix}{c}', timeout=3)
        m = re.search(r'"([^"]+)"', r.text)
        if not m:
            return None
        parts = m.group(1).split('~')
        if len(parts) < 33:
            return None
        price = float(parts[3]) if parts[3] else 0
        close_y = float(parts[4]) if parts[4] else 0
        open_today = float(parts[5]) if parts[5] else 0
        vol = float(parts[6]) if parts[6] else 0
        high = float(parts[33]) if parts[33] else 0
        low = float(parts[34]) if parts[34] else 0
        return {
            'price': price, 'close_y': close_y, 'open': open_today,
            'high': high, 'low': low, 'vol': vol,
            'pct': float(parts[32]) if parts[32] else 0
        }
    except:
        return None

def analyze_buy_points(code, name):
    """分析买点机会"""
    rt = get_realtime_info(code)
    klines = get_kline(code, days=8)
    
    if not rt or not klines:
        return None
    
    results = []
    
    # 计算近期关键数据
    closes = [float(k[1]) for k in klines]
    highs = [float(k[3]) for k in klines]
    lows = [float(k[4]) for k in klines]
    vols = [float(k[5]) for k in klines]
    
    ma5 = sum(closes[-5:]) / 5 if len(closes) >= 5 else closes[-1]
    ma10 = sum(closes[-10:]) / 10 if len(closes) >= 10 else ma5
    
    yesterday_close = closes[-2] if len(closes) >= 2 else rt['close_y']
    today_open = rt['open']
    today_pct = rt['pct']
    # ========== 买点A：首板战法 ==========
    # 条件：昨日涨幅<3%，今高开3-7%，分时图强势
    yesterday_pct = (yesterday_close - (closes[-2] if len(closes) >= 3 else closes[-2])) / (closes[-2] if len(closes) >= 3 else yesterday_close) * 100 if len(closes) >= 3 else 0
    if len(closes) >= 3:
        yesterday_pct = (yesterday_close - closes[-3]) / closes[-3] * 100
    
    # 简化：今日涨停且昨日涨幅不大
    if today_pct >= 9.5 and yesterday_pct < 6:
        gap = (today_open - yesterday_close) / yesterday_close * 100
        if 3 <= gap <= 8:
            results.append({
                'type': '🅰️ 买点A - 首板战法',
                'action': '打板介入',
                'entry_range': f"{today_open*1.0:.2f}（竞价{today_open:.2f}）",
                'stop_loss': f"{yesterday_close*0.95:.2f}（-5%）",
                'condition': f"昨日+{yesterday_pct:.1f}%，今日竞价{gap:+.1f}%",
                'confidence': '高' if 3 <= gap <= 6 else '中'
            })
    
    # ========== 买点B：一进二接力 ==========
    # 条件：昨日涨停，今高开<9%（不能太高），成交适中
    if today_pct >= 9.5 and yesterday_pct >= 9.5:
        gap = (today_open - yesterday_close) / yesterday_close * 100
        avg_vol = sum(vols[-6:-1]) / 5 if len(vols) >= 6 else vols[-1]
        today_vol = vols[-1] if len(vols) >= 1 else 0
        vol_ratio = today_vol / avg_vol if avg_vol > 0 else 0
        
        if gap < 9:  # 高开不超过9%
            # 缩量一进二最佳
            if vol_ratio < 1.2:
                results.append({
                    'type': '🅱️ 买点B - 一进二（缩量）',
                    'action': '打板/半路',
                    'entry_range': f"{today_open:.2f}~涨停价",
                    'stop_loss': f"{yesterday_close*0.93:.2f}（-7%）",
                    'condition': f"竞价{gap:+.1f}%，量比{vol_ratio:.1f}x（缩量最佳）",
                    'confidence': '高'
                })
            else:
                results.append({
                    'type': '🅱️ 买点B - 一进二（放量）',
                    'action': '谨慎打板',
                    'entry_range': f"回踩均线买入",
                    'stop_loss': f"{yesterday_close*0.93:.2f}",
                    'condition': f"竞价{gap:+.1f}%，量比{vol_ratio:.1f}x（放量=分歧大）",
                    'confidence': '中'
                })
    
    # ========== 买点C：5日线低吸（龙头回调） ==========
    # 条件：股价在ma5附近，缩量止跌
    if rt['price'] <= ma5 * 1.05 and rt['price'] >= ma5 * 0.93:
        if len(closes) >= 3:
            body3 = closes[-1] - closes[-3]  # 3日内K线实体总和
            if body3 > 0:  # 整体上涨趋势
                results.append({
                    'type': '🅲 买点C - 5日线低吸',
                    'action': '回踩5日线买入',
                    'entry_range': f"{ma5:.2f}附近",
                    'stop_loss': f"{ma5*0.97:.2f}（-3%）",
                    'condition': f"当前价{rt['price']}，MA5={ma5:.2f}",
                    'confidence': '中'
                })
    
    # ========== 买点D：收敛突破（举重理论） ==========
    # 条件：近3日振幅逐日收窄，缩量整理
    if len(closes) >= 4:
        amp3 = (highs[-1] - lows[-1]) / lows[-1] * 100
        amp2 = (highs[-2] - lows[-2]) / lows[-2] * 100
        amp1 = (highs[-3] - lows[-3]) / lows[-3] * 100
        if amp3 < amp2 < amp1 and amp3 < 5:  # 连续收敛
            results.append({
                'type': '🅳 买点D - 收敛突破',
                'action': '突破颈线买入',
                'entry_range': f"{highs[-1]:.2f}突破后",
                'stop_loss': f"{lows[-1]:.2f}（-3%）",
                'condition': f"3日振幅{amp1:.1f}%→{amp2:.1f}%→{amp3:.1f}%（收敛）",
                'confidence': '高'
            })
    
    # ========== 卖点：高位放量滞涨 ==========
    if len(closes) >= 3:
        avg_vol5 = sum(vols[-5:]) / 5
        today_vol_last = vols[-1]
        vol_ratio5 = today_vol_last / avg_vol5 if avg_vol5 > 0 else 0
        last_high = highs[-1]
        if rt['price'] > 0 and last_high > 0:
            if (last_high - rt['price']) / last_high > 0.05:  # 收盘跌破高位5%
                results.append({
                    'type': '🚨 卖点 - 高位滞涨',
                    'action': '止盈离场',
                    'entry_range': '不追高',
                    'stop_loss': f"{rt['price']*0.97:.2f}",
                    'condition': f"收盘{rt['price']}，高位{last_high}，振幅>5%",
                    'confidence': '-'
                })
    
    return results

def analyze_all(scored_file):
    """对评分结果文件分析买点"""
    with open(scored_file) as f:
        stocks = json.load(f)
    
    print(f"🧠 买点分析报告 - {datetime.now().strftime('%H:%M')}")
    print(f"分析标的: {len(stocks)} 只")
    print("=" * 70)
    
    for i, stock in enumerate(stocks[:8], 1):
        code = stock['code']
        name = stock['name']
        score = stock['total_score']
        
        print(f"\n{i}. **{name}**({code}) 综合评分:{score}")
        print(f"   {stock.get('price',0)}元 {stock.get('pct',0):+.1f}% | 3日+{stock.get('gain3d',0):+.1f}% | 振幅{stock.get('amplitude',0):.1f}%")
        
        buy_points = analyze_buy_points(code, name)
        if buy_points:
            for bp in buy_points:
                tag = "🟢" if "买点" in bp['type'] else "🔴"
                print(f"   {tag} {bp['type']}: {bp['action']}")
                print(f"      买入区间: {bp['entry_range']} | 止损: {bp['stop_loss']}")
                print(f"      条件: {bp['condition']} | 置信度: {bp['confidence']}")
        else:
            print(f"   ⏸️ 暂无明确买点，等待信号")
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    import sys
    date_str = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime('%Y%m%d')
    scored_file = f'/home/dhtaiyi/.openclaw/workspace/stock-patterns/candidates/scored_{date_str}.json'
    analyze_all(scored_file)
