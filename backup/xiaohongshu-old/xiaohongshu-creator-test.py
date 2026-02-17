#!/usr/bin/env python3
"""测试创作者中心"""

from playwright.sync_api import sync_playwright
import json

def test_creator():
    """测试创作者中心"""
    
    print("🔍 测试创作者中心...")
    
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
        except Exception as e:
            print(f"❌ 加载Cookie失败: {e}")
            return
        
        page = context.new_page()
        
        # 访问创作者发贴页
        print("\n📱 访问发贴页...")
        page.goto('https://creator.xiaohongshu.com/publish/publish?source=official', timeout=20000)
        page.wait_for_timeout(5000)
        
        print(f"标题: {page.title()}")
        print(f"URL: {page.url}")
        
        # 获取页面内容
        text = page.inner_text('body')[:1000]
        print(f"\n页面内容:\n{text}")
        
        # 检查是否需要申请创作者
        if '申请' in text or '创作者' in text:
            print("\n⚠️ 可能需要申请创作者资格")
        
        # 查找发贴表单
        print("\n🔍 检查发贴表单...")
        textarea = page.query_selector('textarea') or page.query_selector('[contenteditable]')
        if textarea:
            print("✅ 找到文本输入框")
        else:
            print("❌ 未找到文本输入框")
        
        # 查找发布按钮
        publish_btn = page.query_selector('button:has-text("发布")')
        if publish_btn:
            print("✅ 找到发布按钮")
        else:
            print("❌ 未找到发布按钮")
        
        browser.close()

if __name__ == "__main__":
    test_creator()
