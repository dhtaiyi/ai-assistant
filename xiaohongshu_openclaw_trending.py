#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 小红书内容 - 基于热门趋势
"""

import random

# 基于热门趋势的OpenClaw内容
TRENDING_TOPICS = {
    "AI效率神器": {
        "keywords": ["AI助手", "效率工具", "摸鱼神器", "打工人"],
        "hooks": [
            "救命！这个AI助手让我每天准时下班！",
            "领导不知道的摸鱼神器！",
            "用完这个AI，我的同事都以为我开挂了！",
            "这个AI让我从加班狗变成准时下班族！",
            "后悔没早点发现！工作效率提升300%！"
        ],
        "features": [
            "多模型智能切换（MiniMax/Qwen/Kimi）",
            "自动化任务处理",
            "24小时不间断运行",
            "多平台内容管理",
            "智能任务分配"
        ],
        "benefits": [
            "每天节省3小时+",
            "减少重复性工作",
            "提升工作质量",
            "解放双手和大脑",
            "准时下班不是梦"
        ]
    },
    "ChatGPT替代": {
        "keywords": ["ChatGPT替代", "AI写作", "智能助手"],
        "hooks": [
            "用腻了ChatGPT？这个AI更香！",
            "终于找到比ChatGPT好用的替代品！",
            "这个AI比ChatGPT更适合中国宝宝体质！",
            "ChatGPT有的功能它都有，还免费！",
            "告别ChatGPT，我选这个！"
        ],
        "features": [
            "支持中文优化",
            "多模型切换",
            "免费使用",
            "响应速度快",
            "持续更新"
        ],
        "benefits": [
            "不用翻墙",
            "免费无限使用",
            "中文理解更好",
            "响应更快速",
            "功能更全面"
        ]
    },
    "打工人必备": {
        "keywords": ["打工人", "职场技巧", "效率提升"],
        "hooks": [
            "打工人必入的AI神器！",
            "领导绝对不会告诉你的效率工具！",
            "有了它，摸鱼也能完成KPI！",
            "这个AI，让我在公司横着走！",
            "同事都在偷偷用的效率工具！"
        ],
        "features": [
            "自动化报告生成",
            "智能日程管理",
            "邮件自动处理",
            "数据自动分析",
            "任务提醒功能"
        ],
        "benefits": [
            "准时下班",
            "摸鱼也能完成工作",
            "工作更有成就感",
            "减少加班",
            "提升职场竞争力"
        ]
    },
    "自媒体运营": {
        "keywords": ["自媒体", "内容创作", "小红书运营"],
        "hooks": [
            "做小红书的一定要试试这个AI！",
            "这个AI让我内容产出效率提升10倍！",
            "自媒体人不能错过的AI工具！",
            "有了它，我的内容终于爆了！",
            "AI帮我写文案，流量直接起飞！"
        ],
        "features": [
            "多平台内容生成",
            "小红书笔记创作",
            "数据分析",
            "自动排期发布",
            "热门话题追踪"
        ],
        "benefits": [
            "内容产出更快",
            "数据反馈及时",
            "运营更轻松",
            "流量提升",
            "粉丝增长"
        ]
    },
    "多模型切换": {
        "keywords": ["多模型", "AI对比", "智能切换"],
        "hooks": [
            "一个AI能用4个模型，这也太香了！",
            "还在纠结用哪个AI？这个帮你自动选！",
            "这个AI集合了MiniMax/Qwen/Kimi/Claude！",
            "最懂你的AI，知道什么时候用什么模型！",
            "模型切换不用愁，AI帮你自动匹配！"
        ],
        "features": [
            "MiniMax M2.1模型",
            "Qwen3 Max模型", 
            "Kimi智能模型",
            "自动模型匹配",
            "最优效果输出"
        ],
        "benefits": [
            "不用手动选择",
            "效果更优化",
            "使用更便捷",
            "覆盖更多场景",
            "性价比更高"
        ]
    }
}

def generate_trending_content():
    """生成热门趋势内容"""
    
    topic_type = random.choice(list(TRENDING_TOPICS.keys()))
    template = TRENDING_TOPICS[topic_type]
    
    hook = random.choice(template["hooks"])
    feature = random.choice(template["features"])
    benefit = random.choice(template["benefits"])
    
    # 标题
    title = hook
    
    # 正文
    content = f"""{hook}

作为一个（资深打工人/自媒体人/创业者），平时工作忙到飞起，重复性工作多到让人崩溃...

直到发现了OpenClaw这个AI助手，真的打开了新世界的大门！

💡 为什么推荐OpenClaw？

【核心功能】
✅ {template['features'][0]}
✅ {template['features'][1]}
✅ {template['features'][2]}
✅ {template['features'][3]}
✅ {template['features'][4]}

【我的使用体验】
{benefit}，真的惊艳到我了！

📝 我主要用它来做：
- {random.choice(['自动化日常任务', '智能内容生成', '多平台数据管理', '任务分配提醒', '数据分析报告'])}
- {random.choice(['文章撰写', '文案优化', '数据整理', '日程管理', '邮件处理'])}
- {random.choice(['定时发布', '内容排期', '趋势分析', '竞品研究', '效果追踪'])}

【效果对比】
使用前：
❌ 每天加班到9点
❌ 工作做不完
❌ 周末也要加班

使用后：
✅ 准时6点下班
✅ 工作轻松完成
✅ 周末完全自由

⚠️ 小提示：
- 建议先从小任务开始熟悉
- 可以根据需求定制工作流
- 简单配置就能上手

👭 姐妹们有什么想问的？
评论区告诉我！

#{' #'.join(template['keywords'][:3])} #AI工具 #效率神器 #职场技巧"""

    return {
        "type": topic_type,
        "title": title,
        "content": content,
        "keywords": template["keywords"]
    }

# 生成5个热门内容
print("=" * 75)
print("    🔥 OpenClaw 小红书热门内容 - 基于当前趋势")
print("=" * 75)

for i in range(5):
    content = generate_trending_content()
    
    print(f"\n{'='*75}")
    print(f"🔥 内容 {i+1} - {content['type']}")
    print("=" * 75)
    
    print(f"\n📌 标题：")
    print(content["title"])
    
    print(f"\n📄 正文：")
    print(content["content"][:800] + "...")
    
    print(f"\n🏷️ 标签：")
    print(" ".join(content["keywords"]))
    
    print()

print("=" * 75)
print("💡 提示：根据实际使用体验修改后发布！")
print("=" * 75)
