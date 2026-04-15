#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书内容创作助手
基于 OpenClaw 和 AI 工具创作内容

作者: OpenClaw
版本: 1.0.0
"""

import json
import random


class ContentCreator:
    """小红书内容创作类"""
    
    def __init__(self):
        self.templates = {
            'tutorial': {
                'title': '{keyword}教程：{action}详细指南',
                'content': '''🔥 发现一个超好用的{keyword}工具！

📌 为什么推荐：
• {reason1}
• {reason2}
• {reason3}

💡 使用方法：
1. 第一步...
2. 第二步...
3. 第三步...

📖 详细教程：[待补充]

#关键词 #干货分享 #职场技巧''',
                'hashtags': ['关键词1', '关键词2', '关键词3', '职场技巧', '干货分享']
            },
            'review': {
                'title': '用了{keyword}一个月，真实体验分享',
                'content': '''⏰ 使用{keyword}已经{time}了！

📊 整体评分：⭐⭐⭐⭐⭐

✅ 优点：
• {advantage1}
• {advantage2}

⚠️ 需要改进：
• {disadvantage1}
• {disadvantage2}

💡 适合人群：{target}

📌 总结：{conclusion}

#使用体验 #真实测评 #{keyword}''',
                'hashtags': ['真实测评', '使用体验', '工具推荐', '效率提升']
            },
            'efficiency': {
                'title': '用{keyword}后工作效率提升{percent}%！',
                'content': '''🚀 救命！这个{keyword}也太香了吧！

😫 之前的问题：
• 花费大量时间在{problem}
• 效率低，容易出错

✨ 现在的改变：
• {solution1}
• {solution2}
• {solution3}

📈 效果对比：
之前：{before}
之后：{after}

⏱️ 节省时间：{time_saved}

#效率工具 #工作技巧 #职场生存 #必备工具''',
                'hashtags': ['效率工具', '工作技巧', '职场必备', '时间管理']
            }
        }
        
        self.trending_topics = [
            'AI工具', 'ChatGPT', 'Claude', 'Kimi', 'OpenClaw',
            '编程', '效率', '自动化', '工具推荐', '职场'
        ]
    
    def create_content(self, keyword, content_type='tutorial'):
        """创建内容"""
        template = self.templates.get(content_type, self.templates['tutorial'])
        
        # 随机填充内容
        reasons = [
            '操作简单，适合新手',
            '功能强大，覆盖面广',
            '免费使用，性价比高',
            'AI 驱动，智能高效',
            '社区活跃，资源丰富'
        ]
        
        advantages = [
            '响应速度快',
            '准确率高',
            '界面简洁',
            '功能丰富',
            '支持多平台'
        ]
        
        disadvantages = [
            '上手需要一定时间',
            '部分功能需要付费',
            '网络延迟偶尔存在',
            '需要一定的技术基础'
        ]
        
        content = template['content'].format(
            keyword=keyword,
            reason1=random.choice(reasons),
            reason2=random.choice(reasons),
            reason3=random.choice(reasons),
            advantage1=random.choice(advantages),
            advantage2=random.choice(advantages),
            disadvantage1=random.choice(disadvantages),
            disadvantage2=random.choice(disadvantages),
            time='一个月',
            percent=str(random.randint(30, 80)),
            problem='重复性工作',
            solution1='自动化处理，节省时间',
            solution2='AI 辅助，效率翻倍',
            solution3='一键操作，简单快捷',
            before='手动操作 2 小时/天',
            after='自动处理 30 分钟/天',
            time_saved='每天 1.5 小时',
            action='快速上手',
            target='职场人士',
            conclusion='强烈推荐，值得尝试'
        )
        
        title = template['title'].format(
            keyword=keyword,
            action='快速上手',
            time='一个月',
            percent=str(random.randint(30, 80))
        )
        
        hashtags = template['hashtags'] + [keyword]
        
        return {
            'title': title,
            'content': content,
            'hashtags': hashtags,
            'keyword': keyword,
            'type': content_type
        }
    
    def save_content(self, content, filename='content_draft.json'):
        """保存内容到文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
        print(f"✅ 内容已保存到: {filename}")


def main():
    """主函数"""
    creator = ContentCreator()
    
    print("="*60)
    print("  ✍️ 小红书内容创作助手")
    print("="*60)
    
    # 创建不同类型的内容
    keywords = ['AI助手', 'ChatGPT', '编程工具', '效率软件']
    
    for keyword in keywords:
        print(f"\n📌 创作主题: {keyword}")
        print("-"*60)
        
        # 教程类
        tutorial = creator.create_content(keyword, 'tutorial')
        print(f"📝 教程类: {tutorial['title']}")
        
        # 效率类
        efficiency = creator.create_content(keyword, 'efficiency')
        print(f"⚡ 效率类: {efficiency['title']}")
        
        # 评测类
        review = creator.create_content(keyword, 'review')
        print(f"⭐ 评测类: {review['title']}")
    
    # 保存所有内容
    all_contents = []
    for keyword in keywords:
        all_contents.append(creator.create_content(keyword, 'tutorial'))
        all_contents.append(creator.create_content(keyword, 'efficiency'))
        all_contents.append(creator.create_content(keyword, 'review'))
    
    creator.save_content(all_contents, 'content_drafts.json')
    
    print("\n" + "="*60)
    print("  ✅ 内容创作完成！")
    print("="*60)


if __name__ == "__main__":
    main()
