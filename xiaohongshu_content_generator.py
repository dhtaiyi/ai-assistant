#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书内容生成器 - 基于热门趋势
"""

import random
import json

# 热门内容模板
CONTENT_TEMPLATES = {
    "实用攻略": {
        "topics": [
            "上海省钱攻略", "北京租房指南", "深圳交通攻略",
            "杭州旅游攻略", "成都美食攻略", "广州搬家攻略"
        ],
        "hooks": [
            "姐妹们！答应我一定要看！",
            "后悔没早点知道系列！",
            "吐血整理！建议收藏！",
            "本地人私藏干货！",
            "99%人不知道的隐藏攻略！"
        ],
        "styles": [
            "清单式", "对比式", "时间线式", "问答式"
        ]
    },
    "美食探店": {
        "topics": [
            "上海馄饨", "成都火锅", "北京烤鸭",
            "广州早茶", "西安羊肉泡馍", "长沙小吃"
        ],
        "hooks": [
            "姐妹们！这家我也就吃了5678次！",
            "被问爆了！终于可以说地址了！",
            "连吃一周不腻的宝藏店铺！",
            "本地人推荐才不会出错！"
        ],
        "styles": [
            "测评式", "打卡式", "省钱式", "避雷式"
        ]
    },
    "生活技巧": {
        "topics": [
            "收纳技巧", "清洁技巧", "护肤技巧",
            "时间管理", "省钱技巧", "租房技巧"
        ],
        "hooks": [
            "这个方法我怎么没早点知道！",
            "后悔没早点分享给大家！",
            "真的能省下一个亿！",
            "懒人必备！简单又有效！"
        ],
        "styles": [
            "教程式", "对比式", "清单式", "测评式"
        ]
    },
    "女性话题": {
        "topics": [
            "职场穿搭", "护肤心得", "健身打卡",
            "理财心得", "面试技巧", "自我提升"
        ],
        "hooks": [
            "女生一定要知道的事！",
            "30岁后才明白的道理！",
            "独立女生必看！",
            "拒绝焦虑！做自己！"
        ],
        "styles": [
            "心得分享", "干货教程", "真实测评", "心路历程"
        ]
    }
}

def generate_content(category="随机"):
    """生成小红书内容"""
    
    if category == "随机":
        category = random.choice(list(CONTENT_TEMPLATES.keys()))
    
    template = CONTENT_TEMPLATES.get(category, CONTENT_TEMPLATES["生活技巧"])
    
    topic = random.choice(template["topics"])
    hook = random.choice(template["hooks"])
    style = random.choice(template["styles"])
    
    # 生成标题
    title = f"{hook}\n\n(topic)\n\n今天必须分享给姐妹们！"
    title = title.replace("(topic)", topic)
    
    # 生成正文
    content = f"""【{topic}】{style}来啦！

{hook}

📍 地点/情况：
（填写具体信息）

💡 核心干货：
1. （第一步）
2. （第二步）
3. （第三步）

⚠️ 避坑指南：
- （注意事项1）
- （注意事项2）

📌 小贴士：
（实用小技巧）

👭 姐妹们还有什么问题？
评论区告诉我！

#{topic} #实用攻略 #生活技巧"""
    
    return {
        "category": category,
        "title": title,
        "content": content,
        "tags": [topic, "实用攻略", "生活技巧", "小红书运营"]
    }

def main():
    print("📝 小红书内容生成器")
    print("=" * 60)
    
    # 生成3个不同类型的内容
    categories = ["实用攻略", "美食探店", "生活技巧"]
    
    for i, cat in enumerate(categories, 1):
        print(f"\n{'='*60}")
        print(f"📝 内容 {i} - {cat}")
        print("=" * 60)
        
        content = generate_content(cat)
        
        print(f"\n📌 标题：")
        print(content["title"])
        
        print(f"\n📄 正文：")
        print(content["content"])
        
        print(f"\n🏷️ 标签：")
        print(" ".join(content["tags"]))
        
        print()
    
    print("\n" + "=" * 60)
    print("💡 提示：以上为模板，根据实际情况修改后发布！")
    print("=" * 60)

if __name__ == '__main__':
    main()
