#!/usr/bin/env python3
"""测试创作者功能和发贴"""

from playwright.sync_api import sync_playwright
import json

def test_creation():
    """测试创作者功能"""
    
    print("🔍 测试创作者功能...")
    
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
        
        # 访问首页
        print("\n📱 访问首页...")
        page.goto('https://www.xiaohongshu.com', timeout=20000)
        page.wait_for_timeout(3000)
        
        print(f"标题: {page.title()}")
        print(f"URL: {page.url}")
        
        # 检查登录状态
        print("\n👤 检查登录状态...")
        user_elem = page.query_selector('[class*="user"]') or page.query_selector('[class*="nickname"]')
        if user_elem:
            print(f"✅ 已登录: {user_elem.inner_text()[:50]}")
        else:
            print("❓ 未找到用户信息")
        
        # 检查创作者入口
        print("\n🔍 查找创作者入口...")
        
        # 查找创作者相关按钮
        creator_btns = page.query_selector_all('a:has-text("创作")') or \
                      page.query_selector_all('button:has-text("创作")') or \
                      page.query_selector_all('a:has-text("发布")')
        
        if creator_btns:
            print(f"✅ 找到 {len(creator_btns)} 个创作者入口")
            for i, btn in enumerate(creator_btns[:3], 1):
                text = btn.inner_text()[:50]
                href = btn.get_attribute('href') or '无链接'
                print(f"   {i}. {text} -> {href}")
        else:
            print("❌ 未找到创作者入口")
        
        # 查找+号按钮（发贴）
        plus_btn = page.query_selector('button:has-text("+")') or \
                  page.query_selector('[class*="plus"]') or \
                  page.query_selector('[class*="create"]')
        
        if plus_btn:
            print("\n✅ 找到+号/创建按钮")
            plus_btn.click()
            page.wait_for_timeout(2000)
            print(f"点击后URL: {page.url}")
        
        # 检查页面中所有链接
        print("\n🔗 页面中的链接:")
        links = page.query_selector_all('a[href]')
        for link in links[:10]:
            href = link.get_attribute('href')
            text = link.inner_text()[:30]
            if href and ('creator' in href or 'post' in href or 'publish' in href or 'write' in href):
                print(f"   • {text}: {href}")
        
        browser.close()

if __name__ == "__main__":
    test_creation()
