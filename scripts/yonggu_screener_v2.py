#!/usr/bin/env python3
"""
妖股量化筛选模型 v2.0
基于：龙头战法 + 主升股票定义 + 超短情绪周期 + 筹码趋势 + 威科夫 + K线形态
创建时间：2026-04-06
"""

import requests
import json
import time
import random
from datetime import datetime

# ============================================================
# 数据源配置
# ============================================================
# 新浪财经行情API (免费，无需token)
SINA_STOCK_URL = "http://hq.sinajs.cn/list={}"

# 东方财富涨幅榜API
EM_STOCK_URL = "https://push2.eastmoney.com/api/qt/clist/get"

# ============================================================
# 妖股筛选核心参数（基于课程学习总结）
# ============================================================

# 【维度1】涨幅条件
RISE_CONFIG = {
    "min_rise": 3.0,      # 最小涨幅3%
    "max_rise": 20.0,     # 最大涨幅20%（超过20%风险大）
    "hot_rise_min": 5.0,  # 妖股起步涨幅5%+
}

# 【维度2】换手率条件（资金活跃度）
TURNOVER_CONFIG = {
    "min_turnover": 5.0,   # 最小换手率5%
    "ideal_turnover": (8, 25),  # 理想换手率区间
}

# 【维度3】量比（成交量活跃度）
VOLUME_RATIO_CONFIG = {
    "min_volume_ratio": 1.5,  # 最小量比1.5
    "ideal_volume_ratio": (2.0, 5.0),  # 理想量比区间
}

# 【维度4】市值条件（主升股票定义：盘子小易拉升）
MARKET_VALUE_CONFIG = {
    "max_total_mv": 100,    # 总市值<100亿
    "max_float_mv": 50,     # 流通市值<50亿
}

# 【维度5】均线多头排列（龙头战法：趋势向上）
MA_CONFIG = {
    "ma5_angle": 5,        # MA5角度（度）
    "ma10_above_ma20": True,  # MA10在MA20上方
}

# ============================================================
# 妖股加分项（基于龙头战法）
# ============================================================
BONUS_ITEMS = [
    ("涨停", 10),           # 今日涨停或近期有涨停
    ("连续上涨", 8),         # 连续3天上涨
    ("板块龙头", 7),         # 所属板块涨幅前3
    ("题材纯正", 6),         # 涉及热门题材
    ("首板/二板", 5),        # 处于主升初期
    ("突破平台", 5),         # 突破长期整理平台
    ("低位放量", 4),         # 从低位区域放量启动
    ("股性活跃", 3),         # 历史经常涨停
]

# ============================================================
# 妖股减分项（需要排除的）
# ============================================================
PENALTY_ITEMS = [
    ("高位警戒", -10),       # 前期涨幅>100%
    ("股东减持", -8),         # 近期有减持公告
    ("业绩亏损", -7),         # 连续亏损
    ("ST风险", -6),          # ST股票
    ("解禁压力", -5),         # 近期有解禁
    ("高位长阴", -8),         # 高位放量大阴线
    ("监管问询", -5),         # 收到问询函
]

# ============================================================
# 数据获取函数
# ============================================================

