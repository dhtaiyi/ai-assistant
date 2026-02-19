#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 远程浏览器控制客户端
我通过此脚本控制用户的浏览器

使用方法:
    python client.py --server http://localhost:9999 --command navigate --url https://www.10jqka.com.cn
"""

import argparse
import json
import sys
import time
import requests


class RemoteBrowser:
    """远程浏览器控制器"""
    
    def __init__(self, server_url):
        self.server_url = server_url.rstrip('/')
        self.command_id = None
    
    def _request(self, method, endpoint, data=None):
        """发送请求"""
        url = f"{self.server_url}{endpoint}"
        try:
            if method == 'GET':
                response = requests.get(url, timeout=10)
            else:
                response = requests.request(method, url, json=data, timeout=30)
            
            return response.json()
        except requests.exceptions.ConnectionError:
            return {'success': False, 'error': f'无法连接到 {url}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_command(self, command):
        """发送命令"""
        data = {'command': command}
        result = self._request('POST', '/command', data)
        
        if result.get('success'):
            self.command_id = result.get('id')
            return result
        return result
    
    def get_result(self):
        """获取结果"""
        if not self.command_id:
            return {'success': False, 'error': '没有待获取的结果'}
        
        return self._request('GET', f'/result?id={self.command_id}')
    
    def get_status(self):
        """获取状态"""
        return self._request('GET', '/status')
    
    # 便捷方法
    def navigate(self, url):
        """导航"""
        return self.send_command({'type': 'navigate', 'url': url})
    
    def click(self, selector):
        """点击"""
        return self.send_command({'type': 'click', 'selector': selector})
    
    def type(self, selector, text):
        """输入"""
        return self.send_command({'type': 'type', 'selector': selector, 'text': text})
    
    def scroll(self, direction='down', amount=500):
        """滚动"""
        return self.send_command({'type': 'scroll', 'direction': direction, 'amount': amount})
    
    def get_stock_data(self):
        """获取股票数据"""
        return self.send_command({'type': 'getStockData'})
    
    def get_page_info(self):
        """获取页面信息"""
        return self.send_command({'type': 'getPageInfo'})
    
    def get_html(self):
        """获取HTML"""
        return self.send_command({'type': 'getHTML'})
    
    def evaluate(self, code):
        """执行JavaScript"""
        return self.send_command({'type': 'evaluate', 'code': code})
    
    def wait(self, duration=1000):
        """等待"""
        time.sleep(duration / 1000)
        return {'success': True}


def main():
    parser = argparse.ArgumentParser(description='OpenClaw远程浏览器控制客户端')
    parser.add_argument('--server', '-s', default='http://localhost:9999', help='服务器地址')
    parser.add_argument('--command', '-c', help='命令类型')
    parser.add_argument('--param', '-p', help='参数')
    parser.add_argument('--param2', '-P', help='第二个参数')
    parser.add_argument('--wait', '-w', type=int, default=0, help='等待秒数')
    parser.add_argument('--json', '-j', help='JSON格式命令')
    parser.add_argument('--interactive', '-i', action='store_true', help='交互模式')
    
    args = parser.parse_args()
    
    browser = RemoteBrowser(args.server)
    
    # 检查连接
    print("=" * 60)
    status = browser.get_status()
    print(f"服务器状态: {json.dumps(status, indent=2, ensure_ascii=False)}")
    
    if not status.get('connected'):
        print("⚠️  浏览器未连接到服务器")
        print("请确保：1) 用户已运行 server.py 2) 扩展已连接")
    
    print()
    print("=" * 60)
    print("  OpenClaw 远程浏览器控制")
    print("=" * 60)
    print()
    
    # 交互模式
    if args.interactive:
        print("交互模式可用命令:")
        print("  navigate <url>     - 导航到URL")
        print("  click <selector>  - 点击元素")
        print("  type <sel> <txt>  - 输入文本")
        print("  scroll <dir>     - 滚动 (up/down/top/bottom)")
        print("  stock             - 获取股票数据")
        print("  info              - 获取页面信息")
        print("  html              - 获取页面HTML")
        print("  exit              - 退出")
        print()
        
        while True:
            try:
                cmd = input("命令> ").strip()
                if not cmd: continue
                if cmd == 'exit': break
                
                parts = cmd.split()
                cmd_type = parts[0]
                
                if cmd_type == 'navigate' and len(parts) > 1:
                    browser.navigate(parts[1])
                elif cmd_type == 'click' and len(parts) > 1:
                    browser.click(parts[1])
                elif cmd_type == 'type' and len(parts) > 2:
                    browser.type(parts[1], ' '.join(parts[2:]))
                elif cmd_type == 'scroll' and len(parts) > 1:
                    browser.scroll(parts[1])
                elif cmd_type == 'stock':
                    browser.get_stock_data()
                elif cmd_type == 'info':
                    browser.get_page_info()
                elif cmd_type == 'html':
                    browser.get_html()
                else:
                    print("未知命令")
                    continue
                
                # 等待执行
                if args.wait > 0:
                    time.sleep(args.wait)
                
                # 获取结果
                result = browser.get_result()
                print(json.dumps(result, indent=2, ensure_ascii=False))
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"错误: {e}")
    
    # 单命令模式
    elif args.json:
        command = json.loads(args.json)
        browser.send_command(command)
    
    elif args.command:
        command = {'type': args.command}
        if args.param:
            if args.param.startswith('http'):
                command['url'] = args.param
            else:
                command['selector'] = args.param
        if args.param2:
            command['text'] = args.param2
        
        print(f"发送命令: {json.dumps(command, ensure_ascii=False)}")
        result = browser.send_command(command)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 等待
        if args.wait > 0:
            print(f"等待 {args.wait} 秒...")
            time.sleep(args.wait)
        
        # 获取结果
        result = browser.get_result()
        print("\n执行结果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
