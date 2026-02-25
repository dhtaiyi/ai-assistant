#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书搜索 - 优化版
解决超时和内存问题
"""

from playwright.sync_api import sync_playwright
import json
import sys

def search(keyword):
    """搜索单个关键词"""
    print(f"\n🔍 {keyword}")
    
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--memory-pressure-off',
                '--max_old_space_size=256'
            ]
        )
        
        page = browser.new_page()
        
        try:
            # 访问
            url = f'https://www.xiaohongshu.com/search?keyword={keyword}'
            page.goto(url, timeout=15000, wait_until='domcontentloaded')
            
            print(f"   📄 {page.title()}")
            
            # 提取笔记链接
            all_links = page.query_selector_all('a')
            notes = []
            
            for link in all_links:
                try:
                    href = link.get_attribute('href')
                    if href and '/note/' in href:
                        title = link.inner_text()[:80].strip()
                        if title and len(title) > 5:
                            if title not in [n['title'] for n in notes]:
                                notes.append({
                                    'title': title,
                                    'url': f'https://www.xiaohongshu.com{href}' if href.startswith('/') else href
                                })
                except:
                    continue
            
            print(f"   ✅ {len(notes)} 条笔记")
            return {'keyword': keyword, 'notes': notes[:10]}
            
        except Exception as e:
            print(f"   ❌ {e}")
            return {'keyword': keyword, 'error': str(e)}
        
        finally:
            browser.close()

def main():
    keywords = sys.argv[1:] if len(sys.argv) > 1 else ["穿搭"]
    
    print("="*50)
    print("  🦞 小红书搜索-优化版")
    print("="*50)
    
    results = {}
    for kw in keywords:
        result = search(kw)
        results[kw] = result
        
        if 'notes' in result:
            for i, note in enumerate(result['notes'][:3], 1):
                print(f"   {i}. {note['title'][:40]}")
    
    # 保存
    with open('/root/.openclaw/workspace/xiaohongshu-output.json', 'w') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 已保存")

if __name__ == "__main__":
    main()
