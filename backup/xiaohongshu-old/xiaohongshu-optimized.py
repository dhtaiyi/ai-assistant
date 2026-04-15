#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化版小红书搜索脚本
添加延迟和更真实的请求头，减少被风控的概率
"""

import asyncio
import aiohttp
import random
import time
import json
import sys
import os

# 添加路径
sys.path.insert(0, '/home/dhtaiyi/.openclaw/workspace/skills/xiaohongshutools/scripts')

from request.web.xhs_session import create_xhs_session
from request.web.apis.note import HomeFeedCategory

# 配置
WEB_SESSION = "040069b8fdba81d499ed9f75b83b4b4314e571"

# 延迟配置
DELAY_BEFORE_SEARCH = 2  # 搜索前延迟2秒
DELAY_BETWEEN_REQUESTS = 3  # 每次请求间隔3秒
DELAY_AFTER_ERROR = 5  # 错误后延迟5秒

def random_delay():
    """随机延迟，模拟真实用户行为"""
    delay = DELAY_BETWEEN_REQUESTS + random.uniform(0, 2)
    print(f"⏳ 等待 {delay:.1f} 秒...")
    time.sleep(delay)

async def search_notes_optimized(xhs, keyword, retries=3):
    """带重试和延迟的搜索"""
    
    for attempt in range(retries):
        try:
            print(f"🔍 搜索关键词: {keyword} (尝试 {attempt + 1}/{retries})")
            
            # 搜索前延迟
            print(f"⏳ 搜索前等待 {DELAY_BEFORE_SEARCH} 秒...")
            await asyncio.sleep(DELAY_BEFORE_SEARCH)
            
            # 执行搜索
            result = await xhs.apis.note.search_notes(keyword)
            
            print(f"✅ 搜索成功!")
            return result
            
        except Exception as e:
            error_msg = str(e)
            
            if "461" in error_msg:
                print(f"⚠️  被风控 (461)，等待 {DELAY_AFTER_ERROR} 秒后重试...")
                await asyncio.sleep(DELAY_AFTER_ERROR)
                
                if attempt < retries - 1:
                    print(f"🔄 第 {attempt + 2} 次重试...")
                    continue
                else:
                    print(f"❌ 重试 {retries} 次后仍被风控")
                    return None
            else:
                print(f"❌ 错误: {error_msg}")
                return None
    
    return None

async def main():
    print("╔═══════════════════════════════════════╗")
    print("║   🦞 优化版小红书搜索测试         ║")
    print("╚═══════════════════════════════════════╝")
    print("")
    print("📋 优化项:")
    print("   - 添加搜索前延迟 (2秒)")
    print("   - 添加请求间隔 (3秒)")
    print("   - 错误后等待 (5秒)")
    print("   - 自动重试机制 (最多3次)")
    print("")
    
    try:
        # 创建会话
        print("🔄 正在创建会话...")
        xhs = await create_xhs_session(web_session=WEB_SESSION)
        print("✅ 会话创建成功!")
        print("")
        
        # 测试关键词
        keywords = ["美妆", "穿搭"]
        
        for i, keyword in enumerate(keywords):
            print(f"\n{'='*50}")
            print(f"📝 测试 {i+1}/{len(keywords)}: {keyword}")
            print(f"{'='*50}")
            
            # 搜索
            result = await search_notes_optimized(xhs, keyword)
            
            if result:
                print(f"✅ 搜索成功! 获取到数据")
                print(f"   数据类型: {type(result)}")
            else:
                print(f"❌ 搜索失败")
            
            # 每次请求后延迟（最后一次除外）
            if i < len(keywords) - 1:
                random_delay()
        
        print("\n" + "="*50)
        print("✅ 测试完成!")
        print("="*50)
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭会话
        if 'xhs' in dir():
            await xhs.close_session()

if __name__ == "__main__":
    asyncio.run(main())
