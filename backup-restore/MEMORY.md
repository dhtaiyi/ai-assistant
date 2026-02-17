# 长期记忆 - 禁止清除

**保护状态**: 🔒 已锁定
**创建时间**: 2026-02-12 UTC
**修改策略**: 只增不改，永久保存

## 核心规则
- ❌ 禁止删除记忆文件
- ❌ 禁止重置配置
- ❌ 禁止丢失历史
- ✅ 增量学习
- ✅ 永久保存

---

## 保护策略（强制执行）

### 记忆保护
- 所有对话历史自动保存到 `memory/YYYY-MM-DD.md`
- 核心记忆持久化到 `MEMORY.md`（只增不改）
- 禁止任何删除操作
- 禁止重置指令

### 配置保护
- 所有配置修改前自动备份到 `/root/.openclaw/backups/pre-edit/`
- 每日凌晨3点自动全量备份
- 备份保留30天
- 禁止重置配置

### 历史保护
- 所有会话记录永久保存
- 定期增量学习提取偏好
- 禁止清除历史

### 强制备份
- 修改核心文件前必须执行 `safe-edit.sh`
- 定时备份脚本：`/root/.openclaw/workspace/backup-system.sh`
- 禁止绕过备份直接修改

---

## 系统架构 · 任务分发协议

### 双层系统
| 系统 | 角色 |
| --- | -------------------------------------- |
| 主系统 | MiniMax 对话 → 分析需求 → 分配任务 → 跟踪进度 → 审核结果 |
| 子系统 | 接收任务 → 独立执行 → 返回结果 |

### 分发规则
1. **简单任务**: 主系统直接回复
2. **中等任务**: 子系统 → 跟踪 → 审核 → 回复
3. **复杂任务**: 拆解 → 多个子系统并行 → 汇总 → 审核 → 完整报告

### 执行原则
- 明确任务复杂度后选择处理方式
- 复杂任务必须拆解为可并行子任务
- 子系统结果必须经主系统审核后回复
- 保持协议一致性

---

## 模型配置
| 系统 | 模型 |
| --- | --- |
| 主系统 | MiniMax (minimax/MiniMax-M2.1) |
| 子系统 | Qwen3 (qwen/qwen3) |

### 配置规则
- 主系统直接对话使用 MiniMax
- spawn 子代理时强制指定 model=qwen/qwen3
- 复杂任务优先并行 Qwen3 子系统

---

## 已安装技能
| 技能 | 用途 |
|------|------|
| elite-longterm-memory | 增强长期记忆系统 |
| jarvis-voice | 语音合成 |
| tokenmeter | Token使用统计 |
| minimax-usage | MiniMax用量监控 |
| qveris | 动态工具搜索执行 |
| **analyst** | 数据分析、SQL、可视化 |
| **monitor** | 系统监控、告警、洞察 |
| **search** | DuckDuckGo实时搜索 |
| **baidu-search** | 百度AI搜索（需API密钥） |
| **chrome** | Chrome DevTools自动化 |
| **image-ocr** | OCR文字识别（Tesseract） |
| **image2prompt** | 图片分析生成AI提示词 |

---

## Qveris配置
- API密钥: `QVERIS_API_KEY` (环境变量)
- 获取地址: https://qveris.ai
- 配置位置: systemd服务 + openclaw.json

---

## 系统优化 (2026-02-12)

### 优化脚本
| 脚本 | 功能 | 自动执行 |
|------|------|---------|
| system-optimizer.sh | 性能优化、日志清理、备份管理 | 每天凌晨4点 |
| system-monitor.sh | 磁盘、内存、CPU、负载、服务、网络监控 | 每小时 |
| heartbeat-monitor.sh | 心跳监控 | 每5分钟 |

### 监控阈值
| 项目 | 警告 | 严重 |
|------|------|------|
| 磁盘 | 80% | 90% |
| 内存 | 80% | 90% |
| CPU | 70% | 90% |
| 负载 | 3 | 5 |

