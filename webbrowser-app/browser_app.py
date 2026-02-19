#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
嵌入式浏览器 - 可通过HTTP API远程控制
使用 PyQt5 + QWebEngineView
"""

import sys
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import json
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton, QLabel, QTabWidget, QTextEdit
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt, pyqtSignal, QObject
from PyQt5.QtWebChannel import QWebChannel
import queue


class Communicate(QObject):
    """Qt与Python通信桥梁"""
    navigate_signal = pyqtSignal(str)
    click_signal = pyqtSignal(str)
    type_signal = pyqtSignal(str, str)
    execute_signal = pyqtSignal(str)
    scroll_signal = pyqtSignal(str)
    
    navigate_result = pyqtSignal(dict)
    click_result = pyqtSignal(dict)
    type_result = pyqtSignal(dict)
    execute_result = pyqtSignal(dict)
    scroll_result = pyqtSignal(dict)
    page_info = pyqtSignal(dict)
    stock_data = pyqtSignal(dict)


class BrowserWindow(QMainWindow):
    """浏览器主窗口"""
    
    def __init__(self, port=8080):
        super().__init__()
        self.port = port
        self.current_url = ""
        self.comm = Communicate()
        self.command_queue = queue.Queue()
        self.init_ui()
        self.setup_bridge()
        self.start_server()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("OpenClaw Browser")
        self.resize(1200, 800)
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        
        # 中央控件
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 标签页
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        layout.addWidget(self.tabs)
        
        # 添加第一个标签页
        self.add_new_tab(QUrl('https://www.baidu.com'), '首页')
        
        # 工具栏
        self.create_toolbar()
        
        # 状态栏
        self.statusBar().showMessage("就绪")
    
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = self.addToolBar("导航")
        toolbar.setMovable(False)
        
        # 地址栏
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("输入URL...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.url_bar)
        
        # 刷新按钮
        refresh_btn = QPushButton("🔄")
        refresh_btn.clicked.connect(self.refresh_current_page)
        toolbar.addWidget(refresh_btn)
    
    def add_new_tab(self, qurl=None, label="新标签"):
        """添加新标签页"""
        browser = QWebEngineView()
        
        if qurl is None:
            qurl = QUrl('about:blank')
        
        browser.setUrl(qurl)
        
        # 连接信号
        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_urlbar(qurl, browser))
        browser.loadFinished.connect(lambda _, i=self.tabs.count(), browser=browser: 
                                   self.tabs.setTabText(i, browser.page().title()))
        
        # 创建页面ID
        page_id = id(browser)
        
        # 添加标签
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
    
    def close_tab(self, i):
        """关闭标签页"""
        if self.tabs.count() < 2:
            return
        self.tabs.removeTab(i)
    
    def current_tab_changed(self, i):
        """切换标签页"""
        if self.tabs.count() < 1:
            return
        qurl = self.tabs.currentWidget().url()
        self.update_urlbar(qurl, self.tabs.currentWidget())
    
    def navigate_to_url(self):
        """导航到URL"""
        url = self.url_bar.text().strip()
        if not url.startswith('http'):
            url = 'https://' + url
        self.tabs.currentWidget().setUrl(QUrl(url))
    
    def refresh_current_page(self):
        """刷新当前页面"""
        self.tabs.currentWidget().reload()
    
    def update_urlbar(self, q, browser=None):
        """更新地址栏"""
        if browser != self.tabs.currentWidget():
            return
        self.url_bar.setText(q.toString())
        self.current_url = q.toString()
    
    def setup_bridge(self):
        """设置JavaScript通信桥梁"""
        page = self.tabs.currentWidget().page()
        channel = QWebChannel(page)
        page.setWebChannel(channel)
    
    def start_server(self):
        """启动HTTP服务器"""
        def run_server():
            server = BrowserServer(self, self.port)
            print(f"🌐 HTTP服务器已启动: http://localhost:{self.port}")
            server.serve_forever()
        
        # 在后台线程中运行服务器
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
    
    def execute_command(self, command):
        """执行命令"""
        cmd_type = command.get('type', '')
        
        if cmd_type == 'navigate':
            url = command.get('url', '')
            if url:
                if not url.startswith('http'):
                    url = 'https://' + url
                self.tabs.currentWidget().setUrl(QUrl(url))
                return {'success': True, 'action': 'navigated', 'url': url}
        
        elif cmd_type == 'click':
            selector = command.get('selector', '')
            if selector:
                # 在页面中点击元素
                js = f"""
                (function() {{
                    var el = document.querySelector('{selector}');
                    if (el) {{
                        el.click();
                        return {{success: true, clicked: '{selector}'}};
                    }}
                    return {{success: false, error: '元素未找到'}};
                }})();
                """
                result = self.tabs.currentWidget().page().runJavaScript(js)
                return {'success': True, 'clicked': selector}
        
        elif cmd_type == 'scroll':
            direction = command.get('direction', 'down')
            amount = command.get('amount', 500)
            
            js = f"""
            (function() {{
                var directions = {{
                    'up': [0, -{amount}],
                    'down': [0, {amount}],
                    'top': [0, 0],
                    'bottom': [0, document.body.scrollHeight]
                }};
                var [x, y] = directions['{direction}'] || directions['down'];
                window.scrollTo(x, y);
                return {{success: true}};
            }})();
            """
            self.tabs.currentWidget().page().runJavaScript(js)
            return {'success': True, 'scrolled': direction}
        
        elif cmd_type == 'getPageInfo':
            return {
                'success': True,
                'title': self.tabs.currentWidget().page().title(),
                'url': self.tabs.currentWidget().url().toString()
            }
        
        elif cmd_type == 'getStockData':
            # 获取股票数据
            js = """
            (function() {
                var data = {timestamp: new Date().toISOString()};
                
                var priceSel = '.stock-price .price, #quotation-entry .price, .current-price';
                var priceEl = document.querySelector(priceSel);
                data.price = priceEl?.innerText?.trim() || '未找到';
                
                var changeSel = '.stock-change .change, #quotation-entry .change, .change-percent';
                var changeEl = document.querySelector(changeSel);
                data.change = changeEl?.innerText?.trim() || '未找到';
                
                return data;
            })();
            """
            result = self.tabs.currentWidget().page().runJavaScript(js)
            return {'success': True, 'data': result}
        
        elif cmd_type == 'evaluate':
            code = command.get('code', '')
            if code:
                result = self.tabs.currentWidget().page().runJavaScript(code)
                return {'success': True, 'result': str(result)}
        
        return {'success': False, 'error': '未知命令'}


class BrowserServer(HTTPServer):
    """浏览器HTTP服务器"""
    
    def __init__(self, browser_window, port):
        super().__init__(('localhost', port), RequestHandler)
        self.browser = browser_window
        self.port = port


class RequestHandler(BaseHTTPRequestHandler):
    """HTTP请求处理"""
    
    server: BrowserServer
    
    def log_message(self, format, *args):
        """自定义日志"""
        print(f"[{self.log_date_time_string()}] {format % args}")
    
    def do_GET(self):
        """GET请求"""
        path = self.path.split('?')[0]
        
        if path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            status = {
                'success': True,
                'status': 'running',
                'port': self.server.port,
                'url': self.server.browser.current_url
            }
            self.wfile.write(json.dumps(status, ensure_ascii=False).encode())
        
        elif path == '/pageInfo':
            result = self.server.browser.execute_command({'type': 'getPageInfo'})
            self.send_json(result)
        
        elif path == '/stockData':
            result = self.server.browser.execute_command({'type': 'getStockData'})
            self.send_json(result)
        
        else:
            self.send_error(404)
    
    def do_POST(self):
        """POST请求"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(body)
            command = data.get('command', {})
            cmd_type = command.get('type', '')
            
            if cmd_type == 'navigate':
                result = self.server.browser.execute_command(command)
                self.send_json(result)
            
            elif cmd_type == 'click':
                result = self.server.browser.execute_command(command)
                self.send_json(result)
            
            elif cmd_type == 'scroll':
                result = self.server.browser.execute_command(command)
                self.send_json(result)
            
            elif cmd_type == 'getStockData':
                result = self.server.browser.execute_command(command)
                self.send_json(result)
            
            elif cmd_type == 'getPageInfo':
                result = self.server.browser.execute_command(command)
                self.send_json(result)
            
            elif cmd_type == 'evaluate':
                result = self.server.browser.execute_command(command)
                self.send_json(result)
            
            else:
                self.send_json({'success': False, 'error': '未知命令'})
        
        except Exception as e:
            self.send_json({'success': False, 'error': str(e)})
    
    def send_json(self, data, status=200):
        """发送JSON响应"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("OpenClaw Browser")
    
    # 创建浏览器窗口
    window = BrowserWindow(port=8080)
    window.show()
    
    print("=" * 60)
    print("  OpenClaw 浏览器已启动")
    print("=" * 60)
    print()
    print("  🌐 浏览器窗口已打开")
    print("  📡 HTTP API: http://localhost:8080")
    print()
    print("  可用命令:")
    print("    POST / {command: {type: 'navigate', url: '...'}}")
    print("    POST / {command: {type: 'click', selector: '...'}}")
    print("    POST / {command: {type: 'scroll', direction: 'down'}}")
    print("    POST / {command: {type: 'getStockData'}}")
    print("    GET  /stockData")
    print()
    print("  按 Ctrl+C 停止服务器，关闭窗口退出程序")
    print("=" * 60)
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
