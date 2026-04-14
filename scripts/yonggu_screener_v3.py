#!/usr/bin/env python3
"""
妖股量化筛选系统 v3.0
数据源：腾讯财经行情API (免费，无需token)
策略：龙头战法 + 主升股票定义 + 超短情绪周期 + K线形态 + 筹码趋势

使用方法：
    python3 scripts/yonggu_screener_v3.py              # 筛选全部候选
    python3 scripts/yonggu_screener_v3.py --top 20     # 只看前20只
    python3 scripts/yonggu_screener_v3.py --score 65   # 评分>=65
"""

import requests
import sys
import time
import random
from datetime import datetime

# ============================================================
# 配置
# ============================================================
TENcent_URL = "https://qt.gtimg.cn/q={}"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://gu.qq.com'
}
BATCH_SIZE = 60  # 腾讯API每次最多查询60个

# ============================================================
# 妖股评分权重（基于课程学习）
# ============================================================
SCORE_CONFIG = {
    # 涨幅评分 (权重: 30%)
    "rise": {
        5.0: (+15, "✅ 妖股起步涨幅(5-10%)"),
        10.0: (+10, "⚠️ 涨幅较大(10-20%)"),
        20.0: (-5, "❌ 涨幅过大，风险累积"),
        3.0: (+8, "✅ 启动迹象(3%+)"),
        0.0: (0, "⏸️ 涨幅不足"),
    },
    # 换手率评分 (权重: 25%)
    "turnover": {
        (8.0, 15.0): (+15, "✅ 换手健康(8-15%)"),
        (15.0, 25.0): (+10, "⚠️ 换手偏高(15-25%)"),
        25.0: (-5, "❌ 换手过高，小心主力出货"),
        5.0: (+5, "✅ 有一定换手(5%+)"),
        0.0: (0, "⏸️ 换手不足"),
    },
    # 量比评分 (权重: 15%)
    "volume_ratio": {
        2.0: (+10, "✅ 量比放大(2x+)"),
        1.5: (+5, "✅ 量比尚可(1.5x+)"),
        0.0: (0, "⏸️ 量比不足"),
    },
    # 价格评分 (权重: 10%)
    # 主升股票定义：启动价<10元最佳
    "price": {
        10.0: (+5, "✅ 低价启动(<10元)"),
        20.0: (+2, "⚠️ 中价股"),
        50.0: (-3, "❌ 高价股，拉升难度大"),
        0.0: (0, "❓ 价格异常"),
    },
    # 涨停加成 (额外: 20%)
    "limit_up": {
        True: (+10, "🔥 涨停！"),
        False: (0, ""),
    },
    # 市盈率评分 (权重: 10%)
    # 负PE或过高PE要扣分
    "pe": {
        (0, 50): (+3, "✅ 市盈率正常"),
        0: (-3, "⚠️ 亏损股"),
        100: (-5, "❌ 市盈率过高"),
    },
}

# ============================================================
# 妖股候选股票池（按板块分类，可自行添加）
# ============================================================
# 这个列表包含热门板块的代表性股票，可大幅扩展
WATCHLIST = {
    # 人工智能/AI
    "AI人工智能": [
        "sh600570", "sh600588", "sz000977", "sz002230", "sh688787",
        "sh603019", "sh688981", "sz300024", "sh600536", "sh688111",
    ],
    # 新能源汽车
    "新能源汽车": [
        "sz300750", "sh600733", "sz002594", "sh601238", "sh600699",
        "sz002812", "sh600478", "sz300014", "sh688005", "sh601127",
    ],
    # 半导体/芯片
    "半导体芯片": [
        "sh688981", "sh600584", "sz002371", "sh688396", "sh603986",
        "sz300661", "sh688008", "sh600745", "sz002049", "sh688012",
    ],
    # 医药医疗
    "医药医疗": [
        "sh600276", "sz000538", "sh603259", "sz300760", "sh600196",
        "sh601607", "sz002007", "sz300015", "sh600329", "sh688180",
    ],
    # 白酒消费
    "白酒消费": [
        "sh600519", "sz000858", "sz000568", "sh603369", "sz002304",
        "sh600809", "sz000596", "sh600559", "sh000568", "sz002595",
    ],
    # 银行金融
    "银行金融": [
        "sh600036", "sh601318", "sh600000", "sz000001", "sh601166",
        "sh601398", "sh601288", "sh601328", "sz002142", "sh600015",
    ],
    # 军工
    "军工航天": [
        "sh600893", "sz000738", "sh600316", "sz002025", "sh600038",
        "sz300696", "sh601669", "sz002013", "sh600150", "sh600760",
    ],
    # 光伏新能源
    "光伏新能源": [
        "sh601012", "sz300274", "sh600438", "sh600900", "sh002459",
        "sh688388", "sz002129", "sh601865", "sz300316", "sh600732",
    ],
    # 化工材料
    "化工材料": [
        "sh600309", "sz002601", "sh600352", "sh600989", "sz002092",
        "sh600486", "sz000830", "sh600273", "sh601216", "sz002643",
    ],
    # 元宇宙/VR
    "元宇宙VR": [
        "sz002241", "sh600637", "sh603305", "sz300496", "sh688039",
        "sz300113", "sh603444", "sh300031", "sh002995", "sh300264",
    ],
    # 数字经济
    "数字经济": [
        "sh600131", "sz000034", "sh603636", "sz300578", "sh600588",
        "sh601360", "sz300287", "sh600570", "sz300212", "sh603232",
    ],
    # 机器人
    "机器人": [
        "sz300024", "sh600835", "sz002747", "sh600699", "sz300154",
        "sz002009", "sh601106", "sz300820", "sh688277", "sz002361",
    ],
    # ST/壳资源（高风险，仅供参考）
    "ST板块": [
        "sh600074", "sh600228", "sz000587", "sh600091", "sh600212",
    ],
}

