#!/usr/bin/env python3
"""
妖股预警系统 v1.0
使用方法：
    python3 yonggu_warning.py              # 扫描全部候选
    python3 yonggu_warning.py --score 65    # 只看评分>=65
    python3 yonggu_warning.py --top 10       # 只看前10只
"""

import requests
import pandas as pd
import time
import sys
import os
from datetime import datetime

# ========== 配置 ==========
TENcent_URL = "https://qt.gtimg.cn/q={}"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://gu.qq.com'
}
BATCH_SIZE = 60

# 预警阈值
DEFAULT_THRESHOLD = 50

# 妖股候选股票池（可根据需要扩展）
WATCHLIST = {
    # 人工智能/AI
    "AI人工智能": ["sh600570", "sh600588", "sz000977", "sz002230", "sh603019", "sz300024", "sh600536", "sh688111"],
    # 新能源汽车
    "新能源汽车": ["sz300750", "sh600733", "sz002594", "sh601238", "sh600699", "sz002812", "sh600478", "sz300014"],
    # 半导体/芯片
    "半导体芯片": ["sh600584", "sz002371", "sh688396", "sh603986", "sz300661", "sh688008", "sh600745", "sh688012"],
    # 医药医疗
    "医药医疗": ["sh600276", "sz000538", "sh603259", "sz300760", "sh600196", "sh601607", "sz002007", "sz300015"],
    # 军工
    "军工航天": ["sh600893", "sz000738", "sh600316", "sz002025", "sh600038", "sz300696", "sh601669", "sh600150"],
    # 机器人
    "机器人": ["sz300024", "sh600835", "sz002747", "sh600699", "sz300154", "sz002009", "sh601106", "sz300820"],
    # 数字经济
    "数字经济": ["sh600131", "sz000034", "sh603636", "sz300578", "sh600588", "sh601360", "sz300287", "sh600570"],
}

CUSTOM_CODES = [
    "sh600519", "sz000858", "sh603369", "sz000568", "sh600809",
    "sh600036", "sh601318", "sz000001",
    "sz300750", "sh601166", "sh600050",
    "sz000002", "sh600000",
]

# ========== 数据获取 ==========
def fetch_tencent_stocks(codes):
    """批量获取腾讯行情"""
    code_str = ",".join(codes)
    try:
        r = requests.get(TENcent_URL.format(code_str), headers=HEADERS, timeout=15)
        stocks = {}
        for line in r.text.strip().split('\n'):
            if '~' not in line or 'none_match' in line:
                continue
            stock = parse_tencent_line(line)
            if stock:
                stocks[stock['code']] = stock
        return stocks
    except Exception as e:
        print(f"⚠️  获取数据失败: {e}")
        return {}

def parse_tencent_line(line):
    """解析腾讯行情单行"""
    try:
        code_with_prefix = line.split('=')[0].replace('v_', '').strip()
        market = code_with_prefix[:2]
        code = code_with_prefix[2:]
        
        parts = line.split('~')
        if len(parts) < 40:
            return None
        
        name = parts[1]
        price = float(parts[3]) if parts[3] else 0
        prev_close = float(parts[4]) if parts[4] else 0
        open_price = float(parts[5]) if parts[5] else 0
        
        if prev_close > 0:
            rise = (price - prev_close) / prev_close * 100
        else:
            rise = 0
        
        turnover = float(parts[38]) if parts[38] else 0
        vr_raw = parts[49] if len(parts) > 49 and parts[49] else "0"
        try:
            volume_ratio = float(vr_raw)
        except:
            volume_ratio = 0
        
        try:
            pe_raw = parts[39] if len(parts) > 39 and parts[39] else "0"
            pe = float(pe_raw) if pe_raw not in ['-', '', 'N/A'] else -1
        except:
            pe = -1
        
        high = float(parts[33]) if len(parts) > 33 and parts[33] else price
        low = float(parts[34]) if len(parts) > 34 and parts[34] else price
        
        return {
            "code": code,
            "name": name,
            "market": "SH" if market == "sh" else "SZ",
            "price": price,
            "prev_close": prev_close,
            "open": open_price,
            "rise": rise,
            "high": high,
            "low": low,
            "turnover": turnover,
            "volume_ratio": volume_ratio,
            "pe": pe,
        }
    except:
        return None

