#!/usr/bin/env python3
"""
ClawHub Skill 完整同步工具
拉取 ClawHub 上 ALL skill（不限页数）
"""

import os
import json
import hashlib
import time
import urllib.request
from datetime import datetime

CLAWHUB_API = "https://clawhub.ai/api/v1/skills"
LOCAL_SKILLS_DIR = os.path.expanduser('~/.openclaw/skills')
SYNC_INDEX_FILE = '/home/dhtaiyi/.openclaw/workspace/memory/clawhub-sync-index-full.json'

def fetch_skills_page(cursor=None):
    """获取单页 skill"""
    url = CLAWHUB_API
    if cursor:
        url += f"?cursor={cursor}"
    
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.loads(response.read().decode())
            return data
    except Exception as e:
        print(f"❌ API 请求失败：{e}")
        return None

def parse_skill_info(skill_data):
    """解析 skill 详细信息"""
    return {
        'slug': skill_data.get('slug', 'unknown'),
        'name': skill_data.get('displayName', skill_data.get('slug', 'unknown')),
        'summary': skill_data.get('summary', ''),
        'version': skill_data.get('tags', {}).get('latest', 'unknown'),
        'downloads': skill_data.get('stats', {}).get('downloads', 0),
        'installs': skill_data.get('stats', {}).get('installsAllTime', 0),
        'installs_current': skill_data.get('stats', {}).get('installsCurrent', 0),
        'stars': skill_data.get('stats', {}).get('stars', 0),
        'comments': skill_data.get('stats', {}).get('comments', 0),
        'versions_count': skill_data.get('stats', {}).get('versions', 0),
        'updated_at': skill_data.get('updatedAt', 0),
        'created_at': skill_data.get('createdAt', 0),
        'changelog': skill_data.get('latestVersion', {}).get('changelog', ''),
        'id': hashlib.md5(skill_data.get('slug', '').encode()).hexdigest()[:12]
    }

def check_local_install(slug):
    """检查 skill 是否已本地安装"""
    # 尝试多种可能的路径
    possible_paths = [
        os.path.join(LOCAL_SKILLS_DIR, slug.replace('-', '_')),
        os.path.join(LOCAL_SKILLS_DIR, slug),
        os.path.join(LOCAL_SKILLS_DIR, slug.replace('-', '')),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return {'installed': True, 'path': path}
    
    return {'installed': False, 'path': None}

def sync_all_skills():
    """完整同步所有 skill（不限页数）"""
    print("🔄 开始完整同步 ClawHub Skill...\n")
    print("⚠️  警告：这可能需要几分钟，因为要获取 ALL 分页数据\n")
    
    all_skills = []
    cursor = None
    page = 1
    total_pages = None
    
    # 无限分页，直到没有 nextCursor
    while True:
        print(f"📥 获取第 {page} 页...", end=" ", flush=True)
        data = fetch_skills_page(cursor)
        
        if not data or 'items' not in data:
            print("❌ 获取失败")
            break
        
        items = data.get('items', [])
        print(f"✅ {len(items)} 个 skill")
        
        for item in items:
            skill_info = parse_skill_info(item)
            local_status = check_local_install(skill_info['slug'])
            skill_info.update(local_status)
            all_skills.append(skill_info)
        
        # 检查是否有下一页
        cursor = data.get('nextCursor')
        if not cursor:
            print(f"\n🎉 没有更多页面了！")
            break
        
        page += 1
        
        # 每 10 页休息一下，避免 API 限流
        if page % 10 == 0:
            print(f"   已获取 {page} 页，暂停 2 秒...")
            time.sleep(2)
    
    # 统计
    total = len(all_skills)
    installed = sum(1 for s in all_skills if s['installed'])
    not_installed = total - installed
    
    # 按热度排序（下载量）
    all_skills.sort(key=lambda x: -x['downloads'])
    
    # 分类统计
    categories = {}
    for s in all_skills:
        slug = s['slug'].lower()
        if any(k in slug for k in ['weather', 'climate', 'yr']):
            cat = 'weather'
        elif any(k in slug for k in ['finance', 'stock', 'crypto', 'binance', 'trading', 'equity']):
            cat = 'finance'
        elif any(k in slug for k in ['security', 'guard', 'protect']):
            cat = 'security'
        elif any(k in slug for k in ['email', 'sendgrid', 'mail']):
            cat = 'email'
        elif any(k in slug for k in ['research', 'analysis', 'analyst']):
            cat = 'research'
        elif any(k in slug for k in ['github', 'git']):
            cat = 'dev'
        elif any(k in slug for k in ['image', 'vision', 'ocr', 'qrcode']):
            cat = 'vision'
        elif any(k in slug for k in ['calendar', 'schedule', 'reminder', 'cron']):
            cat = 'productivity'
        elif any(k in slug for k in ['memory', 'recall']):
            cat = 'memory'
        elif any(k in slug for k in ['search', 'fetch', 'query']):
            cat = 'search'
        else:
            cat = 'other'
        
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(s)
    
    # 保存完整索引
    output = {
        'version': '2.0',
        'synced_at': datetime.now().isoformat(),
        'total_skills': total,
        'installed': installed,
        'not_installed': not_installed,
        'categories': {k: len(v) for k, v in categories.items()},
        'top_50': all_skills[:50],
        'all_skills': all_skills,
        'by_category': categories
    }
    
    with open(SYNC_INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    # 输出报告
    print(f"\n{'='*60}")
    print(f"📊 完整同步完成")
    print(f"{'='*60}")
    print(f"总技能数：{total}")
    print(f"已安装：{installed} ✅")
    print(f"未安装：{not_installed} 🆕")
    print(f"总页数：{page}")
    print(f"\n📁 索引已保存到：{SYNC_INDEX_FILE}")
    
    # 分类统计
    print(f"\n📂 分类统计:")
    for cat, skills in sorted(categories.items(), key=lambda x: -len(x[1])):
        print(f"  {cat}: {len(skills)} 个")
    
    # Top 20
    print(f"\n🔥 Top 20 热门 Skill:")
    for i, s in enumerate(all_skills[:20], 1):
        status = "✅" if s['installed'] else "🆕"
        print(f"  {i}. {status} {s['name']} (v{s['version']})")
        print(f"     {s['summary'][:70]}...")
        print(f"     下载：{s['downloads']} | 安装：{s['installs']} | ⭐ {s['stars']}")
    
    return output

def main():
    try:
        sync_all_skills()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"\n❌ 错误：{e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
