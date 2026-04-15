#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
浏览器控制程序
使用 Playwright 控制浏览器
"""

import asyncio
from playwright.async_api import async_playwright
from typing import Optional, Dict, List, Any
import json
from datetime import datetime


class BrowserController:
    """浏览器控制器"""
    
    def __init__(self, headless: bool = True):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.headless = headless
    
    async def start(self):
        """启动浏览器"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        return self
    
    async def stop(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()
    
    async def navigate(self, url: str) -> Dict:
        """导航到URL"""
        await self.page.goto(url)
        return {
            'success': True,
            'url': self.page.url,
            'title': await self.page.title()
        }
    
    async def click(self, selector: str, index: int = 0) -> Dict:
        """点击元素"""
        elements = await self.page.query_selector_all(selector)
        if not elements:
            return {'success': False, 'error': f'元素未找到: {selector}'}
        
        await elements[index].click()
        return {
            'success': True,
            'clicked': selector
        }
    
    async def type(self, selector: str, text: str) -> Dict:
        """输入文本"""
        await self.page.fill(selector, text)
        return {
            'success': True,
            'typed': selector,
            'text': text
        }
    
    async def scroll(self, direction: str = 'down', amount: int = 500) -> Dict:
        """滚动页面"""
        if direction == 'down':
            await self.page.evaluate(f'window.scrollBy(0, {amount})')
        elif direction == 'up':
            await self.page.evaluate(f'window.scrollBy(0, -{amount})')
        elif direction == 'top':
            await self.page.evaluate('window.scrollTo(0, 0)')
        elif direction == 'bottom':
            await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        
        return {'success': True, 'direction': direction}
    
    async def wait(self, seconds: float = 1) -> Dict:
        """等待"""
        await asyncio.sleep(seconds)
        return {'success': True, 'waited': seconds}
    
    async def get_page_info(self) -> Dict:
        """获取页面信息"""
        return {
            'success': True,
            'url': self.page.url,
            'title': await self.page.title()
        }
    
    async def get_html(self) -> str:
        """获取页面HTML"""
        return await self.page.content()
    
    async def get_text(self, selector: str) -> str:
        """获取元素文本"""
        element = await self.page.query_selector(selector)
        if element:
            return await element.inner_text()
        return ''
    
    async def get_stock_data(self) -> Dict:
        """获取股票数据（同花顺）"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'url': self.page.url
        }
        
        # 尝试多种选择器
        price_selectors = [
            '.stock-price .price',
            '#quotation-entry .price',
            '.current-price',
            '.stock-current .price',
            '[class*="price"]'
        ]
        
        change_selectors = [
            '.stock-change .change',
            '#quotation-entry .change',
            '.change-percent',
            '[class*="change"]'
        ]
        
        # 获取价格
        for sel in price_selectors:
            elements = await self.page.query_selector_all(sel)
            if elements:
                text = await elements[0].inner_text()
                if text and text.strip():
                    data['price'] = text.strip()
                    break
        
        # 获取涨跌幅
        for sel in change_selectors:
            elements = await self.page.query_selector_all(sel)
            if elements:
                text = await elements[0].inner_text()
                if text and text.strip():
                    data['change'] = text.strip()
                    break
        
        # 如果没找到，尝试获取页面中所有数字
        if 'price' not in data:
            await self.page.evaluate('''() => {
                const allText = [];
                document.querySelectorAll('span, div, td').forEach(el => {
                    const text = el.innerText?.trim();
                    if (text && /^\\d+\\.?\\d*$/.test(text) && text.length < 15) {
                        allText.push(text);
                    }
                });
                window.__foundPrices = allText.slice(0, 10);
            }''')
            prices = await self.page.evaluate('window.__foundPrices || []')
            data['prices'] = prices
        
        return data
    
    async def execute_js(self, code: str) -> Any:
        """执行JavaScript"""
        return await self.page.evaluate(f'() => ({code})')


# 便捷函数
async def main():
    """测试示例"""
    async with BrowserController() as controller:
        # 打开同花顺
        print("🌐 打开同花顺...")
        result = await controller.navigate('https://www.10jqka.com.cn')
        print(f"标题: {result['title']}")
        
        # 等待加载
        await controller.wait(3)
        
        # 获取股票数据
        print("📊 获取股票数据...")
        data = await controller.get_stock_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    asyncio.run(main())
