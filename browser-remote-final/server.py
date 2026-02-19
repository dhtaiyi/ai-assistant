#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 远程浏览器控制服务器
让AI可以主动控制你的浏览器

使用方法:
    python server.py

然后打开浏览器访问: http://localhost:9999
"""

import http.server
import socketserver
import json
import threading
import time
import os
from datetime import datetime
from urllib.parse import parse_qs, urlparse
import uuid

PORT = 9999

class CommandManager:
    """命令管理器"""
    
    def __init__(self):
        self.commands = {}  # id -> command
        self.results = {}   # id -> result
        self.lock = threading.Lock()
    
    def add_command(self, command):
        """添加命令"""
        cmd_id = str(uuid.uuid4())[:8]
        with self.lock:
            self.commands[cmd_id] = {
                'id': cmd_id,
                'command': command,
                'created_at': datetime.now().isoformat(),
                'executed': False
            }
        return cmd_id
    
    def get_command(self, cmd_id=None):
        """获取命令（扩展轮询时调用）"""
        with self.lock:
            # 如果指定了ID，返回特定命令
            if cmd_id and cmd_id in self.commands:
                cmd = self.commands.pop(cmd_id)
                cmd['executed'] = True
                return cmd
            
            # 否则返回最早的命令
            if self.commands:
                cmd_id = min(self.commands.keys(), key=lambda k: self.commands[k]['created_at'])
                cmd = self.commands.pop(cmd_id)
                cmd['executed'] = True
                return cmd
        return None
    
    def add_result(self, cmd_id, result):
        """添加结果"""
        with self.lock:
            self.results[cmd_id] = {
                'result': result,
                'time': datetime.now().isoformat()
            }
            # 清理旧结果
            for k in list(self.results.keys())[: -100]:
                del self.results[k]
    
    def get_result(self, cmd_id):
        """获取结果"""
        with self.lock:
            return self.results.get(cmd_id)
    
    def get_status(self):
        """获取状态"""
        with self.lock:
            return {
                'waiting_commands': len(self.commands),
                'stored_results': len(self.results)
            }


class APIHandler(http.server.BaseHTTPRequestHandler):
    manager = CommandManager()
    
    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")
    
    def do_GET(self):
        path = self.path.split('?')[0]
        
        if path == '/':
            self.send_html(HTML_PAGE)
        
        elif path == '/status':
            status = self.manager.get_status()
            self.send_json({'success': True, **status})
        
        elif path == '/result':
            params = parse_qs(urlparse(self.path).query)
            cmd_id = params.get('id', [None])[0]
            result = self.manager.get_result(cmd_id) if cmd_id else None
            if result:
                self.send_json({'success': True, **result})
            else:
                self.send_json({'success': True, 'result': None, 'message': '暂无结果'})
        
        else:
            self.send_error(404)
    
    def do_POST(self):
        path = self.path.split('?')[0]
        
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(body)
            
            if path == '/command':
                # 接收命令（我发送的）
                cmd_id = self.manager.add_command(data.get('command', {}))
                print(f"📝 收到命令: {data.get('command')}")
                self.send_json({'success': True, 'id': cmd_id})
            
            elif path == '/poll':
                # 扩展轮询获取命令
                params = parse_qs(urlparse(self.path).query)
                cmd_id = params.get('id', [None])[0]
                cmd = self.manager.get_command(cmd_id)
                if cmd:
                    print(f"📤 发送命令到浏览器: {cmd['command']}")
                    self.send_json({'success': True, **cmd})
                else:
                    self.send_json({'success': True, 'command': None})
            
            elif path == '/result':
                # 扩展报告结果
                cmd_id = data.get('id')
                result = data.get('result')
                if cmd_id and result:
                    print(f"✅ 收到结果: {str(result)[:100]}")
                    self.manager.add_result(cmd_id, result)
                    self.send_json({'success': True})
                else:
                    self.send_json({'success': False, 'error': '缺少参数'})
            
            else:
                self.send_error(404)
        
        except Exception as e:
            self.send_json({'success': False, 'error': str(e)}, status=500)
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def send_html(self, html):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))


HTML_PAGE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenClaw 远程控制</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 30px; color: white; }
        .container { max-width: 600px; margin: 0 auto; }
        h1 { text-align: center; margin-bottom: 30px; }
        .card { background: white; border-radius: 15px; padding: 25px; margin-bottom: 20px; color: #333; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
        .card h3 { color: #667eea; margin-bottom: 20px; }
        .input-group { margin-bottom: 15px; }
        .input-group label { display: block; margin-bottom: 8px; color: #666; }
        .input-group input, .input-group select { width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 10px; font-size: 16px; }
        .btn { width: 100%; padding: 15px; border: none; border-radius: 10px; font-size: 16px; cursor: pointer; margin-bottom: 10px; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .btn-success { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; }
        .btn-secondary { background: #f5f5f5; color: #333; }
        .quick { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 15px; }
        .quick button { padding: 10px 15px; background: #f0f0f0; border: none; border-radius: 8px; cursor: pointer; }
        .quick button:hover { background: #667eea; color: white; }
        .result { background: #1e1e1e; color: #00ff00; padding: 15px; border-radius: 10px; font-family: monospace; max-height: 200px; overflow-y: auto; white-space: pre-wrap; }
        .status { text-align: center; padding: 20px; border-radius: 15px; margin-bottom: 20px; font-size: 18px; }
        .status.connected { background: rgba(102, 187, 106, 0.3); }
        .url-box { background: #f5f5f5; padding: 15px; border-radius: 10px; font-family: monospace; margin-bottom: 20px; word-break: break-all; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 OpenClaw 远程控制</h1>
        
        <div class="url-box" id="server-url">服务器地址加载中...</div>
        
        <div class="status connected">
            🟢 服务器已启动 - 等待Chrome扩展连接
        </div>
        
        <div class="card">
            <h3>📤 发送命令</h3>
            <div class="input-group">
                <label>命令类型</label>
                <select id="cmd-type">
                    <option value="navigate">导航 (navigate)</option>
                    <option value="click">点击 (click)</option>
                    <option value="getStockData">获取股票数据 (getStockData)</option>
                    <option value="getPageInfo">获取页面信息 (getPageInfo)</option>
                    <option value="evaluate">执行代码 (evaluate)</option>
                </select>
            </div>
            <div class="input-group">
                <label>参数 (URL或CSS选择器)</label>
                <input type="text" id="cmd-param" placeholder="如 https://www.10jqka.com.cn 或 .btn-primary">
            </div>
            <button class="btn btn-primary" onclick="sendCommand()">🚀 发送命令</button>
        </div>
        
        <div class="card">
            <h3>⚡ 快捷操作</h3>
            <div class="quick">
                <button onclick="quick('navigate', 'https://www.10jqka.com.cn')">同花顺</button>
                <button onclick="quick('navigate', 'https://quote.eastmoney.com')">东方财富</button>
                <button onclick="quick('getStockData')">股票数据</button>
                <button onclick="quick('getPageInfo')">页面信息</button>
                <button onclick="quick('navigate', 'current')">🔄 刷新</button>
            </div>
        </div>
        
        <div class="card">
            <h3>📥 执行结果</h3>
            <button class="btn btn-secondary" onclick="checkResult()">🔄 刷新结果</button>
            <div class="result" id="result">等待命令执行...</div>
        </div>
    </div>

    <script>
        const API_URL = window.location.origin;
        document.getElementById('server-url').textContent = '控制面板: ' + API_URL;
        
        let lastCommandId = null;
        
        async function sendCommand(type, param) {
            const cmdType = type || document.getElementById('cmd-type').value;
            const paramValue = param || document.getElementById('cmd-param').value;
            
            const command = { type: cmdType };
            if (paramValue) {
                if (cmdType === 'navigate') command.url = paramValue;
                else command.selector = paramValue;
            }
            
            try {
                const response = await fetch('/command', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command })
                });
                const data = await response.json();
                if (data.success) {
                    lastCommandId = data.id;
                    document.getElementById('result').textContent = '✅ 命令已发送!\n' + JSON.stringify(command, null, 2);
                }
            } catch (e) {
                document.getElementById('result').textContent = '❌ 错误: ' + e.message;
            }
        }
        
        function quick(type, param) {
            if (param) {
                document.getElementById('cmd-type').value = type;
                document.getElementById('cmd-param').value = param;
            }
            sendCommand(type, param);
        }
        
        async function checkResult() {
            if (!lastCommandId) {
                document.getElementById('result').textContent = '暂无命令';
                return;
            }
            try {
                const response = await fetch('/result?id=' + lastCommandId);
                const data = await response.json();
                if (data.result) {
                    document.getElementById('result').textContent = JSON.stringify(data.result, null, 2);
                } else {
                    document.getElementById('result').textContent = '命令正在执行或无结果';
                }
            } catch (e) {
                document.getElementById('result').textContent = '❌ ' + e.message;
            }
        }
        
        setInterval(checkResult, 2000);
    </script>
</body>
</html>'''


def run_server(port=PORT):
    print("=" * 60)
    print("  OpenClaw 远程浏览器控制")
    print("=" * 60)
    print()
    print(f"  🌐 控制面板: http://localhost:{port}")
    print()
    print("  📋 使用方法:")
    print()
    print("  1. 安装Chrome扩展 browser-remote-final")
    print("  2. 扩展会自动连接此服务器")
    print("  3. 在此页面发送命令控制浏览器")
    print()
    print("  📝 可用命令:")
    print("    - navigate: 导航到URL")
    print("    - click: 点击元素")
    print("    - getStockData: 获取股票数据")
    print("    - getPageInfo: 获取页面信息")
    print()
    print("=" * 60)
    print()
    
    with socketserver.TCPServer(("", port), APIHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 服务器已停止")


if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    run_server(port)
