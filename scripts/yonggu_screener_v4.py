#!/usr/bin/env python3
"""
妖股量化筛选系统 v4.0 - 混合架构版
数据源：
  1. 腾讯财经API - 实时行情（主力）
  2. Tushare Pro - 历史数据/财务数据（辅助，需token）
  
Token配置：~/.openclaw/.credentials/tushare_token.txt
"""

import requests
import time
import json
import os
import pandas as pd
from datetime import datetime, timedelta
from datetime import date as date_type

# ============================================================
# 配置
# ============================================================
TUSHARE_TOKEN_FILE = os.path.expanduser("~/.openclaw/.credentials/tushare_token.txt")
TENcent_URL = "https://qt.gtimg.cn/q={}"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://gu.qq.com'
}
BATCH_SIZE = 60

# ============================================================
# Tushare 初始化
# ============================================================
def get_tushare():
    """获取Tushare Pro API实例"""
    token_file = TUSHARE_TOKEN_FILE
    if os.path.exists(token_file):
        with open(token_file) as f:
            token = f.read().strip()
        try:
            import tushare as ts
            pro = ts.pro_api(token)
            return pro
        except:
            return None
    return None

# ============================================================
# 腾讯行情数据获取
# ============================================================
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
        print(f"⚠️  腾讯API失败: {e}")
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
        
        try:
            amount_raw = parts[37] if len(parts) > 37 and parts[37] else "0"
            if '/' in amount_raw:
                amount = float(amount_raw.split('/')[-1])
            else:
                amount = float(amount_raw)
        except:
            amount = 0
        
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
            "amount": amount,
        }
    except:
        return None

# ============================================================
# Tushare 数据获取
# ============================================================
def get_tushare_daily(ts_code, days=30):
    """获取个股日线数据"""
    pro = get_tushare()
    if not pro:
        return None
    
    end = datetime.now().strftime('%Y%m%d')
    start = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
    
    try:
        df = pro.daily(ts_code=ts_code, start_date=start, end_date=end)
        return df.sort_values('trade_date')
    except Exception as e:
        return None

def get_tushare_limit_stocks(trade_date=None):
    """获取涨停股列表"""
    pro = get_tushare()
    if not pro:
        return None
    
    if not trade_date:
        trade_date = datetime.now().strftime('%Y%m%d')
    
    try:
        df = pro.limit_list_d(trade_date=trade_date, limit=200)
        return df
    except Exception as e:
        print(f"⚠️  limit_list_d失败: {e}")
        return None

def get_tushare_market_breadth(trade_date=None):
    """获取市场宽度数据（用于判断情绪周期）"""
    pro = get_tushare()
    if not pro:
        return None
    
    if not trade_date:
        trade_date = datetime.now().strftime('%Y%m%d')
    
    try:
        df = pro.bak_basic(trade_date=trade_date, limit=500)
        return df
    except Exception as e:
        return None

# ============================================================
# 妖股评分系统
# ============================================================
def calc_yonggu_score(stock, history=None):
    """
    计算妖股综合评分 (0-100)
    
    评分维度：
    - 涨幅得分 (30%)
    - 换手率得分 (25%)
    - 量比得分 (15%)
    - 价格位置得分 (10%)
    - 涨停加成 (10%)
    - 市盈率得分 (10%)
    """
    score = 50  # 基准分
    details = []
    signals = []
    
    rise = stock.get("rise", 0)
    turnover = stock.get("turnover", 0)
    vr = stock.get("volume_ratio", 0)
    price = stock.get("price", 0)
    pe = stock.get("pe", 0)
    
    # 1. 涨幅评分
    if rise >= 9.9:
        score += 20
        details.append("🔥涨停")
        signals.append(("涨停", 1))
    elif 5.0 <= rise < 9.9:
        score += 15
        details.append("妖股起步涨幅(5-10%)")
        signals.append(("大阳线", 1))
    elif 3.0 <= rise < 5.0:
        score += 10
        details.append("启动迹象(3%+)")
    elif rise > 20.0:
        score -= 10
        details.append("⚠️涨幅过大")
        signals.append(("涨幅过大", -1))
    elif rise < 0:
        score -= 5
        details.append("⚠️下跌")
    
    # 2. 换手率评分
    if 8.0 <= turnover <= 15.0:
        score += 15
        details.append("换手健康(8-15%)")
    elif 15.0 < turnover <= 25.0:
        score += 8
        details.append("换手偏高(15-25%)")
    elif turnover > 25.0:
        score -= 8
        details.append("⚠️换手过高，小心主力出货")
        signals.append(("高换手", -1))
    elif turnover >= 5.0:
        score += 5
        details.append("有一定换手(5%+)")
    
    # 3. 量比评分
    if vr >= 3.0:
        score += 10
        details.append(f"量比大幅放大({vr:.1f}x)")
    elif vr >= 2.0:
        score += 7
        details.append(f"量比放大({vr:.1f}x)")
    elif vr >= 1.5:
        score += 4
        details.append(f"量比尚可({vr:.1f}x)")
    
    # 4. 价格位置（主升定义：低价启动）
    if 0 < price <= 10.0:
        score += 5
        details.append("低价启动(<10元)")
    elif 10.0 < price <= 20.0:
        score += 2
    elif price > 100.0:
        score -= 5
        details.append("⚠️高价股")
    
    # 5. 市盈率（基本面）
    if 0 < pe < 30:
        score += 5
        details.append("PE合理(<30)")
    elif 30 <= pe < 50:
        score += 2
    elif pe <= 0:
        score -= 3
        details.append("⚠️亏损股")
    elif pe >= 100:
        score -= 5
        details.append("⚠️PE泡沫")
    
    # 综合评级
    if score >= 80:
        level = "💥超级妖股候选"
    elif score >= 65:
        level = "🎯重点妖股候选"
    elif score >= 50:
        level = "📈值得关注"
    else:
        level = "⏸️观察"
    
    return {
        "score": min(100, max(0, score)),
        "level": level,
        "details": details,
        "signals": signals,
    }

