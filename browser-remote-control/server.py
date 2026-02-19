#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 远程浏览器控制服务器
用户运行此脚本，我就可以远程控制他的浏览器

使用方法:
    python server.py --port 9999

然后我会连接到这个地址来控制浏览器
"""

import http.server
import socketserver
import json
import threading
import argparse
import time
import os
from datetime import datetime
from urllib.parse import parse_qs, urlparse

# 配置
DEFAULT_PORT = 9999

class BrowserController:
    """浏览器控制器"""
    
    def __init__(self):
        self.commands = []
        self.results = {}
        self.last_poll = time.time()
        self.connected = False
        
    def add_command(self, command):
        """添加命令到队列"""
        cmd_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(time.time_ns() % 10000)
        self.commands.append({
            'id': cmd_id,
            'command': command,
            'timestamp': time.time()
        })
        self.connected = True
        return cmd_id
    
    def get_command(self):
        """获取最早的命令"""
        if self.commands:
            cmd = self.commands.pop(0)
            return cmd
        return None
    
    def add_result(self, cmd_id, result):
        """添加结果"""
        self.results[cmd_id] = result
        # 清理旧结果
        for k in list(self.results.keys())[: -100]:
            del self.results[k]
    
    def get_result(self, cmd_id):
        """获取结果"""
        return self.results.get(cmd_id)
    
    def is_connected(self):
        """检查是否连接"""
        return self.connected and (time.time() - self.last_poll) < 30
    
    def poll(self):
        """轮询获取命令"""
        self.last_poll = time.time()
        cmd = self.get_command()
        if cmd:
            return {'id': cmd['id'], 'command': cmd['command']}
        return None
    
    def __repr__(self):
        return f"BrowserController(commands={len(self.commands)}, connected={self.is_connected()})"


class APIHandler(http.server.BaseHTTPRequestHandler):
    controller = BrowserController()
    
    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")
    
    def do_GET(self):
        """GET请求"""
        path = self.path.split('?')[0]
        
        if path == '/status':
            # 返回状态
            response = {
                'success': True,
                'connected': self.controller.is_connected(),
                'queue_length': len(self.controller.commands),
                'timestamp': datetime.now().isoformat()
            }
            self.send_json(response)
            
        elif path == '/result':
            # 获取结果
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            cmd_id = params.get('id', [None])[0]
            
            if cmd_id:
                result = self.controller.get_result(cmd_id)
                if result:
                    self.send_json({'success': True, 'result': result})
                else:
                    self.send_json({'success': False, 'error': '结果不存在'})
            else:
                self.send_json({'success': False, 'error': '缺少id参数'})
                
        elif path == '/':
            # 返回控制页面
            self.send_html(get_control_page())
            
        else:
            self.send_error(404)
    
    def do_POST(self):
        """POST请求"""
        path = self.path.split('?')[0]
        
        # 读取请求体
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(body)
            
            if path == '/command':
                # 接收命令（我发送的）
                cmd_id = self.controller.add_command(data.get('command', {}))
                self.send_json({'success': True, 'id': cmd_id})
                
            elif path == '/poll':
                # 轮询获取命令（扩展轮询）
                cmd = self.controller.poll()
                if cmd:
                    self.send_json({'success': True, **cmd})
                else:
                    self.send_json({'success': True, 'command': None})
                    
            elif path == '/result':
                # 接收结果（扩展返回的）
                cmd_id = data.get('id')
                result = data.get('result')
                if cmd_id:
                    self.controller.add_result(cmd_id, result)
                    self.send_json({'success': True})
                else:
                    self.send_json({'success': False, 'error': '缺少id'})
                    
            elif path == '/connect':
                # 扩展连接
                self.controller.connected = True
                self.send_json({'success': True, 'message': '已连接'})
                
            elif path == '/disconnect':
                # 扩展断开
                self.controller.connected = False
                self.send_json({'success': True, 'message': '已断开'})
                
            else:
                self.send_error(404)
                
        except Exception as e:
            self.send_json({'success': False, 'error': str(e)}, status=500)
    
    def send_json(self, data, status=200):
        """发送JSON响应"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def send_html(self, html):
        """发送HTML响应"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))


def get_control_page():
    """获取控制页面HTML"""
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenClaw Browser Control</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; color: white; }
        .container { max-width: 600px; margin: 0 auto; }
        h1 { text-align: center; margin-bottom: 30px; }
        .card { background: white; border-radius: 15px; padding: 20px; margin-bottom: 20px; color: #333; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
        .card h3 { color: #667eea; margin-bottom: 15px; }
        .btn { width: 100%; padding: 15px; border: none; border-radius: 10px; font-size: 16px; cursor: pointer; margin-bottom: 10px; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .btn-success { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; }
        .input-group { margin-bottom: 15px; }
        .input-group label { display: block; margin-bottom: 5px; color: #666; }
        .input-group input { width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 14px; }
        .status { text-align: center; padding: 15px; border-radius: 10px; margin-bottom: 20px; }
        .status.connected { background: rgba(102, 187, 106, 0.3); }
        .status.disconnected { background: rgba(239, 83, 80, 0.3); }
        .result { background: #1e1e1e; color: #00ff00; padding: 15px; border-radius: 10px; font-family: monospace; max-height: 200px; overflow-y: auto; white-space: pre-wrap; }
        .log { background: #1e1e1e; color: #00ff00; padding: 10px; border-radius: 8px; font-family: monospace; font-size: 12px; max-height: 150px; overflow-y: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 OpenClaw Browser Control</h1>
        
        <div class="status connected" id="status">
            🟢 服务器已启动，等待连接...
        </div>
        
        <div class="card">
            <h3>🔗 扩展连接地址</h3>
            <div class="input-group">
                <input type="text" id="server-url" readonly>
            </div>
            <p style="font-size: 12px; color: #666; margin-bottom: 10px;">
                在扩展的popup中输入此地址并点击"连接"
            </p>
        </div>
        
        <div class="card">
            <h3>📤 发送命令</h3>
            <div class="input-group">
                <label>命令类型</label>
                <select id="cmd-type" style="width: 100%; padding: 12px; border-radius: 8px;">
                    <option value="navigate">导航</option>
                    <option value="click">点击</option>
                    <option value="getStockData">获取股票数据</option>
                    <option value="getPageInfo">获取页面信息</option>
                    <option value="getHTML">获取HTML</option>
                </select>
            </div>
            <div class="input-group">
                <label>参数 (URL或选择器)</label>
                <input type="text" id="cmd-param" placeholder="https://www.10jqka.com.cn 或 .btn-primary">
            </div>
            <button class="btn btn-primary" onclick="sendCommand()">发送命令</button>
        </div>
        
        <div class="card">
            <h3>📥 接收结果</h3>
            <button class="btn btn-success" onclick="checkResult()">检查结果</button>
            <div class="result" id="result">等待结果...</div>
        </div>
        
        <div class="card">
            <h3>📋 服务器日志</h3>
            <div class="log" id="log">服务器启动...</div>
        </div>
    </div>

    <script>
        // 获取服务器地址
        const serverUrl = window.location.origin;
        document.getElementById('server-url').value = serverUrl;
        
        async function sendCommand() {
            const type = document.getElementById('cmd-type').value;
            const param = document.getElementById('cmd-param').value;
            
            const command = { type };
            if (param) command.url = param;
            if (type === 'click') command.selector = param;
            
            try {
                const response = await fetch('/command', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command })
                });
                
                const data = await response.json();
                document.getElementById('log').textContent = `[${new Date().toLocaleTimeString()}] 命令已发送: ${type}`;
                alert('命令已发送！等待浏览器执行...');
            } catch (e) {
                document.getElementById('log').textContent = `[${new Date().toLocaleTimeString()}] 错误: ${e.message}`;
            }
        }
        
        async function checkResult() {
            // 获取最后一个命令的结果
            try {
                const response = await fetch('/status');
                const data = await response.json();
                
                if (data.queue_length > 0) {
                    document.getElementById('result').textContent = '命令正在执行中...';
                } else {
                    document.getElementById('result').textContent = '没有待处理的结果';
                }
                
                document.getElementById('log').textContent = `[${new Date().toLocaleTimeString()}] 状态检查: ${data.connected ? '已连接' : '未连接'}`;
            } catch (e) {
                document.getElementById('log').textContent = `[${new Date().toLocaleTimeString()}] 错误: ${e.message}`;
            }
        }
        
        // 定时检查状态
        setInterval(checkResult, 3000);
    </script>
</body>
</html>'''


def run_server(port=DEFAULT_PORT):
    """运行服务器"""
    print("=" * 60)
    print("  OpenClaw 远程浏览器控制服务器")
    print("=" * 60)
    print()
    print(f"  🌐 服务器地址: http://localhost:{port}")
    print()
    print("  📋 使用方法:")
    print()
    print("  1. 用户在Chrome扩展中连接此服务器")
    print("     - 打开扩展popup")
    print(f"     - 输入地址: http://localhost:{port}")
    print("     - 点击连接")
    print()
    print("  2. 我发送命令控制浏览器")
    print("     POST /command")
    print("     { \"command\": { \"type\": \"navigate\", \"url\": \"...\" } }")
    print()
    print("  3. 扩展执行并返回结果")
    print()
    print("=" * 60)
    print()
    
    with socketserver.TCPServer(("", port), APIHandler) as httpd:
        print(f"  ✅ 服务器已启动，监听端口 {port}")
        print(f"  📄 控制页面: http://localhost:{port}/")
        print()
        print("  按 Ctrl+C 停止服务器")
        print()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n  👋 服务器已停止")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='OpenClaw远程浏览器控制服务器')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help='服务器端口')
    args = parser.parse_args()
    
    run_server(args.port)
