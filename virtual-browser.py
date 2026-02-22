#!/usr/bin/env python3
"""
虚拟浏览器 - 可视化网页展示
使用Playwright打开网页并生成截图
"""

import json
import base64
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse, parse_qs
import threading

# 全局浏览器实例
browser = None
playwright_instance = None
port = 18090

# 代理配置
PROXY_SERVER = "socks5://xiaoyu:socks5pass123@10.0.0.15:1080"

def get_browser():
    global browser, playwright_instance
    if browser is None:
        playwright_instance = sync_playwright().start()
        browser = playwright_instance.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
    return browser

def close_browser():
    global browser, playwright_instance
    if browser:
        browser.close()
        browser = None
    if playwright_instance:
        playwright_instance.stop()
        playwright_instance = None

class VirtualBrowserHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = '''
<!DOCTYPE html>
<html>
<head>
    <title>虚拟浏览器</title>
    <meta charset="utf-8">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px;
            background: #f5f5f5;
        }
        h1 { color: #333; }
        .form-group { margin: 20px 0; }
        input[type="text"] { 
            width: 70%; 
            padding: 10px; 
            font-size: 16px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button { 
            padding: 10px 20px; 
            font-size: 16px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover { background: #0056b3; }
        #result { margin-top: 20px; }
        #screenshot { 
            max-width: 100%; 
            border: 1px solid #ddd;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        #error { color: red; margin-top: 10px; }
        .info { color: #666; font-size: 14px; margin-top: 5px; }
    </style>
</head>
<body>
    <h1>🌐 虚拟浏览器</h1>
    <p class="info">输入网址，我来帮你打开网页并截图</p>
    
    <div class="form-group">
        <input type="text" id="url" placeholder="输入网址，例如: https://www.baidu.com" value="https://www.baidu.com">
        <button onclick="openUrl()">打开网页</button>
    </div>
    
    <div id="result">
        <img id="screenshot" style="display:none;">
        <pre id="error"></pre>
    </div>

    <script>
        async function openUrl() {
            const url = document.getElementById('url').value;
            const img = document.getElementById('screenshot');
            const error = document.getElementById('error');
            
            img.style.display = 'none';
            error.textContent = '正在打开...';
            
            try {
                const response = await fetch('/browse?url=' + encodeURIComponent(url));
                const data = await response.json();
                
                if (data.error) {
                    error.textContent = '错误: ' + data.error;
                } else {
                    img.src = 'data:image/png;base64,' + data.screenshot;
                    img.style.display = 'block';
                    error.textContent = '';
                }
            } catch(e) {
                error.textContent = '请求失败: ' + e.message;
            }
        }
    </script>
</body>
</html>
            '''
            self.wfile.write(html.encode())
        else:
            self.send_error(404)
    
    def do_GET_browse(self, url):
        try:
            b = get_browser()
            page = b.new_page(viewport={'width': 1280, 'height': 800})
            page.goto(url, wait_until='networkidle', timeout=30000)
            screenshot = page.screenshot()
            page.close()
            
            b64 = base64.b64encode(screenshot).decode()
            return {'screenshot': b64, 'url': url}
        except Exception as e:
            return {'error': str(e)}

    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_html().encode())
        elif parsed.path == '/browse':
            params = parse_qs(parsed.query)
            url = params.get('url', [''])[0]
            
            if not url:
                self.send_error(400, 'Missing url parameter')
                return
            
            # 添加http:// if missing
            if not url.startswith('http'):
                url = 'http://' + url
            
            result = self.browse_url(url)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        else:
            self.send_error(404)
    
    def browse_url(self, url):
        try:
            b = get_browser()
            page = b.new_page(viewport={'width': 1280, 'height': 800})
            page.goto(url, wait_until='networkidle', timeout=30000)
            screenshot = page.screenshot()
            page.close()
            
            b64 = base64.b64encode(screenshot).decode()
            return {'screenshot': b64, 'url': url}
        except Exception as e:
            return {'error': str(e)}
    
    def get_html(self):
        return '''<!DOCTYPE html>
<html>
<head>
    <title>虚拟浏览器</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
        h1 { color: #333; }
        .form-group { margin: 20px 0; }
        input[type="text"] { width: 70%; padding: 10px; font-size: 16px; border: 1px solid #ddd; border-radius: 4px; }
        button { padding: 10px 20px; font-size: 16px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #0056b3; }
        #screenshot { max-width: 100%; border: 1px solid #ddd; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        #error { color: red; margin-top: 10px; }
        .info { color: #666; font-size: 14px; margin-top: 5px; }
    </style>
</head>
<body>
    <h1>🌐 虚拟浏览器</h1>
    <p class="info">输入网址，我来帮你打开网页并截图</p>
    <div class="form-group">
        <input type="text" id="url" placeholder="输入网址" value="https://www.baidu.com">
        <button onclick="openUrl()">打开网页</button>
    </div>
    <div id="result">
        <img id="screenshot" style="display:none;">
        <pre id="error"></pre>
    </div>
    <script>
        async function openUrl() {
            const url = document.getElementById('url').value;
            const img = document.getElementById('screenshot');
            const error = document.getElementById('error');
            img.style.display = 'none';
            error.textContent = '正在打开...';
            try {
                const response = await fetch('/browse?url=' + encodeURIComponent(url));
                const data = await response.json();
                if (data.error) { error.textContent = '错误: ' + data.error; }
                else { img.src = 'data:image/png;base64,' + data.screenshot; img.style.display = 'block'; error.textContent = ''; }
            } catch(e) { error.textContent = '请求失败: ' + e.message; }
        }
    </script>
</body>
</html>'''

def run_server():
    server = HTTPServer(('0.0.0.0', port), VirtualBrowserHandler)
    print(f'虚拟浏览器服务已启动: http://localhost:{port}')
    print(f'或者通过宿主机访问: http://10.0.0.15:{port}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n关闭浏览器...')
        close_browser()
        server.shutdown()

if __name__ == '__main__':
    run_server()
