#!/usr/bin/env python3
"""
每日市场情绪判断 V2.1 - 修复版
=====================================
改进点：
1. 增加市场开盘时间检查（9:30前数据不可靠）
2. 增加数据时效性校验（ticktime一致性）
3. 增加容错机制（单个数据源失败不影响整体）
4. 优化退潮期判断逻辑
"""
import requests
import json
import re
import os
from datetime import datetime, time

LOG_FILE = "/tmp/market_sentiment.log"

def get_realtime_data():
    """获取实时数据，带容错机制"""
    url = 'https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeDataSimple'
    
    # 获取涨幅榜（按涨幅排序）
    try:
        r1 = requests.get(url, params={
            'page': 1, 'num': 200, 
            'sort': 'changepercent', 'asc': 0, 
            'node': 'hs_a'
        }, timeout=10)
        by_pct = r1.json()
    except Exception as e:
        print(f"⚠️ 涨幅榜获取失败: {e}")
        by_pct = []

    # 获取成交额榜（按成交额排序）
    try:
        r2 = requests.get(url, params={
            'page': 1, 'num': 100,
            'sort': 'amount', 'asc': 0,
            'node': 'hs_a'
        }, timeout=10)
        by_amt = r2.json()
    except Exception as e:
        print(f"⚠️ 成交额榜获取失败: {e}")
        by_amt = []

    # 获取指数（注意：批量接口和完整接口格式不同！）
    # 批量接口(s_sh000001): len~=12, parts[3]=价格, parts[5]=涨跌幅
    # 完整接口(sh000001): len~=88, parts[3]=价格, parts[32]=涨跌幅
    indices = {}
    try:
        r_idx = requests.get('http://qt.gtimg.cn/q=s_sh000001,s_sz399001,s_sz399006', timeout=5)
        for line in r_idx.text.strip().split('\n'):
            if '"' not in line:
                continue
            m = re.search(r'="([^"]+)"', line)
            if not m:
                continue
            parts = m.group(1).split('~')
            try:
                if len(parts) > 5:
                    name = parts[1]
                    if not name:
                        continue
                    price = float(parts[3]) if parts[3] else 0
                    # 批量接口：len<20时parts[5]=涨跌幅；完整接口：len>30时parts[32]=涨跌幅
                    if len(parts) < 20:
                        pct = float(parts[5]) if len(parts) > 5 and parts[5] else 0
                    else:
                        pct = float(parts[32]) if len(parts) > 32 and parts[32] else 0
                    indices[name] = {'price': price, 'pct': pct}
            except (ValueError, IndexError):
                continue
    except Exception as e:
        print(f"⚠️ 指数获取失败: {e}")

    return by_pct, by_amt, indices


def check_market_status(by_pct):
    """
    判断市场状态：
    1. 午间休市（11:30-13:00）：优先判断
    2. 集合竞价（9:15-9:25）：ticktime全相同
    3. 盘中（9:30-11:30/13:00-15:00）：ticktime正常推进
    4. 收盘后：价格冻结
    """
    now = datetime.now()
    current_time = now.time()
    
    # 优先判断午间休市
    if time(11, 30) <= current_time < time(13, 0):
        return "lunch", "午间休市"
    
    # 检查是否在交易时段
    morning_open = time(9, 30)
    morning_close = time(11, 30)
    afternoon_open = time(13, 0)
    afternoon_close = time(15, 0)
    
    is_trading = (morning_open <= current_time <= morning_close) or \
                 (afternoon_open <= current_time <= afternoon_close)
    
    # 检查数据时效性（仅在疑似开盘前/收盘后时检查）
    if by_pct and not is_trading:
        try:
            ticktimes = set(s.get('ticktime', '') for s in by_pct[:10])
            if len(ticktimes) == 1 and list(ticktimes)[0]:
                # ticktime都一样，可能是开盘前或刚收盘
                sample_tick = list(ticktimes)[0] if ticktimes else ""
                if sample_tick:
                    tick_hour = int(sample_tick.split(":")[0]) if ":" in sample_tick else 0
                    if tick_hour >= 15 or tick_hour < 9:
                        return "closed", "已收盘"
        except:
            pass
    
    if not is_trading:
        if time(9, 15) <= current_time <= time(9, 25):
            return "auction", "集合竞价中"
        elif time(9, 0) <= current_time < time(9, 30):
            return "pre_market", "等待开盘"
        else:
            return "closed", "非交易时间"
    
    return "trading", "交易中"


def is_clean_stock(s):
    """过滤ST、退市、新股等"""
    name = s.get('name', '')
    if any(x in name for x in ['ST', '*ST', 'N ', '退']):
        return False
    code = s.get('symbol', '')
    if code.startswith('bj'):
        return False
    return True


