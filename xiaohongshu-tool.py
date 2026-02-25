#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书工具箱 - 集成版
搜索 + Cookie管理 + 自动刷新
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

# 配置
COOKIE_FILE = '/root/.openclaw/workspace/xiaohongshu-cookies.json'
RESULT_FILE = '/root/.openclaw/workspace/xiaohongshu-results.json'

class XiaoHongShuTool:
    """小红书工具箱"""
    
    def __init__(self):
        self.cookies = {}
        self.cookie_saved_at = None
        self.load_cookies()
    
    # ============ Cookie管理 ============
    
    def load_cookies(self):
        """加载Cookie"""
        if os.path.exists(COOKIE_FILE):
            try:
                with open(COOKIE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.cookies = data.get('cookies', {})
                    self.cookie_saved_at = data.get('saved_at')
                    return True
            except:
                pass
        return False
    
    def save_cookies(self, cookies):
        """保存Cookie"""
        data = {
            'cookies': cookies,
            'saved_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(hours=24)).isoformat()
        }
        with open(COOKIE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.cookies = cookies
        self.cookie_saved_at = data['saved_at']
        print(f"✅ Cookie已保存: {len(cookies)} 个")
    
    def get_cookie_status(self):
        """获取Cookie状态"""
        if not self.cookies:
            return "❌ 无Cookie", False
        
        if self.cookie_saved_at:
            saved_time = datetime.fromisoformat(self.cookie_saved_at)
            elapsed = (datetime.now() - saved_time).total_seconds()
            hours = elapsed / 3600
            
            if hours < 1:
                age = f"{int(elapsed)}分钟前"
            else:
                age = f"{hours:.1f}小时前"
            
            status = "✅ 有效" if hours < 6 else "⚠️ 建议刷新"
            return f"{status} ({age})", True
        
        return "❌ 未知", False
    
    def save_cookie_from_string(self, cookie_string):
        """从字符串保存Cookie"""
        cookies = {}
        for item in cookie_string.split(';'):
            item = item.strip()
            if '=' in item:
                k, v = item.split('=', 1)
                cookies[k.strip()] = v.strip()
        self.save_cookies(cookies)
        return cookies
    
    # ============ 搜索功能 ============
    
    def search(self, keyword):
        """搜索关键词"""
        print(f"\n🔍 搜索: {keyword}")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'
            )
            
            # 如果有保存的Cookie，使用它
            if self.cookies:
                for name, value in self.cookies.items():
                    context.add_cookies([{
                        'name': name,
                        'value': value,
                        'domain': '.xiaohongshu.com',
                        'path': '/'
                    }])
            
            page = context.new_page()
            
            try:
                # 访问搜索页
                url = f'https://www.xiaohongshu.com/search?keyword={keyword}'
                page.goto(url, timeout=20000)
                
                # 等待渲染
                page.wait_for_selector('div', timeout=10000)
                time.sleep(3)
                
                # 获取内容
                text = page.inner_text('body')
                lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 3]
                
                print(f"   ✅ 获取 {len(lines)} 行内容")
                
                return {
                    'keyword': keyword,
                    'success': True,
                    'lines': lines[:30],
                    'count': len(lines)
                }
                
            except Exception as e:
                print(f"   ❌ 错误: {e}")
                return {'keyword': keyword, 'success': False, 'error': str(e)}
            
            finally:
                browser.close()
    
    def search_multiple(self, keywords):
        """搜索多个关键词"""
        print("="*60)
        print("  🦞 小红书工具箱")
        print("="*60)
        
        # Cookie状态
        status, valid = self.get_cookie_status()
        print(f"\n📋 Cookie状态: {status}")
        
        results = {}
        
        for i, keyword in enumerate(keywords, 1):
            print(f"\n[{i}/{len(keywords)}] {keyword}")
            
            result = self.search(keyword)
            results[keyword] = result
            
            if result.get('success'):
                print(f"   📊 {result['count']} 行内容")
                for line in result['lines'][:3]:
                    if len(line) > 10:
                        print(f"   • {line[:40]}")
            
            # 每次搜索后等待
            if i < len(keywords):
                time.sleep(2)
        
        # 保存结果
        with open(RESULT_FILE, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 结果已保存: {RESULT_FILE}")
        
        return results

# ============ 主程序 ============

def main():
    tool = XiaoHongShuTool()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'status':
            status, valid = tool.get_cookie_status()
            print(f"\n📊 Cookie状态: {status}")
            print(f"数量: {len(tool.cookies)}")
            print(f"保存时间: {tool.cookie_saved_at}")
            
        elif command == 'save':
            if len(sys.argv) > 2:
                cookie_str = ' '.join(sys.argv[2:])
                tool.save_cookie_from_string(cookie_str)
            else:
                print("用法: python3 tool.py save 'Cookie字符串'")
        
        elif command == 'search':
            keywords = sys.argv[2:] if len(sys.argv) > 2 else ['穿搭']
            tool.search_multiple(keywords)
        
        elif command == 'help':
            print("""
使用方法:
  python3 xiaohongshu-tool.py status          # 查看Cookie状态
  python3 xiaohongshu-tool.py save "Cookie"  # 保存Cookie
  python3 xiaohongshu-tool.py search 穿搭     # 搜索关键词
  python3 xiaohongshu-tool.py search 穿搭 美妆  # 搜索多个

示例:
  python3 xiaohongshu-tool.py save "a1=xxx; web_session=xxx"
  python3 xiaohongshu-tool.py search 穿搭 美妆 美食
            """)
        
        else:
            # 当作关键词搜索
            tool.search_multiple([command] + sys.argv[2:])
    
    else:
        # 默认搜索
        tool.search_multiple(['穿搭'])

if __name__ == "__main__":
    main()
