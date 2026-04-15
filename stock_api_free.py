#!/usr/bin/env python3
"""
免费股票数据接口 - 腾讯财经API
直接调用，无需登录，无需代理
"""

import requests
import json
import urllib.parse

# 腾讯财经免费接口
class TencentStockAPI:
    """腾讯财经免费API"""
    
    BASE_URL = "http://qt.gtimg.cn/q="
    
    @staticmethod
    def get_realtime(stock_codes: list) -> dict:
        """
        获取实时行情
        
        参数:
            stock_codes: 股票代码列表，如 ['sh600519', 'sz000001']
            
        返回:
            dict: 股票数据字典
        """
        if isinstance(stock_codes, str):
            stock_codes = [stock_codes]
        
        # 拼接股票代码
        codes_str = "_".join(stock_codes)
        url = f"{TencentStockAPI.BASE_URL}{codes_str}"
        
        try:
            response = requests.get(url, timeout=10)
            response.encoding = 'gbk'  # 新浪使用GBK编码
            
            # 解析返回数据
            result = {}
            for line in response.text.split('\n'):
                if '=' in line:
                    code, data = line.split('=', 1)
                    code = code.replace('v_', '')
                    try:
                        result[code] = json.loads(data.strip('"; '))
                    except:
                        pass
            
            return result
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def parse_stock_data(data: dict) -> dict:
        """
        解析股票数据
        
        腾讯返回的数组索引:
        0: 股票名称
        1: 股票代码
        2: 当前价格
        3: 昨收
        4: 今开
        5: 成交量(手)
        6: 外盘
        7: 内盘
        8: 买一价
        9: 买一量(手)
        ...买二到买五...
        30: 卖一价
        ...卖二到卖五...
        31: 最近交易日期
        32: 最近交易时间
        """
        parsed = {}
        for code, values in data.items():
            if isinstance(values, list) and len(values) > 30:
                parsed[code] = {
                    "name": values[1],
                    "code": values[2],
                    "price": float(values[3]) if values[3] else 0,  # 当前价格
                    "yesterday_close": float(values[4]) if values[4] else 0,
                    "today_open": float(values[5]) if values[5] else 0,
                    "volume": int(values[6]) if values[6] else 0,  # 成交量(手)
                    "amount": float(values[7]) if values[7] else 0,  # 成交额(万)
                    "date": values[31],
                    "time": values[32],
                }
        return parsed


# 新浪财经免费接口
class SinaStockAPI:
    """新浪财经免费API"""
    
    BASE_URL = "http://hq.sinajs.cn/list="
    
    @staticmethod
    def get_realtime(stock_codes: list) -> dict:
        """
        获取实时行情
        
        参数:
            stock_codes: 股票代码列表
            - 上海股票: sh600519
            - 深圳股票: sz000001
        """
        if isinstance(stock_codes, str):
            stock_codes = [stock_codes]
        
        codes_str = ",".join(stock_codes)
        url = f"{SinaStockAPI.BASE_URL}{codes_str}"
        
        try:
            response = requests.get(url, timeout=10)
            response.encoding = 'gbk'
            
            # 解析数据
            result = {}
            for line in response.text.split('\n'):
                if '=' in line:
                    code = line.split('=')[0].split('_')[-1]
                    data = line.split('=')[1].strip('"; ')
                    if data:
                        values = data.split(',')
                        if len(values) > 1:
                            result[code] = {
                                "name": values[0],
                                "open": float(values[1]) if values[1] else 0,
                                "close": float(values[2]) if values[2] else 0,
                                "price": float(values[3]) if values[3] else 0,
                                "high": float(values[4]) if values[4] else 0,
                                "low": float(values[5]) if values[5] else 0,
                                "volume": int(float(values[8])) if values[8] else 0,
                            }
            
            return result
        except Exception as e:
            return {"error": str(e)}


# 测试
if __name__ == "__main__":
    # 测试腾讯财经API
    print("=== 腾讯财经测试 ===")
    codes = ['sh600519', 'sz000001', 's_sh000001']
    data = TencentStockAPI.get_realtime(codes)
    
    for code, info in data.items():
        if isinstance(info, dict) and 'price' in info:
            print(f"{code}: {info.get('name')} - 价格: {info.get('price')}")
    
    print("\n=== 新浪财经测试 ===")
    data2 = SinaStockAPI.get_realtime(['sh600519', 'sz000001'])
    for code, info in data2.items():
        print(f"{code}: {info}")
