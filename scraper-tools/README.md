# 爬虫工具箱

## 概述

基于 deep-scraper 和 playwright-scraper-skill 的爬虫工具箱。

## 组成部分

### 1. deep-scraper
- 深度爬虫工具
- Docker + Crawlee (Playwright) 环境
- 特点: 高性能、穿透反爬保护
- 适合: YouTube、Twitter等复杂网站

### 2. playwright-scraper-skill
- Playwright 爬虫技能
- 特点: 多层次反爬解决方案
- 适合: 普通网站、动态网站、反爬保护网站

### 3. news-aggregator-skill
- 新闻聚合器
- 来源: Hacker News、GitHub Trending、Product Hunt、36Kr、微博、V2EX等
- 特点: 多源聚合、深度分析

---

## 使用场景

### 场景1: 抓取技术文章
```
使用: playwright-simple.js
目标: 博客、技术文档
```

### 场景2: 抓取反爬网站
```
使用: playwright-stealth.js
目标: Cloudflare保护的网站
```

### 场景3: 抓取YouTube
```
使用: deep-scraper
目标: YouTube视频转录
```

### 场景4: 新闻聚合
```
使用: news-aggregator-skill
目标: 多源新闻聚合分析
```

---

## 安装和配置

### 1. deep-scraper
```bash
cd /root/.openclaw/workspace/skills/deep-scraper
docker build -t clawd-crawlee .
```

### 2. playwright-scraper-skill
```bash
cd /root/.openclaw/workspace/skills/playwright-scraper-skill
npm install
npx playwright install chromium
```

---

## 快速使用

### 抓取普通网站
```bash
node scripts/playwright-simple.js "https://example.com"
```

### 抓取反爬网站
```bash
node scripts/playwright-stealth.js "https://m.discuss.com.hk/"
```

### 抓取YouTube
```bash
docker run -t --rm -v $(pwd)/assets:/usr/src/app/assets clawd-crawlee node assets/main_handler.js [VIDEO_URL]
```

### 获取新闻
```bash
python3 scripts/fetch_news.py --source all --limit 10 --deep
```

---

## 最佳实践

### 1. 选择合适的工具
- 普通网站: web_fetch
- 动态网站: playwright-simple
- 反爬网站: playwright-stealth
- 复杂网站: deep-scraper

### 2. 遵守robots.txt
- 尊重网站的爬虫协议
- 控制抓取频率
- 不抓取私人数据

### 3. 数据处理
- 使用 --deep 获取完整内容
- 保存为结构化格式
- 便于后续分析

---

## 相关文件

- /root/.openclaw/workspace/skills/deep-scraper/
- /root/.openclaw/workspace/skills/playwright-scraper-skill/
- /root/.openclaw/workspace/skills/news-aggregator-skill/

