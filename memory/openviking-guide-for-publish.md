# OpenViking 记忆改造指南

> 30 分钟改造，token 省 10 倍，多 Agent 不再陌生

---

## 问题

多 Agent 系统像"陌生人"：
- 每次对话都要重新介绍背景
- Agent 之间不共享信息
- Token 浪费严重

---

## 解决方案

### 1️⃣ 分层记忆 (L0/L1/L2)

| 层级 | 内容 | Token |
|------|------|-------|
| L0 | 目录索引 | ~100 |
| L1 | 内容摘要 | ~500 |
| L2 | 完整内容 | ~5000+ |

### 2️⃣ 记忆保质期 (P0/P1/P2)

| 标签 | 保留时间 | 举例 |
|------|----------|------|
| P0 | 永久 | 用户名、写作风格 |
| P1 | 90 天 | 当前项目 |
| P2 | 30 天 | 调试细节 |

### 3️⃣ 共享记忆层

```
shared-memory/
├── user-profile.md      # 用户画像
├── active-tasks.md      # 当前任务
└── cross-agent-log.md   # 协作日志
```

---

## 实施步骤 (30 分钟)

### 步骤 1: 创建 .abstract 索引 (5 分钟)

```bash
cat > memory/.abstract << 'EOF'
- 用户偏好：写作风格、发布节奏
- 系统配置：Agent 列表、通信方式
- 项目记录：当前任务、历史文章
- 工具笔记：常用命令、API 配置
EOF
```

### 步骤 2: 给记忆打标签 (10 分钟)

```markdown
## [P0] 用户基本信息
- 名字：主人
- 写作风格：简洁

## [P1] 当前项目
- OpenViking 改造
- 状态：进行中

## [P2] 临时记录
- 调试细节
```

### 步骤 3: 创建共享记忆 (10 分钟)

```bash
mkdir -p shared-memory
cat > shared-memory/user-profile.md << 'EOF'
# 用户画像

- 名字：主人
- 时区：Asia/Shanghai
- 偏好：简洁直接
EOF
```

### 步骤 4: 更新 AGENTS.md (5 分钟)

```markdown
## 共享记忆规则

完成重要任务后，追加到：
shared-memory/cross-agent-log.md

格式：
- [日期] [角色] 做了什么，关键结论
```

### 步骤 5: 清理脚本 (自动)

```bash
#!/bin/bash
# 每天运行，归档过期记忆
find memory/ -name "*.md" -mtime +30 -exec mv {} archive/ \;
```

---

## 效果对比

| 指标 | 改造前 | 改造后 |
|------|--------|--------|
| 每次对话 token | 8000+ | ~800 |
| Agent 信息共享 | ❌ | ✅ |
| 过期信息处理 | 手动 | 自动 |
| 新对话介绍 | 每次 | 自动 |

---

## 文件结构

```
workspace/
├── memory/
│   ├── .abstract           # L0 索引
│   ├── MEMORY.md           # P0 长期记忆
│   └── YYYY-MM-DD.md       # P1/P2 日记
├── shared-memory/
│   ├── user-profile.md
│   ├── active-tasks.md
│   └── cross-agent-log.md
└── scripts/
    └── cleanup-memory.sh
```

---

## 适用场景

- ✅ 多 Agent 协作系统
- ✅ Token 成本优化
- ✅ 跨会话记忆连续性
- ✅ OpenClaw 用户

---

*基于字节 OpenViking 思想，OpenClaw 原生实现*
