# Kimi Code CLI 官方技术文档

## 开始使用

Kimi Code CLI 是一个运行在终端中的 AI Agent，帮助你完成软件开发任务和终端操作。

### 功能
- 阅读和编辑代码
- 执行 Shell 命令
- 搜索和抓取网页
- 自主规划和调整行动

### 适用场景
- 编写和修改代码：实现新功能、修复 bug、重构代码
- 理解项目：探索陌生的代码库，解答架构和实现问题
- 自动化任务：批量处理文件、执行构建和测试、运行脚本

## 安装

### Linux / macOS
```bash
curl -LsSf https://code.kimi.com/install.sh | bash
```

### Windows (PowerShell)
```powershell
Invoke-RestMethod https://code.kimi.com/install.ps1 | Invoke-Expression
```

### 验证安装
```bash
kimi --version
```

### 使用 uv 安装
```bash
uv tool install --python 3.13 kimi-cli
```

**注意**: Kimi Code CLI 支持 Python 3.12-3.14，建议使用 3.13。

## 升级与卸载

### 升级
```bash
uv tool upgrade kimi-cli --no-cache
```

### 卸载
```bash
uv tool uninstall kimi-cli
```

## 第一次运行

### 启动
```bash
cd your-project
kimi
```

### 登录配置
首次启动需要配置 API 来源：
1. 输入 `/login` 开始配置
2. 选择平台（推荐 Kimi Code，自动 OAuth 授权）
3. 或选择其他平台输入 API 密钥
4. 配置完成后自动保存并重新加载

### 使用提示
- 用自然语言描述需求
- 可随时切换到 Shell 模式
- 运行 `/init` 生成 AGENTS.md 分析项目
- 运行 `/help` 查看所有命令

## 斜杠命令

详见官方文档：斜杠命令参考
