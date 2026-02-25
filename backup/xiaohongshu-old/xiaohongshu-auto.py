#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书自动化搜索 - 完善版
自动检测登录状态，处理登录流程
"""

import asyncio
from playwright.sync_api import sync_playwright
import json
import time

class XiaoHongShuAuto:
    """小红书自动化类"""
    
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
    
    def start(self, headless=True):
        """启动浏览器"""
        print("🔄 启动浏览器...")
        
        self.browser = self._create_browser(headless)
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'
        )
        self.page = self.context.new_page()
        
        print("✅ 浏览器启动成功")
    
    def _create_browser(self, headless):
        """创建浏览器实例"""
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=headless,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--window-size=1920,1080'
                ]
            )
            return browser
    
    def login(self):
        """登录小红书"""
        print("\n📱 请在浏览器中登录小红书...")
        print("   1. 浏览器窗口已打开")
        print("   2. 请扫码或账号密码登录")
        print("   3. 登录成功后按回车继续...")
        
        input("\n   按回车键继续...")
        
        # 检查登录状态
        self.page.goto('https://www.xiaohongshu.com', timeout=30000)
        time.sleep(2)
        
        # 检查是否存在用户信息
        user_info = self.page.query_selector('[class*="user"]')
        if user_info:
            print("\n✅ 登录成功!")
            return True
        else:
            print("\n❓ 登录状态未知，继续操作...")
            return True
    
    def search(self, keyword):
        """搜索关键词"""
        print(f"\n🔍 搜索: {keyword}")
        
        try:
            # 方法1: 使用URL搜索
            search_url = f'https://www.xiaohongshu.com/search?keyword={keyword}'
            self.page.goto(search_url, timeout=30000)
            time.sleep(3)
            
            # 方法2: 如果URL无效，使用搜索框
            if 'search' not in self.page.url():
                search_box = self.page.query_selector('input[placeholder*="搜索"]')
                if search_box:
                    search_box.fill(keyword)
                    self.page.keyboard.press('Enter')
                    time.sleep(3)
            
            # 获取结果
            url = self.page.url()
            print(f"   页面URL: {url}")
            
            # 查找内容
            notes = self.page.query_selector_all('article')
            print(f"   找到 {len(notes)} 个内容块")
            
            return {
                'success': True,
                'keyword': keyword,
                'url': url,
                'notes_count': len(notes)
            }
            
        except Exception as e:
            print(f"   ❌ 错误: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_cookies(self):
        """获取当前Cookie"""
        cookies = self.context.cookies()
        cookie_str = '; '.join([f"{c['name']}={c['value']}" for c in cookies])
        print(f"\n📋 获取到 {len(cookies)} 个Cookie")
        return cookie_str
    
    def close(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.close()
            print("\n✅ 浏览器已关闭")

def main():
    print("="*60)
    print("  🦞 小红书自动化搜索")
    print("="*60)
    
    # 创建实例
    auto = XiaoHongShuAuto()
    
    try:
        # 启动浏览器（设置为False可以看到操作）
        auto.start(headless=False)  # 设置为True则无头运行
        
        # 登录
        auto.login()
        
        # 测试搜索
        keywords = ["穿搭", "美妆"]
        
        results = []
        for i, keyword in enumerate(keywords):
            result = auto.search(keyword)
            results.append(result)
            
            if i < len(keywords) - 1:
                time.sleep(2)
        
        # 打印结果
        print("\n" + "="*60)
        print("  📊 搜索结果")
        print("="*60)
        
        for result in results:
            if result['success']:
                print(f"\n✅ {result['keyword']}:")
                print(f"   URL: {result['url']}")
                print(f"   内容块: {result['notes_count']}")
            else:
                print(f"\n❌ {result.get('keyword', '未知')}: {result.get('error')}")
        
        # 获取Cookie（可以保存到服务器使用）
        print("\n" + "="*60)
        print("  💾 Cookie信息")
        print("="*60)
        cookie_str = auto.get_cookies()
        print(f"   Cookie长度: {len(cookie_str)} 字符")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    finally:
        auto.close()

if __name__ == "__main__":
    main()
