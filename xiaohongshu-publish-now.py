#!/usr/bin/env python3
"""小红书发贴 - 新人报道"""

from playwright.sync_api import sync_playwright
import json

print("="*60)
print("  🦞 小红书发贴 - 新人报道")
print("="*60)

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    page = b.new_page()
    
    # 加载Cookie
    print("\n📋 加载Cookie...")
    with open('/root/.openclaw/workspace/xiaohongshu-creator-cookies.json') as f:
        data = json.load(f)
        for k, v in data['cookies'].items():
            domain = '.creator.xiaohongshu.com' if 'creator' in k else '.xiaohongshu.com'
            page.context.add_cookies([{'name': k, 'value': v, 'domain': domain, 'path': '/'}])
    print(f"   ✅ {len(data['cookies'])} 个Cookie")
    
    # 访问发贴页
    print("\n📱 访问发贴页...")
    page.goto('https://creator.xiaohongshu.com/publish/publish', timeout=20000)
    
    # 检查登录
    text = page.inner_text('body')
    if '困困困' not in text:
        print("   ❌ 未登录")
        b.close()
        exit()
    
    print("   ✅ 已登录")
    
    # 点击"上传图文"
    print("\n🔍 查找上传图文...")
    
    upload = page.query_selector('span:has-text("上传图文")') or \
            page.query_selector('a:has-text("上传图文")')
    
    if upload:
        print("   ✅ 找到上传图文")
        try:
            upload.click()
            print("   ✅ 已点击")
        except:
            print("   ⚠️ 点击失败")
    
    page.wait_for_timeout(2000)
    
    # 截图
    page.screenshot(path='/root/.openclaw/workspace/xiaohongshu-ready-to-post.png')
    print("\n📸 截图已保存")
    
    # 检查页面
    new_text = page.inner_text('body')[:2000]
    
    # 查找标题输入
    print("\n🔍 查找标题输入框...")
    title_input = page.query_selector('input[placeholder*="标题"]') or \
                 page.query_selector('textarea[placeholder*="标题"]')
    
    if title_input:
        print("   ✅ 找到标题输入框")
        
        # 填写标题
        title = "新人报道｜终于找到我的生活好物清单🛍️"
        title_input.fill(title)
        print(f"   ✅ 标题已填写: {title}")
    
    # 查找内容输入
    print("\n🔍 查找内容输入框...")
    content_input = page.query_selector('textarea[placeholder*="分享"]') or \
                   page.query_selector('div[contenteditable]')
    
    if content_input:
        print("   ✅ 找到内容输入框")
        
        # 填写内容
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
        
        content_input.fill(content)
        print(f"   ✅ 内容已填写 ({len(content)} 字符)")
    
    # 查找发布按钮
    print("\n🔍 查找发布按钮...")
    publish = page.query_selector('button:has-text("发布")')
    
    if publish:
        print("   ✅ 找到发布按钮!")
        print("\n🚀 可以发布笔记了！")
        print("\n请在截图中确认内容是否正确")
    else:
        print("   ⚠️ 未找到发布按钮")
    
    # 最终截图
    page.screenshot(path='/root/.openclaw/workspace/xiaohongshu-filled-form.png')
    print("\n📸 最终截图已保存")
    
    b.close()
    print("\n✅ 完成!")
    print("\n📁 截图文件:")
    print("   - /root/.openclaw/workspace/xiaohongshu-ready-to-post.png")
    print("   - /root/.openclaw/workspace/xiaohongshu-filled-form.png")
