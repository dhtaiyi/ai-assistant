#!/usr/bin/env python3
"""
ClawHub Skill 安装工具
从 ClawHub 安装 skill 到本地
"""

import os
import json
import subprocess
import argparse

SYNC_INDEX_FILE = '/home/dhtaiyi/.openclaw/workspace/memory/clawhub-sync-index.json'
SKILLS_DIR = os.path.expanduser('~/.openclaw/skills')

def load_index():
    """加载同步索引"""
    with open(SYNC_INDEX_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def install_skill(slug):
    """安装单个 skill"""
    print(f"\n📦 安装 skill: {slug}")
    
    # 使用 clawhub CLI 安装
    cmd = ['clawhub', 'install', slug]
    print(f"   执行：{' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print(f"   ✅ 安装成功")
            if result.stdout:
                print(f"   {result.stdout[:200]}")
            return True
        else:
            print(f"   ❌ 安装失败")
            if result.stderr:
                print(f"   {result.stderr[:200]}")
            return False
    except FileNotFoundError:
        print(f"   ❌ clawhub 命令未找到")
        print(f"   提示：运行 'npm install -g clawhub' 安装 CLI")
        return False
    except Exception as e:
        print(f"   ❌ 错误：{e}")
        return False

def list_available(data, category=None):
    """列出可用的 skill"""
    skills = data.get('all_skills', [])
    
    if category == 'top':
        skills = data.get('top_skills', [])
    
    print(f"\n📚 ClawHub 可用 Skill (共 {len(skills)} 个)\n")
    
    for i, s in enumerate(skills[:20], 1):
        status = "✅" if s['installed'] else "🆕"
        print(f"{i}. {status} {s['name']} (v{s['version']})")
        print(f"   {s['summary'][:80]}")
        print(f"   下载：{s['downloads']} | slug: {s['slug']}")
        print()

def search_skill(data, query):
    """搜索 skill"""
    skills = data.get('all_skills', [])
    results = []
    
    query_lower = query.lower()
    for s in skills:
        score = 0
        if query_lower in s['slug'].lower():
            score += 3
        if query_lower in s['name'].lower():
            score += 3
        if query_lower in s['summary'].lower():
            score += 2
        
        if score > 0:
            results.append((score, s))
    
    results.sort(key=lambda x: -x[0])
    
    print(f"\n🔍 搜索结果：{query}\n")
    for score, s in results[:10]:
        status = "✅" if s['installed'] else "🆕"
        print(f"  {status} {s['name']} (v{s['version']})")
        print(f"     {s['summary'][:100]}")
        print(f"     slug: {s['slug']}")

def main():
    parser = argparse.ArgumentParser(description='ClawHub Skill 安装工具')
    parser.add_argument('action', choices=['list', 'install', 'search', 'top'],
                       help='操作类型')
    parser.add_argument('--slug', '-s', type=str, help='skill slug (用于 install)')
    parser.add_argument('--query', '-q', type=str, help='搜索关键词')
    
    args = parser.parse_args()
    
    try:
        data = load_index()
    except FileNotFoundError:
        print("❌ 索引文件不存在，请先运行 sync-clawhub-skills.py")
        return
    
    if args.action == 'list':
        list_available(data)
    elif args.action == 'top':
        list_available(data, category='top')
    elif args.action == 'search':
        if not args.query:
            print("❌ 请提供搜索关键词 (--query)")
            return
        search_skill(data, args.query)
    elif args.action == 'install':
        if not args.slug:
            print("❌ 请提供 skill slug (--slug)")
            print("\n使用 'list' 或 'top' 查看可用 skill")
            return
        install_skill(args.slug)

if __name__ == '__main__':
    main()
