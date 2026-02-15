---
name: multi-model-usage
description: Monitor usage for multiple AI models (Qwen, Kimi, MiniMax). Track API limits, tokens, and costs across providers.
metadata: {"clawdbot":{"emoji":"📊"}}
---

# Multi-Model Usage Monitor

Monitor API usage across MiniMax, Kimi, and Qwen AI models.

## Quick Start

```bash
cd /root/.openclaw/workspace/skills/multi-model-usage
./multi-model-usage.sh
```

## Output Example

```
🔍 检查多模型用量...

📊 ===== MiniMax (编程计划) =====

✅ MiniMax CLI 已配置
   API Key: 已配置

💡 查看用量请访问:
   https://platform.minimax.io/user-center/basic-information

📊 ===== Kimi (Moonshot AI - Coding) =====

✅ Kimi CLI 已安装
   版本: 1.12.0
   状态: 已登录 ✅

💡 查看用量请访问:
   https://platform.moonshot.ai/console/billing

📊 ===== Qwen (阿里云DashScope) =====

✅ Qwen Coding API 已配置
   端点: https://coding.dashscope.aliyuncs.com/v1
   模型: qwen3-coder-plus, qwen3-max-2026-01-23

💡 查看用量请访问:
   https://dashscope.console.aliyun.com/usage/summary
```

## API Status

| Model | Status | Endpoint | Access |
|-------|--------|----------|--------|
| **MiniMax** | ✅ Working | api.minimaxi.com | Console / CLI |
| **Kimi** | ✅ Working | api.kimi.com | CLI OAuth |
| **Qwen** | ✅ Working | coding.dashscope.aliyuncs.com | Console |

## Configuration

Configuration is stored in `/root/.openclaw/.credentials/multi-model-usage.env`:

```bash
MINIMAX_CODING_API_KEY=sk-cp-...
KIMI_API_KEY=(via CLI OAuth)
QWEN_API_KEY=sk-sp-...
```

## Notes

- Each provider has its own usage console
- MiniMax and Kimi CLI are already authenticated
- Qwen API requires DashScope console access
- Usage limits reset at different times for each provider
