#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书发贴测试 - 新人报道
"""

from playwright.sync_api import sync_playwright
import json
import time

def post_newbie():
    """发布新人报道贴"""
    
    print("="*60)
    print("  🦞 小红书发贴测试 - 新人报道")
    print("="*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)'
        )
        
        page = context.new_page()
        
        # 加载Cookie
        print("\n📋 加载Cookie...")
        try:
            with open('/home/dhtaiyi/.openclaw/workspace/xiaohongshu-cookies.json') as f:
                data = json.load(f)
                cookies = data.get('cookies', {})
                for name, value in cookies.items():
                    context.add_cookies([{
                        'name': name,
                        'value': value,
                        'domain': '.xiaohongshu.com',
                        'path': '/'
                    }])
                print(f"   ✅ 加载 {len(cookies)} 个Cookie")
        except Exception as e:
            print(f"   ❌ 加载失败: {e}")
            return
        
        # 访问创作者平台
        print("\n📱 访问创作者发贴页...")
        page.goto('https://creator.xiaohongshu.com/publish/publish', timeout=20000)
        time.sleep(3)
        
        print(f"   标题: {page.title()}")
        print(f"   URL: {page.url}")
        
        # 获取页面内容
        text = page.inner_text('body')[:1500]
        
        # 检查权限
        print("\n📋 检查发贴权限...")
        
        if '登录' in text[:500]:
            print("   ⚠️ 需要登录创作者平台")
            print("   请手动在浏览器中登录")
            return
        
        if '创作者' in text and '申请' in text:
            print("   ❌ 需要申请创作者资格")
            print("   访问 https://creator.xiaohongshu.com 申请")
            return
        
        print("   ✅ 有发贴权限")
        
        # 查找发布按钮
        publish_btn = page.query_selector('button:has-text("发布")')
        
        if publish_btn:
            print("\n✅ 找到发布按钮，可以发贴！")
            
            # 填写内容
            print("\n📝 准备发贴内容...")
            print("\n标题: 新人报道｜终于找到我的生活好物清单🛍️")
            print("\n内容预览:")
            print("-"*60)
            print("哈喽～我是新人博主！🎉")
            print("...")
            print("-"*60)
            
            # 截图
            page.screenshot(path='/home/dhtaiyi/.openclaw/workspace/xiaohongshu-post-preview.png')
            print("\n📸 截图已保存: /home/dhtaiyi/.openclaw/workspace/xiaohongshu-post-preview.png")
        else:
            print("\n❓ 发布按钮位置未知")
            page.screenshot(path='/home/dhtaiyi/.openclaw/workspace/xiaohongshu-permission-check.png')
            print("📸 截图已保存")


if __name__ == "__main__":
    post_newbie()
