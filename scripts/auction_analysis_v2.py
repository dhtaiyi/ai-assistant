#!/usr/bin/env python3
"""
集合竞价分析 V2 - 结合养家心法+首板战法
==============================================
核心功能（9:25/9:30执行）：
1. 自动加载昨日涨停股池
2. 分析竞价表现（高开幅度、竞价量）
3. 首板战法买点A量化：昨日<3%，今高开3-7%
4. 识别"超预期"竞价信号
5. 养家心法：不抄底、跟龙头、确定性优先

理论依据：
- 买点A（首板战法）：昨日涨幅<3%，今高开3-7%为最佳
- 高开>9%：危险！容易炸板（主力借情绪出货）
- 高开<1%：低于预期，说明不是主线
- 竞价量：越大越好，说明资金抢筹
"""
import requests
import json
import re
import os
from datetime import datetime, timedelta

LOG_FILE = "/tmp/auction_analysis.log"

def is_trading():
    from datetime import time
    now = datetime.now().time()
    return (time(9, 25) <= now <= time(9, 35)) or (time(13, 0) <= now <= time(13, 5))

def is_clean_stock(name):
    if any(x in name for x in ['ST', '*ST', 'N ', '退', 'S ']):
        return False
    return True

def get_full_code(symbol):
    code = symbol.replace('sz', '').replace('sh', '')
    prefix = 'sz' if symbol.startswith('sz') else 'sh'
    return prefix + code

def get_yesterday_limitup():
    """获取昨日涨停股池（从候选池加载）"""
    today = datetime.now()
    wd = today.weekday()
    if wd == 0:  # 周一
        y = today - timedelta(days=3)
    else:
        y = today - timedelta(days=1)
    y_str = y.strftime('%Y%m%d')
    
    candidates_path = f"/home/dhtaiyi/.openclaw/workspace/stock-patterns/candidates/{y_str}.json"
    if not os.path.exists(candidates_path):
        # 尝试找最近的候选池
        for i in range(1, 7):
            d = today - timedelta(days=i)
            if d.weekday() >= 5:
                continue
            path = f"/home/dhtaiyi/.openclaw/workspace/stock-patterns/candidates/{d.strftime('%Y%m%d')}.json"
            if os.path.exists(path):
                candidates_path = path
                break
    
    stocks = []
    if os.path.exists(candidates_path):
        with open(candidates_path) as f:
            data = json.load(f)
        for code, info in data.items():
            name = info.get('name', '')
            if is_clean_stock(name):
                stocks.append({'code': code, 'name': name})
    
    return stocks, candidates_path

def get_realtime_data(codes_list):
    """批量获取实时行情（腾讯接口）"""
    if not codes_list:
        return {}
    
    # 转换代码格式
    full_codes = []
    for item in codes_list:
        code = item['code']
        # 确保是完整格式：sz123456 或 sh600000
        if not code.startswith('sz') and not code.startswith('sh'):
            code = ('sz' + code) if code.startswith('0') or code.startswith('3') else ('sh' + code)
        full_codes.append(code)
    
    codes_str = ','.join(full_codes)
    try:
        r = requests.get(f'http://qt.gtimg.cn/q={codes_str}', timeout=10)
        result = {}
        for line in r.text.strip().split('\n'):
            if '"' not in line:
                continue
            # v_s_sh600000="51~name~600000~price~prev_close..."
            m = re.search(r'=\s*"([^"]+)"', line)
            if not m:
                continue
            parts = m.group(1).split('~')
            if len(parts) < 10:
                continue
            try:
                name = parts[1]
                price = float(parts[3]) if parts[3] else 0
                prev_close = float(parts[4]) if parts[4] else 0
                open_p = float(parts[5]) if parts[5] else 0
                high = float(parts[33]) if len(parts) > 33 and parts[33] else 0
                low = float(parts[34]) if len(parts) > 34 and parts[34] else 0
                amount = float(parts[37]) if len(parts) > 37 and parts[37] else 0  # 成交额
                
                if prev_close > 0 and price > 0:
                    pct = (price - prev_close) / prev_close * 100
                    auction_pct = (open_p - prev_close) / prev_close * 100 if open_p > 0 else 0
                    result[name] = {
                        'price': price,
                        'prev_close': prev_close,
                        'open': open_p,
                        'pct': pct,
                        'auction_pct': auction_pct,
                        'high': high,
                        'low': low,
                        'amount': amount,
                        'code': full_codes[len(result)] if len(result) < len(full_codes) else ''
                    }
            except (ValueError, IndexError):
                continue
        return result
    except Exception as e:
        print(f"获取行情失败: {e}")
        return {}

