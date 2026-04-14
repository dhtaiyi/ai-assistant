#!/usr/bin/env python3
"""
A股超短监控系统 v1.0
===================
基于：威科夫交易法 + 炒股养家心法 + 龙之精髓 + 情绪周期

功能：
1. 情绪周期判断（上升/混沌/退潮）
2. 威科夫信号检测（吸筹/派发/Spring/Upthrust）
3. 炒股养家信号（缩量/放量/盘口口诀）
4. 妖股预警（量比/振幅/换手率）
5. 龙头跟踪（空间板/连板梯队）
"""

import requests
import json
import time
import os
from datetime import datetime, time as dtime
from collections import defaultdict

# ========== 配置 ==========
os.environ['NO_PROXY'] = '*'
os.environ['no_proxy'] = '*'

# 腾讯实时行情
TENCENT_URL = "http://qt.gtimg.cn/q={codes}"
# 新浪市场统计
SINA_STATS_URL = "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeDataSimple"
# MX API（东方财富）
MX_APIKEY = "mkt_vu-pj52--GcXTwXkYR5reA8DX0Vq3E2y_fyygU2aB4g"
MX_URL = "https://mkapi2.dfcfs.com/finskillshub/api/claw/query"

# 飞书通知（可选）
FEISHU_WEBHOOK = os.environ.get("FEISHU_WEBHOOK", "")

# ========== 工具函数 ==========
def log(msg):
    """打印带时间戳的日志"""
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] {msg}")

def feishu_notify(text):
    """发送飞书通知"""
    if not FEISHU_WEBHOOK:
        return
    try:
        requests.post(FEISHU_WEBHOOK, json={"msg_type": "text", "content": {"text": text}}, timeout=5)
    except:
        pass

# ========== 数据获取 ==========
def get_tencent_realtime(codes):
    """获取腾讯实时行情"""
    if not codes:
        return []
    codes_str = ",".join(codes) if isinstance(codes, list) else codes
    try:
        r = requests.get(TENCENT_URL.format(codes=codes_str), timeout=10)
        r.encoding = 'gbk'
        stocks = []
        for line in r.text.split(';'):
            if 'v_' not in line:
                continue
            data = line.split('"')[1] if '"' in line else ''
            fields = data.split('~')
            if len(fields) < 32:
                continue
            try:
                stocks.append({
                    'code': fields[2],
                    'name': fields[1],
                    'price': float(fields[3]) if fields[3] else 0,
                    'close': float(fields[4]) if fields[4] else 0,
                    'vol': float(fields[5]) if fields[5] else 0,  # 成交量（手）
                    'amount': float(fields[6]) if fields[6] else 0,  # 成交额（元）
                    'ask1': float(fields[9]) if fields[9] else 0,
                    'bid1': float(fields[19]) if fields[19] else 0,
                    'high': float(fields[33]) if fields[33] else 0,
                    'low': fields[34] if len(fields) > 34 else '',
                    'change': float(fields[31]) if fields[31] else 0,
                    'pct': float(fields[32]) if fields[32] else 0,
                })
            except:
                continue
        return stocks
    except Exception as e:
        log(f"腾讯API错误: {e}")
        return []

def get_mx_query(tool_query):
    """MX API查询"""
    try:
        r = requests.post(MX_URL,
            headers={"Content-Type": "application/json", "apikey": MX_APIKEY},
            json={"toolQuery": tool_query},
            timeout=15)
        return r.json()
    except:
        return {}

def get_mx_table(result):
    """从MX结果提取表格"""
    try:
        tables = result.get('data', {}).get('data', {}).get('searchDataResultDTO', {}).get('dataTableDTOList', [])
        return tables
    except:
        return []

def get_sina_market_stats():
    """获取全市场涨跌统计"""
    try:
        params = {'page': 1, 'num': 5000, 'sort': 'changepercent', 'asc': 0, 'node': 'hs_a'}
        r = requests.get(SINA_STATS_URL, params=params, headers={'Referer': 'https://finance.sina.com.cn'}, timeout=15)
        stocks = r.json() if r.text else []
        if not stocks:
            return None
        
        up = sum(1 for s in stocks if float(s.get('changepercent', 0)) > 0)
        down = sum(1 for s in stocks if float(s.get('changepercent', 0)) < 0)
        flat = len(stocks) - up - down
        zt = sum(1 for s in stocks if float(s.get('changepercent', 0)) >= 9.9)
        zd = sum(1 for s in stocks if float(s.get('changepercent', 0)) <= -9.9)
        
        return {
            'total': len(stocks),
            'up': up,
            'down': down,
            'flat': flat,
            'zt': zt,
            'zd': zd,
        }
    except:
        return None

