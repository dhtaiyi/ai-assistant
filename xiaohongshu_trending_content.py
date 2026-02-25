#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书热门内容创作 - 基于当前趋势
"""

# 基于推荐数据分析的热门话题
TRENDING_TOPICS = {
    "生活服务": {
        "examples": ["护工价格", "家政服务", "搬家"],
        "hook": "姐妹们！这个价格表必须收藏！",
        "format": "价格清单 + 实用信息"
    },
    "省钱攻略": {
        "examples": ["28元馄饨", "省钱技巧", "优惠信息"],
        "hook": "救命！28元两个！",
        "format": "价格对比 + 个人体验"
    },
    "宠物相关": {
        "examples": ["猫咪", "宠物用品", "宠物保暖"],
        "hook": "给毛孩子安排上！",
        "format": "实用教程 + 可爱照片"
    },
    "女性职场": {
        "examples": ["律师包", "职场穿搭", "女性用品"],
        "hook": "女生一定要知道！",
        "format": "好物推荐 + 使用感受"
    },
    "旅游攻略": {
        "examples": ["成都不废腿", "上海旅游", "旅游行程"],
        "hook": "吐血整理！建议收藏！",
        "format": "行程规划 + 避坑指南"
    },
    "美食探店": {
        "examples": ["馄饨", "年夜饭", "地方美食"],
        "hook": "本地人才知道的地道美食！",
        "format": "美食测评 + 推荐理由"
    }
}

def generate_trending_content(topic_type="随机"):
    """生成热门话题内容"""
    
    if topic_type == "随机":
        topic_type = random.choice(list(TRENDING_TOPICS.keys()))
    
    template = TRENDING_TOPICS.get(topic_type, TRENDING_TOPICS["生活服务"])
    
    topic = random.choice(template["examples"])
    
    title = f"{template['hook']}\n\n{topic} | 真实分享"
    
    content = f"""📍 真实体验分享

{topic} | 亲身经历

💡 为什么分享：
（说明分享的原因和背景）

📝 具体内容：

1. 【地点/情况】
（详细信息）

2. 【价格/费用】
（具体价格）

3. 【优缺点】
✅ 优点：
❌ 缺点：

4. 【个人感受】
（真实体验）

5. 【推荐指数】⭐⭐⭐⭐⭐

📌 实用Tips：
- 小贴士1
- 小贴士2

👭 姐妹们有类似经历吗？
评论区聊聊！

#{topic} #{template['examples'][0]} #实用攻略 #生活分享"""

    return {
        "type": topic_type,
        "title": title,
        "content": content,
        "format": template["format"]
    }

def main():
    print("🔥 小红书热门内容创作器")
    print("=" * 70)
    
    # 生成5个热门内容
    types = ["生活服务", "省钱攻略", "宠物相关", "女性职场", "旅游攻略"]
    
    for i, topic_type in enumerate(types, 1):
        content = generate_trending_content(topic_type)
        
        print(f"\n{'='*70}")
        print(f"🔥 内容 {i} - {topic_type}")
        print(f"📐 格式: {content['format']}")
        print("=" * 70)
        
        print(f"\n📌 标题：")
        print(content["title"])
        
        print(f"\n📄 正文：")
        print(content["content"])
        
        print()
    
    print("=" * 70)
    print("💡 提示：根据实际体验修改后发布！")
    print("=" * 70)

if __name__ == '__main__':
    import random
    main()
