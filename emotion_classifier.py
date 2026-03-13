#!/usr/bin/env python3
"""
语言情绪分类器 V2
支持更丰富的情绪识别（30+种）
"""
import re
from typing import Dict, List, Tuple

class EmotionClassifier:
    """情绪分类器 V2"""
    
    # 情绪定义及其关键词（扩展版）
    EMOTIONS = {
        # === 正面情绪 ===
        "开心": {
            "keywords": ["好开心", "开心", "哈哈", "太棒", "厉害", "爱你", "么么", "好喜欢", "太好了", "超开心", "兴奋", "欢乐", "快乐", "happy", "哈哈笑", "笑死了", "笑死", "笑", "嘻"],
            "weight": 1.0
        },
        "超开心": {
            "keywords": ["笑死", "笑疯", "笑到", "太逗", "笑点", "笑喷", "笑抽", "笑岔气", "笑翻天", "笑尿", "笑cry", "笑到肚子疼"],
            "weight": 1.2
        },
        "温柔": {
            "keywords": ["抱抱", "亲亲", "么么哒", "爱你", "好想", "乖", "么么", "乖乖", "宝贝", "小心肝", "甜", "柔软", "温暖", "柔和", "温顺", "柔和"],
            "weight": 1.0
        },
        "可爱": {
            "keywords": ["可爱", "哇", "好棒", "宝宝", "小可爱", "萌", "撒娇", "羞羞", "心动了", "喜欢", "好感", "少女心", "嫩", "甜甜", "偶像"],
            "weight": 1.0
        },
        "超级可爱": {
            "keywords": ["可爱死", "可爱炸", "可爱爆", "可爱到", "萌死", "萌翻", "萌化了", "少女心炸裂", "可爱捏", "卡哇伊", "awsl", "awsl"],
            "weight": 1.2
        },
        "暧昧": {
            "keywords": ["好坏", "坏人", "讨厌", "哼", "不理你了", "吃醋", "情人", "亲爱的", "小坏蛋", "坏蛋", "撩", "心动", "小鹿乱撞"],
            "weight": 1.0
        },
        "感动": {
            "keywords": ["感动", "泪目", "哭了", "眼泪", "谢谢", "感谢", "感恩", "暖心", "窝心", "心疼", "感性", "破防", "绷不住"],
            "weight": 1.0
        },
        "骄傲": {
            "keywords": ["骄傲", "自豪", "厉害", "牛逼", "牛", "太强", "佩服", "崇拜", "偶像", "大佬", "大神", "666", "NB", "真棒"],
            "weight": 1.0
        },
        "兴奋": {
            "keywords": ["兴奋", "激动", "超激动", "炸裂", "沸腾", "热血", "燃烧", "沸腾", "嗨", "爽", "刺激", "冲"],
            "weight": 1.0
        },
        "期待": {
            "keywords": ["期待", "盼望", "希望", "想要", "想要", "想要", "想要", "想要", "想看", "想玩", "想学", "搓手手", "等不及"],
            "weight": 1.0
        },
        "满足": {
            "keywords": ["满足", "满意", "知足", "够了", "值了", "幸福", "美滋滋", "爽歪歪", "perfect", "完美", "赞"],
            "weight": 1.0
        },
        "安心": {
            "keywords": ["放心", "安心", "踏实", "稳妥", "稳", "安全", "平安", "还好", "好在", "还好有", "有你在"],
            "weight": 1.0
        },
        
        # === 负面情绪 ===
        "生气": {
            "keywords": ["生气", "哼", "太过分", "讨厌", "不理", "愤怒", "气死了", "恼火", "火大", "不爽", "怒", "气的", "怒了", "愤"],
            "weight": 1.0
        },
        "超生气": {
            "keywords": ["气炸", "气疯", "气死", "气到", "炸裂", "火冒三丈", "怒不可遏", "暴怒", "气呼呼", "哼一声", "怒目"],
            "weight": 1.2
        },
        "难过": {
            "keywords": ["难过", "伤心", "哭", "委屈", "想哭", "难受", "心痛", "失落", "沮丧", "郁闷", "泪", "哭唧唧", "哭哭"],
            "weight": 1.0
        },
        "伤心": {
            "keywords": ["心碎", "心凉", "心累", "崩溃", "绝望", "无助", "孤单", "孤独", "寂寞", "空巢", "空虚"],
            "weight": 1.0
        },
        "失落": {
            "keywords": ["失落", "失望", "无奈", "算了", "没关系", "好吧", "就这样", "随缘", "认命", "没劲"],
            "weight": 1.0
        },
        "害怕": {
            "keywords": ["害怕", "怕", "恐惧", "紧张", "慌", "担心", "忧虑", "不安", "后怕", "慌得", "忐忑", "胆怯"],
            "weight": 1.0
        },
        "焦虑": {
            "keywords": ["焦虑", "着急", "急", "慌", "急死了", "急死了", "火烧眉毛", "焦灼", "烦躁", "烦躁", "抓狂"],
            "weight": 1.0
        },
        "无奈": {
            "keywords": ["无奈", "无语", "服了", "醉", "吐血", "抓狂", "崩溃", "心累", "身心俱疲", "佛了", "麻了"],
            "weight": 1.0
        },
        "后悔": {
            "keywords": ["后悔", "悔", "不该", "早知道", "如果", "当初", "怪", "怪自己", "自责", "内疚", "抱歉"],
            "weight": 1.0
        },
        "委屈": {
            "keywords": ["委屈", "憋屈", "冤枉", "被误会", "不被理解", "冤枉啊", "委屈巴巴", "委屈死了"],
            "weight": 1.0
        },
        
        # === 中性/其他 ===
        "关心": {
            "keywords": ["吃了吗", "睡了吗", "累不累", "注意安全", "早点睡", "照顾好自己", "关心", "担心", "挂念", "叮嘱", "叮咛"],
            "weight": 1.0
        },
        "询问": {
            "keywords": ["?", "吗", "呢", "怎么", "为什么", "是不是", "有没有", "要不要", "可以", "能", "多少", "几点"],
            "weight": 0.5
        },
        "命令": {
            "keywords": ["去", "做", "来", "滚", "别", "不准", "不要", "快", "赶紧", "马上", "立即", "给我"],
            "weight": 0.7
        },
        "困倦": {
            "keywords": ["困", "累", "想睡", "睡觉", "晚安", "安", "眯一会", "打盹", "困死", "困死", "睁不开", "想休息"],
            "weight": 1.0
        },
        "饥饿": {
            "keywords": ["饿", "想吃", "吃饭", "外卖", "点餐", "饿了", "好饿", "饿死了", "想吃", "嘴馋"],
            "weight": 1.0
        },
        "疲惫": {
            "keywords": ["累", "疲惫", "疲倦", "累死", "累坏了", "精疲力尽", "心力交瘁", "扛不住", "撑不住"],
            "weight": 1.0
        },
        "无聊": {
            "keywords": ["无聊", "闲", "没事干", "闲得", "发霉", "闲得慌", "没事做", "打发时间"],
            "weight": 1.0
        },
        "惊讶": {
            "keywords": ["惊讶", "震惊", "吃惊", "意外", "没想到", "居然", "竟然", "还可以这样", "还可以", "666"],
            "weight": 1.0
        },
        "困惑": {
            "keywords": ["困惑", "迷茫", "蒙", "懵", "不懂", "不会", "怎么办", "到底", "什么意思", "啥意思"],
            "weight": 1.0
        },
        "恍然大悟": {
            "keywords": ["原来", "懂了", "明白了", "知道了", "原来如此", "原来是这样", "啊原来", "噢原来"],
            "weight": 1.0
        }
    }
    
    # 语气词映射
    PARTICLES = {
        "～": "温柔",
        "呀": "开心",
        "啦": "开心",
        "哦": "关心",
        "啊": "开心",
        "嗷": "可爱",
        "嗯": "温柔",
        "哼": "生气",
        "嘛": "可爱",
        "呢": "询问",
        "诶": "惊讶",
        "哎": "无奈",
        "哇": "超开心",
        "嘿嘿": "开心",
        "哈哈": "超开心",
        "呜呜": "难过",
        "略略略": "可爱",
        "么么哒": "温柔"
    }
    
    def __init__(self):
        self.cache = {}
    
    def classify(self, text: str, use_particles: bool = True) -> Tuple[str, float, Dict[str, float]]:
        """分类文本情绪"""
        if not text:
            return "中性", 0.0, {}
        
        if text in self.cache:
            return self.cache[text]
        
        text_lower = text.lower().strip()
        scores = {emotion: 0.0 for emotion in self.EMOTIONS}
        
        # 关键词匹配
        for emotion, config in self.EMOTIONS.items():
            keywords = config["keywords"]
            weight = config["weight"]
            for keyword in keywords:
                if keyword in text_lower:
                    scores[emotion] += weight
        
        # 语气词分析
        if use_particles:
            for particle, emotion in self.PARTICLES.items():
                count = text_lower.count(particle)
                if count > 0:
                    scores[emotion] += count * 0.3
        
        # 标点符号分析
        if "!!" in text or "！！" in text:
            scores["超开心"] += 0.5
        if "?? " in text or "？？" in text:
            scores["询问"] += 0.5
        if "..." in text or "。。。":
            scores["失落"] += 0.3
        if "!!!" in text or "！！！":
            scores["超开心"] += 0.7
            
        # 叠字分析
        if "哈哈哈" in text or "hhhh" in text_lower:
            scores["超开心"] += 1.0
        if "呜呜" in text or "哭哭" in text:
            scores["难过"] += 0.8
        
        # 归一化
        total = sum(scores.values())
        if total > 0:
            normalized = {k: v/total for k, v in scores.items()}
            max_emotion = max(normalized, key=normalized.get)
            confidence = normalized[max_emotion]
            
            if confidence < 0.15:
                result = ("中性", 0.3, normalized)
            else:
                result = (max_emotion, confidence, normalized)
        else:
            result = ("中性", 0.0, scores)
        
        self.cache[text] = result
        return result
    
    def get_voice_id(self, emotion: str) -> str:
        """根据情绪返回对应的语音ID"""
        voice_map = {
            "开心": "uu3_happy",
            "超开心": "uu3_happy",
            "温柔": "uu3_gentle", 
            "可爱": "uu3_cute",
            "超级可爱": "uu3_cute",
            "暧昧": "uu3_ambiguous",
            "感动": "uu3_gentle",
            "骄傲": "uu3_happy",
            "兴奋": "uu3_happy",
            "期待": "uu3_cute",
            "满足": "uu3_gentle",
            "安心": "uu3_gentle",
            "生气": "uu3_angry",
            "超生气": "uu3_angry",
            "难过": "uu3_crying",
            "伤心": "uu3_crying",
            "失落": "uu3_depressed",
            "害怕": "uu3_depressed",
            "焦虑": "uu3_depressed",
            "无奈": "uu3_depressed",
            "后悔": "uu3_depressed",
            "委屈": "uu3_crying",
            "关心": "uu3_gentle",
            "询问": "uu3_normal",
            "命令": "uu3_angry",
            "困倦": "uu3_depressed",
            "饥饿": "uu3_normal",
            "疲惫": "uu3_depressed",
            "无聊": "uu3_depressed",
            "惊讶": "uu3_happy",
            "困惑": "uu3_normal",
            "恍然大悟": "uu3_happy",
            "中性": "uu3_normal"
        }
        return voice_map.get(emotion, "uu3_normal")
    
    def get_all_emotions(self) -> List[str]:
        """返回所有支持的情绪类型"""
        return list(self.EMOTIONS.keys())