def get_mx_market_stats():
    """用MX API获取市场统计数据"""
    try:
        result = get_mx_query("上涨家数")
        tables = get_mx_table(result)
        stats = {}
        for table in tables:
            rows = table.get('tr', [])
            for row in rows:
                cells = row.get('td', [])
                if len(cells) >= 2:
                    name = cells[0].get('text', '')
                    value = cells[1].get('text', '')
                    if '涨停' in name:
                        stats['zt'] = int(value) if value.isdigit() else 0
                    elif '跌停' in name:
                        stats['zd'] = int(value) if value.isdigit() else 0
                    elif '上涨' in name:
                        stats['up'] = int(value) if value.isdigit() else 0
                    elif '下跌' in name:
                        stats['down'] = int(value) if value.isdigit() else 0
        return stats if stats else None
    except:
        return None

def get_limit_up_list():
    """获取涨停股列表"""
    try:
        params = {'page': 1, 'num': 100, 'sort': 'changepercent', 'asc': 0, 'node': 'hs_a'}
        r = requests.get(SINA_STATS_URL, params=params, headers={'Referer': 'https://finance.sina.com.cn'}, timeout=15)
        stocks = r.json() if r.text else []
        # 过滤涨停股
        zt_stocks = [s for s in stocks if float(s.get('changepercent', 0)) >= 9.9]
        return zt_stocks
    except:
        return []

# ========== 模块1：情绪周期判断 ==========
def detect_market_sentiment(stats):
    """
    基于龙之精髓 + 情绪周期理论判断市场情绪
    
    上升期：涨停 > 50家，赚钱效应强
    混沌期：涨停 20-50家，轮动快
    退潮期：涨停 < 20家，亏钱效应
    """
    if not stats:
        return None, None
    
    zt = stats.get('zt', 0)
    zd = stats.get('zd', 0)
    up = stats.get('up', 0)
    down = stats.get('down', 0)
    total = stats.get('total', up + down)
    
    # 涨跌比
    up_ratio = up / total if total > 0 else 0
    
    # 判断周期
    if zt >= 50:
        cycle = "🟢 上升期"
        phase = "赚钱效应强，激进操作"
        risk_level = 3  # 1-10，10最高风险
    elif zt >= 30:
        cycle = "🟡 上升期(初期)"
        phase = "情绪升温，可以操作"
        risk_level = 4
    elif zt >= 20:
        cycle = "🟡 混沌期"
        phase = "轮动加快，轻仓试错"
        risk_level = 5
    elif zt >= 10:
        cycle = "🟠 退潮期(初期)"
        phase = "控仓休息，不追高位"
        risk_level = 7
    else:
        cycle = "🔴 退潮期"
        phase = "空仓休息，等待机会"
        risk_level = 9
    
    # 补充：跌停家数过多也是退潮信号
    if zd >= 30:
        cycle = "🔴 退潮期(恐慌)"
        phase = "市场恐慌，保命为主"
        risk_level = 10
    
    # 补充：涨跌家数比
    if up_ratio > 0.7:
        cycle += " | 普涨"
    elif up_ratio < 0.3:
        cycle += " | 普跌"
    
    return cycle, phase, risk_level, zt, zd, up, down

