# OpenClaw 新技能使用指南

## 🎉 已成功安装5个新技能！

### 1️⃣ Analyst - 数据分析专家

**功能**：
- SQL查询和数据分析
- 数据质量检查和验证
- 数据可视化指导
- 分析报告生成

**使用场景**：
- 分析日志数据
- 生成图表和报告
- 数据质量评估

**技能文件**：
- `/root/.openclaw/workspace/skills/analyst/SKILL.md`

---

### 2️⃣ Monitor - 系统监控框架

**功能**：
- 创建自定义监控脚本
- 结构化日志记录
- 多渠道告警（Agent/Pushover/Webhook）
- 智能洞察分析

**使用场景**：
- 网站可用性监控
- API健康检查
- 内容变更检测
- 社交媒体监控

**目录结构**：
```
.monitors/
├── config.json
├── monitors/
│   ├── web-site.sh
│   └── api-health.py
├── logs/
└── alerts/
```

**技能文件**：
- `/root/.openclaw/workspace/skills/monitor/SKILL.md`

---

### 3️⃣ Search - 网络实时搜索

**功能**：
- DuckDuckGo实时搜索
- 获取最新网络信息

**使用命令**：
```bash
web_search --query "你的搜索词"
```

**示例**：
```
搜索最新新闻、技术文档、研究主题
```

**技能文件**：
- `/root/.openclaw/workspace/skills/search/SKILL.md`

---

### 4️⃣ Baidu Search - 百度AI搜索

**功能**：
- 百度搜索引擎集成
- 高级搜索过滤
- 时间范围筛选
- 指定资源类型（网页/视频/图片）

**环境配置**：
```bash
export BAIDU_API_KEY="your_api_key"
```

**使用命令**：
```bash
python3 skills/baidu-search/scripts/search.py '{"query":"人工智能"}'
```

**高级用法**：
```bash
# 按时间筛选
{"query":"新闻", "search_recency_filter":"week"}

# 指定网站
{"query":"技术", "search_filter":{"site":["baike.baidu.com"]}}

# 资源类型过滤
{"query":"旅游", "resource_type_filter":[{"type":"web","top_k":20},{"type":"video","top_k":5}]}
```

**技能文件**：
- `/root/.openclaw/workspace/skills/baidu-search/SKILL.md`

---

### 5️⃣ Chrome - Chrome自动化

**功能**：
- Chrome DevTools Protocol (CDP)
- Chrome扩展开发最佳实践
- 性能调试
- 网络调试
- 安全上下文检测

**使用场景**：
- 网页自动化测试
- 性能分析
- 扩展开发调试

**关键技巧**：
- 总是先获取WebSocket URL
- 启用domains后再操作
- CDP是异步的，需要等待响应

**技能文件**：
- `/root/.openclaw/workspace/skills/chrome/SKILL.md`

---

## 📚 技能使用优先级

### 🔥 立即可用
1. **Search** - 无需配置，直接使用
2. **Analyst** - 直接读取SKILL.md学习

### ⚙️ 需要配置
1. **Baidu Search** - 需要百度API密钥
2. **Monitor** - 需要创建监控脚本

### 🛠️ 高级技能
1. **Chrome** - 高级自动化，需要CDP知识

---

## 💡 使用建议

### 日常使用
- **Search** 替代部分web_search需求
- **Analyst** 用于数据分析和报告

### 监控系统
- 使用 **Monitor** 创建自定义监控
- 配置告警渠道

### 搜索增强
- **Baidu Search** 需要API密钥
- 先用 **Search** (DuckDuckGo)

### 自动化
- **Chrome** 用于高级网页自动化
- 参考最佳实践避免常见错误

---

## 🔗 相关文档

- OpenClaw文档: `/root/.nvm/versions/node/v22.22.0/lib/node_modules/openclaw/docs`
- 技能市场: https://clawhub.com

---

## 📝 下一步

1. 阅读各技能的SKILL.md文件
2. 尝试使用Search进行网络搜索
3. 配置Baidu Search（如有需要）
4. 创建自定义Monitor
5. 提升数据分析能力

---

**安装时间**: 2026-02-12
**技能数量**: 5个
**总技能数**: 12个
