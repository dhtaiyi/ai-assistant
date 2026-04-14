#!/usr/bin/env python3
"""
东方财富妖股筛选器
基于东方财富公开API，筛选潜在妖股
"""

import requests
import json
import time
from datetime import datetime

# 东方财富API基础地址
BASE_URL = "https://push2.eastmoney.com/api/qt/clist/get"

def get_top_stocks(limit=50, sort_by="f3"):
    """
    获取涨幅榜股票
    sort_by: f3=涨幅, f3=-为跌幅
    """
    params = {
        "pn": 1,
        "pz": limit,
        "po": 1,  # 1=降序
        "np": 1,
        "fltt": 2,
        "invt": 2,
        "fid": sort_by,
        "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",  # 沪深A股
        "fields": "f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152",
        "_": int(time.time() * 1000)
    }
    
    try:
        resp = requests.get(BASE_URL, params=params, timeout=10)
        data = resp.json()
        if data.get("rc") == 0:
            return data["data"]["diff"]
        return []
    except Exception as e:
        print(f"获取数据失败: {e}")
        return []

def get_stock_detail(ts_code):
    """获取单个股票详细信息"""
    # 东方财富股票详情API
    url = f"https://push2.eastmoney.com/api/qt/stock/get"
    # 判断市场
    if ts_code.startswith("6"):
        secid = f"1.{ts_code}"
    else:
        secid = f"0.{ts_code}"
    
    params = {
        "secid": secid,
        "fields": "f57,f58,f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f116,f117,f128,f136",
        "_": int(time.time() * 1000)
    }
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        return resp.json()
    except:
        return {}

def filter_yonggu(top_stocks, min_rise=5.0, max_rise=20.0, min_turnover=5.0):
    """
    妖股筛选条件
    min_rise: 最小涨幅(%)
    max_rise: 最大涨幅(%)
    min_turnover: 最小换手率(%)
    """
    candidates = []
    
    for stock in top_stocks:
        try:
            rise = float(stock.get("f3", 0) or 0)  # 涨幅%
            turnover = float(stock.get("f8", 0) or 0)  # 换手率%
            volume_ratio = float(stock.get("f10", 0) or 0)  # 量比
            price = float(stock.get("f2", 0) or 0)  # 现价
            
            # 基础筛选：涨幅5%-20%，换手率>5%
            if min_rise <= rise <= max_rise and turnover >= min_turnover and price > 0:
                candidates.append({
                    "代码": stock.get("f12", ""),
                    "名称": stock.get("f14", ""),
                    "现价": price,
                    "涨幅": f"{rise:.2f}%",
                    "涨跌额": stock.get("f4", ""),
                    "换手率": f"{turnover:.2f}%",
                    "量比": volume_ratio,
                    "成交额": stock.get("f6", ""),
                    "振幅": f"{float(stock.get('f7', 0) or 0):.2f}%",
                    "流通股": stock.get("f20", ""),
                    "流通市值": stock.get("f21", ""),
                    "市盈率": stock.get("f9", ""),
                })
        except:
            continue
    
    return candidates

def filter_continuously_rising(top_stocks, min_rise=3.0, min_continue_days=3):
    """
    筛选连续上涨股票（基于当日涨幅和换手率）
    min_continue_days: 虚拟连续天数（简化版，实际需要历史数据）
    """
    candidates = []
    for stock in top_stocks:
        try:
            rise = float(stock.get("f3", 0) or 0)
            turnover = float(stock.get("f8", 0) or 0)
            volume_ratio = float(stock.get("f10", 0) or 0)
            price = float(stock.get("f2", 0) or 0)
            
            if rise >= min_rise and turnover >= 3.0 and volume_ratio >= 1.5 and price > 0:
                candidates.append({
                    "代码": stock.get("f12", ""),
                    "名称": stock.get("f14", ""),
                    "现价": price,
                    "涨幅": f"{rise:.2f}%",
                    "换手率": f"{turnover:.2f}%",
                    "量比": volume_ratio,
                    "成交额": stock.get("f6", ""),
                    "综合评分": round(rise * 0.4 + turnover * 0.3 + volume_ratio * 10 * 0.3, 2),
                })
        except:
            continue
    
    # 按综合评分排序
    candidates.sort(key=lambda x: x["综合评分"], reverse=True)
    return candidates

def print_stocks(stocks, title="筛选结果"):
    print(f"\n{'='*60}")
    print(f"📊 {title} ({datetime.now().strftime('%H:%M:%S')})")
    print(f"{'='*60}")
    
    if not stocks:
        print("未找到符合条件的股票")
        return
    
    print(f"{'代码':<8}{'名称':<10}{'现价':<8}{'涨幅':<8}{'换手率':<8}{'量比':<6}{'综合评分':<8}")
    print("-" * 60)
    
    for i, s in enumerate(stocks[:20], 1):
        print(f"{s.get('代码', ''):<8}{s.get('名称', ''):<10}{s.get('现价', ''):<8}{s.get('涨幅', ''):<8}{s.get('换手率', ''):<8}{s.get('量比', ''):<6}{s.get('综合评分', ''):<8}")
        if i >= 20:
            print(f"... 还有 {len(stocks) - 20} 只")
            break

def main():
    print("🚀 东方财富妖股筛选器启动...")
    print(f"⏰ 数据时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 获取涨幅前100
    print("\n📥 正在获取涨幅榜数据...")
    top_stocks = get_top_stocks(limit=200, sort_by="f3")
    print(f"✅ 获取到 {len(top_stocks)} 只股票")
    
    if not top_stocks:
        print("获取数据失败，请检查网络")
        return
    
    # 妖股筛选：涨幅5-20%，换手率>5%
    print("\n🔍 筛选妖股特征股票...")
    yonggu = filter_yonggu(top_stocks, min_rise=5.0, max_rise=20.0, min_turnover=5.0)
    print_stocks(yonggu, "🎯 妖股候选（涨幅5-20%，换手率>5%）")
    
    # 连续强势股筛选
    print("\n" + "="*60)
    strong = filter_continuously_rising(top_stocks, min_rise=3.0)
    print_stocks(strong[:15], "🔥 强势股候选（涨幅>3%，量比>1.5）")
    
    # 涨停股
    limit_up = [s for s in top_stocks if float(s.get("f3", 0) or 0) >= 9.9]
    print_stocks([{
        "代码": s.get("f12", ""),
        "名称": s.get("f14", ""),
        "现价": s.get("f2", ""),
        "涨幅": f"{s.get('f3', '')}%",
        "换手率": f"{s.get('f8', '')}%",
        "量比": s.get("f10", ""),
        "成交额": s.get("f6", ""),
        "综合评分": "-"
    } for s in limit_up[:20]], "💥 涨停股（涨幅>9.9%）")
    
    print("\n" + "="*60)
    print("⚠️  仅供参考，不构成投资建议！")
    print("="*60)

if __name__ == "__main__":
    main()