# ========== 模块2：妖股预警 ==========
def detect_yanggu_stocks(stocks):
    """
    基于妖股预警系统检测异动股
    
    预警指标（基于历史妖股研究）：
    - 妖股TOP特征：特力A(+993%)/暴风科技(+1950%)/东方通信(+1200%)
    - 选股公式：人气>强度>题材>盘子 | 盘子10-50亿 | 启动价<10元
    - 预警评分 = 成交量30% + 涨幅25% + 换手率20% + 价格位置15% + PE10%
    - 启动信号：量比>1.5x + 振幅扩大 + 股价突破关键位
    """
    warnings = []
    
    for s in stocks[:500]:  # 扫描前500只
        try:
            pct = float(s.get('changepercent', 0))
            vol = float(s.get('volume', s.get('vol', 0)))
            amount = float(s.get('amount', 0))
            price = float(s.get('trade', s.get('price', 0)))
            
            # 跳过ST和新股
            name = s.get('name', '')
            if 'ST' in name or '*' in name:
                continue
            
            # 妖股特征检测
            score = 0
            reasons = []  # 预警原因列表
            
            # 1. 涨幅因子（25%权重）
            # 历史妖股特征：启动时涨幅通常>7%
            if pct >= 9.5:
                score += 25
                reasons.append(f"涨停({pct:.1f}%)")
            elif pct >= 7:
                score += 20
                reasons.append(f"高涨幅({pct:.1f}%)")
            elif pct >= 5:
                score += 15
                reasons.append(f"启动迹象({pct:.1f}%)")
            
            # 2. 成交额因子（30%权重）
            # 妖股特征：成交额通常>5亿（大资金参与）
            if amount >= 10e8:  # ≥10亿
                score += 30
                reasons.append(f"巨量成交({amount/1e8:.1f}亿)")
            elif amount >= 5e8:  # ≥5亿
                score += 20
                reasons.append(f"放量({amount/1e8:.1f}亿)")
            elif amount >= 1e8:  # ≥1亿
                score += 10
                reasons.append(f"量能放大({amount/1e8:.1f}亿)")
            
            # 3. 价格位置因子（15%权重）
            # 妖股特征：启动价通常<10元，低价股更容易成妖
            if 3 <= price <= 10:
                score += 15
                reasons.append(f"低价妖股潜质({price:.2f}元)")
            elif 10 < price <= 20:
                score += 10
                reasons.append(f"中价股({price:.2f}元)")
            elif price < 3:
                score += 5
                reasons.append(f"超低价(可能有退市风险)")
            
            # 4. 振幅因子（20%权重）
            # 妖股特征：高波动，振幅通常>7%
            # 用当日高低点估算振幅
            high = float(s.get('high', price * 1.1))
            low = float(s.get('low', price * 0.9))
            amplitude = (high - low) / price * 100 if price > 0 else 0
            
            if amplitude >= 15:
                score += 20
                reasons.append(f"剧烈波动(振幅{amplitude:.1f}%)")
            elif amplitude >= 10:
                score += 15
                reasons.append(f"高波动(振幅{amplitude:.1f}%)")
            elif amplitude >= 7:
                score += 10
                reasons.append(f"活跃(振幅{amplitude:.1f}%)")
            
            # 5. 换手率因子（通过成交额/市值估算，10%权重）
            # 简化：成交额>1亿且价格适中
            if amount >= 1e8 and 5 <= price <= 30:
                score += 10
                reasons.append("高换手率嫌疑")
            
            # 综合判断
            if score >= 60:
                warnings.append({
                    'code': s.get('symbol', '').replace('sh', '').replace('sz', ''),
                    'name': name,
                    'pct': pct,
                    'price': price,
                    'amount': amount,
                    'score': score,
                    'reasons': reasons,  # 预警原因列表
                    'amplitude': amplitude,
                })
        except:
            continue
    
    # 按评分排序
    warnings.sort(key=lambda x: x['score'], reverse=True)
    return warnings[:10]

