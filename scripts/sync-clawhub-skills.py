#!/usr/bin/env python3
"""
ClawHub Skill 同步工具
主动拉取 ClawHub 上的 skill 并与本地同步
"""

import os
import json
import hashlib
import subprocess
from datetime import datetime

CLAWHUB_API = "https://clawhub.ai/api/v1/skills"
LOCAL_SKILLS_DIR = os.path.expanduser('~/.openclaw/skills')
SYNC_INDEX_FILE = '/home/dhtaiyi/.openclaw/workspace/memory/clawhub-sync-index.json'

def fetch_skills(cursor=None):
    """从 ClawHub API 获取 skill 列表"""
    url = CLAWHUB_API
    if cursor:
        url += f"?cursor={cursor}"
    
    try:
        result = subprocess.run(
            ['curl', '-s', url],
            capture_output=True,
            text=True,
            timeout=30
        )
        data = json.loads(result.stdout)
        return data
    except Exception as e:
        print(f"❌ API 请求失败：{e}")
        return None

def parse_skill_info(skill_data):
    """解析 skill 信息"""
    return {
        'slug': skill_data.get('slug', 'unknown'),
        'name': skill_data.get('displayName', skill_data.get('slug', 'unknown')),
        'summary': skill_data.get('summary', '')[:200],
        'version': skill_data.get('tags', {}).get('latest', 'unknown'),
        'downloads': skill_data.get('stats', {}).get('downloads', 0),
        'installs': skill_data.get('stats', {}).get('installsAllTime', 0),
        'stars': skill_data.get('stats', {}).get('stars', 0),
        'updated_at': skill_data.get('updatedAt', 0),
        'created_at': skill_data.get('createdAt', 0),
        'changelog': skill_data.get('latestVersion', {}).get('changelog', '')[:200],
        'id': hashlib.md5(skill_data.get('slug', '').encode()).hexdigest()[:12]
    }

def check_local_install(slug):
    """检查 skill 是否已本地安装"""
    local_path = os.path.join(LOCAL_SKILLS_DIR, slug.replace('-', '_'))
    if not os.path.exists(local_path):
        # 尝试原始 slug
        local_path = os.path.join(LOCAL_SKILLS_DIR, slug)
    
    return {
        'installed': os.path.exists(local_path),
        'path': local_path if os.path.exists(local_path) else None
    }

def sync_skills():
    """主同步函数"""
    print("🔄 开始同步 ClawHub Skill...\n")
    
    all_skills = []
    cursor = None
    page = 1
    
    # 获取所有 skill（分页）
    while True:
        print(f"📥 获取第 {page} 页...")
        data = fetch_skills(cursor)
        
        if not data or 'items' not in data:
            print("❌ 获取失败")
            break
        
        items = data.get('items', [])
        print(f"   获取到 {len(items)} 个 skill")
        
        for item in items:
            skill_info = parse_skill_info(item)
            local_status = check_local_install(skill_info['slug'])
            skill_info.update(local_status)
            all_skills.append(skill_info)
        
        # 检查是否有下一页
        cursor = data.get('nextCursor')
        if not cursor:
            break
        
        page += 1
        if page > 5:  # 最多获取 5 页
            break
    
    # 统计
    total = len(all_skills)
    installed = sum(1 for s in all_skills if s['installed'])
    not_installed = total - installed
    
    # 按热度排序
    all_skills.sort(key=lambda x: -x['downloads'])
    top_skills = all_skills[:20]
    
    # 保存索引
    output = {
        'version': '1.0',
        'synced_at': datetime.now().isoformat(),
        'total_skills': total,
        'installed': installed,
        'not_installed': not_installed,
        'top_skills': top_skills,
        'all_skills': all_skills
    }
    
    with open(SYNC_INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    # 输出报告
    print(f"\n{'='*50}")
    print(f"📊 同步完成")
    print(f"{'='*50}")
    print(f"总技能数：{total}")
    print(f"已安装：{installed} ✅")
    print(f"未安装：{not_installed} 🆕")
    print(f"\n📁 索引已保存到：{SYNC_INDEX_FILE}")
    
    # 显示 Top 10
    print(f"\n🔥 Top 10 热门 Skill:")
    for i, s in enumerate(top_skills[:10], 1):
        status = "✅" if s['installed'] else "🆕"
        print(f"  {i}. {status} {s['name']} (v{s['version']})")
        print(f"     {s['summary'][:60]}...")
        print(f"     下载：{s['downloads']} | 安装：{s['installs']}")
    
    return output

def main():
    try:
        sync_skills()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"\n❌ 错误：{e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
