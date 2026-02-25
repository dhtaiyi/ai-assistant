#!/usr/bin/env python3
"""小红书最终发贴"""

from playwright.sync_api import sync_playwright
import json

print("="*60)
print("  🦞 小红书发贴")
print("="*60)

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox'])
    page = b.new_page()
    
    # 加载Cookie
    with open('/root/.openclaw/workspace/xiaohongshu-creator-cookies.json') as f:
        data = json.load(f)
        for k, v in data['cookies'].items():
            domain = '.creator.xiaohongshu.com' if 'creator' in k else '.xiaohongshu.com'
            page.context.add_cookies([{'name': k, 'value': v, 'domain': domain, 'path': '/'}])
    
    print("\n📱 访问发贴页...")
    page.goto('https://creator.xiaohongshu.com/publish/publish', timeout=20000)
    
    print(f"   标题: {page.title()}")
    
    # 检查登录
    text = page.inner_text('body')
    if '困困困' not in text:
        print("\n❌ 未登录")
        b.close()
        exit()
    
    print("\n✅ 已登录")
    
    # 查找并点击"上传图文"
    print("\n🔍 查找上传图文...")
    
    # 方法1: 点击文字链接
    upload_link = page.query_selector('span:has-text("上传图文")') or \
                page.query_selector('a:has-text("上传图文")')
    
    if upload_link:
        print("   ✅ 找到上传图文")
        try:
            upload_link.click()
            print("   ✅ 已点击")
            page.wait_for_timeout(2000)
        except Exception as e:
            print(f"   ⚠️ 点击失败: {e}")
    
    # 截图
    page.screenshot(path='/root/.openclaw/workspace/xiaohongshu-uploading.png')
    print("\n📸 截图已保存")
    
    # 检查页面变化
    new_text = page.inner_text('body')[:2000]
    print("\n📄 页面内容:")
    print("-"*60)
    print(new_text[:1000])
    print("-"*60)
    
    # 查找标题和内容输入框
    print("\n🔍 查找输入框...")
    
    inputs = page.query_selector_all('input')
    textareas = page.query_selector_all('textarea')
    
    print(f"   输入框: {len(inputs)}")
    print(f"   文本框: {len(textareas)}")
    
    if inputs:
        for i, inp in enumerate(inputs[:5], 1):
            ph = inp.get_attribute('placeholder') or '无'
            print(f"   {i}. input: {ph[:40]}")
    
    b.close()
    print("\n✅ 完成!")
