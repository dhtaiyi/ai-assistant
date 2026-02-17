#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书搜索提取 - 最终版
"""

from playwright.sync_api import sync_playwright
import json
import time
import sys

def extract_notes(page, limit=10):
    """提取笔记信息"""
    notes = []
    
    # 获取页面主要内容
    container = page.query_selector('main') or page.query_selector('[class*="container"]') or page.query_selector('body')
    
    if container:
        # 查找所有可点击的链接（通常是笔记）
        links = container.query_selector_all('a')[:limit*2]
        
        for link in links:
            try:
                href = link.get_attribute('href')
                if href and '/note/' in href:
                    # 获取父元素的文本内容作为标题
                    parent = link.evaluate_handle('el => el.parentElement')
                    text = ''
                    if parent:
                        text = parent.inner_text()[:200]
                    
                    if text and len(text) > 10:  # 过滤太短的文本
                        note = {
                            'title': text.split('\n')[0].strip()[:100],
                            'url': f'https://www.xiaohongshu.com{href}' if href.startswith('/') else href
                        }
                        
                        # 查找点赞数（可能在附近）
                        like_elem = link.query_selector('[class*="like"]') or link.query_selector('[class*="collect"]')
                        if like_elem:
                            note['likes'] = like_elem.inner_text().strip()
                        
                        if note['title'] not in [n['title'] for n in notes]:
                            notes.append(note)
                            
            except Exception:
                continue
    
    return notes[:limit]

def search(keyword):
    """搜索并提取"""
    print(f"\n🔍 搜索: {keyword}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        page = browser.new_page()
        
        try:
            # 访问搜索页
            url = f'https://www.xiaohongshu.com/search?keyword={keyword}'
            page.goto(url, timeout=20000, wait_until='domcontentloaded')
            time.sleep(3)
            
            print(f"   📄 标题: {page.title()}")
            
            # 提取笔记
            notes = extract_notes(page)
            print(f"   ✅ 提取 {len(notes)} 条笔记")
            
            return {
                'keyword': keyword,
                'url': url,
                'notes': notes,
                'count': len(notes)
            }
            
        except Exception as e:
            print(f"   ❌ 错误: {e}")
            return {'keyword': keyword, 'error': str(e)}
        finally:
            browser.close()

def main():
    if len(sys.argv) > 1:
        keywords = sys.argv[1:]
    else:
        keywords = ["穿搭", "美妆"]
    
    print("="*60)
    print("  🦞 小红书搜索提取")
    print("="*60)
    
    results = {}
    for kw in keywords:
        result = search(kw)
        results[kw] = result
        
        if 'notes' in result:
            print(f"\n📝 结果:")
            for i, note in enumerate(result['notes'][:5], 1):
                print(f"   {i}. {note['title'][:50]}")
                if note.get('url'):
                    print(f"      🔗 {note['url'][:60]}...")
    
    # 保存结果
    output = '/root/.openclaw/workspace/xiaohongshu-results.json'
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 结果已保存: {output}")

if __name__ == "__main__":
    main()
