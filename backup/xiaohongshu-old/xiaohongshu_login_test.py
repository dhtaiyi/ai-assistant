#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书登录测试脚本
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'skills', 'xiaohongshutools', 'scripts'))

async def test_login(web_session, proxy=None):
    from request.web.xhs_session import create_xhs_session
    
    print("=" * 60)
    print("  🦞 小红书登录测试")
    print("=" * 60)
    print()
    
    # 创建会话
    print("🔄 正在创建会话...")
    xhs = await create_xhs_session(proxy=proxy, web_session=web_session)
    print("✅ 会话创建成功!\n")
    
    # 获取用户信息
    print("🔄 正在获取用户信息...")
    res = await xhs.apis.auth.get_self_simple_info()
    
    if res is None:
        print("❌ 获取用户信息失败")
        await xhs.close_session()
        return False
    
    data = await res.json()
    
    print()
    print("=" * 60)
    
    if data.get('success'):
        user_info = data.get('data', {})
        print("  ✅ 登录成功!")
        print()
        print(f"  👤 用户ID: {user_info.get('user_id', '未知')}")
        print(f"  👤 用户名: {user_info.get('nickname', '未知')}")
        print(f"  📝 个人简介: {user_info.get('desc', '暂无')}")
        print(f"  🆔 小红书ID: {user_info.get('red_id', '未知')}")
        print()
        print("  登录成功！已可以正常使用小红书功能。")
    else:
        print("  ❌ 登录失败")
        print(f"  错误信息: {data.get('msg', '未知错误')}")
    
    print("=" * 60)
    
    await xhs.close_session()
    return data.get('success', False)

if __name__ == "__main__":
    web_session = sys.argv[1] if len(sys.argv) > 1 else "040069b8fdba81d499ed9f75b83b4b4314e571"
    proxy = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = asyncio.run(test_login(web_session, proxy))
    sys.exit(0 if result else 1)
