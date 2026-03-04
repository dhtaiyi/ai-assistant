#!/usr/bin/env python3
"""
小雨与小小雨的数据交互系统 v1.0
- 接收小小雨发送的已转录文件列表
- 记录交互日志到文件
- 定期同步日志到飞书文档
"""

import json
import os
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

RECORDINGS_DIR = "/root/douyin_recordings/"
LOG_FILE = "/tmp/xiaoyu_xiaoxiaoyu_interaction.log"
FEISHU_DOC_TOKEN = "oc_55c53c31afbfee92e3edcc8fe2048550"  # 群聊ID当日志用

class InteractionLogger:
    def __init__(self):
        self.log_file = LOG_FILE
        self._init_log()
    
    def _init_log(self):
        """初始化日志文件"""
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                f.write(f"=== 小雨与小小雨交互系统 ===\n")
                f.write(f"启动时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    def log(self, direction, message, data=None):
        """记录交互"""
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = {
            "timestamp": timestamp,
            "direction": direction,  # "小小雨->小雨" 或 "小雨->小小雨"
            "message": message,
            "data": data
        }
        
        with open(self.log_file, "a") as f:
            f.write(f"\n[{timestamp}] {direction}\n")
            f.write(f"  消息: {message}\n")
            if data:
                f.write(f"  数据: {json.dumps(data, ensure_ascii=False)}\n")
        
        return log_entry
    
    def get_recent_logs(self, count=20):
        """获取最近日志"""
        if not os.path.exists(self.log_file):
            return []
        
        with open(self.log_file, "r") as f:
            lines = f.readlines()
        
        return lines[-count:]

logger = InteractionLogger()

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # 静默日志
    
    def do_GET(self):
        """查询接口"""
        parsed = urlparse(self.path)
        
        if parsed.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
        
        elif parsed.path == "/logs":
            # 获取最近日志
            logs = logger.get_recent_logs(50)
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("".join(logs).encode("utf-8"))
        
        elif parsed.path == "/files":
            # 获取服务器上的文件列表
            files = os.listdir(RECORDINGS_DIR)
            video_files = [f for f in files if f.endswith(('.mp4', '.flv'))]
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "total": len(video_files),
                "files": sorted(video_files)
            }).encode())
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """接收小小雨的数据"""
        if self.path != "/transcribed-files":
            self.send_response(404)
            self.end_headers()
            return
        
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body.decode("utf-8"))
            
            # 小小雨发送已转录的文件列表
            files = data.get("files", [])
            action = data.get("action", "report")  # report/delete
            
            if action == "report":
                # 记录小小雨的报告
                logger.log("小小雨 -> 小雨", "收到已转录文件列表", {"files": files})
                
                # 尝试删除对应的服务器文件
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
                
                # 返回结果
                result = {
                    "status": "done",
                    "reported": len(files),
                    "deleted": deleted,
                    "failed": failed
                }
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(result, ensure_ascii=False).encode())
                
                # 通知困困
                self._notify_human(deleted, failed)
            
            elif action == "ping":
                # 小小雨的心跳
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
    
    def _notify_human(self, deleted, failed):
        """通知困困删除结果"""
        # 这里可以扩展为发送飞书消息
        pass

def run_server(port=18080):
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"🌸 小雨与小小雨交互系统 v1.0")
    print(f"📡 服务地址: http://0.0.0.0:{port}")
    print(f"📝 API:")
    print(f"   GET  /health   - 健康检查")
    print(f"   GET  /logs     - 查看交互日志")
    print(f"   GET  /files    - 查看服务器文件列表")
    print(f"   POST /transcribed-files - 发送已转录文件")
    print(f"📁 日志文件: {LOG_FILE}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
