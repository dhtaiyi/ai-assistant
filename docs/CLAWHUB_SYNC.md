# 🔄 ClawHub Skill 同步指南

> 主动拉取、同步和安装 ClawHub 上的 skill

---

## 📊 同步统计

| 指标 | 数值 |
|------|------|
| **ClawHub 总技能** | 116 个 |
| **已安装** | 44 个 |
| **可安装** | 72 个 |
| **最后同步** | 2026-02-26 13:58 |

---

## 🚀 快速开始

### 1. 同步最新 skill 列表

```bash
# 从 ClawHub API 拉取最新 skill 列表
python3 scripts/sync-clawhub-skills.py
```

**输出示例：**
```
🔄 开始同步 ClawHub Skill...
📥 获取第 1 页... 24 个 skill
📥 获取第 2 页... 24 个 skill
...
📊 同步完成
总技能数：116
已安装：44
未安装：72
```

---

### 2. 查看可用 skill

```bash
# 查看 Top 热门 skill
python3 scripts/install-clawhub-skill.py top

# 查看所有可用 skill
python3 scripts/install-clawhub-skill.py list
```

**输出示例：**
```
🔥 Top 10 热门 Skill:
1. ✅ MoltGuard - OpenClaw Security Plugin (v6.6.14)
   下载：6515 | 安装：19
2. 🆕 Square (v1.0.2)
   下载：2324
...
```

---

### 3. 搜索 skill

```bash
# 搜索关键词
python3 scripts/install-clawhub-skill.py search --query "weather"

# 搜索中文
python3 scripts/install-clawhub-skill.py search --query "天气"
```

---

### 4. 安装 skill

```bash
# 通过 slug 安装
python3 scripts/install-clawhub-skill.py install --slug "yr-weather"

# 或使用 clawhub CLI 直接安装
clawhub install yr-weather
```

---

## 📁 文件结构

```
/root/.openclaw/workspace/
├── memory/
│   ├── clawhub-sync-index.json      # 同步索引 (116 个 skill)
│   ├── clawhub-skills-index.json    # 本地 skill 索引 (44 个)
│   └── clawhub-skills-for-lancedb.json # LanceDB 格式
├── scripts/
│   ├── sync-clawhub-skills.py       # 同步脚本
│   ├── install-clawhub-skill.py     # 安装工具
│   ├── auto-sync-clawhub.sh         # 自动同步 (cron)
│   ├── build-skill-index.py         # 构建本地索引
│   ├── import-skills-to-lancedb.py  # 导入 LanceDB
│   └── query-skills.py              # 查询工具
└── docs/
    └── CLAWHUB_SYNC.md              # 本文档
```

---

## ⏰ 自动同步

### 设置定时任务

```bash
# 编辑 crontab
crontab -e

# 添加每天凌晨 2 点同步
0 2 * * * /root/.openclaw/workspace/scripts/auto-sync-clawhub.sh
```

### 手动触发

```bash
# 运行自动同步脚本
/root/.openclaw/workspace/scripts/auto-sync-clawhub.sh
```

---

## 🔍 热门 Skill 推荐

### 安全类
- **MoltGuard** - OpenClaw 安全插件 (6515 下载)

### 支付类
- **Square** - Square API 集成 (2324 下载)
- **Sendgrid Skills** - SendGrid 邮件 (868 下载)

### 研究类
- **CueCue Deep Research** - 深度金融研究 (1121 下载)
- **Equity Analyst** - 韩国股票分析 (831 下载)

### 交易类
- **Binance-Hunter** - 币安交易工具 (797 下载)

### 工具类
- **Openclaw Config** - 配置编辑器 (690 下载)
- **Windows Remote** - Windows 远程控制 (672 下载)

---

## 💡 使用场景

### 场景 1: 发现新 skill
```bash
# 每天自动同步，发现新 skill
python3 scripts/sync-clawhub-skills.py
```

### 场景 2: 搜索特定功能
```bash
# 搜索天气相关
python3 scripts/install-clawhub-skill.py search --query "weather"
```

### 场景 3: 安装推荐 skill
```bash
# 安装热门 security 插件
python3 scripts/install-clawhub-skill.py install --slug "moltguard"
```

### 场景 4: 批量安装
```bash
# 安装 Top 10 热门 skill
for slug in moltguard square agent-church; do
  python3 scripts/install-clawhub-skill.py install --slug "$slug"
done
```

---

## 📊 统计对比

| 来源 | Skill 数量 | 状态 |
|------|-----------|------|
| **ClawHub** | 116 个 | 🌐 在线 |
| **本地已安装** | 44 个 | ✅ 可用 |
| **可安装** | 72 个 | 🆕 待安装 |

---

## 🎯 下一步

1. **定期同步**: 设置 cron 每天自动同步
2. **安装推荐**: 安装 Top 热门 skill
3. **导入 LanceDB**: 将新 skill 导入向量数据库
4. **主动推荐**: AI 根据上下文主动推荐 skill

---

*最后更新：2026-02-26*