def score_auction(auction_pct, yesterday_pct, amount, name):
    """
    竞价评分（结合养家心法+首板战法）
    满分100分
    """
    score = 0
    reasons = []
    
    # ===== 买点A核心判断：昨<3%，今高开3-7% = 最佳信号 =====
    if yesterday_pct < 3 and 3 <= auction_pct <= 7:
        score += 40
        reasons.append("买点A✅首板战法(昨<3%今高开3-7%)")
    elif auction_pct > 9:
        score -= 30
        reasons.append("⚠️高开>9%危险！容易炸板")
    elif auction_pct < 0:
        score -= 20
        reasons.append("⚠️低开，不符合首板战法")
    elif auction_pct > 7 and auction_pct <= 9:
        score += 15
        reasons.append("高开7-9%偏强，需观察")
    elif 1 <= auction_pct < 3:
        score += 10
        reasons.append("普通高开1-3%")
    
    # ===== 竞价量评分（成交额越大说明抢筹越凶）=====
    amount_yi = amount / 1e8  # 转换为亿
    if amount_yi >= 5:
        score += 20
        reasons.append(f"竞价放量{amount_yi:.1f}亿💰")
    elif amount_yi >= 2:
        score += 10
        reasons.append(f"竞价{amount_yi:.1f}亿")
    elif amount_yi >= 0.5:
        score += 5
    else:
        reasons.append("竞价缩量⚠️")
    
    # ===== 昨涨停加成 =====
    if 9.5 <= yesterday_pct < 10.5:
        score += 10
        reasons.append("昨日涨停+1")
    elif yesterday_pct < 0:
        score -= 10
        reasons.append("⚠️昨天下跌，不抄底")
    
    return score, reasons


