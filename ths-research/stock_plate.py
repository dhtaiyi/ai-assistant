#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票排行查询工具
使用新浪API获取数据
"""
import urllib.request
import time
from datetime import datetime

def get_stock(code):
    """获取单只股票数据"""
    prefix = 'sh' if code.startswith('6') else 'sz'
    url = f"http://hq.sinajs.cn/list={prefix}{code}"
    
    try:
        req = urllib.request.Request(url, headers={
            'Referer': 'http://finance.sina.com.cn/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        r = urllib.request.urlopen(req, timeout=10).read().decode('gbk')
        
        # 解析: 贵州茅台,1486.600,1486.600,1485.300,1507.800,1470.580,1485.300,1485.390,4167901,6216379203.000,249,1485.300,800,1485.280,100,1485.180,100,1485.150,2100,1485.100,1700,1485.390,100,1485
        
        if '=' not in r:
            return None
            
        parts = r.split('=')[1].split(',')
        
        if len(parts) < 32:
            return None
        
        name = parts[0]
        open_price = float(parts[1])
        yesterday = float(parts[2])
        current = float(parts[3])
        high = float(parts[4])
        low = float(parts[5])
        
        change = current - yesterday
        change_pct = (change / yesterday) * 100
        
        return {
            'code': code,
            'name': name,
            'price': current,
            'open': open_price,
            'high': high,
            'low': low,
            'change': change,
            'change_pct': change_pct
        }
        
    except Exception as e:
        print(f"  获取 {code} 失败: {e}")
        return None


# 板块成分股
PLATES = {
    '酿酒行业': ['600519','000858','000568','603288','600809','002304','600559','603589'],
    '新能源车': ['002594','300750','600104','600406','300124','002129','600438','600733'],
    '光伏行业': ['601012','600703','002506','300118','002459','601877','300316','002610'],
    '半导体': ['688981','300474','600460','688396','603986','300223','688981','688981'],
    '医药行业': ['600276','000651','002007','600529','600436','600566','603707','600518'],
    '银行板块': ['600036','601398','601939','600000','601229','601288','600015','600016'],
}


def get_plate_avg(pl):
    """计算板块平均涨幅"""
    total = 0
    count = 0
    for code in pl:
        s = get_stock(code)
        if s:
            total += s['change_pct']
            count += 1
        time.sleep(0.2)  # 避免请求过快
    return total / count if count else 0


def main():
    print("="*70)
    print("  📊 板块排行查询 - 各板块内涨幅前五")
    print("="*70)
    
    # 计算板块平均涨幅
    plate_data = []
    for name, stocks in PLATES.items():
        avg = get_plate_avg(stocks)
        plate_data.append((name, stocks, avg))
    
    # 排序
    plate_data.sort(key=lambda x: x[2], reverse=True)
    
    # 显示前三
    for i, (name, stocks, avg) in enumerate(plate_data[:3], 1):
        print(f"\n{'='*70}")
        print(f"  📊 第{i}名: {name} (平均涨幅: {avg:+.2f}%)")
        print(f"{'='*70}")
        print(f"  {'排名':<4} {'代码':<8} {'名称':<12} {'价格':<10} {'涨幅':<12}")
        print(f"  {'-'*4} {'-'*8} {'-'*12} {'-'*10} {'-'*12}")
        
        stocks_data = []
        for code in stocks:
            s = get_stock(code)
            if s:
                stocks_data.append(s)
            time.sleep(0.2)
        
        stocks_data.sort(key=lambda x: x['change_pct'], reverse=True)
        
        for j, s in enumerate(stocks_data[:5], 1):
            print(f"  {j:<4} {s['code']:<8} {s['name']:<12} ¥{s['price']:<8.2f} {s['change_pct']:+.2f}%")
    
    print("\n"+"="*70)
    print(f"  时间: {datetime.now().strftime('%H:%M:%S')}")
    print("="*70)


if __name__ == '__main__':
    main()