# 额外候选：历史妖股、热门题材股（需要用户自行维护）
CUSTOM_CODES = [
    # 近期强势股（请根据每日行情自行添加）
    "sh600519", "sz000001", "sh601318", "sh600036",
    "sz300750", "sh601166", "sh600050", "sh601888",
    "sz000002", "sh600000", "sh601238", "sh600745",
]

def get_stock_batch(codes):
    """批量获取腾讯行情数据"""
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
        print(f"⚠️  批量获取失败: {e}")
        return {}

def parse_tencent_line(line):
    """解析腾讯行情单行数据"""
    try:
        # v_sh600519="1~贵州茅台~600519~1460.00~1459.88~..."
        code_with_prefix = line.split('=')[0].replace('v_', '').strip()
        code = code_with_prefix[2:] if code_with_prefix.startswith(('sh', 'sz', 'hk')) else code_with_prefix
        
        parts = line.split('~')
        if len(parts) < 40:
            return None
        
        name = parts[1]
        price = float(parts[3]) if parts[3] else 0
        prev_close = float(parts[4]) if parts[4] else 0
        open_price = float(parts[5]) if parts[5] else 0
        vol = int(parts[6]) if parts[6] else 0  # 成交量(手)
        
        # 计算涨幅
        if prev_close > 0:
            rise = (price - prev_close) / prev_close * 100
        else:
            rise = 0
        
        # 换手率 (field 38)
        try:
            turnover = float(parts[38]) if parts[38] else 0
        except:
            turnover = 0
        
        # 量比 (field 49 - varies)
        try:
            # 字段49是量比
            vr_raw = parts[49] if len(parts) > 49 and parts[49] else "0"
            volume_ratio = float(vr_raw)
        except:
            volume_ratio = 0
        
        # 市盈率 (field 39)
        try:
            pe_raw = parts[39] if len(parts) > 39 and parts[39] else "0"
            pe = float(pe_raw) if pe_raw not in ['-', '', 'N/A'] else -1
        except:
            pe = -1
        
        # 最高最低
        high = float(parts[33]) if len(parts) > 33 and parts[33] else price
        low = float(parts[34]) if len(parts) > 34 and parts[34] else price
        
        # 成交额
        try:
            amount_raw = parts[37] if len(parts) > 37 and parts[37] else "0"
            # parts[37] might be in format "price/vol/amount"
            if '/' in amount_raw:
                amount = float(amount_raw.split('/')[-1])
            else:
                amount = float(amount_raw)
        except:
            amount = 0
        
        # 日期时间
        date_time = parts[30] if len(parts) > 30 else ""
        
        return {
            "code": code,
            "name": name,
            "price": price,
            "prev_close": prev_close,
            "open": open_price,
            "rise": rise,
            "high": high,
            "low": low,
            "vol": vol,
            "turnover": turnover,
            "volume_ratio": volume_ratio,
            "pe": pe,
            "amount": amount,
            "date_time": date_time,
            "market": "SH" if code.startswith(('6', '5', '9')) else "SZ",
        }
    except Exception as e:
        return None

