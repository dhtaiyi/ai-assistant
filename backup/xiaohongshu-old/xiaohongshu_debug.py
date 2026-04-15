#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书登录调试脚本
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'skills', 'xiaohongshutools', 'scripts'))

async def debug_login(web_session, proxy=None):
    from request.web.xhs_session import create_xhs_session
    
    print("🔄 正在创建会话...")
    xhs = await create_xhs_session(proxy=proxy, web_session=web_session)
    print("✅ 会话创建成功\n")
    
    print("🔄 正在获取用户信息...")
    res = await xhs.apis.auth.get_self_simple_info()
    
    if res is None:
        print("❌ 获取用户信息失败")
        await xhs.close_session()
        return
    
    data = await res.json()
    
    print("📊 完整返回数据:")
    print("-" * 50)
    import json
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("-" * 50)
    
    await xhs.close_session()

if __name__ == "__main__":
    web_session = sys.argv[1] if len(sys.argv) > 1 else "040069b8fdba81d499ed9f75b83b4b4314e571"
    asyncio.run(debug_login(web_session))
