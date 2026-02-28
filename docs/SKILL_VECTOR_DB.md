# 🧠 ClawHub Skill 向量数据库

> 将 ClawHub 上的可靠 Skill 存储到 LanceDB 向量数据库，方便 AI 学习和调用

---

## 📊 数据库统计

| 指标 | 数值 |
|------|------|
| **总 Skill 数** | 44 个 |
| **分类数** | 8 个 |
| **向量维度** | 自动检测 |
| **检索模式** | 混合检索 (Vector + BM25) |

---

## 📁 分类统计

| 分类 | Skill 数量 | 代表 Skill |
|------|-----------|-----------|
| search | 4 | baidu-search, ddg-web-search, deep-research-pro |
| vision | 3 | image-generator, image-ocr, image2prompt |
| productivity | 2 | cron-scheduling, todoist |
| dev | 2 | github, xiaohongshu-mcp-github |
| data | 2 | news-aggregator-skill, tushare-finance |
| browser | 1 | agent-browser |
| memory | 1 | elite-longterm-memory |
| unknown | 29 | 待分类 |

---

## 🔍 使用方法

### 1. 自然语言查询

```
"我需要一个能搜索网页的 skill"
→ 返回：baidu-search, ddg-web-search, deep-research-pro

"有没有处理图片的 skill？"
→ 返回：image-generator, image-ocr, image2prompt

"帮我找个任务管理的 skill"
→ 返回：todoist, cron-scheduling
```

### 2. 按分类查询

```bash
# 列出所有 search 分类的 skill
python3 scripts/query-skills.py --category search

# 列出所有 vision 分类的 skill
python3 scripts/query-skills.py --category vision
```

### 3. 语义搜索

```bash
# 搜索与"网页爬虫"相关的 skill
python3 scripts/query-skills.py --query "网页爬虫"

# 搜索与"财务报表"相关的 skill
python3 scripts/query-skills.py --query "财务报表"
```

---

## 📂 文件结构

```
/root/.openclaw/workspace/
├── memory/
│   ├── clawhub-skills-index.json       # Skill 索引 (JSON)
│   └── clawhub-skills-for-lancedb.json # LanceDB 导入格式
├── scripts/
│   ├── build-skill-index.py            # 构建索引脚本
│   ├── import-skills-to-lancedb.py     # 导入 LanceDB 脚本
│   └── query-skills.py                 # 查询脚本
└── docs/
    └── SKILL_VECTOR_DB.md              # 本文档
```

---

## 🔄 更新流程

```bash
# 1. 重新扫描本地 skill
python3 scripts/build-skill-index.py

# 2. 导入到 LanceDB
python3 scripts/import-skills-to-lancedb.py

# 3. 验证
python3 scripts/query-skills.py --list
```

---

## 💡 最佳实践

1. **定期更新**: 每次安装新 skill 后运行更新脚本
2. **语义检索**: 使用自然语言查询，利用向量搜索优势
3. **分类浏览**: 按分类快速定位相关 skill
4. **描述优化**: 为 skill 添加清晰的 SKILL.md 描述

---

## 🎯 示例查询

### 场景 1: 需要搜索功能
```
用户："我想搜索最新的技术新闻"
AI 检索："搜索 新闻 技术"
返回：news-aggregator-skill, deep-research-pro
```

### 场景 2: 需要图像处理
```
用户："帮我分析这张图片的内容"
AI 检索："图片 分析 OCR"
返回：image-ocr, image2prompt
```

### 场景 3: 需要自动化
```
用户："有没有定时执行任务的工具？"
AI 检索："定时 任务 自动化 cron"
返回：cron-scheduling, automation-workflows
```

---

*最后更新：2026-02-26*
