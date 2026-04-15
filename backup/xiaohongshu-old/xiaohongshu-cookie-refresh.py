#!/usr/bin/env python3
"""小红书Cookie刷新器"""

from playwright.sync_api import sync_playwright
import json
import os

def refresh_cookie():
    """刷新Cookie"""
    
    print("="*60)
    print("  🔄 小红书Cookie刷新器")
    print("="*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,  # 显示浏览器，手动登录
            args=['--no-sandbox']
        )
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = context.new_page()
        
        print("\n📱 打开创作者平台...")
        page.goto('https://creator.xiaohongshu.com/', timeout=30000)
        
        print(f"   URL: {page.url}")
        
        if 'login' in page.url:
            print("\n⚠️ 需要登录!")
            print("\n请手动完成以下步骤：")
            print("1. 使用手机扫码登录")
            print("2. 登录成功后按回车继续...")
            input()
            
            # 等待登录完成
            page.wait_for_load_state('networkidle', timeout=30000)
        
        print("\n✅ 登录成功或已登录!")
        
        # 获取所有Cookie
        print("\n📋 获取Cookie...")
        cookies = context.cookies()
        
        print(f"   获取到 {len(cookies)} 个Cookie")
        
        # 转换格式
        cookie_dict = {}
        for c in cookies:
            name = c['name']
            value = c['value']
            cookie_dict[name] = value
            print(f"   • {name}: {value[:30]}...")
        
        # 保存Cookie
        data = {
            'cookies': cookie_dict,
            'saved_at': __import__('datetime').datetime.now().isoformat(),
            'type': 'creator',
            'note': '从浏览器导出的创作者Cookie'
        }
        
        with open('/home/dhtaiyi/.openclaw/workspace/xiaohongshu-creator-cookies.json', 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Cookie已保存!")
        print(f"   文件: /home/dhtaiyi/.openclaw/workspace/xiaohongshu-creator-cookies.json")
        
        # 截图确认
        page.screenshot(path='/home/dhtaiyi/.openclaw/workspace/xiaohongshu-cookie-saved.png')
        print(f"   截图: /home/dhtaiyi/.openclaw/workspace/xiaohongshu-cookie-saved.png")
        
        browser.close()
        print("\n✅ 完成!")

if __name__ == "__main__":
    refresh_cookie()