def filter_candidates(stocks, min_score=50, min_rise=0, max_rise=100):
    """筛选候选股票"""
    results = []
    for code, stock in stocks.items():
        if stock.get("price", 0) <= 0:
            continue
        
        rise = stock.get("rise", 0)
        if rise < min_rise or rise > max_rise:
            continue
        
        score_info = calc_yonggu_score(stock)
        if score_info["score"] >= min_score:
            stock["yonggu_score"] = score_info["score"]
            stock["yonggu_level"] = score_info["level"]
            stock["yonggu_details"] = score_info["details"]
            results.append(stock)
    
    results.sort(key=lambda x: x["yonggu_score"], reverse=True)
    return results

# ============================================================
# 股票池
# ============================================================
WATCHLIST = {
    # 人工智能/AI
    "AI人工智能": [
        "sh600570", "sh600588", "sz000977", "sz002230",
        "sh603019", "sz300024", "sh600536", "sh688111",
    ],
    # 新能源汽车
    "新能源汽车": [
        "sz300750", "sh600733", "sz002594", "sh601238", "sh600699",
        "sz002812", "sh600478", "sz300014", "sh601127",
    ],
    # 半导体/芯片
    "半导体芯片": [
        "sh600584", "sz002371", "sh688396", "sh603986",
        "sz300661", "sh688008", "sh600745", "sh688012",
    ],
    # 医药医疗
    "医药医疗": [
        "sh600276", "sz000538", "sh603259", "sz300760", "sh600196",
        "sh601607", "sz002007", "sz300015",
    ],
    # 军工
    "军工航天": [
        "sh600893", "sz000738", "sh600316", "sz002025", "sh600038",
        "sz300696", "sh601669", "sh600150", "sh600760",
    ],
    # 光伏新能源
    "光伏新能源": [
        "sh601012", "sz300274", "sh600438", "sz002459",
        "sh688388", "sz002129", "sh601865",
    ],
    # 化工
    "化工材料": [
        "sh600309", "sz002601", "sh600352", "sh600989", "sz002092",
        "sh600486", "sz000830", "sh600273",
    ],
    # 机器人
    "机器人": [
        "sz300024", "sh600835", "sz002747", "sh600699", "sz300154",
        "sz002009", "sh601106", "sz300820",
    ],
    # 数字经济
    "数字经济": [
        "sh600131", "sz000034", "sh603636", "sz300578", "sh600588",
        "sh601360", "sz300287", "sh600570",
    ],
    # 银行金融
    "银行金融": [
        "sh600036", "sh601318", "sh600000", "sz000001", "sh601166",
        "sh601398", "sh601288", "sh601328",
    ],
}

CUSTOM_CODES = [
    "sh600519", "sz000858", "sh603369", "sz000568", "sh600809",
    "sh600036", "sh601318", "sz000001",
    "sz300750", "sh601166", "sh600050",
    "sz000002", "sh600000",
]

def build_code_list():
    codes = []
    for codes_list in WATCHLIST.values():
        codes.extend(codes_list)
    codes.extend(CUSTOM_CODES)
    return list(dict.fromkeys(codes))

# ============================================================
# 输出格式化
# ============================================================
def format_amount(amount):
    """格式化成交额"""
    if amount <= 0:
        return "-"
    if amount >= 1e8:
        return f"{amount/1e8:.2f}亿"
    elif amount >= 1e4:
        return f"{amount/1e4:.0f}万"
    return f"{amount:.0f}"

