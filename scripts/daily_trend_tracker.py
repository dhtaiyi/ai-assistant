#!/usr/bin/env python3
"""
每日趋势股跟踪器

功能：
1. 每日跟踪趋势股（均线多头/箱体突破/旗型整理/历史新高等）
2. 记录趋势演变过程
3. 识别趋势启动/加速/衰竭信号
4. 配合涨停图形库，寻找"即将涨停"前的趋势形态

趋势类型：
- 均线多头：5/10/20日线从上到下依次排列
- 箱体突破：震荡整理后向上突破
- 旗型整理：振幅逐渐收窄的收敛形态
- 缩量回踩：回调缩量，在均线获得支撑
- 历史新高：突破历史最高价
- 加速上涨：成交量放大+涨幅扩大
"""

import requests
import json
import os
from datetime import datetime, timedelta

BASE = os.path.expanduser("~/.openclaw/workspace/stock-patterns")
TREND_DIR = f"{BASE}/trend_history"
os.makedirs(TREND_DIR, exist_ok=True)

# ==================== 趋势股池（每日收盘后手动更新）====================
# 格式：代码 -> {name, close_yesterday, trend_type, resist_level, sector, note}
TREND_POOL = {
    # ===== 上升趋势（均线多头/历史新高）=====
    "sz300308": {"name": "中际旭创", "close_y": 680.00, "trend": "均线多头+历史新高", "resist": 700.00, "sector": "光模块", "note": "突破700元历史新高，光模块龙头"},
    "sz002049": {"name": "紫光国微", "close_y": 0, "trend": "均线多头", "resist": 0, "sector": "AI芯片", "note": "AI主线，历史新高"},
    
    # ===== 箱体/旗型整理，即将突破 =====
    "sz002281": {"name": "光迅科技", "close_y": 98.20, "trend": "旗型整理", "resist": 108.09, "sector": "光模块+AI", "note": "首板后横盘3天，关注突破108.09"},
    
    # ===== 趋势启动/突破 =====
    "sz002384": {"name": "东山精密", "close_y": 131.90, "trend": "加速上涨", "resist": 131.90, "sector": "算力+消费电子", "note": "3连板加速，主线龙头"},
    
    # ===== 趋势股（待观察）=====
    "sh600507": {"name": "江苏租赁", "close_y": 5.80, "trend": "均线多头", "resist": 0, "sector": "金融", "note": "缓慢上升趋势"},
    "sz002555": {"name": "三七互娱", "close_y": 28.50, "trend": "箱体突破", "resist": 30.00, "sector": "游戏+AI", "note": "突破整理区间，AI应用"},
    "sz300124": {"name": "汇川技术", "close_y": 0, "trend": "均线多头", "resist": 0, "sector": "机器人", "note": "机器人龙头，均线多头"},
}

TREND_TYPES = {
    "均线多头": {"信号": "📈中长期上升趋势，顺势而为", "操作": "缩量回踩均线买入，不追高"},
    "均线多头+历史新高": {"信号": "🚀空间打开，无套牢盘压力", "操作": "突破后缩量回踩买入"},
    "箱体突破": {"信号": "🎯盘整结束，新趋势启动", "操作": "突破回踩确认买入"},
    "旗型整理": {"信号": "⏳主力控盘，即将选择方向", "操作": "向上突破跟进，向下破位放弃"},
    "缩量回踩": {"信号": "🛡️主力洗盘，筹码稳定", "操作": "均线附近低吸"},
    "加速上涨": {"信号": "🔥资金加速，主升浪", "操作": "持有，跌破5日线离场"},
    "高位震荡": {"信号": "⚠️高位分歧，可能是出货", "操作": "减仓，跌破20日线清仓"},
}

def get_realtime(codes):
    if not codes:
        return {}
    url = "http://qt.gtimg.cn/q=" + ",".join(codes)
    r = requests.get(url, timeout=10)
    result = {}
    for line in r.text.strip().split("\n"):
        if "~" not in line: continue
        parts = line.split("~")
        if len(parts) < 50: continue
        code = line.split("=")[0].replace("v_", "")
        try:
            result[code] = {
                "name": parts[1],
                "price": float(parts[3]) if parts[3] else 0,
                "close_y": float(parts[4]) if parts[4] else 0,
                "open": float(parts[5]) if parts[5] else 0,
                "high": float(parts[33]) if parts[33] else 0,
                "low": float(parts[34]) if parts[34] else 0,
                "pct": float(parts[32]) if parts[32] else 0,
                "vol": float(parts[36]) if parts[36] else 0,
                "circ_mv": float(parts[45]) if parts[45] else 0,
            }
        except: pass
    return result

