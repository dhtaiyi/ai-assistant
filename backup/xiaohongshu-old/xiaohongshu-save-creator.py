#!/usr/bin/env python3
"""小红书创作者Cookie保存工具"""

import json
import sys

def save_cookie(cookie_str):
    """保存Cookie字符串"""
    cookies = {}
    
    # 解析Cookie字符串
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
        'note': '手动保存的创作者Cookie'
    }
    
    with open('/root/.openclaw/workspace/xiaohongshu-creator-cookies.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return len(cookies)

def main():
    print("="*60)
    print("  💾 小红书创作者Cookie保存工具")
    print("="*60)
    
    if len(sys.argv) > 1:
        # 从参数读取
        cookie_str = ' '.join(sys.argv[1:])
        count = save_cookie(cookie_str)
        print(f"\n✅ 保存成功!")
        print(f"   Cookie数量: {count}")
    else:
        print("\n使用方法:")
        print("  python3 xiaohongshu-save-creator.py 'Cookie字符串'")
        print("")
        print("步骤:")
        print("  1. 浏览器访问 https://creator.xiaohongshu.com")
        print("  2. 完成登录")
        print("  3. F12 → Console")
        print("  4. 粘贴:")
        print("     copy(document.cookie)")
        print("  5. 运行:")
        print('     python3 xiaohongshu-save-creator.py "粘贴的Cookie"')
        print("")
        print("示例:")
        print('  python3 xiaohongshu-save-creator.py "a1=xxx; web_session=xxx; ..."')

if __name__ == "__main__":
    main()
