#!/usr/bin/env python3
"""
小雨与小小雨的可视化交互系统 v2.0
"""

import json
import os
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

RECORDINGS_DIR = "/root/douyin_recordings/"
LOG_FILE = "/tmp/xiaoyu_xiaoxiaoyu_interaction.log"

class InteractionLogger:
    def __init__(self):
        self.log_file = LOG_FILE
        self._init_log()
    
    def _init_log(self):
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                f.write(f"=== 小雨与小小雨交互系统 v2.0 ===\n")
                f.write(f"启动时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    def log(self, direction, message, data=None):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.log_file, "a") as f:
            f.write(f"\n[{timestamp}] {direction}\n")
            f.write(f"  消息: {message}\n")
            if data:
                f.write(f"  数据: {json.dumps(data, ensure_ascii=False)}\n")
    
    def get_logs(self, count=50):
        if not os.path.exists(self.log_file):
            return []
        with open(self.log_file, "r") as f:
            lines = f.readlines()
        return lines[-count:]

logger = InteractionLogger()

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>🌸 小雨与小小雨 - 交互系统</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { 
            color: white; 
            text-align: center; 
            margin-bottom: 30px;
            font-size: 2em;
        }
        .card {
            background: white;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        .card h2 {
            color: #333;
            margin-bottom: 16px;
            font-size: 1.3em;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .status { 
            display: inline-block;
            width: 10px; 
            height: 10px; 
            border-radius: 50%;
            background: #10b981;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .log-entry {
            padding: 12px;
            margin: 8px 0;
            border-radius: 8px;
            background: #f8f9fa;
            border-left: 4px solid #667eea;
        }
        .log-entry.xiaoxiaoyu { border-left-color: #10b981; }
        .log-entry.xiaoyu { border-left-color: #f59e0b; }
        .log-entry.system { border-left-color: #ef4444; }
        .log-time { color: #666; font-size: 0.85em; }
        .log-dir { font-weight: bold; margin-right: 8px; }
        .log-msg { color: #333; margin-top: 4px; }
        .log-data { 
            background: #eef2ff; 
            padding: 8px; 
            border-radius: 4px; 
            font-size: 0.9em;
            margin-top: 8px;
            font-family: monospace;
            white-space: pre-wrap;
            overflow-x: auto;
        }
        .file-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 8px;
        }
        .file-item {
            background: #f1f5f9;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 0.85em;
            word-break: break-all;
        }
        .stats {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }
        .stat-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 30px;
            border-radius: 12px;
            text-align: center;
        }
        .stat-num { font-size: 2em; font-weight: bold; }
        .stat-label { font-size: 0.9em; opacity: 0.9; }
        .api-box {
            background: #1e293b;
            color: #a5b4fc;
            padding: 16px;
            border-radius: 8px;
            font-family: monospace;
            font-size: 0.9em;
            overflow-x: auto;
        }
        .api-box .method { color: #10b981; }
        .api-box .path { color: #60a5fa; }
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            margin-bottom: 16px;
        }
        .refresh-btn:hover { background: #5568d3; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌸 小雨与小小雨 - 交互系统</h1>
        
        <div class="card">
            <h2><span class="status"></span> 系统状态: 运行中</h2>
            <div class="stats">
                <div class="stat-box">
                    <div class="stat-num">{file_count}</div>
                    <div class="stat-label">服务器视频文件</div>
                </div>
                <div class="stat-box">
                    <div class="stat-num">{log_count}</div>
                    <div class="stat-label">交互记录</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>📡 API 接口</h2>
            <div class="api-box">
<span class="method">GET</span>  /files      - 查看服务器文件列表<br>
<span class="method">GET</span>  /logs      - 查看交互日志<br>
<span class="method">POST</span> /transcribed-files - 小小雨发送已转录文件
            </div>
        </div>
        
        <div class="card">
            <h2>📁 服务器文件 ({file_count}个)</h2>
            <div class="file-list">
{files_html}
            </div>
        </div>
        
        <div class="card">
            <h2>💬 交互记录</h2>
            <button class="refresh-btn" onclick="location.reload()">🔄 刷新</button>
            {logs_html}
        </div>
    </div>
</body>
</html>"""

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
            return
        
        if parsed.path == "/files":
            files = os.listdir(RECORDINGS_DIR)
            video_files = sorted([f for f in files if f.endswith(('.mp4', '.flv'))])
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"total": len(video_files), "files": video_files}).encode())
            return
        
        # 默认返回可视化页面
        files = os.listdir(RECORDINGS_DIR)
        video_files = sorted([f for f in files if f.endswith(('.mp4', '.flv'))])
        logs = logger.get_logs(30)
        
        # 构建文件列表HTML
        files_html = "".join([f'<div class="file-item">{f}</div>' for f in video_files])
        
        # 构建日志HTML
        logs_html = ""
        for line in logs:
            line = line.strip()
            if not line:
                continue
            if line.startswith("["):
                # 时间戳行
                parts = line.split("]")
                if len(parts) >= 2:
                    timestamp = parts[0][1:]
                    direction = parts[1].strip().split(" -> ")
                    if len(direction) == 2:
                        logs_html += f'<div class="log-entry xiaoxiaoyu"><span class="log-time">{timestamp}</span> <span class="log-dir">{direction[0]} → {direction[1]}</span></div>'
                    else:
                        logs_html += f'<div class="log-entry system"><span class="log-time">{timestamp}</span> {direction[0]}</div>'
            elif line.startswith("  消息:"):
                logs_html += f'<div class="log-msg">{line.replace("  消息:", "").strip()}</div>'
            elif line.startswith("  数据:"):
                logs_html += f'<div class="log-data">{line.replace("  数据:", "").strip()}</div>'
        
        if not logs_html:
            logs_html = '<p style="color:#666;">暂无交互记录</p>'
        
        html = HTML_TEMPLATE.format(
            file_count=len(video_files),
            log_count=len([l for l in logs if l.strip()]),
            files_html=files_html or '<p style="color:#666;">暂无文件</p>',
            logs_html=logs_html
        )
        
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))
    
    def do_POST(self):
        if self.path != "/transcribed-files":
            self.send_response(404)
            self.end_headers()
            return
        
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body.decode("utf-8"))
            files = data.get("files", [])
            action = data.get("action", "report")
            
            if action == "report":
                logger.log("小小雨 -> 小雨", "收到已转录文件列表", {"files": files})
                
                deleted = []
                failed = []
                for fn in files:
                    fp = os.path.join(RECORDINGS_DIR, fn)
                    if os.path.exists(fp):
                        try:
                            os.remove(fp)
                            deleted.append(fn)
                            logger.log("系统", f"删除文件: {fn}")
                        except Exception as e:
                            failed.append((fn, str(e)))
                    else:
                        failed.append((fn, "文件不存在"))
                
                result = {"status": "done", "deleted": deleted, "failed": failed}
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(result, ensure_ascii=False).encode())
            
            elif action == "ping":
                logger.log("小小雨 -> 小雨", "心跳ping", data)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "pong"}).encode())
        
        except Exception as e:
            logger.log("系统错误", str(e))
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

def run_server(port=18080):
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"🌸 可视化交互系统 v2.0 启动: http://0.0.0.0:{port}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