# ========== 模块3：威科夫信号检测 ==========
def detect_wyckoff_signals(stocks):
    """
    基于威科夫交易法检测信号
    
    Spring（弹簧效应）：假突破支撑后反弹
    Upthrust（顶击）：假突破阻力后回落
    放量不涨：主力出货信号
    缩量不跌：主力吸筹信号
    """
    signals = {
        'spring': [],      # 弹簧效应（买入信号）
        'upthrust': [],   # 顶击（卖出信号）
        'distribution': [], # 派发信号
        'accumulation': [], # 吸筹信号
    }
    
    for s in stocks[:500]:
        try:
            pct = float(s.get('changepercent', 0))
            price = float(s.get('trade', s.get('price', 0)))
            close = float(s.get('settlement', s.get('close', 0)))
            vol = float(s.get('volume', s.get('vol', 0)))
            amount = float(s.get('amount', 0))
            high = float(s.get('high', 0))
            low = float(s.get('low', 0))
            name = s.get('name', '')
            
            if 'ST' in name or price <= 0:
                continue
            
            # 计算振幅
            amplitude = (high - low) / close * 100 if close > 0 else 0
            
            # Spring信号：价格接近低点但出现反弹
            # 简化：收盘价在中上部，但当天创了日内新低后回升
            if low < close * 0.98 and pct > 0 and pct < 3:
                signals['spring'].append({
                    'code': s.get('symbol', '').replace('sh', '').replace('sz', ''),
                    'name': name,
                    'price': price,
                    'pct': pct,
                    'signal': 'Spring（假破位反弹）'
                })
            
            # Upthrust信号：价格接近高点但无法突破
            if high > close * 1.02 and pct < 0 and pct > -3:
                signals['upthrust'].append({
                    'code': s.get('symbol', '').replace('sh', '').replace('sz', ''),
                    'name': name,
                    'price': price,
                    'pct': pct,
                    'signal': 'Upthrust（假突破滞涨）'
                })
            
            # 派发信号：高位 + 放量不涨（高位震荡）
            if pct < 2 and pct > -2 and amount > 5e7 and price > 15 and high > price * 1.05:
                signals['distribution'].append({
                    'code': s.get('symbol', '').replace('sh', '').replace('sz', ''),
                    'name': name,
                    'price': price,
                    'pct': pct,
                    'amount': amount,
                    'signal': '高位放量滞涨（疑似派发）'
                })
            
            # 吸筹信号：低位 + 缩量不跌
            if pct > -3 and pct < 3 and amount < 2e7 and price < 15 and vol > 1000:
                signals['accumulation'].append({
                    'code': s.get('symbol', '').replace('sh', '').replace('sz', ''),
                    'name': name,
                    'price': price,
                    'pct': pct,
                    'signal': '低位缩量横盘（疑似吸筹）'
                })
        except:
            continue
    
    return signals

# ========== 模块4：龙头跟踪 ==========
def track_longtou(zt_stocks):
    """
    跟踪龙头股梯队
    基于龙之精髓：空间板 > 二板 > 首板 > 跟风
    """
    if not zt_stocks:
        return []
    
    # 简化：取涨幅前10的涨停股
    zt_stocks.sort(key=lambda x: float(x.get('changepercent', 0)), reverse=True)
    
    longtou = []
    for i, s in enumerate(zt_stocks[:10]):
        pct = float(s.get('changepercent', 0))
        name = s.get('name', '')
        symbol = s.get('symbol', '').replace('sh', 'sh').replace('sz', 'sz')
        price = s.get('trade', 0)
        
        if pct < 9.9:  # 排除非涨停
            continue
        
        tier = ""
        if i == 0:
            tier = "🐉 空间板"
        elif i < 3:
            tier = "🔺 二板梯队"
        elif i < 6:
            tier = "📈 三板梯队"
        else:
            tier = "⚡ 首板跟风"
        
        longtou.append({
            'tier': tier,
            'rank': i + 1,
            'name': name,
            'code': s.get('symbol', ''),
            'pct': pct,
            'price': price,
        })
    
    return longtou

# ========== 模块5：炒股养家信号 ==========
def detect_yangjia_signals(stats):
    """
    基于炒股养家心法检测信号
    
    核心口诀：
    - 早上大跌要加仓，早上大涨要减仓
    - 放量涨定回落，放量跌定反弹
    - 缩量跌底部显，放量不涨头部现
    """
    signals = []
    
    if not stats:
        return signals
    
    zt = stats.get('zt', 0)
    zd = stats.get('zd', 0)
    up = stats.get('up', 0)
    down = stats.get('down', 0)
    
    # 早上大跌信号（跌停家数过多）
    if zd >= 30:
        signals.append({
            'type': '⚠️ 恐慌信号',
            'signal': f'跌停{zd}家，市场恐慌',
            'action': '减仓休息，不抄底',
            'source': '炒股养家：高位放大量，股价近云端'
        })
    
    # 普涨信号
    if up > down * 3:
        signals.append({
            'type': '✅ 普涨信号',
            'signal': f'上涨{up}家 vs 下跌{down}家',
            'action': '顺势而为，跟随热点',
            'source': '炒股养家：得散户心者得天下'
        })
    
    # 涨停家数判断
    if zt >= 50:
        signals.append({
            'type': '🔥 赚钱效应',
            'signal': f'涨停{zt}家，情绪高涨',
            'action': '积极操作，追逐龙头',
            'source': '龙之精髓：上升期'
        })
    elif zt < 10:
        signals.append({
            'type': '❄️ 冰点信号',
            'signal': f'涨停{zt}家，情绪冰点',
            'action': '空仓休息，等待机会',
            'source': '炒股养家：永不止损，永不止盈'
        })
    
    return signals

