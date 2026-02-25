#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书查询工具 - 完整版
"""

import requests
import json
import sys

API = "http://localhost:18060/api/v1"

def check_login():
    """检查登录状态"""
    r = requests.get(f"{API}/login/status", timeout=15)
    return r.json()

def get_user_info():
    """获取用户信息"""
    r = requests.get(f"{API}/user/me", timeout=15)
    return r.json()

def get_feeds(limit=5):
    """获取推荐列表"""
    r = requests.get(f"{API}/feeds/list", timeout=15)
    data = r.json()
    
    if data.get('success') and data.get('data', {}).get('feeds'):
        return data['data']['feeds'][:limit]
    return []

def search_feeds(keyword):
    """搜索内容"""
    r = requests.post(f"{API}/feeds/search", json={"keyword": keyword}, timeout=15)
    return r.json()

def main():
    print("=" * 70)
    print("    📱 小红书查询工具")
    print("=" * 70)
    
    # 1. 登录状态
    print("\n✅ 1. 登录状态:")
    login = check_login()
    if login.get('success'):
        data = login.get('data', {})
        print(f"   登录状态: {'✅ 已登录' if data.get('is_logged_in') else '❌ 未登录'}")
        if data.get('username'):
            print(f"   用户名: {data.get('username')}")
    else:
        print(f"   获取失败: {login.get('message')}")
    
    # 2. 用户信息
    print("\n👤 2. 用户信息:")
    user = get_user_info()
    if user.get('success'):
        data = user.get('data', {}).get('data', {})
        basic = data.get('userBasicInfo', {})
        print(f"   昵称: {basic.get('nickname', 'N/A')}")
        print(f"   ID: {basic.get('redId', 'N/A')}")
        print(f"   IP: {basic.get('ipLocation', 'N/A')}")
        print(f"   简介: {basic.get('desc', 'N/A')}")
    else:
        print(f"   获取失败")
    
    # 3. 推荐列表
    print("\n📝 3. 推荐笔记:")
    feeds = get_feeds(5)
    if feeds:
        for i, feed in enumerate(feeds, 1):
            card = feed.get('noteCard', {})
            user = card.get('user', {})
            interact = card.get('interactInfo', {})
            
            title = card.get('displayTitle', 'N/A')[:30]
            author = user.get('nickname', 'N/A')
            likes = interact.get('likedCount', '0')
            
            print(f"   {i}. {title}...")
            print(f"      👤 {author} | 👍 {likes}赞")
    else:
        print("   获取失败")
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    main()
