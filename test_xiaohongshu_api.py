#!/usr/bin/env python3
"""使用xiaohongshutools调用小红书API - 带登录会话"""

import asyncio
import sys
import json

# 添加路径
sys.path.insert(0, '/root/.openclaw/workspace/skills/xiaohongshutools/scripts')

from request.web.xhs_session import create_xhs_session
from request.web.apis.note import Note, HomeFeedCategory
from request.web.apis.user import User

async def main():
    # 使用保存的web_session
    web_session = "040069b8fdba81d499ed8b10a13b4b4a755af3"
    
    # 创建会话（带登录会话）
    xhs = await create_xhs_session(proxy=None, web_session=web_session)
    
    # 获取首页Feeds
    print("=" * 50)
    print("获取首页Feeds:")
    print("=" * 50)
    try:
        note_api = Note(xhs)
        res = await note_api.get_homefeed(category=HomeFeedCategory.homefeed_for_u)
        data = await res.json()
        print(json.dumps(data, indent=2, ensure_ascii=False)[:3000])
    except Exception as e:
        print(f"Error: {e}")
    
    # 搜索笔记
    print("\n" + "=" * 50)
    print("搜索笔记 (关键词: 美食):")
    print("=" * 50)
    try:
        res = await note_api.search_notes("美食", page=1, page_size=5)
        data = await res.json()
        print(json.dumps(data, indent=2, ensure_ascii=False)[:3000])
    except Exception as e:
        print(f"Error: {e}")
    
    # 获取用户信息
    print("\n" + "=" * 50)
    print("获取当前用户信息:")
    print("=" * 50)
    try:
        user_api = User(xhs)
        res = await user_api.get_self_info()
        data = await res.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")
    
    await xhs.close_session()

asyncio.run(main())
