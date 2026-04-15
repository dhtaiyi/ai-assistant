#!/usr/bin/env python3
"""实际测试小红书登录状态"""

from playwright.sync_api import sync_playwright
import json
import time

print("="*60)
print("  🔍 实际登录测试")
print("="*60)
print()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        proxy={'server': 'http://127.0.0.1:13128'}
    )
    page = context.new_page()
    
    # 加载Cookie
    print("1️⃣ 加载Cookie...")
    with open('/home/dhtaiyi/.openclaw/workspace/xiaohongshu-creator-cookies.json') as f:
        data = json.load(f)
        for k, v in data['cookies'].items():
            domain = '.creator.xiaohongshu.com' if 'creator' in k else '.xiaohongshu.com'
            context.add_cookies([{
                'name': k,
                'value': v,
                'domain': domain,
                'path': '/'
            }])
    print(f"   ✅ 加载 {len(data['cookies'])} 个Cookie")
    
    # 访问创作者平台
    print()
    print("2️⃣ 访问创作者平台...")
    page.goto('https://creator.xiaohongshu.com/', timeout=30000)
    time.sleep(3)
    
    # 截图
    page.screenshot(path='/home/dhtaiyi/.openclaw/workspace/xiaohongshu-cookie-test.png')
    print("   📸 截图已保存")
    
    # 检查登录状态
    print()
    print("3️⃣ 检查登录状态...")
    text = page.inner_text('body')[:3000]
    
    # 保存页面内容用于分析
    with open('/home/dhtaiyi/.openclaw/workspace/xiaohongshu-login-test.html', 'w') as f:
        f.write(f"<html><body><pre>{text}</pre></body></html>")
    
    # 检查关键词
    checks = [
        ('困困困', '✅ 找到用户名'),
        ('安全限制', '⚠️ 被IP检测拦截'),
        ('登录', 'ℹ️ 需要登录'),
        ('发布笔记', '✅ 已登录，可发贴'),
        ('IP存在风险', '⚠️ IP被标记'),
        ('新人报道', '✅ 已登录'),
    ]
    
    print()
    print("   检查结果:")
    print("-"*60)
    
    found_status = None
    for keyword, msg in checks:
        if keyword in text:
            print(f"   {msg}")
            if '安全限制' in keyword or 'IP存在风险' in keyword:
                found_status = 'blocked'
            elif '困困困' in keyword or '发布笔记' in keyword:
                found_status = 'logged_in'
            elif '登录' in keyword:
                found_status = 'need_login'
    
    if not found_status:
        print("   ⚠️ 状态未知")
        print(f"   页面长度: {len(text)} 字符")
    
    print()
    print("4️⃣ 最终状态")
    print("-"*60)
    
    if found_status == 'logged_in':
        print("   🎉 Cookie有效！已登录")
    elif found_status == 'blocked':
        print("   ❌ Cookie有效，但被IP检测拦截")
        print("   💡 建议：更换代理IP或本地浏览器访问")
    elif found_status == 'need_login':
        print("   ⚠️ Cookie已过期，需要重新登录")
    else:
        print("   ❓ 状态未知，需要进一步检查")
    
    browser.close()
    
    print()
    print("="*60)
    print("  ✅ 测试完成")
    print("="*60)
