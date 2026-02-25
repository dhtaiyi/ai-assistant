#!/usr/bin/env python3
"""小红书Cookie最终保存工具"""

import json
import sys

# 尝试从命令行参数读取
if len(sys.argv) > 1:
    cookie_str = ' '.join(sys.argv[1:])
else:
    # 从stdin读取
    cookie_str = sys.stdin.read().strip()

if not cookie_str:
    print("="*60)
    print("  💾 小红书Cookie保存工具")
    print("="*60)
    print("\n使用方法:")
    print("  1. 浏览器访问创作者平台并登录")
    print("  2. F12 → Console")
    print("  3. 粘贴: copy(document.cookie)")
    print("  4. 运行:")
    print('     python3 xiaohongshu-save-now.py "Cookie"')
    print("")
    print("  或管道方式:")
    print("     echo 'Cookie' | python3 xiaohongshu-save-now.py")
    sys.exit(0)

# 解析Cookie
cookies = {}
for item in cookie_str.split(';'):
    item = item.strip()
    if '=' in item:
        k, v = item.split('=', 1)
        cookies[k.strip()] = v.strip()

# 保存
data = {
    'cookies': cookies,
    'saved_at': __import__('datetime').datetime.now().isoformat(),
    'type': 'creator',
    'count': len(cookies)
}

with open('/root/.openclaw/workspace/xiaohongshu-creator-cookies.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("="*60)
print("  💾 Cookie已保存!")
print("="*60)
print(f"\n✅ 保存 {len(cookies)} 个Cookie")
print(f"\n📋 Cookie列表:")
for k, v in cookies.items():
    print(f"   • {k}: {v[:30]}...")
print(f"\n📁 文件: /root/.openclaw/workspace/xiaohongshu-creator-cookies.json")
