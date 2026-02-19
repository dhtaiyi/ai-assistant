#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 远程浏览器控制服务器
提供HTTP API，让OpenClaw可以远程控制Chrome浏览器
"""

import http.server
import socketserver
import json
import urllib.request
import urllib.parse
import threading
import time
import os
from urllib.parse import parse_qs

# 配置
PORT = 9999
EXTENSION_PORT = 9998

class BrowserController:
    """浏览器控制器"""
    
    def __init__(self):
        self.extension_url = f"http://localhost:{EXTENSION_PORT}"
    
    def send_command(self, command):
        """发送命令到Chrome扩展"""
        try:
            data = json.dumps(command).encode('utf-8')
            req = urllib.request.Request(
                self.extension_url,
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = response.read().decode('utf-8')
                return json.loads(result)
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def navigate(self, url):
        """导航到URL"""
        return self.send_command({'type': 'navigate', 'url': url})
    
    def click(self, selector, index=0):
        """点击元素"""
        return self.send_command({'type': 'click', 'selector': selector, 'index': index})
    
    def type(self, selector, text):
        """输入文本"""
        return self.send_command({'type': 'type', 'selector': selector, 'text': text})
    
    def scroll(self, direction='down', amount=500):
        """滚动页面"""
        return self.send_command({'type': 'scroll', 'direction': direction, 'amount': amount})
    
    def wait(self, duration=1000):
        """等待"""
        return self.send_command({'type': 'wait', 'duration': duration})
    
    def screenshot(self):
        """截图"""
        return self.send_command({'type': 'screenshot'})
    
    def evaluate(self, script):
        """执行JavaScript"""
        return self.send_command({'type': 'evaluate', 'script': script})
    
    def get_page_info(self):
        """获取页面信息"""
        return self.send_command({'type': 'getPageInfo'})
    
    def find_element(self, selector):
        """查找元素"""
        return self.send_command({'type': 'findElement', 'selector': selector})
    
    def execute_script(self, code):
        """执行脚本"""
        return self.send_command({'type': 'executeScript', 'code': code})


class APIHandler(http.server.BaseHTTPRequestHandler):
    """HTTP请求处理器"""
    
    controller = BrowserController()
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[{self.log_date_time_string()}] {format % args}")
    
    def do_GET(self):
        """处理GET请求"""
        path = self.path.split('?')[0]
        
        if path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'success': True, 'status': 'running', 'port': PORT}
            self.wfile.write(json.dumps(response).encode('utf-8'))
        
        elif path == '/page':
            result = self.controller.get_page_info()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
        
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def do_POST(self):
        """处理POST请求"""
        path = self.path.split('?')[0]
        
        # 读取请求体
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(body)
            command = data.get('command', {})
            cmd_type = command.get('type', '')
            
            # 执行命令
            if cmd_type == 'navigate':
                result = self.controller.navigate(command.get('url'))
            elif cmd_type == 'click':
                result = self.controller.click(
                    command.get('selector'),
                    command.get('index', 0)
                )
            elif cmd_type == 'type':
                result = self.controller.type(
                    command.get('selector'),
                    command.get('text')
                )
            elif cmd_type == 'scroll':
                result = self.controller.scroll(
                    command.get('direction', 'down'),
                    command.get('amount', 500)
                )
            elif cmd_type == 'wait':
                result = self.controller.wait(command.get('duration', 1000))
            elif cmd_type == 'screenshot':
                result = self.controller.screenshot()
            elif cmd_type == 'evaluate':
                result = self.controller.evaluate(command.get('script', ''))
            elif cmd_type == 'getPageInfo':
                result = self.controller.get_page_info()
            elif cmd_type == 'findElement':
                result = self.controller.find_element(command.get('selector', ''))
            elif cmd_type == 'executeScript':
                result = self.controller.execute_script(command.get('code', ''))
            else:
                result = {'success': False, 'error': f'未知命令: {cmd_type}'}
            
            # 发送响应
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode('utf-8'))
    
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


def run_server():
    """运行服务器"""
    # 创建HTTP服务器
    with socketserver.TCPServer(("", PORT), APIHandler) as httpd:
        print(f"=" * 60)
        print(f"  OpenClaw 远程浏览器控制服务器")
        print(f"=" * 60)
        print(f"")
        print(f"  🌐 监听端口: {PORT}")
        print(f"  📡 API端点: http://localhost:{PORT}")
        print(f"")
        print(f"  📋 API命令:")
        print(f"")
        print(f"  POST /api/execute")
        print(f"    {{")
        print(f"      \"command\": {{")
        print(f"        \"type\": \"navigate\",")
        print(f"        \"url\": \"https://www.xiaohongshu.com\"")
        print(f"      }}")
        print(f"    }}")
        print(f"")
        print(f"  POST /api/execute")
        print(f"    {{")
        print(f"      \"command\": {{")
        print(f"        \"type\": \"click\",")
        print(f"        \"selector\": \".btn-primary\"")
        print(f"      }}")
        print(f"    }}")
        print(f"")
        print(f"  GET /api/status")
        print(f"  GET /api/page")
        print(f"")
        print(f"=" * 60)
        print(f"")
        print(f"  ⚠️  请确保Chrome扩展已安装并运行！")
        print(f"")
        print(f"  💡 使用方法:")
        print(f"    1. 安装Chrome扩展")
        print(f"    2. 启动此服务器")
        print(f"    3. OpenClaw通过API调用控制浏览器")
        print(f"")
        print(f"=" * 60)
        print(f"")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n\n👋 服务器已停止")


if __name__ == '__main__':
    run_server()
