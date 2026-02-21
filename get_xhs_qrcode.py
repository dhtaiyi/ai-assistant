#!/usr/bin/env python3
"""获取小红书登录二维码 - 使用aiohttp处理SSE"""

import asyncio
import json
import aiohttp

MCP_URL = "http://127.0.0.1:18060/mcp"

async def main():
    async with aiohttp.ClientSession() as session:
        # 初始化
        async with session.post(
            MCP_URL,
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
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            },
            proxy=None
        ) as resp:
            init_result = await resp.json()
            print("初始化:", init_result)
        
        # 调用工具 - 使用SSE
        async with session.post(
            MCP_URL,
            json={
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "get_login_qrcode",
                    "arguments": {}
                }
            },
            headers={
                "Content-Type": "application/json",
                "Accept": "text/event-stream"
            },
            proxy=None
        ) as resp:
            print("响应状态:", resp.status)
            
            # 读取SSE数据
            async for line in resp.content:
                if line:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        data = line[6:]
                        print("收到数据:", data[:500])
                        try:
                            result = json.loads(data)
                            if 'result' in result:
                                print("\n二维码结果:")
                                print(json.dumps(result, indent=2, ensure_ascii=False))
                                return
                        except:
                            pass

asyncio.run(main())
