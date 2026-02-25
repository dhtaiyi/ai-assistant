#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书发贴功能测试
"""

from playwright.sync_api import sync_playwright
import json

def test_posting():
    """测试发贴功能"""
    
    print("🔍 测试发贴功能...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'
        )
        
        # 加载Cookie
        try:
            with open('/root/.openclaw/workspace/xiaohongshu-cookies.json', 'r') as f:
                data = json.load(f)
                cookies = data.get('cookies', {})
                for name, value in cookies.items():
                    context.add_cookies([{
                        'name': name,
                        'value': value,
                        'domain': '.xiaohongshu.com',
                        'path': '/'
                    }])
        except Exception as e:
            print(f"❌ 加载Cookie失败: {e}")
            return
        
        page = context.new_page()
        
        # 尝试多种发贴入口
        urls = [
            'https://www.xiaohongshu.com/explore',
            'https://www.xiaohongshu.com/',
            'https://www.xiaohongshu.com/search?keyword=发布'
        ]
        
        for url in urls:
            print(f"\n📱 访问: {url}")
            page.goto(url, timeout=20000)
            page.wait_for_timeout(3000)
            
            # 查找发贴按钮
            post_btn = page.query_selector('a:has-text("发布")') or \
                      page.query_selector('button:has-text("发布")') or \
                      page.query_selector('a:has-text("＋")') or \
                      page.query_selector('[class*="publish"]')
            
            if post_btn:
                text = post_btn.inner_text()[:50]
                href = post_btn.get_attribute('href') or '无链接'
                print(f"   ✅ 找到: {text} -> {href}")
            else:
                print(f"   ❌ 未找到发布按钮")
        
        # 查找＋号按钮（常见于App端）
        print("\n🔍 查找＋号按钮...")
        plus_btn = page.query_selector('a:has-text("＋")') or \
                  page.query_selector('[class*="plus"]')
        
        if plus_btn:
            print("✅ 找到＋号按钮")
            try:
                plus_btn.click()
                page.wait_for_timeout(2000)
                print(f"   点击后URL: {page.url}")
            except:
                print("   点击失败")
        
        browser.close()

def check_user_info():
    """检查用户信息"""
    
    print("\n" + "="*60)
    print("  检查用户创作者权限")
    print("="*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'
        )
        
        # 加载Cookie
        try:
            with open('/root/.openclaw/workspace/xiaohongshu-cookies.json', 'r') as f:
                data = json.load(f)
                cookies = data.get('cookies', {})
                for name, value in cookies.items():
                    context.add_cookies([{
                        'name': name,
                        'value': value,
                        'domain': '.xiaohongshu.com',
                        'path': '/'
                    }])
        except:
            return
        
        page = context.new_page()
        
        # 访问用户主页
        page.goto('https://www.xiaohongshu.com/user/profile', timeout=20000)
        page.wait_for_timeout(3000)
        
        print(f"标题: {page.title()}")
        print(f"URL: {page.url}")
        
        # 获取用户信息
        text = page.inner_text('body')[:800]
        print(f"\n页面内容:\n{text}")
        
        # 检查是否有创作者标识
        if '创作者' in text:
            print("\n✅ 账号有创作者资格")
        elif '普通' in text:
            print("\n⚠️ 账号是普通用户")
        
        browser.close()

if __name__ == "__main__":
    test_posting()
    check_user_info()
