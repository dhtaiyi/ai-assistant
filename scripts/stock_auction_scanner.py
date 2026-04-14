#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集合竞价强势扫描 + 突破形态确认
9:24运行，结合股票知识分析，9:25推送飞书
"""
import requests
import json
import time
from mootdx.quotes import Quotes
from datetime import datetime

# Feishu Bot credentials (from TOOLS.md)
FEISHU_APP_ID = "cli_a92923c6a2f99bc0"
FEISHU_APP_SECRET = "H4CdLHf1NwM1iv3JWzBsfdFFUY8bO4At"
FEISHU_USER_ID = "ou_04add8ebe219f09799570c70e3cdc732"

# 盯盘白名单（今日重点）
WATCH = {
    '000586': {'name': '汇源通信', 'reason': '光纤龙头4连板', 'level': '🔥🔥🔥'},
    '002491': {'name': '通鼎互联', 'reason': '龙虎榜主力买入1.93亿', 'level': '🔥🔥'},
    '000919': {'name': '金陵药业', 'reason': '2连板低位启动', 'level': '🔥🔥'},
    '600654': {'name': '中安科', 'reason': 'AI应用跟风强势', 'level': '🔥'},
    '603538': {'name': '美诺华', 'reason': '一字涨停强势', 'level': '🔥🔥'},
    '600488': {'name': '津药药业', 'reason': '7板炸板注意风险', 'level': '⚠️'},
    '300308': {'name': '中际旭创', 'reason': '历史新高突破', 'level': '🔥🔥'},
}

# Tencent internal code to standard code mapping
REVERSE_MAP = {
    '8686': '000586',
    '111295': '002491',
    '84311': '000919',
    '109676': '600654',
    '72935': '603538',
    '219214': '600488',
    '2647988': '300308',
}

TENCENT_CODES = [('sh' if c.startswith('6') else 'sz') + c for c in WATCH.keys()]


def get_auction_data():
    """获取集合竞价数据 from 腾讯"""
    headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://finance.qq.com'}
    url = 'https://qt.gtimg.cn/q=' + ','.join(TENCENT_CODES)
    try:
        r = requests.get(url, timeout=5, headers=headers)
        r.encoding = 'gbk'
        lines = r.text.strip().split('\n')
        result = {}
        for line in lines:
            if '="' not in line:
                continue
            parts = line.split('="')[1].rstrip('";').split('~')
            if len(parts) < 40:
                continue
            raw = parts[37] if len(parts) > 37 else ''
            code = raw
            for c in WATCH:
                if c == raw or c == parts[3]:
                    code = c
                    break
            # Map Tencent internal codes to standard codes
            if code not in WATCH and raw in REVERSE_MAP:
                code = REVERSE_MAP[raw]
            result[code] = {
                'prev_close': float(parts[4]) if parts[4] else 0,
                'open': float(parts[5]) if parts[5] else 0,
                'current': float(parts[3]) if parts[3] else 0,
                'high': float(parts[33]) if parts[33] else 0,
                'low': float(parts[34]) if parts[34] else 0,
            }
        return result
    except Exception as e:
        print('auction error:', e)
        return {}


def get_vol_ratio(code):
    """获取量比 (今日成交量/5日均量)"""
    try:
        client = Quotes.factory(market='std')
        market = 0 if code[0] in '03' else 1
        bars = client.bars(symbol=code, frequency=9, market=market, offset=25)
        client.close()
        if bars is None or len(bars) < 20:
            return None, None
        vol_ma5 = bars['volume'].iloc[-5:].mean()
        vol_ma20 = bars['volume'].iloc[-20:].mean()
        today_vol = bars['volume'].iloc[-1]
        vol_r5 = today_vol / vol_ma5 if vol_ma5 > 0 else 0
        vol_r20 = today_vol / vol_ma20 if vol_ma20 > 0 else 0
        return vol_r5, vol_r20
    except Exception as e:
        print('vol_ratio error:', e)
        return None, None


def get_kline_info(code):
    """获取K线关键信息"""
    try:
        client = Quotes.factory(market='std')
        market = 0 if code[0] in '03' else 1
        bars = client.bars(symbol=code, frequency=9, market=market, offset=40)
        client.close()
        if bars is None or len(bars) < 20:
            return {}
        close = bars['close']
        high20 = bars['high'].iloc[-20:].max()
        low20 = bars['low'].iloc[-20:].min()
        vol_ma5 = bars['volume'].iloc[-5:].mean()
        vol_now = bars['volume'].iloc[-1]
        vola = (high20 - low20) / low20 * 100 if low20 > 0 else 0

        # 均线
        ma5 = close.iloc[-5:].mean()
        ma10 = close.iloc[-10:].mean() if len(close) >= 10 else ma5
        ma20 = close.iloc[-20:].mean() if len(close) >= 20 else ma10
        current_price = close.iloc[-1]

        # MACD
        ema12_s = close.ewm(span=12, adjust=False).mean()
        ema26_s = close.ewm(span=26, adjust=False).mean()
        dif_series = ema12_s - ema26_s
        dea_series = dif_series.ewm(span=9, adjust=False).mean()
        dif_val = float(dif_series.iloc[-1])
        dea_val = float(dea_series.iloc[-1])
        macd_hist = 2 * (dif_val - dea_val)

        # 形态判断
        pattern = []
        if current_price > ma5 > ma10 > ma20:
            pattern.append('多头排列')
        if current_price > high20 * 0.97:
            pattern.append('near_high')
        if vola < 10:
            pattern.append('低波动')
        if vol_now < vol_ma5 * 0.7:
            pattern.append('缩量')

        # 压力支撑
        pressure = high20
        support = low20
        dist_to_pressure = (pressure - current_price) / current_price * 100 if pressure > 0 else 0

        return {
            'price': current_price,
            'ma5': ma5, 'ma10': ma10, 'ma20': ma20,
            'high20': high20, 'low20': low20,
            'vola': vola,
            'vol_r': vol_now / vol_ma5 if vol_ma5 > 0 else 1,
            'pattern': pattern,
            'pressure': pressure,
            'support': support,
            'dist_to_pressure': dist_to_pressure,
            'dif': dif_val,
            'dea': dea_val,
            'macd_hist': macd_hist,
        }
    except Exception as e:
        print('kline error:', e)
        return {}


def analyze_stock(code, auction_data, vol_ratio, kline_info):
    """综合分析单只股票"""
    info = WATCH.get(code, {})
    auction = auction_data.get(code, {})
    prev = auction.get('prev_close', 0)
    open_p = auction.get('open', 0)
    current_p = auction.get('current', 0)

    if not prev or prev <= 0:
        return None

    open_pct = (open_p - prev) / prev * 100 if open_p > 0 else 0
    current_pct = (current_p - prev) / prev * 100 if current_p > 0 else 0

    # === 股票知识综合评分 ===
    score = 0
    signals = []
    risks = []

    # 1. 竞价涨幅评分 (权重30%)
    if abs(open_pct) < 20:  # 合法的竞价涨幅
        if 5 <= open_pct <= 10:
            score += 30
            signals.append(f'竞价高开{open_pct:.1f}%（主力进攻信号）')
        elif 2 <= open_pct < 5:
            score += 20
            signals.append(f'竞价温和高开{open_pct:.1f}%')
        elif 10 <= open_pct < 20:
            score += 25
            signals.append(f'竞价涨停开{open_pct:.1f}%（强势）')
        elif -2 <= open_pct < 2:
            score += 10
        elif open_pct > 20:
            signals.append('竞价涨幅异常，谨慎')
            risks.append('竞价涨幅过大')

    # 2. 竞价量能评分 (权重20%)
    vr5, vr20 = vol_ratio if vol_ratio else (None, None)
    if vr5 is not None:
        if vr5 >= 3.0:
            score += 20
            signals.append(f'极度放量（量比{vr5:.1f}x，积极换手）')
        elif vr5 >= 1.5:
            score += 15
            signals.append(f'放量（量比{vr5:.1f}x）')
        elif vr5 >= 0.8:
            score += 10
        elif vr5 < 0.5:
            signals.append(f'缩量（量比{vr5:.1f}x，筹码稳定）')

    # 3. K线形态评分 (权重30%)
    if kline_info:
        pattern = kline_info.get('pattern', [])
        if '多头排列' in pattern:
            score += 15
            signals.append('均线多头排列（上升趋势）')
        if 'near_high' in pattern:
            score += 10
            signals.append('股价接近20日高点（突破临界）')
        if '低波动' in pattern:
            score += 5
            signals.append('低波动整理（酝酿突破）')

        # MACD
        dif = kline_info.get('dif', 0)
        dea = kline_info.get('dea', 0)
        hist = kline_info.get('macd_hist', 0)
        if dif > 0 and dif > dea:
            score += 10
            signals.append('MACD金叉（动量向上）')
        if hist > 0:
            signals.append('MACD红柱（上涨动能充足）')

    # 4. 距离压力位 (权重20%)
    dist = kline_info.get('dist_to_pressure', 999) if kline_info else 999
    if dist < 1.0:
        score += 20
        signals.append(f'距离压力位仅{dist:.1f}%（一触即发）')
    elif dist < 3.0:
        score += 15
        signals.append(f'距离压力位{dist:.1f}%（即将突破）')
    elif dist < 5.0:
        score += 10
    elif dist >= 10:
        risks.append(f'距离压力位{dist:.1f}%（较远）')

    # === 风险评估 ===
    if current_pct < -5:
        risks.append(f'当前跌幅{current_pct:.1f}%（走弱）')
    if kline_info and kline_info.get('vola', 0) > 30:
        risks.append('波动率过大（风险高）')

    # === 综合评级 ===
    if score >= 75:
        rating = '⭐⭐⭐⭐⭐ 强烈关注'
    elif score >= 55:
        rating = '⭐⭐⭐⭐ 重点关注'
    elif score >= 35:
        rating = '⭐⭐⭐ 可观察'
    else:
        rating = '⭐⭐ 观望'

    return {
        'code': code,
        'name': info.get('name', code),
        'reason': info.get('reason', ''),
        'level': info.get('level', ''),
        'prev': prev,
        'open': open_p,
        'open_pct': open_pct,
        'current': current_p,
        'current_pct': current_pct,
        'score': score,
        'rating': rating,
        'signals': signals,
        'risks': risks,
        'kline': kline_info,
        'vol_ratio_5': vr5,
    }


def build_feishu_message(results):
    """构建飞书消息卡片"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    lines = []

    # Header
    lines.append(f"📊 **集合竞价扫描报告**")
    lines.append(f"🕐 扫描时间：{now}")
    lines.append(f"📈 监控数量：{len(WATCH)} 只")
    lines.append("")

    # Score sorted
    valid = [r for r in results if r is not None]
    valid.sort(key=lambda x: x['score'], reverse=True)

    # Top picks
    top = valid[:5]
    if top:
        lines.append("🔥 **强势候选 TOP 5**")
        lines.append("")
        for r in top:
            level_emoji = '🔴' if r['score'] >= 75 else '🟡' if r['score'] >= 55 else '⚪'
            lines.append(f"{level_emoji} **{r['name']}({r['code']})** {r['rating']}")
            lines.append(f"   竞价: {r['open']:.2f}({r['open_pct']:+.2f}%) | 现价: {r['current']:.2f}({r['current_pct']:+.2f}%)")
            lines.append(f"   📍 {r['reason']}")
            if r['vol_ratio_5']:
                lines.append(f"   📊 量比: {r['vol_ratio_5']:.1f}x | 评分: {r['score']}分")
            if r['signals']:
                lines.append(f"   信号: {' | '.join(r['signals'][:2])}")
            if r['risks']:
                lines.append(f"   ⚠️ 风险: {' '.join(r['risks'][:1])}")
            lines.append("")

    # All stocks summary
    lines.append("📋 **全市场扫描**")
    lines.append("")
    header = "代码 | 名称 | 竞价涨幅 | 现价涨幅 | 评分 | 信号"
    lines.append(header)
    lines.append("---|---:|---:|---:|---:|---")
    for r in valid:
        sig = r['signals'][0][:15] + '...' if r['signals'] and len(r['signals'][0]) > 15 else (r['signals'][0] if r['signals'] else '-')
        risk_str = '⚠️' + r['risks'][0][:10] if r['risks'] else ''
        lines.append(f"{r['code']} | {r['name']} | {r['open_pct']:+.1f}% | {r['current_pct']:+.1f}% | {r['score']} | {sig}{risk_str}")

    lines.append("")
    lines.append("---")
    lines.append("💡 竞价涨幅5-10% + 放量 = 主力进攻信号")
    lines.append("💡 集合竞价是关键，9:15-9:25 重点关注!")

    return '\n'.join(lines)


