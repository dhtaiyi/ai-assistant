#!/usr/bin/env python3
"""
ClawHub Skill 查询工具
支持分类浏览和语义搜索
"""

import json
import argparse
import sys

INDEX_FILE = '/home/dhtaiyi/.openclaw/workspace/memory/clawhub-skills-index.json'

def load_index():
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def list_all(data):
    """列出所有 skill"""
    print(f"📚 ClawHub Skill 列表 (共 {data['total_skills']} 个)\n")
    for s in data['skills']:
        cat_emoji = {
            'search': '🔍', 'browser': '🌐', 'memory': '🧠',
            'dev': '💻', 'vision': '🖼️', 'data': '📊',
            'productivity': '✅', 'unknown': '📦'
        }.get(s['category'], '📦')
        print(f"  {cat_emoji} {s['name']} ({s['category']})")
        if s['description'] and s['description'] != '---':
            print(f"     └─ {s['description'][:80]}")

def list_by_category(data, category):
    """按分类列出"""
    print(f"📁 分类：{category}\n")
    count = 0
    for s in data['skills']:
        if s['category'] == category:
            print(f"  - {s['name']}")
            if s['description'] and s['description'] != '---':
                print(f"    {s['description'][:100]}")
            count += 1
    print(f"\n共 {count} 个 skill")

def search(data, query):
    """简单关键词搜索"""
    print(f"🔍 搜索：{query}\n")
    results = []
    query_lower = query.lower()
    
    for s in data['skills']:
        score = 0
        # 名称匹配
        if query_lower in s['name'].lower():
            score += 3
        # 描述匹配
        if s['description'] and query_lower in s['description'].lower():
            score += 2
        # 分类匹配
        if query_lower in s['category'].lower():
            score += 1
        
        if score > 0:
            results.append((score, s))
    
    # 排序
    results.sort(key=lambda x: -x[0])
    
    if not results:
        print("  未找到匹配的 skill")
        return
    
    print(f"找到 {len(results)} 个匹配的 skill:\n")
    for score, s in results[:10]:
        print(f"  ⭐ {s['name']} (分类：{s['category']})")
        if s['description'] and s['description'] != '---':
            print(f"     {s['description'][:100]}")
        print(f"     路径：{s['path']}")

def show_stats(data):
    """显示统计"""
    print("📊 ClawHub Skill 统计\n")
    print(f"总技能数：{data['total_skills']}")
    print(f"更新时间：{data['updated_at']}")
    print(f"\n分类分布:")
    for cat, count in sorted(data['categories'].items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count} 个")

def main():
    parser = argparse.ArgumentParser(description='ClawHub Skill 查询工具')
    parser.add_argument('--list', action='store_true', help='列出所有 skill')
    parser.add_argument('--category', '-c', type=str, help='按分类列出')
    parser.add_argument('--search', '-s', type=str, help='搜索 skill')
    parser.add_argument('--stats', action='store_true', help='显示统计')
    
    args = parser.parse_args()
    
    try:
        data = load_index()
    except FileNotFoundError:
        print("❌ 索引文件不存在，请先运行 build-skill-index.py")
        sys.exit(1)
    
    if args.stats:
        show_stats(data)
    elif args.category:
        list_by_category(data, args.category)
    elif args.search:
        search(data, args.search)
    elif args.list:
        list_all(data)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
