#!/usr/bin/env python3
"""小红书最终发贴"""

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
    with open('/home/dhtaiyi/.openclaw/workspace/xiaohongshu-creator-cookies.json') as f:
        data = json.load(f)
        for k, v in data['cookies'].items():
            domain = '.creator.xiaohongshu.com' if 'creator' in k else '.xiaohongshu.com'
            page.context.add_cookies([{'name': k, 'value': v, 'domain': domain, 'path': '/'}])
    print(f"   ✅ {len(data['cookies'])} 个Cookie")
    
    # 访问发贴页
    print("\n📱 访问发贴页...")
    page.goto('https://creator.xiaohongshu.com/publish/publish', timeout=20000)
    
    print(f"   标题: {page.title()}")
    print(f"   URL: {page.url}")
    
    # 检查是否已登录
    text = page.inner_text('body')[:1500]
    
    if '困困困' in text:
        print("\n✅ 已登录!")
        
        # 截图
        page.screenshot(path='/home/dhtaiyi/.openclaw/workspace/xiaohongshu-logged-in.png')
        print("\n📸 截图已保存")
        
        # 查找发布按钮
        links = page.query_selector_all('a')
        for link in links[:15]:
            try:
                txt = link.inner_text().strip()[:30]
                href = link.get_attribute('href') or ''
                if txt and ('发布' in txt or '上传' in txt or '写' in txt):
                    print(f"\n✅ 找到: {txt} -> {href}")
            except:
                pass
        
        print("\n🚀 可以发贴了！")
        
    elif '登录' in text[:500]:
        print("\n⚠️ 需要登录!")
    else:
        print("\n❓ 状态未知")
    
    b.close()
    print("\n✅ 完成!")