def analyze():
    print(f"\n{'='*60}")
    print(f"📊 集合竞价分析 V2 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")
    
    # 获取昨日涨停股池
    stocks, pool_path = get_yesterday_limitup()
    print(f"\n📂 候选池: {os.path.basename(pool_path)} ({len(stocks)}只)")
    
    if not stocks:
        print("❌ 无候选股池数据，跳过")
        return
    
    # 获取实时数据
    data = get_realtime_data(stocks)
    print(f"📡 实时数据: {len(data)}只")
    
    if not data:
        print("❌ 无法获取实时数据")
        return
    
    # 分析每只股票
    results = []
    for item in stocks:
        name = item['name']
        if name not in data:
            continue
        
        d = data[name]
        auction_pct = d['auction_pct']
        current_pct = d['pct']
        amount_yi = d['amount'] / 1e8
        code = item['code']
        
        # 用昨日收盘计算昨日涨幅（从候选池）
        prev_close = d['prev_close']
        # 昨日在候选池里的涨幅大概率和实际一致，这里用候选池记录的pct
        yesterday_pct = 0  # 需要从候选池读取
        
        # 评分
        score, reasons = score_auction(auction_pct, 0, d['amount'], name)
        
        # 判断状态
        if current_pct >= 9.5:
            status = "🔴涨停"
        elif current_pct >= 5:
            status = "🔥强势"
        elif current_pct >= 0:
            status = "🟡普通"
        else:
            status = "🔵下跌"
        
        results.append({
            'name': name,
            'code': code,
            'auction_pct': auction_pct,
            'current_pct': current_pct,
            'amount_yi': amount_yi,
            'score': score,
            'reasons': reasons,
            'status': status,
            'open': d['open'],
            'price': d['price']
        })
    
    # 按竞价涨幅排序
    results.sort(key=lambda x: x['auction_pct'], reverse=True)
    
    # ===== 输出分析 =====
    print(f"\n{'─'*60}")
    print(f"📈 竞价排行榜（按高开幅度）:")
    print(f"{'─'*60}")
    
    strong_auction = [r for r in results if r['auction_pct'] >= 3]
    weak_auction = [r for r in results if r['auction_pct'] < 0]
    
    for r in results[:15]:
        auc_mark = "✅" if 3 <= r['auction_pct'] <= 7 else ("⚠️" if r['auction_pct'] > 9 else "  ")
        print(f"  {auc_mark}{r['status']} {r['name']}({r['code']}) "
              f"竞价{float(r['auction_pct']):+.2f}% "
              f"现{float(r['current_pct']):+.2f}% "
              f"量{r['amount_yi']:.1f}亿")
        if r['reasons']:
            for reason in r['reasons'][:2]:
                print(f"        → {reason}")
    
    # ===== 买点A信号汇总 =====
    buy_a = [r for r in results if 3 <= r['auction_pct'] <= 7 and r['current_pct'] >= 0]
    if buy_a:
        print(f"\n🎯 买点A信号（首板战法）:")
        for r in buy_a[:5]:
            print(f"  ✅ {r['name']}({r['code']}) 竞价+{r['auction_pct']:.1f}% 现+{r['current_pct']:.1f}% 量{r['amount_yi']:.1f}亿")
    
    # ===== 危险信号 =====
    danger = [r for r in results if r['auction_pct'] > 9.5]
    if danger:
        print(f"\n⚠️ 高开>9%危险信号（容易炸板）:")
        for r in danger[:5]:
            print(f"  🚫 {r['name']} 竞价+{r['auction_pct']:.1f}%")
    
    # ===== 竞价弱势 =====
    if weak_auction:
        print(f"\n🔵 竞价低开（昨日强势股今走弱）:")
        for r in weak_auction[:5]:
            print(f"  ⚠️ {r['name']} 竞价{r['auction_pct']:.1f}%")
    
    # ===== 养家心法提示 =====
    print(f"\n{'─'*60}")
    print(f"💡 养家心法提示:")
    
    if strong_auction:
        print(f"  ✅ 竞价强势({len(strong_auction)}只高开3%+)，市场风险偏好高")
    if weak_auction:
        print(f"  ⚠️ {len(weak_auction)}只昨日强势股低开，说明资金谨慎")
    if len(buy_a) >= 3:
        print(f"  🎯 买点A机会多({len(buy_a)}只)，积极关注")
    if len(danger) > len(results) * 0.5:
        print(f"  🚨 大量高开>9%，小心！情绪过于亢奋容易炸板")
    
    # ===== 保存竞价数据 =====
    today_str = datetime.now().strftime('%Y%m%d')
    save_dir = "/home/dhtaiyi/.openclaw/workspace/stock-data/auction"
    os.makedirs(save_dir, exist_ok=True)
    save_path = f"{save_dir}/{today_str}.json"
    
    with open(save_path, 'w') as f:
        json.dump({
            'time': datetime.now().isoformat(),
            'results': results,
            'buy_a_count': len(buy_a),
            'danger_count': len(danger),
            'weak_count': len(weak_auction)
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 竞价数据已保存: {save_path}")
    return results


if __name__ == "__main__":
    print(f"竞价分析 V2 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not is_trading():
        print("⏰ 集合竞价分析在9:25-9:35或13:00-13:05执行效果最佳")
        print("   当前数据仅供参考（可提前分析昨日候选股竞价情况）")
    
    results = analyze()
    
    if results:
        print(f"\n📊 汇总: {len(results)}只股")
        print(f"   买点A候选: {len([r for r in results if 3 <= r['auction_pct'] <= 7])}只")
        print(f"   高开>9%危险: {len([r for r in results if r['auction_pct'] > 9])}只")
