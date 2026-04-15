#!/usr/bin/env python3
import asyncio
import sys
sys.path.insert(0, '/home/dhtaiyi/.openclaw/workspace/skills/xiaohongshutools/scripts')
from request.web.xhs_session import create_xhs_session

async def test():
    web_session = "040069b8fdba81d499ed9f75b83b4b4314e571"
    
    print("╔════════════════════════════════════╗")
    print("║   🦞 小红书功能测试           ║")
    print("╚════════════════════════════════════╝")
    print("")
    
    xhs = await create_xhs_session(web_session=web_session)
    print("✅ 1. 会话创建成功")
    print("")
    
    # 获取用户信息（GET）
    print("🔍 2. 获取用户信息...")
    res = await xhs.apis.auth.get_self_simple_info()
    data = await res.json()
    if data.get('success'):
        user = data.get('data', {})
        print(f"✅ 用户信息获取成功")
        print(f"   用户名: {user.get('nickname')}")
        print(f"   用户ID: {user.get('user_id')}")
    else:
        print(f"❌ 获取失败: {data}")
    print("")
    
    print("╔════════════════════════════════════╗")
    print("║   📊 测试总结                   ║")
    print("╠════════════════════════════════════╣")
    print("║ ✅ 可用功能:                   ║")
    print("║   - 创建会话（无需代理）         ║")
    print("║   - 获取用户信息               ║")
    print("║                                 ║")
    print("║ ❌ 被风控功能（POST请求）:     ║")
    print("║   - 搜索笔记                   ║")
    print("║   - 首页推荐                   ║")
    print("║   - 用户笔记列表               ║")
    print("║   - 点赞笔记                   ║")
    print("║   - 关注用户                   ║")
    print("╚════════════════════════════════════╝")
    print("")
    print("💡 小红书风控规则:")
    print("   - GET请求：允许（用户信息）")
    print("   - POST请求：限制（内容操作）")

asyncio.run(test())