def print_table(candidates, title, limit=None):
    print(f"\n{'='*80}")
    print(f"📊 {title} ({datetime.now().strftime('%H:%M:%S')})")
    print(f"{'='*80}")
    
    if not candidates:
        print("⚠️  未找到符合条件的股票")
        return
    
    n = limit or len(candidates)
    header = f"{'排名':<4}{'代码':<8}{'名称':<10}{'现价':<8}{'涨幅':<8}{'换手率':<8}{'量比':<6}{'评分':<6}  信号"
    print(f"\n{header}")
    print("-" * 80)
    
    for i, s in enumerate(candidates[:n], 1):
        rise_str = f"{s['rise']:.2f}%"
        turnover_str = f"{s['turnover']:.2f}%" if s['turnover'] > 0 else "-"
        vr_str = f"{s['volume_ratio']:.1f}x" if s['volume_ratio'] > 0 else "-"
        details = " ".join(s.get("yonggu_details", [])[:3])
        
        print(f"{i:<4}{s['code']:<8}{s['name']:<10}{s['price']:<8.2f}{rise_str:<8}"
              f"{turnover_str:<8}{vr_str:<6}{s['yonggu_score']:<6}  {details}")
    
    if limit and len(candidates) > limit:
        print(f"\n... 还有 {len(candidates) - limit} 只")

def print_summary(candidates, all_stocks):
    """打印汇总信息"""
    # 统计
    total = len(candidates)
    limit_up = len([s for s in all_stocks.values() if s.get('rise', 0) >= 9.9])
    hot = len([s for s in candidates if s.get('yonggu_score', 0) >= 65])
    
    # 板块分布
    sectors = {}
    for s in candidates:
        # Try to find sector
        for sec, codes in WATCHLIST.items():
            if s['code'] in codes:
                sectors[sec] = sectors.get(sec, 0) + 1
                break
    
    print(f"\n📊 市场概况:")
    print(f"   监控股票: {len(all_stocks)} 只")
    print(f"   妖股候选: {total} 只")
    print(f"   其中涨停: {limit_up} 只")
    print(f"   重点候选: {hot} 只")
    
    if sectors:
        top_sectors = sorted(sectors.items(), key=lambda x: -x[1])[:5]
        print(f"   热门板块: {', '.join(f'{k}({v})' for k, v in top_sectors)}")

# ============================================================
# 主程序
# ============================================================
def main():
    import argparse
    parser = argparse.ArgumentParser(description='妖股量化筛选系统 v4.0')
    parser.add_argument('--score', type=int, default=50, help='最低评分(默认50)')
    parser.add_argument('--top', type=int, default=0, help='显示前N只(默认全部)')
    parser.add_argument('--sector', type=str, default='', help='指定板块')
    parser.add_argument('--tushare', action='store_true', help='使用Tushare数据')
    args = parser.parse_args()
    
    print("=" * 80)
    print("🚀 妖股量化筛选系统 v4.0（混合架构版）")
    print("=" * 80)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📚 策略：龙头战法 + 主升定义 + 超短情绪 + 筹码趋势")
    
    # 获取数据
    codes = build_code_list()
    if args.sector and args.sector in WATCHLIST:
        codes = WATCHLIST[args.sector]
        print(f"📂 板块: {args.sector} ({len(codes)}只)")
    else:
        print(f"📂 股票池: 全部 ({len(codes)}只)")
    
    print("\n📥 获取实时行情...")
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
    
    # Tushare 涨停数据（如果可用）
    if args.tushare:
        print("\n📥 尝试获取Tushare涨停数据...")
        ts_data = get_tushare_limit_stocks()
        if ts_data is not None and len(ts_data) > 0:
            print(f"✅ Tushare涨停股: {len(ts_data)} 只")
        time.sleep(3)
    
    # 筛选
    print(f"\n🔍 筛选: 评分>={args.score}")
    candidates = filter_candidates(all_stocks, min_score=args.score)
    
    # 输出
    print_table(candidates, "妖股筛选结果", limit=args.top if args.top > 0 else None)
    
    # 重点候选
    top = [c for c in candidates if c.get('yonggu_score', 0) >= 65]
    if top:
        print_table(top, "💥 重点妖股候选（评分≥65）")
    
    # 涨停
    limit_up = [s for s in all_stocks.values() if s.get('rise', 0) >= 9.9]
    limit_up.sort(key=lambda x: x.get('turnover', 0), reverse=True)
    if limit_up:
        for s in limit_up[:15]:
            s['yonggu_score'] = 100
            s['yonggu_level'] = "💥涨停"
            s['yonggu_details'] = [f"换手{s['turnover']:.1f}%"]
        print_table(limit_up, "💥 今日涨停股")
    
    # 飙升候选
    strong = [s for s in candidates if 5.0 <= s.get('rise', 0) <= 20.0]
    if strong:
        print_table(strong[:10], "🚀 飙升股候选（涨幅5-20%）")
    
    print_summary(candidates, all_stocks)
    
    print("\n" + "=" * 80)
    print("⚠️  仅供学习研究，不构成投资建议！")
    print("=" * 80)

if __name__ == "__main__":
    main()
