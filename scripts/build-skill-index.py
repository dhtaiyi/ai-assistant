#!/usr/bin/env python3
"""
ClawHub Skill 索引构建器
从本地已安装 skill 提取信息并存储到 LanceDB 向量数据库
"""

import os
import json
import hashlib
from datetime import datetime

SKILLS_DIR = os.path.expanduser('~/.openclaw/skills')
OUTPUT_FILE = '/home/dhtaiyi/.openclaw/workspace/memory/clawhub-skills-index.json'

def extract_skill_info(skill_path):
    """提取 skill 信息"""
    skill_name = os.path.basename(skill_path)
    info = {
        'id': hashlib.md5(skill_path.encode()).hexdigest()[:12],
        'name': skill_name,
        'path': skill_path,
        'description': '',
        'category': 'unknown',
        'files': [],
        'has_skill_md': False,
        'has_readme': False,
        'created_at': datetime.now().isoformat()
    }
    
    # 扫描文件
    for root, dirs, files in os.walk(skill_path):
        for f in files:
            filepath = os.path.join(root, f)
            info['files'].append(f)
            
            if f.lower() == 'skill.md':
                info['has_skill_md'] = True
                # 读取 SKILL.md 获取描述
                try:
                    with open(filepath, 'r', encoding='utf-8') as sf:
                        content = sf.read()
                        # 提取第一行作为描述
                        lines = content.strip().split('\n')
                        for line in lines:
                            if line.strip() and not line.startswith('#'):
                                info['description'] = line.strip()[:200]
                                break
                except:
                    pass
            
            if f.lower() in ['readme.md', 'readme.txt']:
                info['has_readme'] = True
    
    # 分类
    if any(k in skill_name.lower() for k in ['search', 'fetch']):
        info['category'] = 'search'
    elif any(k in skill_name.lower() for k in ['memory', 'recall']):
        info['category'] = 'memory'
    elif any(k in skill_name.lower() for k in ['browser', 'web']):
        info['category'] = 'browser'
    elif any(k in skill_name.lower() for k in ['github', 'git']):
        info['category'] = 'dev'
    elif any(k in skill_name.lower() for k in ['weather', 'finance', 'news']):
        info['category'] = 'data'
    elif any(k in skill_name.lower() for k in ['todoist', 'cron', 'schedule']):
        info['category'] = 'productivity'
    elif any(k in skill_name.lower() for k in ['image', 'vision']):
        info['category'] = 'vision'
    elif any(k in skill_name.lower() for k in ['message', 'telegram', 'discord']):
        info['category'] = 'messaging'
    
    return info

def main():
    print("🔍 扫描本地 Skill...")
    skills = []
    
    if not os.path.exists(SKILLS_DIR):
        print(f"❌ Skills 目录不存在：{SKILLS_DIR}")
        return
    
    for skill_name in os.listdir(SKILLS_DIR):
        skill_path = os.path.join(SKILLS_DIR, skill_name)
        if os.path.isdir(skill_path):
            info = extract_skill_info(skill_path)
            skills.append(info)
            print(f"  ✅ {skill_name} - {info['category']}")
    
    # 保存索引
    output = {
        'version': '1.0',
        'updated_at': datetime.now().isoformat(),
        'total_skills': len(skills),
        'categories': {},
        'skills': skills
    }
    
    # 统计分类
    for s in skills:
        cat = s['category']
        output['categories'][cat] = output['categories'].get(cat, 0) + 1
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 索引已保存到：{OUTPUT_FILE}")
    print(f"📊 总计：{len(skills)} 个 skill")
    print(f"📁 分类：{output['categories']}")

if __name__ == '__main__':
    main()
