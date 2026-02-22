#!/usr/bin/env python3
"""
腾讯财经API - 实时股票行情
无需登录，无需代理，完全免费
"""

import requests
import time

STOCKS = {
    # A股
    'sh600519': '贵州茅台',
    'sh601318': '中国平安',
    'sh000858': '五粮液',
    'sz000001': '平安银行',
    'sz000002': '万科A',
    'sh600036': '招商银行',
    'sh600030': '中信证券',
    'sh600016': '民生银行',
    'sh601012': '隆基绿能',
    'sh300750': '宁德时代',
    
    # 指数
    's_sh000001': '上证指数',
    's_sz399001': '深证成指',
    's_sh000300': '沪深300',
    's_sh000016': '上证50',
    's_sz399006': '创业板指',
}

def get_stock(code):
    """获取单只股票数据"""
    url = f"http://qt.gtimg.cn/q={code}"
    response = requests.get(url, timeout=10)
    response.encoding = 'gbk'
    return response.text

def parse_stock(code, data):
    """解析股票数据"""
    # 指数格式
    if code.startswith('s_'):
        fields = data.split('~')
        if len(fields) > 5:
            name = fields[1]
            current = float(fields[3]) if fields[3] else 0
            change = float(fields[4]) if fields[4] else 0
            change_pct = float(fields[5]) if fields[5] else 0
            return {
                'name': name,
                'current': current,
                'change': change,
                'change_pct': change_pct,
                'type': 'index'
            }
    else:
        # 股票格式
        fields = data.split('~')
        if len(fields) > 4:
            name = fields[1]
            current = float(fields[3]) if fields[3] else 0
            yesterday = float(fields[4]) if fields[4] else 0
            change = current - yesterday
            change_pct = (change / yesterday * 100) if yesterday else 0
            return {
                'name': name,
                'current': current,
                'yesterday': yesterday,
                'change': change,
                'change_pct': change_pct,
                'type': 'stock'
            }
    return None

def get_all_stocks():
    """获取所有配置的股票数据"""
    results = []
    for code, name in STOCKS.items():
        data = get_stock(code)
        time.sleep(0.1)  # 避免请求太快
        
        result = parse_stock(code, data)
        if result:
            result['code'] = code
            results.append(result)
    return results

def print_stocks():
    """打印股票行情"""
    results = get_all_stocks()
    
    print("=" * 60)
    print("📈 腾讯财经API - 实时行情")
    print("=" * 60)
    
    for r in results:
        emoji = "🔴" if r['change'] < 0 else "🟢"
        print(f"{emoji} {r['name']} ({r['code']})")
        print(f"   当前: {r['current']:.2f}")
        
        if r['type'] == 'stock':
            print(f"   昨收: {r['yesterday']:.2f}")
        
        print(f"   涨跌: {r['change']:+.2f} ({r['change_pct']:+.2f}%)")
        print()
    
    print("=" * 60)

if __name__ == "__main__":
    print_stocks()