def judge_status(pct, trend, resist, price):
    """判断趋势状态"""
    if pct >= 9.9:
        return "🔴涨停突破！", "🟢强烈买入"
    elif pct >= 5:
        return "🚀强势加速", "✅继续持有"
    elif pct >= 2:
        return "📈稳步上涨", "✅持筹"
    elif pct >= 0:
        return "📍小幅波动", "🟡观察"
    elif pct >= -3:
        return "📉小幅回调", "🟡关注是否破均线"
    else:
        return "🔴大幅下跌", "⚠️警惕离场"

def detect_breakout(price, resist, pct):
    """检测是否突破"""
    if resist <= 0:
        return ""
    if price > resist:
        return "✅突破关键位！"
    elif price > resist * 0.97:
        return "⚠️接近突破"
    else:
        return ""

def daily_trend_report(date_str):
    print(f"📈 每日趋势股跟踪 | {date_str}")
    print("=" * 75)
    
    # 加载历史数据
    history_path = f"{TREND_DIR}/history.json"
    if os.path.exists(history_path):
        with open(history_path) as f:
            history = json.load(f)
    else:
        history = {}
    
    codes = list(TREND_POOL.keys())
    data = get_realtime(codes)
    
    # 当日数据
    today_data = {}
    for code, pool_info in TREND_POOL.items():
        real = data.get(code, {})
        price = real.get("price", pool_info["close_y"]) or pool_info["close_y"]
        pct = real.get("pct", 0) or 0
        close_y = pool_info["close_y"] or price
        circ = real.get("circ_mv", 0) or 0
        high = real.get("high", 0)
        low = real.get("low", 0)
        resist = pool_info["resist"]
        
        amp = (high - low) / close_y * 100 if close_y > 0 else 0
        status, action = judge_status(pct, pool_info["trend"], resist, price)
        breakout = detect_breakout(price, resist, pct)
        
        # MACD信号检查
        candles = get_kline_tencent(code, 60)
        macd_info = check_macd_signal(candles)
        
        today_data[code] = {
            "name": pool_info["name"],
            "code": code,
            "price": round(price, 2),
            "close_y": close_y,
            "pct": round(pct, 2),
            "circ_mv": round(circ, 1),
            "amplitude": round(amp, 2),
            "trend": pool_info["trend"],
            "resist": resist,
            "sector": pool_info["sector"],
            "note": pool_info["note"],
            "status": status,
            "breakout": breakout,
            "action": action,
            "macd_signal": macd_info['signal'],
            "macd_hist": macd_info['hist_today'],
        }
        
        # 更新历史
        if code not in history:
            history[code] = {"name": pool_info["name"], "history": []}
        history[code]["history"].append({
            "date": date_str,
            "price": round(price, 2),
            "pct": round(pct, 2),
            "trend": pool_info["trend"],
        })
    
    # 保存历史
    with open(history_path, "w") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    
    # 输出报告
    print(f"\n{'股票':<10} {'收盘':>7} {'涨幅':>8} {'趋势类型':<18} {'MACD':>12} {'状态':<14} {'操作建议'}")
    print("-" * 90)
    
    # 按涨幅排序
    sorted_data = sorted(today_data.values(), key=lambda x: x["pct"], reverse=True)
    
    hot_trends = []
    for d in sorted_data:
        # MACD信号描述
        macd_sig = d.get('macd_signal', 'none')
        macd_emoji = {
            'green_appear': '🟢出现',
            'green_shortening': '⚠️缩短',
            'green_growing': '🟢放大',
            'red_shortening': '🟡缩窄',
            'red_appear': '🔴出现',
            'dif_cross_zero': '🟢零轴',
            'none': '⚪中性'
        }.get(macd_sig, '⚪中性')
        macd_str = f"{macd_emoji}({d.get('macd_hist', 0):+.2f})"
        
        trend_desc = TREND_TYPES.get(d["trend"], {}).get("信号", "")
        action = d["action"]
        resist_str = f"{d['resist']:.2f}" if d["resist"] > 0 else "-"
        
        print(f"{d['name']:<10} {d['price']:>6.2f} {d['pct']:>+7.1f}% {d['trend']:<18} {macd_str:>14} {d['status']:<14} {action}")
        if d["breakout"] or d["pct"] >= 5:
            hot_trends.append(d)
    
    print()
    print("=" * 75)
    print("🎯 趋势股重点关注")
    print("-" * 75)
    
    if hot_trends:
        for d in hot_trends:
            macd_sig = d.get('macd_signal', 'none')
            macd_desc = {
                'green_appear': '✅绿柱刚出现(动能转强)',
                'green_shortening': '⚠️绿柱缩短(动能减弱)',
                'green_growing': '✅绿柱放大(动能加强)',
                'red_shortening': '🟡红柱缩窄(接近零)',
                'red_appear': '⚠️红柱出现(动能转弱)',
                'dif_cross_zero': '✅DIF穿零轴(强势)',
                'none': '中性'
            }.get(macd_sig, '中性')
            print(f"\n👉 {d['name']}({d['code'][-6:]})")
            print(f"   今日: {d['price']}元 {d['pct']:+.1f}% | {d['trend']}")
            print(f"   流通市值: {d['circ_mv']:.0f}亿 | 板块: {d['sector']}")
            print(f"   MACD: {macd_desc}")
            print(f"   操作: {d['action']}")
            print(f"   备注: {d['note']}")
    
    print()
    print("=" * 75)
    print("📊 趋势演变追踪（近5日）")
    print("-" * 75)
    
    for code, hist_data in list(history.items())[-5:]:
        name = hist_data["name"]
        hist = hist_data["history"][-5:] if hist_data["history"] else []
        if hist:
            pct_str = " ".join([f"{h['price']}({h['pct']:+.1f}%)" for h in hist])
            print(f"  {name}: {pct_str}")
    
    print()
    print("=" * 75)
    print("📚 趋势图形分类说明")
    print("-" * 75)
    for name, info in TREND_TYPES.items():
        print(f"  【{name}】{info['信号']} → {info['操作']}")
    
    # 保存今日趋势数据
    trend_data = {
        "date": date_str,
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "stocks": today_data,
    }
    with open(f"{TREND_DIR}/{date_str}.json", "w") as f:
        json.dump(trend_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 趋势数据已保存: {TREND_DIR}/{date_str}.json")
    print(f"⚠️ 投资有风险，仅供参考～", datetime.now().strftime("%H:%M"))


# ==================== MACD Helper Functions ====================

def get_kline_tencent(code, count=60):
    """获取日线前复权K线数据"""
    url = f'https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_dayhfq&param={code},day,2026-01-01,2026-04-20,{count},qfq'
    try:
        r = requests.get(url, timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        text = r.text
        if '=' in text:
            text = text.split('=', 1)[1]
        data = json.loads(text)
        key = list(data['data'].keys())[0]
        return data['data'][key]['qfqday']
    except:
        return []

def calc_ema(prices, period):
    ema = []
    k = 2 / (period + 1)
    for i, p in enumerate(prices):
        if i == 0:
            ema.append(p)
        else:
            ema.append(p * k + ema[-1] * (1 - k))
    return ema

def calc_macd(prices):
    """计算MACD"""
    ema12 = calc_ema(prices, 12)
    ema26 = calc_ema(prices, 26)
    dif = [e12 - e26 for e12, e26 in zip(ema12, ema26)]
    dea = calc_ema(dif, 9)
    macd_hist = [(d - d9) * 2 for d, d9 in zip(dif, dea)]
    return dif, dea, macd_hist

def check_macd_signal(candles):
    """
    检查MACD信号
    返回: {'signal': 'green_appear'|'green_shortening'|'red_shortening'|'none',
          'hist_today': float, 'hist_yesterday': float, 'dif_today': float}
    """
    if len(candles) < 30:
        return {'signal': 'none', 'hist_today': 0, 'hist_yesterday': 0, 'dif_today': 0}
    
    closes = [float(c[2]) for c in candles]
    dif, dea, macd_hist = calc_macd(closes)
    
    hist_today = macd_hist[-1]
    hist_yesterday = macd_hist[-2]
    hist_2days_ago = macd_hist[-3]
    dif_today = dif[-1]
    
    signal = 'none'
    if hist_today > 0 and hist_yesterday <= 0:
        signal = 'green_appear'  # 绿柱刚出现（由负转正）
    elif hist_today > 0 and hist_yesterday > 0 and hist_today < hist_yesterday:
        signal = 'green_shortening'  # 绿柱缩短（但仍是正的）
    elif hist_today > 0 and hist_yesterday > 0 and hist_today >= hist_yesterday:
        signal = 'green_growing'  # 绿柱放大（动能加强）
    elif hist_today < 0 and hist_yesterday < 0 and abs(hist_today) < abs(hist_yesterday):
        signal = 'red_shortening'  # 红柱缩短（接近零）
    elif hist_today < 0 and hist_yesterday <= 0 and hist_today > hist_yesterday:
        signal = 'red_appear'  # 红柱刚出现（由正转负）
    elif dif_today > 0 and dif[-2] <= 0:
        signal = 'dif_cross_zero'  # DIF穿越零轴
    
    return {
        'signal': signal,
        'hist_today': round(hist_today, 3),
        'hist_yesterday': round(hist_yesterday, 3),
        'dif_today': round(dif_today, 3)
    }



if __name__ == "__main__":
    daily_trend_report(datetime.now().strftime("%Y%m%d"))
