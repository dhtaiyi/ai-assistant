#!/usr/bin/env python3
"""测试小红书Cookie是否有效"""

import json
import subprocess

print("="*60)
print("  🔍 小红书Cookie状态测试")
print("="*60)
print()

# 1. 检查Cookie文件
print("1️⃣ Cookie文件检查")
print("-"*60)
try:
    with open('/home/dhtaiyi/.openclaw/workspace/xiaohongshu-creator-cookies.json') as f:
        data = json.load(f)
    
    cookies = data.get('cookies', {})
    saved_at = data.get('saved_at', 'N/A')
    
    print(f"✅ 文件存在")
    print(f"   保存时间: {saved_at}")
    print(f"   Cookie数量: {len(cookies)}")
    
except Exception as e:
    print(f"❌ 文件错误: {e}")
    exit(1)

# 2. 检查关键Cookie
print()
print("2️⃣ 关键Cookie检查")
print("-"*60)

key_cookies = [
    'access-token-creator.xiaohongshu.com',
    'web_session',
    'customer-sso-sid',
    'x-user-id-creator.xiaohongshu.com',
    'galaxy_creator_session_id'
]

for cookie in key_cookies:
    if cookie in cookies:
        val = cookies[cookie][:20] + '...' if len(cookies[cookie]) > 20 else cookies[cookie]
        print(f"✅ {cookie}: {val}")
    else:
        print(f"❌ 缺失: {cookie}")

# 3. 检查保存时间
print()
print("3️⃣ Cookie时效性")
print("-"*60)

from datetime import datetime

try:
    saved_time = datetime.fromisoformat(saved_at.replace('Z', '+00:00'))
    now = datetime.now()
    age_hours = (now - saved_time).total_seconds() / 3600
    
    print(f"   保存时间: {saved_time}")
    print(f"   当前时间: {now}")
    print(f"   保存时长: {age_hours:.1f} 小时")
    
    if age_hours > 24:
        print("⚠️  警告: Cookie已超过24小时，可能过期")
    else:
        print("✅ Cookie在24小时内")
        
except Exception as e:
    print(f"⚠️  时间解析错误: {e}")

# 4. 生成Cookie字符串
print()
print("4️⃣ Cookie格式")
print("-"*60)

cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
print(f"总长度: {len(cookie_str)} 字符")
print(f"前100字符: {cookie_str[:100]}...")

print()
print("="*60)
print("  ✅ 测试完成")
print("="*60)
