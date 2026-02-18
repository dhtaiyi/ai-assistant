# 新闻聚合应用

## 概述

基于 news-aggregator-skill 的新闻聚合应用。

## 功能特点

### 多源聚合
- Hacker News
- GitHub Trending
- Product Hunt
- 36Kr
- 微博
- V2EX
- 腾讯新闻
- 华尔街见闻

### 智能分析
- 关键词扩展
- 深度内容抓取
- 语义过滤

---

## 使用方法

### 1. 获取AI新闻 (Hacker News)
```bash
python3 scripts/fetch_news.py \
    --source hackernews \
    --limit 20 \
    --keyword "AI,LLM,GPT,Claude,DeepSeek" \
    --deep
```

### 2. 获取GitHubTrending
```bash
python3 scripts/fetch_news.py \
    --source github \
    --limit 10 \
    --deep
```

### 3. 全局扫描
```bash
python3 scripts/fetch_news.py \
    --source all \
    --limit 15 \
    --deep
```

### 4. 特定关键词搜索
```bash
python3 scripts/fetch_news.py \
    --source all \
    --limit 10 \
    --keyword "OpenAI" \
    --deep
```

---

## 应用场景

### 场景1: 每日技术新闻简报
```bash
# 获取今日AI和编程相关新闻
python3 scripts/fetch_news.py \
    --source hackernews,github,producthunt \
    --limit 10 \
    --keyword "AI,Programming,Developer" \
    --deep
```

### 场景2: 竞品监控
```bash
# 监控竞争对手动态
python3 scripts/fetch_news.py \
    --source weibo,v2ex,36kr \
    --limit 15 \
    --keyword "竞品关键词" \
    --deep
```

### 场景3: 行业趋势分析
```bash
# 分析特定行业发展趋势
python3 scripts/fetch_news.py \
    --source all \
    --limit 20 \
    --keyword "AI,LLM,Agent,RAG" \
    --deep
```

---

## 输出格式

### 新闻列表
```json
[
  {
    "title": "新闻标题",
    "url": "原文链接",
    "source": "来源",
    "time": "发布时间",
    "heat": "热度分数",
    "content": "深度内容（使用--deep时）"
  }
]
```

### 分析报告
- 格式: Markdown
- 语言: 简体中文
- 风格: 专业简洁
- 结构:
  - 全球头条
  - 科技与AI
  - 财经与社会
  - 深度解读

---

## 定时任务配置

### 每日技术新闻简报
```bash
# 每天早上9点获取AI新闻
0 9 * * * cd /root/.openclaw/workspace/skills/news-aggregator-skill && \
python3 scripts/fetch_news.py \
    --source hackernews,github \
    --limit 10 \
    --keyword "AI,Programming" \
    --deep >> /root/.openclaw/workspace/logs/news-ai.log 2>&1
```

---

## 相关文件

- /root/.openclaw/workspace/skills/news-aggregator-skill/
- /root/.openclaw/workspace/reports/ (新闻报告输出目录)

