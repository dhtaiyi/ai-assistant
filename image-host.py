#!/usr/bin/env python3
"""
简单的图片托管服务 - 无需依赖
"""

import os
import json
import uuid
import time
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import mimetypes

# 配置
PORT = 18081
UPLOAD_FOLDER = '/root/.openclaw/workspace/images'
BASE_URL = 'http://10.0.0.15:18081'

# 确保目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXT = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}

class ImageHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        
        # 访问图片
        if path.startswith('/images/'):
            filename = path.split('/')[-1]
            fpath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.exists(fpath):
                self.send_response(200)
                ext = os.path.splitext(filename)[1].lower()
                self.send_header('Content-Type', mimetypes.types_map.get(ext, 'image/jpeg'))
                self.send_header('Content-Length', os.path.getsize(fpath))
                self.end_headers()
                with open(fpath, 'rb') as f:
                    self.wfile.write(f.read())
                return
        
        # 列出图片
        if path == '/list':
            files = os.listdir(UPLOAD_FOLDER)
            images = []
            for f in files:
                if os.path.splitext(f)[1].lower() in ALLOWED_EXT:
                    pf = os.path.join(UPLOAD_FOLDER, f)
                    images.append({
                        'filename': f,
                        'url': f'{BASE_URL}/images/{f}',
                        'size': os.path.getsize(pf)
                    })
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'images': images}).encode())
            return
        
        # 健康检查
        if path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok'}).encode())
            return
        
        # 默认返回说明
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        html = '''<html><head><title>图片托管服务</title></head>
<body>
<h1>📷 图片托管服务</h1>
<p>上传: POST /upload (multipart form data, field name: file)</p>
<p>列表: GET /list</p>
<p>访问: GET /images/filename</p>
</body></html>'''
        self.wfile.write(html.encode('utf-8'))
    
    def do_POST(self):
        if self.path == '/upload':
            content_type = self.headers.get('Content-Type', '')
            if 'multipart/form-data' not in content_type:
                self.send_error(400, 'Need multipart form data')
                return
            
            # 解析boundary
            boundary = content_type.split('boundary=')[-1]
            boundary = boundary.encode()
            
            # 读取全部内容
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            # 简单解析 - 找文件内容
            parts = body.split(b'--' + boundary)
            for part in parts:
                if b'Content-Type:' in part and b'image' in part:
                    # 找文件数据
                    idx = part.find(b'\r\n\r\n')
                    if idx > 0:
                        data = part[idx+4:]
                        # 去除末尾的\r\n
                        if data.endswith(b'\r\n'):
                            data = data[:-2]
                        
                        # 生成文件名
                        ext = '.png'
                        for e in ALLOWED_EXT:
                            if e.encode() in part:
                                ext = e
                                break
                        
                        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}{ext}"
                        filepath = os.path.join(UPLOAD_FOLDER, filename)
                        
                        with open(filepath, 'wb') as f:
                            f.write(data)
                        
                        # 返回
                        url = f'{BASE_URL}/images/{filename}'
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({
                            'success': True,
                            'url': url,
                            'filename': filename
                        }).encode())
                        return
            
            self.send_error(400, 'No image found')
        else:
            self.send_error(404)

    def log_message(self, format, *args):
        pass  # 禁用日志

print(f"📷 图片托管服务启动!")
print(f"   端口: {PORT}")
print(f"   存储: {UPLOAD_FOLDER}")
print(f"   访问: {BASE_URL}")

HTTPServer(('0.0.0.0', PORT), ImageHandler).serve_forever()