# ========== 预警计算 ==========
def calc_warning_score(stock):
    """
    计算妖股预警评分 (0-100)
    
    妖股启动三大信号：
    1. 成交量放大
    2. 振幅扩大
    3. 股价突破关键位
    """
    score = 0
    signals = []
    
    rise = stock.get("rise", 0)
    turnover = stock.get("turnover", 0)
    vr = stock.get("volume_ratio", 0)
    price = stock.get("price", 0)
    high = stock.get("high", price)
    low = stock.get("low", price)
    pe = stock.get("pe", 0)
    
    # 1. 成交量因子 (30%)
    if vr >= 3.0:
        score += 30
        signals.append(f"✅量比{vr:.1f}x")
    elif vr >= 2.0:
        score += 25
        signals.append(f"✅量比{vr:.1f}x")
    elif vr >= 1.5:
        score += 20
        signals.append(f"✅量比{vr:.1f}x")
    elif vr >= 1.2:
        score += 10
        signals.append(f"⚠️量比{vr:.1f}x")
    elif vr >= 1.0:
        score += 5
        signals.append(f"⚠️量比{vr:.1f}x")
    
    # 2. 涨幅因子 (25%)
    if 5.0 <= rise < 10.0:
        score += 25
        signals.append(f"✅涨幅{rise:.1f}%(最佳区间)")
    elif 3.0 <= rise < 5.0:
        score += 20
        signals.append(f"✅涨幅{rise:.1f}%")
    elif 10.0 <= rise < 15.0:
        score += 18
        signals.append(f"⚠️涨幅{rise:.1f}%")
    elif rise >= 15.0:
        score += 10
        signals.append(f"⚠️涨幅过大{rise:.1f}%")
    elif rise >= 9.9:
        score += 30
        signals.append(f"🔥涨停!")
    elif rise < 0:
        score -= 5
        signals.append(f"⚠️下跌{rise:.1f}%")
    
    # 3. 换手率因子 (20%)
    if 8.0 <= turnover <= 15.0:
        score += 20
        signals.append(f"✅换手{turnover:.1f}%")
    elif 15.0 < turnover <= 25.0:
        score += 15
        signals.append(f"⚠️换手偏高{turnover:.1f}%")
    elif turnover > 25.0:
        score += 5
        signals.append(f"❌换手过高{turnover:.1f}%")
    elif 5.0 <= turnover < 8.0:
        score += 12
        signals.append(f"✅换手适中{turnover:.1f}%")
    elif turnover >= 3.0:
        score += 8
        signals.append(f"⚠️换手偏低{turnover:.1f}%")
    
    # 4. 价格位置因子 (15%)
    if low > 0:
        amplitude = (high - low) / low * 100
        price_pos = (price - low) / (high - low) * 100 if high != low else 50
        
        if price_pos >= 90:
            score += 15
            signals.append("✅接近区间高点")
        elif price_pos >= 70:
            score += 10
            signals.append("✅股价强势")
        elif price_pos >= 50:
            score += 5
            signals.append("⚠️区间中部")
        
        # 振幅
        if amplitude > 15:
            score += 10
            signals.append(f"✅振幅{amplitude:.1f}%")
        elif amplitude > 10:
            score += 7
            signals.append(f"⚠️振幅{amplitude:.1f}%")
    
    # 5. 市盈率因子 (10%) - 妖股市盈率通常为负
    if pe <= 0:
        score += 5
        signals.append("⚠️亏损股(题材炒作)")
    elif 0 < pe < 50:
        score += 3
        signals.append("✅PE正常")
    elif pe >= 100:
        score -= 3
        signals.append("❌PE过高")
    
    # 综合评级
    if score >= 80:
        level = "💥红色预警"
    elif score >= 65:
        level = "🔴橙色预警"
    elif score >= 50:
        level = "🟡黄色预警"
    elif score >= 35:
        level = "🔵蓝色观察"
    else:
        level = "⚪绿色"
    
    return {
        "score": min(100, max(0, score)),
        "level": level,
        "signals": signals,
    }

def filter_warnings(all_stocks, min_score=50):
    """筛选预警股票"""
    results = []
    for code, stock in all_stocks.items():
        if stock.get("price", 0) <= 0:
            continue
        
        warn = calc_warning_score(stock)
        if warn["score"] >= min_score:
            stock["warning_score"] = warn["score"]
            stock["warning_level"] = warn["level"]
            stock["warning_signals"] = warn["signals"]
            results.append(stock)
    
    results.sort(key=lambda x: x["warning_score"], reverse=True)
    return results

