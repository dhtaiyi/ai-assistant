#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 远程浏览器控制客户端
让OpenClaw可以通过API控制Chrome浏览器
"""

import requests
import json
import time

class RemoteBrowser:
    """远程浏览器控制器"""
    
    def __init__(self, server_url='http://localhost:9999'):
        self.server_url = server_url.rstrip('/')
    
    def _execute(self, command_type, **kwargs):
        """执行命令"""
        command = {'type': command_type, **kwargs}
        
        try:
            response = requests.post(
                f'{self.server_url}/api/execute',
                json={'command': command},
                timeout=30
            )
            
            return response.json()
        
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': f'无法连接到浏览器控制服务器 ({self.server_url})'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def navigate(self, url):
        """导航到URL"""
        return self._execute('navigate', url=url)
    
    def click(self, selector, index=0):
        """点击元素"""
        return self._execute('click', selector=selector, index=index)
    
    def type_text(self, selector, text):
        """输入文本"""
        return self._execute('type', selector=selector, text=text)
    
    def scroll(self, direction='down', amount=500):
        """滚动页面"""
        return self._execute('scroll', direction=direction, amount=amount)
    
    def wait(self, duration=1000):
        """等待"""
        return self._execute('wait', duration=duration)
    
    def screenshot(self):
        """截图"""
        return self._execute('screenshot')
    
    def evaluate(self, script):
        """执行JavaScript"""
        return self._execute('evaluate', script=script)
    
    def get_page_info(self):
        """获取页面信息"""
        return self._execute('getPageInfo')
    
    def find_element(self, selector):
        """查找元素"""
        return self._execute('findElement', selector=selector)
    
    def execute_script(self, code):
        """执行脚本"""
        return self._execute('executeScript', code=code)
    
    def status(self):
        """检查状态"""
        try:
            response = requests.get(f'{self.server_url}/api/status', timeout=5)
            return response.json()
        except:
            return {'success': False, 'error': '服务器未运行'}
    
    def open_xiaohongshu(self):
        """打开小红书"""
        return self.navigate('https://www.xiaohongshu.com')
    
    def publish_note(self, title, content):
        """发布笔记（需要配合小红书MCP）"""
        # 先获取页面信息
        info = self.get_page_info()
        
        if info.get('success'):
            # 如果在小红书发布页面，可以尝试填写表单
            self.evaluate(f'''
                const titleInput = document.querySelector('input[placeholder*="标题"]');
                if (titleInput) titleInput.value = "{title}";
                
                const contentInput = document.querySelector('textarea[placeholder*="正文"]');
                if (contentInput) contentInput.value = `{content}`;
            ''')
        
        return info
    
    def xiaohongshu_login_check(self):
        """检查小红书登录状态"""
        self.evaluate('''
            const loginBtn = document.querySelector('button:contains("登录")');
            const userInfo = document.querySelector('.user-info, .nickname');
            
            if (userInfo) {
                "已登录";
            } else if (loginBtn) {
                "未登录";
            } else {
                "状态未知";
            }
        ''')
        
        return self.evaluate('document.querySelector(".user-name, .nick-name")?.innerText || "未找到用户信息"')


# 使用示例
if __name__ == '__main__':
    browser = RemoteBrowser()
    
    # 检查状态
    print("🔍 检查服务器状态...")
    status = browser.status()
    print(json.dumps(status, indent=2, ensure_ascii=False))
    
    if status.get('success'):
        # 打开小红书
        print("\n🌐 打开小红书...")
        result = browser.open_xiaohongshu()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 等待加载
        print("\n⏳ 等待页面加载...")
        time.sleep(3)
        
        # 获取页面信息
        print("\n📄 获取页面信息...")
        info = browser.get_page_info()
        print(json.dumps(info, indent=2, ensure_ascii=False))
    else:
        print("\n❌ 服务器未运行，请先启动服务器！")
