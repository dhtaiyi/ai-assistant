#!/usr/bin/env python3
"""小红书终极发贴脚本"""

from playwright.sync_api import sync_playwright
import json

print("="*60)
print("  🦞 小红书发贴测试")
print("="*60)

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox'])
    page = b.new_page()
    
    # 加载Cookie
    print("\n📋 加载Cookie...")
    try:
        with open('/home/dhtaiyi/.openclaw/workspace/xiaohongshu-creator-cookies.json') as f:
            data = json.load(f)
            for k, v in data['cookies'].items():
                domain = '.creator.xiaohongshu.com' if 'creator' in k else '.xiaohongshu.com'
                page.context.add_cookies([{'name': k, 'value': v, 'domain': domain, 'path': '/'}])
            print(f"   ✅ {len(data['cookies'])} 个Cookie")
    except Exception as e:
        print(f"   ❌ 失败: {e}")
        exit()
    
    # 访问发贴页
    print("\n📱 访问发贴页...")
    page.goto('https://creator.xiaohongshu.com/publish/publish', timeout=20000)
    
    print(f"   标题: {page.title()}")
    print(f"   URL: {page.url}")
    
    # 查找按钮
    print("\n🔍 查找按钮...")
    
    # 所有a标签
    links = page.query_selector_all('a')
    print(f"   发现 {len(links)} 个链接")
    
    for link in links[:15]:
        try:
            text = link.inner_text().strip()[:30]
            href = link.get_attribute('href') or ''
            if text and len(text) > 1:
                print(f"   • {text}: {href[:50]}")
        except:
            pass
    
    # 截图
    page.screenshot(path='/home/dhtaiyi/.openclaw/workspace/xiaohongshu-post-final.png')
    print(f"\n📸 截图: /home/dhtaiyi/.openclaw/workspace/xiaohongshu-post-final.png")
    
    b.close()
    print("\n✅ 完成!")
