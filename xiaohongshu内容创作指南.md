# 小红书内容创作系统

## 工具列表

### 1. 内容生成器
**位置**: `/root/.openclaw/workspace/xiaohongshu_content_generator.py`

**功能**: 基于模板生成各种类型的内容

```bash
python3 /root/.openclaw/workspace/xiaohongshu_content_generator.py
```

**生成内容类型**:
- 实用攻略
- 美食探店
- 生活技巧
- 女性话题

---

### 2. 热门内容创作器
**位置**: `/root/.openclaw/workspace/xiaohongshu_trending_content.py`

**功能**: 基于当前热门趋势生成内容

```bash
python3 /root/.openclaw/workspace/xiaohongshu_trending_content.py
```

**热门话题**:
- 生活服务（护工价格、家政）
- 省钱攻略（28元美食）
- 宠物相关（猫咪用品）
- 女性职场（穿搭、用品）
- 旅游攻略（城市攻略）
- 美食探店（地方美食）

---

## 热门趋势分析

### 当前热门笔记 TOP 5
1. 💗 猫咪暖气猫窝 - 10万+赞
2. 🏊 泳池拍照 - 1947赞
3. 🍖 小狗年夜饭 - 2047赞
4. 👜 律师电脑包 - 422赞
5. 🥟 上海28元馄饨 - 1.1万赞

### 热门话题
- 💰 价格清单类
- 🐱 宠物用品
- 👩 女性职场
- ✈️ 旅游攻略
- 🍜 地方美食

---

## 发布建议

### 发布频率
- 每天 1-2 篇
- 定时发布（早上8点、中午12点、晚上8点）

### 内容技巧
1. 标题要带数字和情绪词
2. 开头要有冲突感
3. 内容要有实用价值
4. 结尾要引导互动

### 热门标签
- #实用攻略
- #生活技巧
- #省钱攻略
- #租房攻略
- #美食探店

---

## 相关文件

- `xiaohongshu_query.py` - 数据查询
- `xiaohongshu_content_generator.py` - 内容生成
- `xiaohongshu_trending_content.py` - 热门内容
- `xiaohongshu发布结果.md` - 发布记录