def calc_score(stock):
    """计算妖股综合评分(0-100)"""
    score = 50
    details = []
    
    rise = stock.get("rise", 0)
    turnover = stock.get("turnover", 0)
    vr = stock.get("volume_ratio", 0)
    price = stock.get("price", 0)
    pe = stock.get("pe", 0)
    
    # 1. 涨幅评分
    if rise >= 5.0 and rise <= 10.0:
        score += 15
        details.append("妖股起步涨幅")
    elif rise > 10.0 and rise <= 20.0:
        score += 10
        details.append("涨幅较大")
    elif rise > 20.0:
        score -= 5
        details.append("涨幅过大⚠️")
    elif rise >= 3.0:
        score += 8
        details.append("启动迹象")
    
    # 2. 换手率评分
    if turnover >= 8.0 and turnover <= 15.0:
        score += 15
        details.append("换手健康")
    elif turnover > 15.0 and turnover <= 25.0:
        score += 10
        details.append("换手偏高")
    elif turnover > 25.0:
        score -= 5
        details.append("换手过高⚠️")
    elif turnover >= 5.0:
        score += 5
        details.append("有一定换手")
    
    # 3. 量比评分
    if vr >= 2.0:
        score += 10
        details.append(f"量比放大({vr:.1f}x)")
    elif vr >= 1.5:
        score += 5
        details.append(f"量比尚可({vr:.1f}x)")
    
    # 4. 价格位置
    if 0 < price <= 10.0:
        score += 5
        details.append("低价启动")
    elif 10.0 < price <= 20.0:
        score += 2
    elif price > 50.0:
        score -= 3
        details.append("高价股⚠️")
    
    # 5. 涨停加成
    if rise >= 9.9:
        score += 10
        details.append("🔥涨停")
    elif rise >= 5.0:
        score += 5
        details.append("🔥大阳线")
    
    # 6. 市盈率
    if 0 < pe < 100:
        score += 3
        details.append("PE正常")
    elif pe <= 0:
        score -= 3
        details.append("亏损⚠️")
    elif pe >= 100:
        score -= 5
        details.append("PE过高⚠️")
    
    # 封定等级
    if score >= 80:
        level = "💥超级妖股"
    elif score >= 65:
        level = "🎯重点候选"
    elif score >= 50:
        level = "📈值得关注"
    else:
        level = "⏸️观察"
    
    return {
        "score": min(100, max(0, score)),
        "level": level,
        "details": details,
    }

def filter_and_rank(all_stocks, min_score=50):
    """筛选并排名"""
    results = []
    for code, stock in all_stocks.items():
        if stock.get("price", 0) <= 0 or stock.get("rise", 0) == 0:
            continue
        
        score_info = calc_score(stock)
        if score_info["score"] >= min_score:
            stock["yonggu_score"] = score_info["score"]
            stock["yonggu_level"] = score_info["level"]
            stock["yonggu_details"] = score_info["details"]
            results.append(stock)
    
    results.sort(key=lambda x: x["yonggu_score"], reverse=True)
    return results

def print_report(candidates, title, limit=None):
    print(f"\n{'='*75}")
    print(f"📊 {title} ({datetime.now().strftime('%H:%M:%S')})")
    print(f"{'='*75}")
    
    if not candidates:
        print("⚠️  未找到符合条件的股票")
        return
    
    n = limit or len(candidates)
    print(f"\n{'排名':<4}{'代码':<8}{'名称':<10}{'现价':<8}{'涨幅':<8}{'换手率':<8}{'量比':<6}{'评分':<6}  信号")
    print("-" * 75)
    
    for i, s in enumerate(candidates[:n], 1):
        rise_str = f"{s['rise']:.2f}%"
        turnover_str = f"{s['turnover']:.2f}%" if s['turnover'] > 0 else "-"
        vr_str = f"{s['volume_ratio']:.1f}x" if s['volume_ratio'] > 0 else "-"
        pe_str = f"PE:{s['pe']:.1f}" if s['pe'] > 0 else "亏损"
        details = " ".join(s.get("yonggu_details", [])[:3])
        
        print(f"{i:<4}{s['code']:<8}{s['name']:<10}{s['price']:<8.2f}{rise_str:<8}"
              f"{turnover_str:<8}{vr_str:<6}{s['yonggu_score']:<6}  {details}")
    
    if limit and len(candidates) > limit:
        print(f"\n... 还有 {len(candidates) - limit} 只符合条件的股票")
    
    # 统计
    levels = {}
    for s in candidates:
        lv = s.get("yonggu_level", "❓")
        levels[lv] = levels.get(lv, 0) + 1
    
    print(f"\n📈 共筛选出 {len(candidates)} 只候选 | 评级分布:", " ".join(f"{k}({v})" for k, v in sorted(levels.items(), key=lambda x: -x[1])))

