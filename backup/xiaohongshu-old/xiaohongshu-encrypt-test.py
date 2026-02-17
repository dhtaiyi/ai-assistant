#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用xiaohongshutools的完整加密模块进行搜索
"""

import asyncio
import sys
import json

# 添加xiaohongshutools路径
sys.path.insert(0, '/root/.openclaw/workspace/skills/xiaohongshutools/scripts')

from request.web.xhs_session import create_xhs_session

# 使用web_session
WEB_SESSION = "040069b8fdba81d499ed90a5b83b4ba5a54c4a"

async def search_with_encrypt():
    print("=== xiaohongshutools加密搜索测试 ===\n")
    
    try:
        # 创建会话（会自动处理所有加密）
        print("1. 创建会话...")
        xhs = await create_xhs_session(web_session=WEB_SESSION)
        print("   ✅ 会话创建成功\n")
        
        # 检查加密头是否已设置
        print("2. 检查加密头...")
        headers = xhs._session.headers
        print(f"   x-s: {headers.get('x-s', '未设置')[:50]}...")
        print(f"   x-s-common: {headers.get('x-s-common', '未设置')[:50]}...")
        print(f"   x-t: {headers.get('x-t', '未设置')}")
        print(f"   x-b3-traceid: {headers.get('x-b3-traceid', '未设置')}")
        print(f"   x-xray-traceid: {headers.get('x-xray-traceid', '未设置')}")
        print("")
        
        # 测试搜索
        print("3. 执行搜索...")
        print("   关键词: 穿搭\n")
        
        # 调用搜索API（会自动添加加密）
        result = await xhs.apis.note.search_notes("穿搭")
        
        print("4. 搜索结果:")
        if result:
            print(f"   ✅ 成功!")
            print(f"   数据类型: {type(result)}")
            if isinstance(result, dict):
                code = result.get('code')
                msg = result.get('msg')
                print(f"   状态码: {code}")
                print(f"   消息: {msg}")
                
                if code == 0:
                    notes = result.get('data', {}).get('notes', [])
                    print(f"   笔记数量: {len(notes)}")
                    return notes
        else:
            print("   ❌ 返回空结果")
        
        return None
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    finally:
        # 关闭会话
        if 'xhs' in dir():
            await xhs.close_session()

async def main():
    notes = await search_with_encrypt()
    
    print("\n" + "="*50)
    if notes:
        print("✅ 测试成功!")
        if notes:
            print(f"\n获取到 {len(notes)} 条笔记")
            # 显示第一条笔记的标题
            if notes[0]:
                title = notes[0].get('note_card', {}).get('title', '无标题')
                print(f"第一条笔记: {title}")
    else:
        print("❌ 测试失败")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main())
