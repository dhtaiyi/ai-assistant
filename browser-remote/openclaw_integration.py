#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 远程浏览器控制集成
让OpenClaw AI可以直接通过API控制浏览器
"""

import requests
import json
import time
from datetime import datetime

class OpenClawBrowser:
    """
    OpenClaw 远程浏览器控制器
    提供简洁的API让AI可以直接调用
    """
    
    def __init__(self, server_url='http://localhost:9999'):
        self.server_url = server_url.rstrip('/')
        self.command_history = []
    
    def _call(self, command):
        """调用API"""
        try:
            response = requests.post(
                f'{self.server_url}/api/execute',
                json={'command': command},
                timeout=30
            )
            result = response.json()
            
            # 记录命令历史
            self.command_history.append({
                'time': datetime.now().isoformat(),
                'command': command,
                'result': result
            })
            
            return result
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'command': command
            }
    
    # ============ 基础操作 ============
    
    def go_to(self, url):
        """打开网页"""
        return self._call({'type': 'navigate', 'url': url})
    
    def refresh(self):
        """刷新页面"""
        return self._call({'type': 'navigate', 'url': 'current'})
    
    def back(self):
        """后退"""
        # 通过JavaScript实现
        return self._call({'type': 'evaluate', 'script': 'history.back()'})
    
    def forward(self):
        """前进"""
        return self._call({'type': 'evaluate', 'script': 'history.forward()'})
    
    def scroll_down(self, amount=500):
        """向下滚动"""
        return self._call({'type': 'scroll', 'direction': 'down', 'amount': amount})
    
    def scroll_up(self, amount=500):
        """向上滚动"""
        return self._call({'type': 'scroll', 'direction': 'up', 'amount': amount})
    
    def scroll_to_bottom(self):
        """滚动到底部"""
        return self._call({'type': 'scroll', 'direction': 'bottom'})
    
    def scroll_to_top(self):
        """滚动到顶部"""
        return self._call({'type': 'scroll', 'direction': 'top'})
    
    def wait(self, seconds=1):
        """等待"""
        return self._call({'type': 'wait', 'duration': seconds * 1000})
    
    # ============ 元素操作 ============
    
    def click(self, selector, index=0):
        """点击元素"""
        return self._call({
            'type': 'click',
            'selector': selector,
            'index': index
        })
    
    def type(self, selector, text):
        """输入文本"""
        return self._call({
            'type': 'type',
            'selector': selector,
            'text': text
        })
    
    def find(self, selector):
        """查找元素"""
        return self._call({
            'type': 'findElement',
            'selector': selector
        })
    
    # ============ 高级操作 ============
    
    def get_html(self):
        """获取页面HTML"""
        return self._call({
            'type': 'evaluate',
            'script': 'document.body.innerHTML'
        })
    
    def get_title(self):
        """获取页面标题"""
        return self._call({
            'type': 'evaluate',
            'script': 'document.title'
        })
    
    def get_url(self):
        """获取当前URL"""
        return self._call({
            'type': 'evaluate',
            'script': 'window.location.href'
        })
    
    def screenshot(self):
        """截图"""
        return self._call({'type': 'screenshot'})
    
    def run_js(self, code):
        """执行JavaScript代码"""
        return self._call({
            'type': 'evaluate',
            'script': code
        })
    
    def get_info(self):
        """获取页面完整信息"""
        return self._call({'type': 'getPageInfo'})
    
    # ============ 小红书专用 ============
    
    def xiaohongshu_open(self):
        """打开小红书"""
        return self.go_to('https://www.xiaohongshu.com')
    
    def xiaohongshu_publish(self, title, content):
        """
        发布小红书笔记
        注意：需要先手动登录
        """
        # 1. 检查是否在小红书
        info = self.get_info()
        if not info.get('success'):
            return {'success': False, 'error': '无法获取页面信息'}
        
        # 2. 点击发布按钮
        self.click('button:contains("发布")', timeout=3)
        time.sleep(2)
        
        # 3. 填写标题
        self.click('input[placeholder*="标题"]')
        self.type('input[placeholder*="标题"]', title)
        
        # 4. 填写内容
        self.click('textarea[placeholder*="正文"]')
        self.type('textarea[placeholder*="正文"]', content)
        
        return {
            'success': True,
            'message': '笔记已填写，请手动确认发布'
        }
    
    def xiaohongshu_check_login(self):
        """检查小红书登录状态"""
        result = self.find('.user-info, .nick-name, [class*="user"]')
        
        if result.get('success') and result.get('result'):
            return {
                'success': True,
                'logged_in': True,
                'message': '已登录'
            }
        else:
            return {
                'success': True,
                'logged_in': False,
                'message': '未登录'
            }
    
    # ============ 工具方法 ============
    
    def status(self):
        """检查连接状态"""
        try:
            response = requests.get(f'{self.server_url}/api/status', timeout=5)
            return response.json()
        except:
            return {'success': False, 'error': '服务器未运行'}
    
    def history(self, limit=10):
        """获取命令历史"""
        return self.command_history[-limit:]
    
    def clear_history(self):
        """清除命令历史"""
        self.command_history = []


# 便捷函数
def xiaohongshu_publish(browser, title, content):
    """发布小红书笔记"""
    return browser.xiaohongshu_publish(title, content)

def get_page_content(browser):
    """获取页面内容"""
    info = browser.get_info()
    if info.get('success'):
        return info.get('result', {}).get('body', '')
    return ''


# 使用示例
if __name__ == '__main__':
    browser = OpenClawBrowser()
    
    print("=" * 60)
    print("  OpenClaw 远程浏览器控制")
    print("=" * 60)
    print()
    
    # 检查状态
    status = browser.status()
    print(f"服务器状态: {status.get('status', '未知')}")
    print()
    
    if status.get('success'):
        print("可用命令:")
        print("  browser.go_to(url)")
        print("  browser.click(selector)")
        print("  browser.type(selector, text)")
        print("  browser.scroll_down()")
        print("  browser.screenshot()")
        print("  browser.get_info()")
        print()
        print("小红书专用:")
        print("  browser.xiaohongshu_open()")
        print("  browser.xiaohongshu_publish(title, content)")
        print("  browser.xiaohongshu_check_login()")
    else:
        print("⚠️  服务器未运行，请先启动服务器！")
    
    print()
    print("=" * 60)