# ========== 输出 ==========
def print_warning_table(candidates, title, limit=None):
    print(f"\n{'='*80}")
    print(f"🚨 {title} ({datetime.now().strftime('%H:%M:%S')})")
    print(f"{'='*80}")
    
    if not candidates:
        print("⚠️  没有符合条件的预警股票")
        return
    
    n = limit or len(candidates)
    header = f"{'排名':<4}{'代码':<8}{'名称':<10}{'现价':<8}{'涨幅':<8}{'换手率':<8}{'量比':<6}{'评分':<6} 信号"
    print(f"\n{header}")
    print("-" * 80)
    
    for i, s in enumerate(candidates[:n], 1):
        rise_str = f"{s['rise']:.2f}%"
        turnover_str = f"{s['turnover']:.2f}%" if s['turnover'] > 0 else "-"
        vr_str = f"{s['volume_ratio']:.1f}x" if s['volume_ratio'] > 0 else "-"
        signals = " ".join(s.get("warning_signals", [])[:4])
        
        print(f"{i:<4}{s['code']:<8}{s['name']:<10}{s['price']:<8.2f}{rise_str:<8}"
              f"{turnover_str:<8}{vr_str:<6}{s['warning_score']:<6}  {signals}")
    
    if limit and len(candidates) > limit:
        print(f"\n... 还有 {len(candidates) - limit} 只")
    
    # 统计
    levels = {}
    for s in candidates:
        lv = s.get("warning_level", "❓")
        levels[lv] = levels.get(lv, 0) + 1
    
    print(f"\n📊 预警统计: 共{len(candidates)}只 | ", end="")
    print(" | ".join(f"{k}({v})" for k, v in sorted(levels.items(), key=lambda x: -x[1])))

# ========== 主程序 ==========
def main():
    import argparse
    parser = argparse.ArgumentParser(description='妖股预警系统 v1.0')
    parser.add_argument('--score', type=int, default=0, help='最低评分筛选(默认0,显示全部)')
    parser.add_argument('--top', type=int, default=0, help='只显示前N只(默认全部)')
    parser.add_argument('--sector', type=str, default='', help='指定板块')
    args = parser.parse_args()
    
    print("=" * 80)
    print("🚀 妖股预警系统 v1.0")
    print("=" * 80)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📚 预警依据：妖股启动三大信号(放量+振幅+价格位置)")
    
    # 构建查询列表
    codes = []
    if args.sector and args.sector in WATCHLIST:
        codes = WATCHLIST[args.sector]
        print(f"📂 板块: {args.sector} ({len(codes)}只)")
    else:
        for codes_list in WATCHLIST.values():
            codes.extend(codes_list)
        codes.extend(CUSTOM_CODES)
        codes = list(dict.fromkeys(codes))
        print(f"📂 股票池: 全部 ({len(codes)}只)")
    
    # 获取数据
    print("\n📥 获取行情数据...")
    all_stocks = {}
    for i in range(0, len(codes), BATCH_SIZE):
        batch = codes[i:i+BATCH_SIZE]
        result = fetch_tencent_stocks(batch)
        all_stocks.update(result)
        if i + BATCH_SIZE < len(codes):
            time.sleep(0.3)
    
    print(f"✅ 获取 {len(all_stocks)} 只股票数据")
    
    if not all_stocks:
        print("❌ 数据获取失败")
        return
    
    # 筛选预警
    min_score = args.score if args.score > 0 else 0
    candidates = filter_warnings(all_stocks, min_score=min_score)
    
    # 输出
    if min_score > 0:
        print(f"\n🔍 筛选条件：评分 >= {min_score}")
    
    print_warning_table(candidates, "妖股预警结果", limit=args.top if args.top > 0 else None)
    
    # 红色预警
    red = [c for c in candidates if c.get("warning_score", 0) >= 80]
    if red:
        print_warning_table(red, "💥红色预警(极高危妖股)")
    
    # 橙色预警
    orange = [c for c in candidates if 65 <= c.get("warning_score", 0) < 80]
    if orange:
        print_warning_table(orange, "🔴橙色预警(高危妖股候选)")
    
    print("\n" + "=" * 80)
    print("⚠️  预警系统仅供参考，不构成投资建议！")
    print("⚠️  股市有风险，投资需谨慎！止损线：-7%")
    print("=" * 80)

if __name__ == "__main__":
    main()