def main():
    classifier = EmotionClassifier()
    
    # 更多测试用例
    test_texts = [
        # 开心
        "笑死了！太逗了！",
        "哈哈哈笑到我肚子疼",
        # 温柔
        "爱你么么哒～",
        "抱抱～",
        # 可爱
        "awsl也太可爱了吧",
        "萌死我算了",
        # 暧昧
        "好坏哦你～",
        "哼！不理你了！",
        # 生气
        "气死了！太过分了！",
        "怒不可遏！",
        # 难过
        "想哭...难过",
        "呜呜呜伤心",
        # 关心
        "吃了吗宝宝～",
        "早点睡哦",
        # 疲惫
        "累死了...不想动",
        # 期待
        "搓手手期待！",
        # 惊讶
        "震惊！还可以这样？！",
        # 恍然大悟
        "原来如此！懂了！",
    ]
    
    print("=== 情绪分类器 V2 测试 ===\n")
    for text in test_texts:
        emotion, confidence, all_scores = classifier.classify(text)
        voice_id = classifier.get_voice_id(emotion)
        
        print(f"📝 {text}")
        print(f"   情绪: {emotion} (置信度: {confidence:.1%})")
        print(f"   语音: {voice_id}")
        print()
    
    print("=" * 40)
    print(f"\n✅ 共支持 {len(classifier.get_all_emotions())} 种情绪:")
    print(classifier.get_all_emotions())


if __name__ == "__main__":
    main()
