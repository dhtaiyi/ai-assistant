#!/usr/bin/env python3
"""
小雨与小小雨的可视化交互系统 v3.1
"""

import json
import os
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

RECORDINGS_DIR = "/root/douyin_recordings/"
TRASH_DIR = "/root/douyin_recordings/.trash"
LOG_FILE = "/tmp/xiaoyu_xiaoxiaoyu_interaction.log"

class InteractionLogger:
    def __init__(self):
        self.log_file = LOG_FILE
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                f.write(f"=== 交互系统 v3.1 ===\n")
    
    def log(self, direction, message, data=None):
        ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.log_file, "a") as f:
            f.write(f"\n[{ts}] {direction}\n  消息: {message}\n")
            if data:
                f.write(f"  数据: {json.dumps(data, ensure_ascii=False)}\n")
    
    def get_logs(self, n=50):
        if not os.path.exists(self.log_file): return []
        with open(self.log_file) as f: lines = f.readlines()
        return lines[-n:]

logger = InteractionLogger()

def make_html():
    files = sorted([f for f in os.listdir(RECORDINGS_DIR) if f.endswith(('.mp4', '.flv'))])
    logs = logger.get_logs(50)
    
    # 文件列表
    if files:
        file_items = ''.join([f'<div class="fi">{f}</div>' for f in files])
    else:
        file_items = '<p style="color:#666;">暂无文件</p>'
    
    # 日志
    log_html = ""
    for line in logs:
        line = line.strip()
        if not line: continue
        if line.startswith("["):
            parts = line.split("]")
            if len(parts) >= 2:
                ts = parts[0][1:]
                direction = parts[1].strip()
                log_html += f'<div class="le"><span class="tm">{ts}</span> <span class="dr">{direction}</span></div>'
        elif line.startswith("  消息:"):
            log_html += f'<div class="msg">{line.replace("  消息:", "").strip()}</div>'
        elif line.startswith("  数据:"):
            log_html += f'<div class="dat">{line.replace("  数据:", "").strip()}</div>'
    
    if not log_html:
        log_html = '<p style="color:#999;font-style:italic;">暂无交互记录...</p>'
    
    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta http-equiv="refresh" content="5"><title>小雨与小小雨</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,sans-serif;background:linear-gradient(135deg,#1a1a2e,#16213e);min-height:100vh;padding:20px;color:#eee}}
.c{{max-width:900px;margin:0 auto}}
h1{{color:#fff;text-align:center;margin-bottom:20px;font-size:1.8em}}
.card{{background:rgba(255,255,255,0.05);border-radius:12px;padding:20px;margin-bottom:16px;border:1px solid rgba(255,255,255,0.1)}}
.card h2{{color:#a5b4fc;margin-bottom:12px;font-size:1.1em}}
.st{{display:inline-block;width:8px;height:8px;border-radius:50%;background:#10b981;animation:pulse 2s infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:0.6}}}}
.sr{{display:flex;gap:20px;justify-content:center}}
.si{{text-align:center}}
.sn{{font-size:1.5em;font-weight:bold;color:#fff}}
.sl{{font-size:0.85em;color:#888}}
.bt{{background:rgba(102,126,234,0.2);color:#a5b4fc;border:1px solid rgba(102,126,234,0.3);padding:10px 20px;border-radius:6px;cursor:pointer}}
.bt:hover{{background:rgba(102,126,234,0.3)}}
.fl{{display:none;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:6px;margin-top:12px}}
.fl.sh{{display:grid}}
.fi{{background:rgba(255,255,255,0.05);padding:6px 10px;border-radius:4px;font-size:0.8em;word-break:break-all;color:#999}}
.le{{padding:10px 12px;margin:6px 0;border-radius:6px;background:rgba(255,255,255,0.03);border-left:3px solid #667eea}}
.tm{{color:#666;font-size:0.8em}}
.dr{{font-weight:600;margin-right:8px;color:#a5b4fc}}
.msg{{color:#ddd;margin-top:4px;font-size:0.95em}}
.dat{{background:rgba(102,126,234,0.1);padding:8px;border-radius:4px;font-size:0.85em;margin-top:6px;font-family:monospace;color:#aaa;word-break:break-all}}
.ar{{text-align:center;color:#666;font-size:0.8em;margin-bottom:10px}}
</style></head>
<body><div class="c">
<h1>🌸 小雨与小小雨</h1>
<div class="card"><h2><span class="st"></span> 系统运行中</h2><div class="sr"><div class="si"><div class="sn">{len(files)}</div><div class="sl">视频文件</div></div><div class="si"><div class="sn">{len(logs)}</div><div class="sl">交互记录</div></div></div></div>
<div class="card"><h2>📁 服务器文件</h2><button class="bt" onclick="document.querySelector('.fl').classList.toggle('sh')">👁️ 点击查看 ({len(files)}个)</button><div class="fl">{file_items}</div></div>
<div class="card"><h2>💬 实时交互记录</h2><div class="ar">🔄 自动刷新中 (每5秒)</div>{log_html}</div>
</div></body></html>"""
    return html

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args): pass
    
    def do_GET(self):
        p = urlparse(self.path)
        if p.path == "/health":
            self.send_response(200); self.send_header("Content-Type","text/plain"); self.end_headers(); self.wfile.write(b"OK"); return
        if p.path == "/files":
            f = sorted([f for f in os.listdir(RECORDINGS_DIR) if f.endswith(('.mp4', '.flv'))])
            self.send_response(200); self.send_header("Content-Type","application/json"); self.end_headers(); self.wfile.write(json.dumps({"total":len(f),"files":f}).encode()); return
        if p.path == "/logs":
            l = logger.get_logs(50)
            self.send_response(200); self.send_header("Content-Type","text/plain; charset=utf-8"); self.end_headers(); self.wfile.write("".join(l).encode()); return
        
        html = make_html()
        self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.end_headers(); self.wfile.write(html.encode())
    
    def do_POST(self):
        if self.path != "/transcribed-files": self.send_response(404); self.end_headers(); return
        cl = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(cl)
        try:
            data = json.loads(body.decode())
            files = data.get("files", [])
            action = data.get("action", "report")
            if action == "report":
                logger.log("小小雨 -> 小雨", "收到已转录文件列表", {"files": files})
                deleted, failed = [], []
                for fn in files:
                    fp = os.path.join(RECORDINGS_DIR, fn)
                    if os.path.exists(fp):
                        try: 
                            import shutil
                            dest = os.path.join(TRASH_DIR, fn)
                            shutil.move(fp, dest)
                            deleted.append(fn); logger.log("系统", f"移到垃圾箱: {fn}")
                        except Exception as e: failed.append((fn,str(e)))
                    else: failed.append((fn,"不存在"))
                r = {"status":"done","deleted":deleted,"failed":failed}
                self.send_response(200); self.send_header("Content-Type","application/json"); self.end_headers(); self.wfile.write(json.dumps(r,ensure_ascii=False).encode())
            elif action == "ping":
                logger.log("小小雨 -> 小雨", "心跳", data)
                self.send_response(200); self.send_header("Content-Type","application/json"); self.end_headers(); self.wfile.write(b'{"status":"pong"}')
        except Exception as e:
            logger.log("错误", str(e))
            self.send_response(500); self.send_header("Content-Type","application/json"); self.end_headers(); self.wfile.write(json.dumps({"error":str(e)}).encode())

if __name__ == "__main__":
    HTTPServer(("0.0.0.0",18080),Handler).serve_forever()
