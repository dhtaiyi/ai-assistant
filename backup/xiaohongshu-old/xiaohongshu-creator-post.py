#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书创作者发贴测试
"""

from playwright.sync_api import sync_playwright
import json
import time

def try_post():
    """尝试发贴"""
    
    print("="*60)
    print("  🦞 小红书创作者发贴测试")
    print("="*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = context.new_page()
        
        # 加载创作者Cookie
        print("\n📋 加载创作者Cookie...")
        try:
            with open('/root/.openclaw/workspace/xiaohongshu-creator-cookies.json') as f:
                data = json.load(f)
                cookies = data.get('cookies', {})
                
                for name, value in cookies.items():
                    # 根据Cookie名称确定domain
                    if 'creator' in name:
                        domain = '.creator.xiaohongshu.com'
                    else:
                        domain = '.xiaohongshu.com'
                    
                    context.add_cookies([{
                        'name': name,
                        'value': value,
                        'domain': domain,
                        'path': '/'
                    }])
                
                print(f"   ✅ 加载 {len(cookies)} 个Cookie")
        except Exception as e:
            print(f"   ❌ 加载失败: {e}")
            return
        
        # 访问创作者发贴页
        print("\n📱 访问发贴页面...")
        page.goto('https://creator.xiaohongshu.com/publish/publish', timeout=20000)
        time.sleep(3)
        
        print(f"   标题: {page.title()}")
        print(f"   URL: {page.url}")
        
        # 获取页面内容
        text = page.inner_text('body')[:2000]
        
        print("\n📄 页面内容预览:")
        print("-"*60)
        print(text[:1500])
        print("-"*60)
        
        # 查找发贴表单
        print("\n🔍 查找发贴表单...")
        
        # 查找标题
        title_input = None
        for sel in ['input[placeholder*="标题"]', 'textarea[placeholder*="标题"]']:
            elem = page.query_selector(sel)
            if elem:
                title_input = elem
                print(f"   ✅ 找到标题输入框")
                break
        
        # 查找内容
        content_input = None
        for sel in ['textarea[placeholder*="分享"]', 'div[contenteditable]']:
            elem = page.query_selector(sel)
            if elem:
                content_input = elem
                print(f"   ✅ 找到内容输入框")
                break
        
        # 查找发布按钮
        publish_btn = None
        for sel in ['button:has-text("发布")', 'button:has-text("发布笔记")']:
            elem = page.query_selector(sel)
            if elem:
                publish_btn = elem
                print(f"   ✅ 找到发布按钮")
                break
        
        # 如果找到了表单，填写并准备发布
        if title_input and content_input:
            print("\n📝 准备发贴内容...")
            
            # 新人报道内容
            title = "新人报道｜终于找到我的生活好物清单🛍️"
            content = """哈喽～我是新人博主！🎉

✨ 关于我：
• 刚开始分享生活好物
• 喜欢发掘实用小物件
• 每天分享1-2个心水好物

🌟 为什么开始：
之前刷小红书看到好多生活好物分享，
自己也忍不住想分享一下！

📦 近期新入的好物：
- 收纳神器
- 桌面整理
- 日常小物

💕 希望能在这里交到志同道合的朋友！

#新人报道 #生活好物 #好物分享 #新人博主 #日常分享"""
            
            print(f"   标题: {title}")
            print(f"   内容长度: {len(content)} 字符")
            
            # 截图
            page.screenshot(path='/root/.openclaw/workspace/xiaohongshu-creator-page.png')
            print(f"\n📸 截图已保存: /root/.openclaw/workspace/xiaohongshu-creator-page.png")
            
            if publish_btn:
                print("\n🚀 可以发布笔记了！")
                print("   需要手动点击发布按钮")
        else:
            print("\n❓ 发贴表单位置未知")
        
        # 查找是否有登录重定向
        if '登录' in text[:500]:
            print("\n⚠️ 需要登录！")
            print("   请在浏览器中手动登录创作者平台")
        
        browser.close()

if __name__ == "__main__":
    try_post()
