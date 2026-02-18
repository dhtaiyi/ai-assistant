# 技能清理建议

## 重复技能分析

### 1. analyst vs data-analysis ⚠️

**analyst**
- 功能: SQL查询、数据可视化、结果沟通
- 评分: ⭐3.282
- 安装时间: 2026-02-12

**data-analysis** ⭐ 推荐
- 功能: 统计分析、假设检验、陷阱分析、完整方法论
- 评分: ⭐3.461
- 安装时间: 2026-02-18

**建议**: 删除 analyst，保留 data-analysis

```bash
rm -rf /root/.openclaw/workspace/skills/analyst
```

### 2. search vs baidu-search

**search**
- 功能: 通用网络搜索
- 评分: ⭐3.446

**baidu-search**
- 功能: 百度搜索引擎
- 评分: ⭐3.295

**建议**: 两个都可保留
- search 用于通用场景
- baidu-search 用于需要百度搜索时

### 3. 搜索相关技能

- search (通用搜索)
- baidu-search (百度搜索)
- brave-search (Brave搜索 - 在子目录中)

**建议**: 都保留，按需使用

---

## 其他技能分析

### 不重复的技能

✅ **小红书系列** (3个)
- xiaohongshutools - 基础工具
- xiaohongshu-api - API工具
- xiaohongshu-mcp-github - MCP服务器

✅ **内容创作系列** (2个)
- content-repurposing-engine - 内容复用
- humanize-zh - 去AI味

✅ **自动化系列** (1个)
- automation-workflows - 自动化工作流

✅ **数据分析系列** (1个)
- data-analysis - 数据分析

---

## 技能分类统计

### 核心运营类 (3个)
- proactive-agent
- tokenmeter
- minimax-usage

### 内容创作类 (2个) ⭐
- content-repurposing-engine
- humanize-zh

### 自动化类 (1个) ⭐
- automation-workflows

### 数据分析类 (1个) ⭐
- data-analysis

### 平台运营类 (4个)
- xiaohongshutools
- xiaohongshu-api
- xiaohongshu-mcp-github
- wechat-mp-publisher

### 开发工具类 (4个)
- github
- kimi-code
- deep-research-pro
- deploy

### 其他工具类 (15个)
- search, baidu-search
- image-ocr, image2prompt, image-generator
- jarvis-voice
- monitor
- qveris
- chrome
- agent-browser, agent-team-orchestration
- adaptive-reasoning
- stock-monitor
- zhipu-ai
- elite-longterm-memory

---

## 清理建议

### 可立即删除 (1个)

```bash
# 删除重复的 analyst 技能
rm -rf /root/.openclaw/workspace/skills/analyst
```

### 谨慎删除 (0个)
- 无需要谨慎删除的技能

### 保留所有 (29个)
- 其他技能都有独立功能

---

## 执行清理

### 方案A: 立即删除 analyst

```bash
# 检查 analyst 技能
ls -la /root/.openclaw/workspace/skills/analyst/

# 删除
rm -rf /root/.openclaw/workspace/skills/analyst

# 验证
ls /root/.openclaw/workspace/skills/ | grep analyst
```

### 方案B: 暂时保留

如果不确认，建议暂时保留 analyst，后续根据使用情况再决定。

---

## 总结

- **总计技能**: 30个
- **建议删除**: 1个 (analyst)
- **保留**: 29个

**清理后可节省**: ~50KB 磁盘空间
**主要收益**: 减少混淆，统一数据分析工具
