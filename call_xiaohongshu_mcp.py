#!/usr/bin/env python3
"""直接调用小红书MCP工具"""

import requests
import json

MCP_URL = "http://127.0.0.1:18060/mcp"

def mcp_request(method, params=None):
    """发送MCP请求"""
    session = requests.Session()
    
    # 首先初始化
    init_resp = session.post(
        MCP_URL,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        },
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "cli", "version": "1.0"}
            }
        },
        proxies={"http": None, "https": None}
    )
    print("初始化:", init_resp.json())
    
    # 调用工具
    resp = session.post(
        MCP_URL,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        },
        json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": method,
                "arguments": params or {}
            }
        },
        proxies={"http": None, "https": None}
    )
    return resp.json()

# 检查登录状态
print("=" * 50)
print("检查小红书登录状态:")
print("=" * 50)
result = mcp_request("check_login_status")
print(json.dumps(result, indent=2, ensure_ascii=False))

# 获取首页Feeds
print("\n" + "=" * 50)
print("获取首页Feeds:")
print("=" * 50)
result = mcp_request("list_feeds", {"limit": 3})
print(json.dumps(result, indent=2, ensure_ascii=False))
