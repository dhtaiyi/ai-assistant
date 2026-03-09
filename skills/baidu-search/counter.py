#!/usr/bin/env python3
"""
百度搜索用量追踪
每月1000次，用完提醒
"""
import json
import os
from datetime import datetime

COUNTER_FILE = "/root/.openclaw/workspace/skills/baidu-search/counter.json"
MONTHLY_LIMIT = 1000

def load_counter():
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, 'r') as f:
            data = json.load(f)
            # 检查是否是当月
            now = datetime.now()
            if data.get('month') != f"{now.year}-{now.month:02d}":
                # 新月份，重置计数器
                return {'month': f"{now.year}-{now.month:02d}", 'count': 0, 'limit': MONTHLY_LIMIT}
            return data
    else:
        now = datetime.now()
        return {'month': f"{now.year}-{now.month:02d}", 'count': 0, 'limit': MONTHLY_LIMIT}

def save_counter(data):
    with open(COUNTER_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def increment_and_check():
    data = load_counter()
    data['count'] += 1
    
    remaining = data['limit'] - data['count']
    save_counter(data)
    
    if remaining <= 0:
        return {
            'count': data['count'],
            'limit': data['limit'],
            'remaining': remaining,
            'alert': True,
            'message': "⚠️ 百度搜索本月1000次已用完！请提醒主人续费或充值！"
        }
    elif remaining <= 100:
        return {
            'count': data['count'],
            'limit': data['limit'],
            'remaining': remaining,
            'alert': True,
            'message': f"⚠️ 百度搜索剩余次数不足100次 ({remaining}次)！"
        }
    
    return {
        'count': data['count'],
        'limit': data['limit'],
        'remaining': remaining,
        'alert': False,
        'message': f"百度搜索本月已用 {data['count']} / {data['limit']} 次，剩余 {remaining} 次"
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        result = increment_and_check()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        result = increment_and_check()
        print(result['message'])