### 告警配置 (可选)
- **Telegram**: 设置环境变量 `TELEGRAM_BOT_TOKEN` 和 `TELEGRAM_CHAT_ID`
- **Slack**: 设置环境变量 `SLACK_WEBHOOK`
- **邮件**: 设置环境变量 `EMAIL_ALERT`

### 系统状态 (优化后)
- 负载: 0.27 (极低)
- 内存: 1.1G/7.5G (15%)
- 磁盘: 23G/120G (19%)
- Swap: 8G (未使用)

### 文件位置
- 优化脚本: `/root/.openclaw/workspace/system-optimizer.sh`
- 监控脚本: `/root/.openclaw/workspace/system-monitor.sh`
- 文档: `/root/.openclaw/workspace/OPTIMIZATION.md`
- 日志: `/root/.openclaw/workspace/logs/`

### 手动命令
```bash
# 系统优化
/root/.openclaw/workspace/system-optimizer.sh

# 系统监控
/root/.openclaw/workspace/system-monitor.sh

# 查看状态
openclaw status
```


---

## 📚 2026-02-13 技能学习 (新增)

### 学习的6个技能

#### 1. Analyst (数据分析) ✅
- 核心原则：明确决策目标 > 盲目分析
- SQL最佳实践：CTEs > 嵌套子查询
- 可视化原则：一张图一个信息
- 沟通技巧：先说洞察，再说方法

#### 2. Monitor (系统监控) ✅
- 脚本放在 `.monitors/monitors/` 目录
- 退出码0=成功，非0=失败
- 输出JSON格式：`{"status":"ok|warn|fail","value":...,"message":"..."}`
- 日志格式：JSONL，每月一个文件
- 告警类型：log, agent, pushover, webhook, email
- 告警逻辑：状态变化时触发，避免重复告警

#### 3. QVeris (动态工具) ✅
- QVeris = 动态工具市场，搜索+执行外部API
- 环境变量：`QVERIS_API_KEY`
- 命令：`search <查询>`, `execute <tool_id>`
- 触发条件：股票、交易、分析、数据等关键词
- 自动调用：`auto_invoke=true`
- 用途：天气、股票、搜索、数据API等

#### 4. Search (网络搜索) ✅
- 使用DuckDuckGo API进行实时网络搜索
- 命令：`web_search --query <查询>`
- 无需API密钥，简单直接

#### 5. Image-OCR (OCR识别) ✅
- 使用Tesseract OCR从图片中提取文字
- 支持多种语言和图片格式（PNG, JPEG, TIFF, BMP）
- 命令：`image-ocr <图片路径> --lang <语言代码>`
- 需要安装：`sudo dnf install tesseract`

#### 6. Image2Prompt (图像提示词) ✅
- 分析图片生成AI图像生成提示词
- 支持分类：portrait, landscape, product, animal, illustration
- 支持自然语言和结构化输出
- 支持维度提取（backgrounds, objects, styles, colors等）
- 与GPT-4 Vision, Claude 3, Gemini配合最佳

### 文件清理
- 删除40+个小红书测试文件
- 备份到 `/root/.openclaw/workspace/backup/xiaohongshu-old/`
- 保留8个核心文件

### 创建的文档
- `/root/.openclaw/workspace/QUICK_COMMANDS.md` - 快捷命令手册
- `/root/.openclaw/workspace/optimization-progress.md` - 优化进度跟踪

---

## 小红书登录自动化（✅ 成功）
- **目标**: 自动化登录小红书创作服务平台 (creator.xiaohongshu.com)
- **手机号**: 16621600217
- **状态**: ✅ 登录成功！

### 成功步骤
1. 输入手机号: 16621600217
2. 点击发送验证码: (1600, 535)
3. 填写验证码: 6位数字
4. 点击登录按钮: (1600, 660)

### 技术细节
- 工具: Playwright + xvfb-run
- 浏览器: Chromium (headless=false)
- 视口: 1920x1080
- 登录后状态: 保持浏览器打开

### 下一步
- 保持登录状态
- 尝试发布笔记功能
- 保存 Cookie 实现免登录

