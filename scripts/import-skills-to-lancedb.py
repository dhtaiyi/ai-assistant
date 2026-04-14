#!/usr/bin/env python3
"""
将 ClawHub Skill 索引导入 LanceDB 向量数据库
使用 memory-lancedb-pro 插件的存储层
"""

import os
import json
import sys

# 添加 skill 文本到记忆
INDEX_FILE = '/home/dhtaiyi/.openclaw/workspace/memory/clawhub-skills-index.json'

def main():
    print("📚 导入 Skill 到 LanceDB...")
    
    # 读取索引
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    skills = data.get('skills', [])
    print(f"  找到 {len(skills)} 个 skill")
    
    # 按分类分组
    by_category = {}
    for s in skills:
        cat = s['category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(s)
    
    # 为每个分类创建记忆条目
    memories = []
    for cat, cat_skills in by_category.items():
        text = f"""ClawHub Skill 分类：{cat}

包含 {len(cat_skills)} 个 skill:
"""
        for s in cat_skills[:10]:  # 每个分类最多 10 个
            text += f"\n- {s['name']}: {s['description'][:100] if s['description'] else '无描述'}"
            text += f" (路径：{s['path']})"
        
        if len(cat_skills) > 10:
            text += f"\n... 还有 {len(cat_skills) - 10} 个"
        
        memories.append({
            'category': cat,
            'text': text,
            'count': len(cat_skills)
        })
    
    print(f"\n✅ 准备导入 {len(memories)} 条分类记忆")
    print("\n分类统计:")
    for cat, skills_list in by_category.items():
        print(f"  - {cat}: {len(skills_list)} 个")
    
    # 保存为可导入格式
    output_file = '/home/dhtaiyi/.openclaw/workspace/memory/clawhub-skills-for-lancedb.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({'memories': memories}, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 已保存到：{output_file}")
    print("\n💡 提示：这些记忆会自动被 memory-lancedb-pro 捕获")

if __name__ == '__main__':
    main()
