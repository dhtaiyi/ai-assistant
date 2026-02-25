#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取市场热点
"""

import subprocess
import sys

def get_market_hot():
    """使用 stock-monitor 获取市场热点"""
    print("📈 获取市场热点...")
    print("")
    
    # 今日热点
    print("🔥 今日热点板块:")
    subprocess.run(['stock', 'hot'])
    
    print("")
    print("🏭 行业板块:")
    subprocess.run(['stock', 'industry'])
    
    print("")
    print("💡 概念板块:")
    subprocess.run(['stock', 'concept'])

if __name__ == "__main__":
    get_market_hot()
