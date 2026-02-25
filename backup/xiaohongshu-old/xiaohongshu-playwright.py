#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书自动化搜索 - Playwright版
完全模拟浏览器行为，自动处理Cookie和验证
"""

import asyncio
from playwright.sync_api import sync_playwright
import json
import time

def search_xiaohongshu(keyword):
    """使用Playwright搜索小红书"""
    
    print(f"\n🔍 搜索: {keyword}")
    
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = context.new_page()
        
        try:
            # 访问小红书
            print("   📱 访问小红书...")
            page.goto('https://www.xiaohongshu.com', timeout=30000, wait_until='networkidle')
            time.sleep(2)
            
            # 使用搜索URL
            print(f"   🔍 执行搜索...")
            search_url = f'https://www.xiaohongshu.com/search?keyword={keyword}'
            page.goto(search_url, timeout=30000, wait_until='networkidle')
            time.sleep(3)
            
            # 获取结果
            url = page.url()
            print(f"   📄 页面URL: {url}")
            
            # 查找内容
            notes = page.query_selector_all('article')
            print(f"   ✅ 找到 {len(notes)} 个内容块")
            
            # 获取页面标题
            title = page.title()
            print(f"   📋 页面标题: {title}")
            
            return {
                'success': True,
                'keyword': keyword,
                'url': url,
                'notes_count': len(notes),
                'title': title
            }
            
        except Exception as e:
            print(f"   ❌ 错误: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            browser.close()

def main():
    print("="*60)
    print("  🦞 小红书自动化搜索 - Playwright版")
    print("="*60)
    print("")
    print("功能:")
    print("  ✓ 完全模拟浏览器行为")
    print("  ✓ 自动处理Cookie")
    print("  ✓ 无需手动获取Cookie")
    print("")
    
    # 测试搜索
    keywords = ["穿搭", "美妆"]
    
    for i, keyword in enumerate(keywords):
        print(f"\n{'='*60}")
        print(f"  测试 {i+1}/{len(keywords)}: {keyword}")
        print(f"{'='*60}")
        
        result = search_xiaohongshu(keyword)
        
        if result['success']:
            print(f"\n✅ 搜索成功!")
            print(f"   关键词: {result['keyword']}")
            print(f"   页面: {result['url']}")
            print(f"   内容块: {result['notes_count']}")
        else:
            print(f"\n❌ 失败: {result.get('error')}")
        
        # 每次搜索后等待
        if i < len(keywords) - 1:
            time.sleep(3)
    
    print("\n" + "="*60)
    print("  ✅ 测试完成!")
    print("="*60)

if __name__ == "__main__":
    main()
