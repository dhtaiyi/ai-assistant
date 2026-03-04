#!/usr/bin/env python3
"""
小雨的抖音转录文件接收服务
监听端口 18080，接收小小雨发送的已转录文件列表
"""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

RECORDINGS_DIR = "/root/douyin_recordings/"
LOG_FILE = "/tmp/xiaoyu_xiaoxiaoyu_transfer.log"

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        msg = f"{self.address_string()} - {format % args}"
        print(msg)
        with open(LOG_FILE, "a") as f:
            f.write(msg + "\n")
    
    def do_GET(self):
        """测试接口，返回状态"""
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """接收小小雨发送的已转录文件列表"""
        if self.path != "/transcribed-files":
            self.send_response(404)
            self.end_headers()
            return
        
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body.decode("utf-8"))
            files = data.get("files", [])
            
            if not files:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "No files provided"}).encode())
                return
            
            # 记录收到的小小雨转录文件列表
            with open(LOG_FILE, "a") as f:
                f.write(f"\n=== 收到小小雨的转录文件列表 ===\n")
                for fn in files:
                    f.write(f"  - {fn}\n")
            
            # 返回成功
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "received",
                "count": len(files),
                "files": files
            }).encode())
            
            print(f"收到小小雨的转录文件列表: {len(files)} 个文件")
            
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

def run_server(port=18080):
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"🌸 小雨服务启动: http://0.0.0.0:{port}")
    print(f"📁 监听路径: /transcribed-files (POST)")
    print(f"📝 日志文件: {LOG_FILE}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