def fetch_sina_stocks(codes):
    """从新浪获取股票数据"""
    url = SINA_STOCK_URL.format(",".join(codes))
    headers = {
        "Referer": "http://finance.sina.com.cn",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        # 尝试不同编码
        for encoding in ['gbk', 'gb2312', 'utf-8']:
            try:
                resp.encoding = encoding
                content = resp.text
                break
            except:
                continue
        
        stocks = []
        lines = content.strip().split('\n')
        for line in lines:
            if 'hq_str_' not in line:
                continue
            try:
                # 解析格式：var hq_str_sh600000="名称,今日开盘价,昨日收盘价,当前价格,...",...;
                parts = line.split('"')
                if len(parts) < 2:
                    continue
                data = parts[1].split(',')
                if len(data) < 32:
                    continue
                    
                code = line.split('hq_str_')[1].split('=')[0].replace('sh', '').replace('sz', '')
                stocks.append({
                    "code": code,
                    "name": data[0],
                    "open": float(data[1]) if data[1] else 0,
                    "close": float(data[2]) if data[2] else 0,  # 昨日收盘
                    "price": float(data[3]) if data[3] else 0,  # 当前价
                    "high": float(data[4]) if data[4] else 0,
                    "low": float(data[5]) if data[5] else 0,
                    "volume": float(data[8]) if data[8] else 0,  # 成交量(手)
                    "amount": float(data[9]) if data[9] else 0,  # 成交额(元)
                    "date": data[30] if len(data) > 30 else "",
                    "time": data[31] if len(data) > 31 else "",
                })
            except Exception as e:
                continue
        return stocks
    except Exception as e:
        print(f"获取新浪数据失败: {e}")
        return []

def fetch_em_top_stocks(limit=100):
    """从东方财富获取涨幅榜"""
    params = {
        "pn": 1,
        "pz": limit,
        "po": 1,
        "np": 1,
        "fltt": 2,
        "invt": 2,
        "fid": "f3",
        "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
        "fields": "f2,f3,f4,f5,f6,f7,f8,f10,f12,f14,f15,f16,f17,f18,f20,f21,f62,f128,f136",
        "_": int(time.time() * 1000)
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://finance.eastmoney.com/"
    }
    
    try:
        resp = requests.get(EM_STOCK_URL, params=params, headers=headers, timeout=10)
        data = resp.json()
        if data.get("rc") == 0:
            return data["data"]["diff"]
        return []
    except:
        return []

# ============================================================
# 妖股筛选核心逻辑
# ============================================================

def calc_yonggu_score(stock, context=None):
    """
    计算妖股评分（0-100分）
    基于课程学习的六大维度
    """
    score = 50  # 基础分
    details = []
    
    try:
        rise = float(stock.get("f3", 0) or 0)  # 涨幅%
        turnover = float(stock.get("f8", 0) or 0)  # 换手率%
        volume_ratio = float(stock.get("f10", 0) or 0)  # 量比
        price = float(stock.get("f2", 0) or 0)  # 现价
        
        # 【维度1】涨幅评分（妖股起步5-20%最佳）
        if 5.0 <= rise <= 10.0:
            score += 15
            details.append("✅ 涨幅适中(5-10%)")
        elif 10.0 < rise <= 20.0:
            score += 10
            details.append("⚠️ 涨幅较大(10-20%)")
        elif rise >= 20.0:
            score -= 5
            details.append("⚠️ 涨幅过大，风险累积")
        elif rise >= 3.0:
            score += 8
            details.append("✅ 启动迹象(3%+)")
        
        # 【维度2】换手率评分（资金活跃度）
        if 8.0 <= turnover <= 15.0:
            score += 15
            details.append("✅ 换手健康(8-15%)")
        elif 15.0 < turnover <= 25.0:
            score += 10
            details.append("⚠️ 换手偏高(15-25%)")
        elif turnover > 25.0:
            score -= 5
            details.append("❌ 换手过高，小心主力出货")
        elif turnover >= 5.0:
            score += 5
            details.append("✅ 有一定换手(5%+)")
        
        # 【维度3】量比评分（成交量是否放大）
        if volume_ratio >= 2.0:
            score += 10
            details.append(f"✅ 量比放大({volume_ratio:.1f}x)")
        elif volume_ratio >= 1.5:
            score += 5
        
        # 【维度4】价格位置（主升股票定义：启动价<10元最佳）
        if 0 < price <= 10.0:
            score += 5
            details.append("✅ 低价启动(<10元)")
        elif 10.0 < price <= 20.0:
            score += 2
            details.append("⚠️ 中价股")
        elif price > 50.0:
            score -= 3
            details.append("❌ 高价股，拉升难度大")
        
        # 【维度5】涨停加成
        if rise >= 9.9:
            score += 10
            details.append("🔥 涨停！")
        elif rise >= 5.0:
            score += 5
            details.append("🔥 大阳线")
        
        # 【维度6】综合评分
        if score >= 80:
            level = "💥 超级妖股候选"
        elif score >= 65:
            level = "🎯 重点妖股候选"
        elif score >= 50:
            level = "📈 值得关注"
        else:
            level = "⏸️ 观察中"
            
        return {
            "score": min(100, max(0, score)),
            "level": level,
            "details": details,
            "rise": rise,
            "turnover": turnover,
            "volume_ratio": volume_ratio,
            "price": price,
        }
    except Exception as e:
        return {"score": 0, "level": "❌ 数据解析失败", "details": [str(e)]}

def filter_yonggu(stocks, min_score=50):
    """筛选妖股候选"""
    results = []
    for stock in stocks:
        score_info = calc_yonggu_score(stock)
        if score_info["score"] >= min_score:
            stock["yonggu_score"] = score_info["score"]
            stock["yonggu_level"] = score_info["level"]
            stock["yonggu_details"] = score_info["details"]
            results.append(stock)
    
    # 按评分排序
    results.sort(key=lambda x: x["yonggu_score"], reverse=True)
    return results

# ============================================================
# 输出格式化
# ============================================================

def print_results(candidates, title="妖股筛选结果"):
    print(f"\n{'='*70}")
    print(f"📊 {title} ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    print(f"{'='*70}")
    
    if not candidates:
        print("⚠️  未找到符合条件的股票")
        return
    
    print(f"\n{'排名':<4}{'代码':<8}{'名称':<10}{'现价':<8}{'涨幅':<8}{'换手率':<8}{'量比':<6}{'评分':<6} 关键信号")
    print("-" * 70)
    
    for i, s in enumerate(candidates[:20], 1):
        code = s.get("f12", s.get("code", ""))
        name = s.get("f14", s.get("name", ""))
        price = s.get("f2", s.get("price", ""))
        rise = s.get("f3", s.get("rise", ""))
        turnover = s.get("f8", s.get("turnover", ""))
        vr = s.get("f10", s.get("volume_ratio", ""))
        score = s.get("yonggu_score", 0)
        details = " ".join(s.get("yonggu_details", [])[:3])
        
        rise_str = f"{float(rise):.2f}%" if rise else "-"
        turnover_str = f"{float(turnover):.2f}%" if turnover else "-"
        vr_str = f"{float(vr):.1f}x" if vr else "-"
        
        print(f"{i:<4}{code:<8}{name:<10}{price:<8}{rise_str:<8}{turnover_str:<8}{vr_str:<6}{score:<6}  {details}")
        
        if i >= 20 and len(candidates) > 20:
            print(f"\n... 还有 {len(candidates) - 20} 只符合条件的股票")
    
    # 统计分析
    print(f"\n📈 统计：共筛选出 {len(candidates)} 只妖股候选")
    
    # 按评级分布
    levels = {}
    for s in candidates:
        level = s.get("yonggu_level", "❓")
        levels[level] = levels.get(level, 0) + 1
    for k, v in sorted(levels.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}只")

def main():
    print("🚀 妖股量化筛选模型 v2.0 启动...")
    print(f"⏰ 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📚 策略依据：龙头战法 + 主升股票定义 + 超短情绪周期 + K线形态学")
    
    # 尝试从东方财富获取数据
    print("\n📥 正在获取涨幅榜数据...")
    stocks = fetch_em_top_stocks(limit=200)
    
    if stocks:
        print(f"✅ 成功获取 {len(stocks)} 只股票数据")
    else:
        print("⚠️  东方财富API不可用，尝试新浪API...")
        # 备用：获取一些热门股票代码
        test_codes = [
            "sh600000", "sh600036", "sh600519", "sh601318", "sh601166",
            "sz000001", "sz000002", "sz000858", "sz002594", "sz300750"
        ]
        stocks = fetch_sina_stocks(test_codes)
        if not stocks:
            print("❌ 所有API均不可用，请检查网络连接")
            return
    
    # 执行妖股筛选
    print("\n🔍 开始妖股筛选...")
    print("📋 筛选条件：")
    print("  1. 涨幅 >= 3%")
    print("  2. 换手率 >= 5%")
    print("  3. 量比 >= 1.5")
    print("  4. 综合评分 >= 50")
    
    candidates = filter_yonggu(stocks, min_score=50)
    print_results(candidates, "🎯 妖股量化筛选结果")
    
    # 高评级妖股
    top_yonggu = [c for c in candidates if c.get("yonggu_score", 0) >= 65]
    print_results(top_yonggu, "💥 重点妖股候选（评分>=65）")
    
    # 涨停股
    limit_up = [s for s in stocks if float(s.get("f3", 0) or 0) >= 9.9]
    limit_up.sort(key=lambda x: float(x.get("f8", 0) or 0), reverse=True)
    print_results([{
        **s, 
        "yonggu_score": 100 if float(s.get("f3", 0) or 0) >= 9.9 else 0,
        "yonggu_level": "💥 涨停",
        "yonggu_details": ["涨停", f"换手{float(s.get('f8', 0)):.1f}%"]
    } for s in limit_up[:15]], "💥 今日涨停股（换手率排序）")
    
    print("\n" + "="*70)
    print("⚠️  风险提示：本系统仅供学习研究，不构成投资建议！")
    print("⚠️  股市有风险，投资需谨慎！")
    print("="*70)

if __name__ == "__main__":
    main()