def build_watchlist():
    """构建完整监控股票池"""
    all_codes = []
    for sector, codes in WATCHLIST.items():
        all_codes.extend(codes)
    
    # 去重
    seen = set()
    unique_codes = []
    for c in all_codes + CUSTOM_CODES:
        if c not in seen:
            seen.add(c)
            unique_codes.append(c)
    
    return unique_codes

def main():
    import argparse
    parser = argparse.ArgumentParser(description='妖股量化筛选系统')
    parser.add_argument('--score', type=int, default=50, help='最低评分筛选(默认50)')
    parser.add_argument('--top', type=int, default=0, help='只显示前N只(默认全部)')
    parser.add_argument('--sector', type=str, default='', help='只看指定板块')
    args = parser.parse_args()
    
    print("=" * 75)
    print("🚀 妖股量化筛选系统 v3.0")
    print("=" * 75)
    print(f"⏰ 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📚 策略依据：龙头战法 + 主升股票定义 + 超短情绪 + K线形态 + 筹码趋势")
    
    # 确定查询范围
    if args.sector and args.sector in WATCHLIST:
        sectors = [args.sector]
        print(f"📂 板块: {args.sector}")
    else:
        sectors = list(WATCHLIST.keys())
        print(f"📂 板块: 全部 ({len(sectors)}个)")
    
    # 构建查询列表
    codes_to_query = []
    for sector in sectors:
        codes_to_query.extend(WATCHLIST.get(sector, []))
    codes_to_query = list(dict.fromkeys(codes_to_query))  # 去重
    
    if args.sector:
        codes_to_query = WATCHLIST.get(args.sector, [])
    
    print(f"📋 股票总数: {len(codes_to_query)} 只")
    
    # 分批查询
    print("\n📥 正在获取行情数据...")
    all_stocks = {}
    for i in range(0, len(codes_to_query), BATCH_SIZE):
        batch = codes_to_query[i:i+BATCH_SIZE]
        stocks = get_stock_batch(batch)
        all_stocks.update(stocks)
        if i + BATCH_SIZE < len(codes_to_query):
            time.sleep(0.3)  # 避免请求过快
    
    print(f"✅ 成功获取 {len(all_stocks)} 只股票数据")
    
    if not all_stocks:
        print("❌ 未能获取数据，请检查网络")
        return
    
    # 执行筛选
    print(f"\n🔍 筛选条件：综合评分 >= {args.score}")
    candidates = filter_and_rank(all_stocks, min_score=args.score)
    
    # 输出结果
    print_report(candidates, "妖股筛选结果", limit=args.top if args.top > 0 else None)
    
    # 重点候选
    top = [c for c in candidates if c.get("yonggu_score", 0) >= 65]
    if top:
        print_report(top, "💥 重点妖股候选（评分≥65）")
    
    # 涨停股
    limit_up = [s for s in all_stocks.values() if s.get("rise", 0) >= 9.9]
    limit_up.sort(key=lambda x: x.get("turnover", 0), reverse=True)
    if limit_up:
        print_report([{
            **s,
            "yonggu_score": 100,
            "yonggu_level": "💥涨停",
            "yonggu_details": [f"换手{s['turnover']:.1f}%"]
        } for s in limit_up[:15]], "💥 今日涨停股（换手率排序）")
    
    # 飙升股（涨幅5-20%，高换手）
    strong = [s for s in candidates if 5.0 <= s.get("rise", 0) <= 20.0 and s.get("turnover", 0) >= 5.0]
    if strong:
        print_report(strong[:15], "🚀 飙升股候选（涨幅5-20% + 换手>5%）")
    
    print("\n" + "=" * 75)
    print("⚠️  风险提示：仅供学习研究，不构成投资建议！")
    print("⚠️  股市有风险，投资需谨慎！")
    print("=" * 75)

if __name__ == "__main__":
    main()
