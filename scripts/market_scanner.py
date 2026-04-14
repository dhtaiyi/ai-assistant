#!/usr/bin/env python3
"""
每日市场扫描工具 v2.1
使用新浪API获取实时数据
使用方法：python3 market_scanner.py
"""

import requests
import time
from datetime import datetime

# ========== 配置 ==========
SINA_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://finance.sina.com.cn"
}

def get_zt_stocks():
    """获取涨停股（涨幅>=9.9%，成交额排序）"""
    url = "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeDataSimple"
    params = {
        "page": 1, "num": 100,
        "sort": "changepercent", "asc": 0,
        "node": "hs_a", "symbol": "", "_s_r_a": "page"
    }
    try:
        r = requests.get(url, params=params, headers=SINA_HEADERS, timeout=10)
        data = r.json()
        zt = [s for s in data if float(s.get("changepercent", 0)) >= 9.9]
        # 过滤ST
        zt_filtered = [s for s in zt if not s.get("name", "").startswith("ST") and not s.get("name", "").startswith("*ST")]
        return zt_filtered
    except Exception as e:
        print(f"获取涨停失败: {e}")
        return []

def get_dt_stocks():
    """获取跌停股（跌幅<=-9.9%，成交额排序）"""
    url = "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeDataSimple"
    params = {
        "page": 1, "num": 100,
        "sort": "changepercent", "asc": 1,
        "node": "hs_a", "symbol": "", "_s_r_a": "page"
    }
    try:
        r = requests.get(url, params=params, headers=SINA_HEADERS, timeout=10)
        data = r.json()
        dt = [s for s in data if float(s.get("changepercent", 0)) <= -9.9]
        return dt
    except Exception as e:
        print(f"获取跌停失败: {e}")
        return []

def get_hot_sector():
    """获取热门板块（成交额前20中的涨停股板块统计）"""
    url = "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeDataSimple"
    params = {
        "page": 1, "num": 100,
        "sort": "amount", "asc": 0,
        "node": "hs_a", "symbol": "", "_s_r_a": "page"
    }
    try:
        r = requests.get(url, params=params, headers=SINA_HEADERS, timeout=10)
        data = r.json()
        # 涨幅前20的股票
        hot = sorted(data, key=lambda x: float(x.get("changepercent", 0)), reverse=True)[:20]
        return hot
    except Exception as e:
        print(f"获取热门股失败: {e}")
        return []

def get_index_data():
    """获取主要指数"""
    indices = {
        "sh000001": "上证指数",
        "sz399001": "深证成指",
        "sz399006": "创业板指",
        "sh000300": "沪深300",
    }
    url = "http://qt.gtimg.cn/q=" + ",".join(indices.keys())
    try:
        r = requests.get(url, timeout=10)
        result = {}
        for line in r.text.strip().split("\n"):
            if "=" not in line:
                continue
            code = line.split("=")[0].replace("v_", "")
            parts = line.split("~")
            if len(parts) < 33:
                continue
            name = indices.get(code, code)
            result[name] = {
                "现价": float(parts[3]) if parts[3] else 0,
                "涨跌幅": float(parts[32]) if parts[32] else 0,
            }
        return result
    except Exception as e:
        print(f"获取指数失败: {e}")
        return {}

def analyze():
    """综合分析"""
    print("\n" + "="*65)
    print("📊 每日市场扫描报告")
    print(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*65)
    
    print("\n🔄 获取数据中...")
    indices = get_index_data()
    zt_list = get_zt_stocks()
    dt_list = get_dt_stocks()
    
    # 指数
    print("\n【一、指数表现】")
    for name, info in indices.items():
        pct = info.get("涨跌幅", 0)
        arrow = "🔴" if pct < 0 else "🟢" if pct > 0 else "⚪"
        print(f"  {arrow} {name}: {info.get('现价', 0):.2f} ({pct:+.2f}%)")
    
    # 涨停
    print(f"\n【二、涨停分析 ({len(zt_list)}家，非ST)】")
    if zt_list:
        top10 = sorted(zt_list, key=lambda x: float(x.get("amount", 0)), reverse=True)[:10]
        for i, s in enumerate(top10, 1):
            amt = float(s.get("amount", 0)) / 1e8
            print(f"  {i}. {s['name']}({s['symbol']}) +{s['changepercent']}% 额:{amt:.1f}亿")
    
    # 跌停
    print(f"\n【三、跌停分析 ({len(dt_list)}家)】")
    if dt_list:
        top5 = sorted(dt_list, key=lambda x: float(x.get("amount", 0)), reverse=True)[:5]
        for i, s in enumerate(top5, 1):
            amt = float(s.get("amount", 0)) / 1e8
            print(f"  {i}. {s['name']}({s['symbol']}) {s['changepercent']}% 额:{amt:.1f}亿")
    else:
        print("  暂无跌停股（数据可能在收盘后更新）")
    
    # 情绪判断
    print("\n【四、情绪周期五维判断】")
    zt_count = len(zt_list)
    dt_count = len(dt_list)
    
    print(f"  ① 涨停数: {zt_count} 家", end="")
    if zt_count >= 50:
        print(" ✅ (强势)")
    elif zt_count >= 30:
        print(" ⚠️ (一般)")
    else:
        print(" ❌ (偏弱)")
    
    print(f"  ② 跌停数: {dt_count} 家", end="")
    if dt_count == 0:
        print(" ✅ (无跌停)")
    elif dt_count <= 10:
        print(" ⚠️ (少量)")
    else:
        print(" ❌ (过多)")
    
    # 综合判断
    print("\n【五、综合判断】")
    if zt_count >= 50 and dt_count <= 5:
        cycle = "🌟 上升期"
        action = "重仓龙头，积极做多（仓位60-80%）"
        pattern = "首板战法 + 弱转强"
    elif zt_count >= 30 and dt_count <= 15:
        cycle = "⚠️ 分化期"
        action = "轻仓龙头+低位首板，不追高（仓位30-40%）"
        pattern = "低位首板 + 回调低吸"
    elif zt_count >= 20 and dt_count <= 20:
        cycle = "⚡ 混沌期"
        action = "快进快出，不恋战（仓位10-20%）"
        pattern = "首板快出"
    else:
        cycle = "❄️ 退潮期"
        action = "空仓休息，等待机会（仓位0-10%）"
        pattern = "绝对不操作"
    
    print(f"  当前周期: {cycle}")
    print(f"  操作策略: {action}")
    print(f"  推荐模式: {pattern}")
    
    # 选股方向
    print("\n【六、选股方向建议】")
    if zt_list:
        # 找出成交最大的涨停股
        biggest = sorted(zt_list, key=lambda x: float(x.get("amount", 0)), reverse=True)[0]
        amt = float(biggest.get("amount", 0)) / 1e8
        print(f"  今日最强: {biggest['name']} 成交{amt:.1f}亿")
        
        # 按成交额前5
        top5 = sorted(zt_list, key=lambda x: float(x.get("amount", 0)), reverse=True)[:5]
        print(f"  重点关注: {', '.join([s['name'] for s in top5])}")
    
    print("\n" + "="*65)
    print("⚠️  本报告仅供参考，不构成投资建议。股市有风险！")
    print("="*65 + "\n")
    
    return {
        "zt_count": zt_count,
        "dt_count": dt_count,
        "indices": indices
    }

if __name__ == "__main__":
    analyze()
