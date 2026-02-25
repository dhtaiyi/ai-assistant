#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 Tushare 配置
"""

import os
import sys

def test_tushare():
    """测试 Tushare 配置"""
    
    # 检查 Token
    token = os.getenv('TUSHARE_TOKEN')
    
    if not token:
        print("❌ 错误: TUSHARE_TOKEN 环境变量未设置")
        print("")
        print("请先配置 Token:")
        print('  export TUSHARE_TOKEN="your_token"')
        return False
    
    print(f"✅ Token 已设置: {token[:10]}...")
    
    # 测试连接
    try:
        import tushare as ts
        pro = ts.pro_api(token)
        
        # 测试获取交易日
        df = pro.trade_cal(exchange='SSE', start_date='20250101', end_date='20250110')
        
        if df is not None and len(df) > 0:
            print("✅ Tushare 连接成功!")
            print(f"   获取到 {len(df)} 条交易日数据")
            print("")
            print("📊 示例数据:")
            print(df.head(5).to_string())
            return True
        else:
            print("❌ 获取数据失败")
            return False
            
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

if __name__ == "__main__":
    # 尝试从配置文件加载
    config_file = '/root/.openclaw/workspace/.tushare.env'
    if os.path.exists(config_file):
        with open(config_file) as f:
            for line in f:
                if line.startswith('export TUSHARE_TOKEN='):
                    token = line.split('=')[1].strip().strip('"')
                    os.environ['TUSHARE_TOKEN'] = token
    
    test_tushare()