def push_feishu(message):
    """通过飞书机器人API推送消息"""
    try:
        # Get tenant access token
        token_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        token_resp = requests.post(token_url, json={
            "app_id": FEISHU_APP_ID,
            "app_secret": FEISHU_APP_SECRET,
        }, timeout=10)
        token_data = token_resp.json()
        tenant_token = token_data.get('tenant_access_token', '')
        if not tenant_token:
            print('Failed to get tenant token:', token_data)
            return

        # Send message
        send_url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
        headers = {
            "Authorization": f"Bearer {tenant_token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        payload = {
            "receive_id": FEISHU_USER_ID,
            "msg_type": "text",
            "content": json.dumps({"text": message})
        }
        send_resp = requests.post(send_url, headers=headers, json=payload, timeout=10)
        print('Feishu push result:', send_resp.status_code, send_resp.text[:200])
    except Exception as e:
        print('Feishu push error:', e)


def scan_and_report():
    """主扫描流程"""
    print('=' * 60)
    print(f'集合竞价扫描开始 {datetime.now().strftime("%H:%M:%S")}')
    print('=' * 60)

    # 1. 获取集合竞价数据
    print('获取集合竞价数据...')
    auction_data = get_auction_data()
    print(f'获取到 {len(auction_data)} 只股票竞价数据')

    # 2. 批量获取量比
    print('获取量比数据...')
    vol_ratios = {}
    for code in WATCH:
        vr5, vr20 = get_vol_ratio(code)
        vol_ratios[code] = (vr5, vr20)
        print(f'  {code}: 量比5日={vr5:.2f}x' if vr5 else f'  {code}: 无数据')
        time.sleep(0.1)

    # 3. 批量获取K线信息
    print('获取K线信息...')
    kline_infos = {}
    for code in WATCH:
        ki = get_kline_info(code)
        kline_infos[code] = ki
        time.sleep(0.1)

    # 4. 综合分析
    print('综合分析中...')
    results = []
    for code in WATCH:
        r = analyze_stock(code, auction_data, vol_ratios.get(code), kline_infos.get(code))
        if r:
            results.append(r)
            print(f"  {r['name']}: 评分={r['score']} 竞价={r['open_pct']:+.1f}%")

    # 5. 构建并推送消息
    if results:
        msg = build_feishu_message(results)
        print('\n飞书推送内容:\n')
        print(msg[:500])
        print('...')
        push_feishu(msg)
    else:
        print('无有效数据，跳过推送')

    return results


if __name__ == '__main__':
    scan_and_report()