def get_sentiment():
    log = []
    by_pct, by_amt, indices = get_realtime_data()
    
    # 检查市场状态
    status, status_desc = check_market_status(by_pct)
    
    sh_pct = indices.get('上证指数', {}).get('pct', 0)
    sz_pct = indices.get('深证成指', {}).get('pct', 0)
    cy_pct = indices.get('创业板指', {}).get('pct', 0)
    
    log.append(f"市场状态: {status_desc} ({status})")
    
    # 非交易时段，但午休时仍显示上午数据分析
    if status in ["pre_market", "closed", "auction"]:
        log.append(f"\n📊 当前指数: 上证 {indices.get('上证指数',{}).get('price','?')} ({sh_pct:+.2f}%)")
        log.append(f"  深证 {indices.get('深证成指',{}).get('price','?')} ({sz_pct:+.2f}%)")
        log.append(f"  创业板 {indices.get('创业板指',{}).get('price','?')} ({cy_pct:+.2f}%)")
        log.append(f"\n{'='*50}")
        log.append(f"⏰ 等待市场开盘/休市")
        log.append(f"{'='*50}")
        return "\n".join(log), None
    
    if status == "lunch":
        # 午休时仍执行分析（用上午数据）
        pass  # 继续执行盘中分析

    # ===== 盘中分析 =====
    limit_up = [s for s in by_pct if float(s.get('changepercent', 0)) >= 9.5 and is_clean_stock(s)]
    big_up = [s for s in by_pct if 5 <= float(s.get('changepercent', 0)) < 9.5 and is_clean_stock(s)]
    lu = len(limit_up)
    
    total_amount = sum(float(s.get('amount', 0)) for s in by_amt[:50]) / 1e8 if by_amt else 0

    log.append(f"\n📊 市场概况")
    log.append(f"  涨停: {lu} | 大涨5-9%: {len(big_up)}")
    for name, info in indices.items():
        log.append(f"  {name}: {info['price']} {info['pct']:+.2f}%")

    # 成交额TOP5分析
    log.append(f"\n💰 成交额TOP5:")
    top5_non_lu = []
    top5_amt = []
    for s in (by_amt[:10] if by_amt else []):
        amount_yi = float(s.get('amount', 0)) / 1e8
        pct = float(s.get('changepercent', 0))
        tag = "🔴" if pct >= 9.5 else "🔵"
        log.append(f"  {tag} {s['name']} {pct:+.1f}% 成交{amount_yi:.0f}亿")
        top5_amt.append({'name': s['name'], 'pct': pct, 'amount': amount_yi})
        if pct < 9.5 and pct >= 3:
            top5_non_lu.append(s)

    # ========== 核心判断 ==========
    # 机构主导信号：成交额TOP5中至少2只不是涨停(涨幅2%+)，且总成交额大
    is_institutional = (len(top5_non_lu) >= 2 and total_amount > 200)
    
    # 退潮期信号：涨停少、成交额低、ST涨停占比高
    st_ratio = sum(1 for s in limit_up if 'ST' in s.get('name','')) / max(lu, 1)
    is_retreat = (lu < 20 and total_amount < 100)

    if is_retreat:
        sentiment = "❄️ 退潮期"
        strategy = "空仓或1成，极端谨慎"
        action = "空仓"
        hot_stocks = []
        inst_list = []
    elif is_institutional:
        top5_names = [s['name'] for s in top5_non_lu[:5]]
        inst_list = [f"{s['name']}({float(s.get('changepercent',0)):+.0f}%)" for s in top5_non_lu[:5]]
        sentiment = "🔵 机构主导行情"
        strategy = "跟机构抱团趋势股；重点关注成交额前5"
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
    elif lu >= 10:
        sentiment = "🌙 弱势整理"
        strategy = "极轻仓练习，不追高"
        action = "仓位1成"
        hot_stocks = [s['name'] for s in big_up[:5]] if big_up else []
        inst_list = []
    else:
        sentiment = "🆘 极端弱势"
        strategy = "清仓，空仓等待"
        action = "空仓"
        hot_stocks = []
        inst_list = []

    log.append(f"\n{'='*50}")
    log.append(f"{sentiment}")
    log.append(f"📋 策略: {strategy}")
    log.append(f"🎯 建议: 仓位{action}")
    log.append(f"{'='*50}")
    
    if inst_list:
        log.append(f"\n📌 机构抱团: {', '.join(inst_list[:3])}")
    if hot_stocks:
        log.append(f"📌 热点标的: {', '.join(hot_stocks[:5])}")
    
    # 额外警示
    if st_ratio > 0.3:
        log.append(f"\n⚠️ 注意：ST股占比{st_ratio:.0%}，谨慎追高！")
    if total_amount < 150:
        log.append(f"\n⚠️ 注意：成交额偏低({total_amount:.0f}亿)，市场偏弱")

    return "\n".join(log), {
        'sentiment': sentiment,
        'action': action,
        'lu': lu,
        'big_up': len(big_up),
        'hot_stocks': hot_stocks,
        'institutional': inst_list
    }


if __name__ == "__main__":
    print("=" * 50)
    print(f"市场情绪判断 V2.1 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)
    
    log, data = get_sentiment()
    print(log)
    
    # 保存结果供后续脚本使用
    if data:
        save_path = "/home/dhtaiyi/.openclaw/workspace/stock-data/market_sentiment_latest.json"
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        data['updated'] = datetime.now().isoformat()
        with open(save_path, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
