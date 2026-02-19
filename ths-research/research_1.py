#!/usr/bin/env python3
"""
同花顺数据采集研究 - 第1部分
测试各种数据获取方式
"""
import asyncio
from playwright.async_api import async_playwright
import json
import time

async def test_ths_data():
    """测试同花顺数据获取"""
    print("=" * 60)
    print("  同花顺数据采集研究")
    print("=" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        # 测试1: 同花顺首页
        print("\n[1] 测试同花顺首页...")
        await page.goto("https://www.10jqka.com.cn/")
        await page.wait_for_load_state("networkidle", timeout=15000)
        await asyncio.sleep(3)
        
        title = await page.title()
        print(f"    标题: {title}")
        
        # 查找所有可能的股票相关元素
        print("\n[2] 分析页面结构...")
        data = await page.evaluate('''() => {
            const info = {
                url: window.location.href,
                title: document.title,
                allLinks: [],
                allScripts: [],
                allIframes: []
            };
            
            // 链接
            document.querySelectorAll('a').forEach((el, i) => {
                if (i < 50) {
                    info.allLinks.push({
                        href: el.href?.substring(0, 100),
                        text: el.innerText?.substring(0, 50)
                    });
                }
            });
            
            return info;
        }''')
        
        print(f"    链接数量: {len(data['allLinks'])}")
        print(f"    标题: {data['title']}")
        
        # 测试2: 直接访问股票页面
        print("\n[3] 测试股票详情页...")
        
        stock_codes = [
            '600519',  # 贵州茅台
            '000001',  # 平安银行
            '600036',  # 招商银行
        ]
        
        for code in stock_codes:
            try:
                stock_url = f"https://stock.10jqka.com.cn/stockcode/{code}.html"
                print(f"\n    访问: {code}")
                await page.goto(stock_url, timeout=15000)
                await page.wait_for_load_state("domcontentloaded", timeout=10000)
                await asyncio.sleep(3)
                
                result = await page.evaluate('''() => {
                    const data = {
                        code: "''' + str(code) + '''",
                        title: document.title,
                        prices: [],
                        tables: []
                    };
                    
                    // 查找价格
                    const priceKeywords = ['price', 'current', 'stock-price', 'quotation'];
                    document.querySelectorAll('span, div, td').forEach(el => {
                        const text = el.innerText?.trim();
                        if (text && /^[¥￥$]?\\d+\\.?\\d*$/.test(text)) {
                            const parent = el.parentElement;
                            if (parent) {
                                data.prices.push({
                                    text: text,
                                    tag: el.tagName,
                                    parent: parent.tagName,
                                    class: el.className?.substring(0, 30)
                                });
                            }
                        }
                    });
                    
                    return data;
                }''')
                
                print(f"    标题: {result['title'][:50]}")
                print(f"    找到价格元素: {len(result['prices'])}")
                if result['prices']:
                    print(f"    示例价格: {result['prices'][0]['text']}")
                
            except Exception as e:
                print(f"    错误: {e}")
        
        # 测试3: API接口
        print("\n[4] 尝试查找API...")
        
        # 查看页面中的所有请求
        async def handle_request(request):
            url = request.url
            if '10jqka' in url and ('api' in url.lower() or 'json' in url.lower() or 'quote' in url.lower()):
                print(f"    发现API: {url[:100]}")
        
        page.on("request", handle_request)
        
        # 访问同花顺数据页面
        await page.goto("https://data.10jqka.com.cn/")
        await asyncio.sleep(3)
        
        print("\n[5] 分析data页面...")
        data_result = await page.evaluate('''() => {
            const links = [];
            document.querySelectorAll('a').forEach(el => {
                const href = el.href;
                const text = el.innerText?.trim();
                if (href && text && text.length < 30) {
                    links.push({href: href.substring(0, 80), text: text});
                }
            });
            return links.slice(0, 20);
        }''')
        
        print(f"    发现链接: {len(data_result)}")
        for link in data_result[:10]:
            print(f"      - {link['text']}: {link['href'][:60]}")
        
        await browser.close()
        print("\n" + "=" * 60)
        print("  研究完成")
        print("=" * 60)

if __name__ == '__main__':
    asyncio.run(test_ths_data())
