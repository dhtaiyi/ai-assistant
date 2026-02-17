# 🔑 API Key 测试指南

## 快速测试命令

### 使用测试脚本

```bash
# 测试OpenAI兼容API (Qwen, Kimi等)
python3 /root/.openclaw/workspace/test-api-key.py Qwen \
  https://coding.dashscope.aliyuncs.com/v1 \
  sk-sp-645687cbbd854d2ab15251e5086e5ac5 \
  qwen3-max-2026-01-23

# 测试Anthropic兼容API (MiniMax等)
python3 /root/.openclaw/workspace/test-api-key.py MiniMax \
  https://api.minimaxi.com/anthropic \
  sk-cp-xxx \
  MiniMax-M2.1

# 测试简单GET API (QVeris等)
python3 /root/.openclaw/workspace/test-api-key.py QVeris \
  https://api.qveris.ai/v1/tools \
  sk-P1hxxx
```

---

## 手动测试命令

### MiniMax (Anthropic格式)
```bash
curl -X POST "https://api.minimaxi.com/anthropic/v1/messages" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-cp-xxx" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "MiniMax-M2.1",
    "max_tokens": 100,
    "messages": [{"role": "user", "content": "Hi"}]
  }'
```

### Qwen / Kimi (OpenAI格式)
```bash
curl -X POST "https://coding.dashscope.aliyuncs.com/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-sp-xxx" \
  -d '{
    "model": "qwen3-max-2026-01-23",
    "max_tokens": 100,
    "messages": [{"role": "user", "content": "Hi"}]
  }'
```

### QVeris (GET请求)
```bash
curl -H "Authorization: Bearer sk-P1hxxx" \
  https://api.qveris.ai/v1/tools
```

---

## 常见错误处理

### 401 Invalid Authentication
- ❌ **原因**: API Key无效或过期
- ✅ **解决**: 重新生成API Key

### 404 Not Found
- ❌ **原因**: API端点错误
- ✅ **解决**: 检查baseUrl配置

### 429 Too Many Requests
- ❌ **原因**: 请求频率超限
- ✅ **解决**: 降低请求频率

### 403 Forbidden
- ❌ **原因**: 无权限访问
- ✅ **解决**: 检查API权限设置

---

## 当前已配置的API

| API | Key | 状态 | 测试命令 |
|-----|-----|------|---------|
| MiniMax | sk-cp-...nxM | ✅ 工作 | 见上方 |
| Qwen | sk-sp-...6e5ac5 | ✅ 工作 | 见上方 |
| QVeris | sk-P1...YZI | ✅ 工作 | 见上方 |
| Kimi | sk-kimi-...FUx4 | ❌ 失败 | 需要修复 |

