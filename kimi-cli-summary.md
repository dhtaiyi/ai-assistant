# Kimi CLI 技术摘要 (由小u生成)

## 📖 概述

Kimi Code CLI 是一个**终端 AI Agent**，帮助开发者完成软件开发任务。

## 🎯 核心能力

### 1. 代码操作
- 阅读和编辑代码
- 实现新功能
- 修复 bug
- 重构代码

### 2. 终端操作
- 执行 Shell 命令
- 搜索和抓取网页
- 批量处理文件

### 3. 智能规划
- 自主规划任务
- 根据反馈调整行动
- 理解项目架构

## 📦 安装方式

### 快速安装 (Linux/macOS)
```bash
curl -LsSf https://code.kimi.com/install.sh | bash
```

### Python uv 安装
```bash
uv tool install --python 3.13 kimi-cli
```

## 🚀 快速开始

### 1. 进入项目目录
```bash
cd your-project
```

### 2. 启动 Kimi Code CLI
```bash
kimi
```

### 3. 登录配置
```bash
/login
```
- 推荐 Kimi Code (OAuth 自动授权)
- 或选择其他平台输入 API 密钥

### 4. 开始对话
- 用自然语言描述需求
- `/init` - 分析项目生成 AGENTS.md
- `/help` - 查看所有命令

## 💡 使用技巧

1. **项目初始化**: 首次使用运行 `/init` 生成 AGENTS.md
2. **切换 Shell**: 可随时切换到 Shell 模式执行命令
3. **自然语言**: 直接用自然语言描述任务
4. **API 集成**: 支持 Agent Client Protocol，集成到 IDE

## 🔧 常用命令

| 命令 | 功能 |
|------|------|
| `/login` | 配置 API 来源 |
| `/init` | 分析项目生成配置 |
| `/help` | 查看帮助 |
| `/shell` | 切换到 Shell 模式 |

## ⚠️ 注意事项

- Python 版本: 3.12-3.14 (推荐 3.13)
- macOS 首次启动较慢，需在系统设置中添加终端
- 支持 Agent Client Protocol，可集成到 IDE

## 📚 相关文档

- [平台与模型配置](https://code.kimi.com/configuration/providers.html)
- [斜杠命令参考](https://code.kimi.com/reference/slash-commands.html)
- [IDE 集成](https://code.kimi.com/ides.html)

---

**文档来源**: https://www.kimi-cli.com/zh/guides/getting-started.html
**生成时间**: $(date '+%Y-%m-%d %H:%M')
