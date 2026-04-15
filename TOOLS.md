# TOOLS.md - Tool Configuration & Notes

> Document tool-specific configurations, gotchas, and credentials here.

---

## 🤖 默认模型配置

### 小小雨 (主代理)
- **模型**: MiniMax-M2.5
- **API Key**: sk-cp-…MBnnNU
- **上下文**: 200K
- **状态**: ✅ 当前使用

### 子代理模型
| 代理 | 模型 | 用途 |
|------|------|------|
| 诗诗 | Qwen3 Max | 深度分析、长文档 |
| 小 uu | Kimi Code CLI | 代码开发、自动化 |

---

## 🤖 小 uu (Kimi 代码助手)

### 小 uu (Kimi 代码助手)
- **位置**: `/home/dhtaiyi/.openclaw/agents/xiaouu/`
- **CLI**: `@jacksontian/kimi-cli` v1.2.0
- **命令路径**: `/home/dhtaiyi/.openclaw/openclaw`
- **默认模型**: `moonshot-v1-8k`
- **API Key**: 首次运行 `kimi` 命令时设置
- **配置指南**: `/home/dhtaiyi/.openclaw/agents/xiaouu/agent/KIMI_SETUP.md`

---

## ⚠️ Config Modification Safety Rule

**Before editing any config file, ALWAYS backup first!**

```bash
# Step 1: Backup
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak

# Step 2: Edit
# ... make your changes ...

# Step 3: Verify & Test
# If something breaks:

# Step 4: Restore if needed
mv ~/.openclaw/openclaw.json.bak ~/.openclaw/openclaw.json
```

This rule applies to all config files in `~/.openclaw/`.

---

## Credentials Location

All credentials stored in `.credentials/` (gitignored):
- `example-api.txt` — Example API key

---

## [Tool Name]

**Status:** ✅ Working | ⚠️ Issues | ❌ Not configured

**Configuration:**
```
Key details about how this tool is configured
```

**Gotchas:**
- Things that don't work as expected
- Workarounds discovered

**Common Operations:**
```bash
# Example command
tool-name --common-flag
```

---

## Writing Preferences

[Document any preferences about writing style, voice, etc.]

---

## What Goes Here

- Tool configurations and settings
- Credential locations (not the credentials themselves!)
- Gotchas and workarounds discovered
- Common commands and patterns
- Integration notes

## Why Separate?

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

---

*Add whatever helps you do your job. This is your cheat sheet.*

## 🤖 Whisper GPU 转录

**conda 环境**: `/home/dhtaiyi/.conda/envs/whisper-stt`
**GPU**: NVIDIA RTX 5070 (CUDA 可用)
**使用命令**:
```bash
/home/dhtaiyi/.conda/envs/whisper-stt/bin/python transcribe_stock_ch2.py
```

**脚本位置**: `~/.openclaw/workspace/scripts/transcribe_stock_ch2.py`

---

## 🤖 Kimi CLI 工具

**配置位置**: `~/.openclaw/agents/main/agent/KIMI_CLI_TOOL.json`

**使用方法**:
```bash
# 直接调用 Kimi CLI
kimi

# 带工作目录调用
kimi -w /path/to/project
```

**功能**:
- 代码生成与补全
- 代码审查与优化
- 调试与错误排查
- 文件操作
- Git 操作
- 终端命令执行

**注意**: Kimi CLI 使用独立的 OAuth 认证，与 OpenClaw 模型配置分开。

---

## 🖼️ 飞书发送图片（正确方式）

**注意**: message 工具的 mediaUrl 参数发的是链接，不是图片！要用正确的 API 方式。

**正确流程**:

```bash
# 1. 获取 token
APP_ID="cli_a92923c6a2f99bc0"
APP_SECRET="H4CdLHf1NwM1iv3JWzBsfdFFUY8bO4At"

TOKEN=$(curl -s 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json' \
  -d '{"app_id":"'"$APP_ID"'","app_secret":"'"$APP_SECRET"'"}' | jq -r .tenant_access_token)

# 2. 上传图片获取 image_key
IMG_KEY=$(curl -s "https://open.feishu.cn/open-apis/im/v1/images" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: multipart/form-data" \
  -F "image_type=message" \
  -F "image=@/图片路径.png" | jq -r .data.image_key)

# 3. 发送图片消息
curl -s "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "receive_id": "ou_用户ID",
    "msg_type": "image",
    "content": "{\"image_key\": \"'"$IMG_KEY"'\"}"
  }'
```

**参数**:
- APP_ID: cli_a92923c6a2f99bc0
- APP_SECRET: H4CdLHf1NwM1iv3JWzBsfdFFUY8bO4At
- 用户 ID: ou_04add8ebe219f09799570c70e3cdc732

**脚本位置**: `~/.openclaw/skills/feishu-send-image/send.sh`