# ========== 主监控函数 ==========
def run_monitor():
    """运行完整监控"""
    print("\n" + "=" * 60)
    print("  🌸 A股超短监控系统 v1.0")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 获取市场数据
    log("📡 获取市场数据...")
    stats = get_mx_market_stats() or get_sina_market_stats()
    zt_list = get_limit_up_list()
    
    if not stats:
        log("❌ 无法获取市场数据")
        return
    
    # 2. 情绪周期判断
    log("🔍 分析情绪周期...")
    cycle_info = detect_market_sentiment(stats)
    if cycle_info[0]:
        print(f"\n📈 【市场情绪】")
        print(f"  {cycle_info[0]}")
        print(f"  阶段：{cycle_info[1]}")
        print(f"  风险等级：{cycle_info[2]}/10")
        print(f"  涨停：{cycle_info[3]} | 跌停：{cycle_info[4]}")
        print(f"  上涨：{cycle_info[5]} | 下跌：{cycle_info[6]}")
        
        # 发飞书通知（只发高风险）
        if cycle_info[2] >= 7:
            feishu_notify(f"⚠️ 风险提示\n{cycle_info[0]}\n{cycle_info[1]}\n涨停{cycle_info[3]}家 跌停{cycle_info[4]}家")
    
    # 3. 涨停股分析
    if zt_list:
        log(f"📊 分析涨停股({len(zt_list)}只)...")
        
        # 龙头跟踪
        longtou = track_longtou(zt_list)
        if longtou:
            print(f"\n🐉 【龙头梯队】")
            for lt in longtou[:5]:
                print(f"  {lt['tier']} {lt['name']}({lt['code']}) {lt['pct']:.1f}%")
        
        # 妖股预警
        warnings = detect_yanggu_stocks(zt_list)
        if warnings:
            print(f"\n⚠️ 【妖股预警】(评分≥60分)")
            for w in warnings[:5]:
                reasons_str = " | ".join(w['reasons'])
                print(f"\n  📌 {w['name']}({w['code']}) {w['pct']:.1f}%")
                print(f"     评分: {w['score']}/100 | {w['price']:.2f}元 | 成交{abs(w['amount'])/1e8:.1f}亿")
                print(f"     🚨 预警原因: {reasons_str}")
    
    # 4. 威科夫信号
    log("🔎 检测威科夫信号...")
    # 获取更多股票数据用于威科夫分析
    tencent_codes = [s.get('symbol', '') for s in zt_list[:100]]
    if tencent_codes:
        tencent_stocks = get_tencent_realtime(tencent_codes)
        wyckoff = detect_wyckoff_signals(tencent_stocks)
        
        if wyckoff['spring']:
            print(f"\n🟢 【Spring信号】({len(wyckoff['spring'])}只)")
            for s in wyckoff['spring'][:3]:
                print(f"  {s['name']} {s['price']} | {s['signal']}")
        
        if wyckoff['distribution']:
            print(f"\n🔴 【派发信号】({len(wyckoff['distribution'])}只)")
            for s in wyckoff['distribution'][:3]:
                print(f"  {s['name']} {s['pct']:.1f}% | {s['signal']}")
    
    # 5. 炒股养家信号
    signals = detect_yangjia_signals(stats)
    if signals:
        print(f"\n💡 【炒股养家信号】")
        for sig in signals:
            print(f"  {sig['type']}：{sig['signal']}")
            print(f"    → {sig['action']}")
    
    print("\n" + "=" * 60)

# ========== 快速检查（用于频繁轮询）==========
def quick_check():
    """快速检查，只输出核心数据"""
    stats = get_mx_market_stats() or get_sina_market_stats()
    if not stats:
        return "❌ 数据获取失败"
    
    zt = stats.get('zt', 0)
    zd = stats.get('zd', 0)
    
    cycle = detect_market_sentiment(stats)
    cycle_name = cycle[0] if cycle[0] else "未知"
    risk = cycle[2] if len(cycle) > 2 else 0
    
    return f"{cycle_name} | 涨停{zt} | 跌停{zd} | 风险{risk}/10"

# ========== 入口 ==========
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        # 快速模式：单行输出
        result = quick_check()
        print(result)
    else:
        # 完整模式
        run_monitor()
