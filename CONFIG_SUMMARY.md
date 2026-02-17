# 📊 OpenClaw 配置总结

## 🤖 模型配置

### MiniMax（当前主模型）
```json
{
  "provider": "minimax",
  "baseUrl": "https://api.minimaxi.com/anthropic",
  "apiKey": "sk-cp-urIBOUm3ibSFf3B6i1vQc6mC7fTqtItyFpqLa7KH6K8VNue3YPh5A3x2oqHYMuXRTXsWDheWA1giq3V4jCNOn2qSW1im2jN_z0BVoiB2R2gnBb_tweRvnxM",
  "primaryModel": "MiniMax-M2.1",
  "status": "✅ 已配置，可使用"
}
```

### Kimi（Moonshot）
```json
{
  "provider": "moonshot",
  "baseUrl": "https://api.moonshot.cn/v1",
  "apiKey": "sk-kimi-Jz9cAiaQhR3L53XEkMEY8ic8ia6EFOuC5a24x5HcyhOYU14HGtTLNdraKDKZFUx4",
  "models": [
    "kimi-k2-thinking",
    "kimi-k2.5",
    "moonshot-v1-128k"
  ],
  "status": "⚠️ 需测试API是否正常"
}
```

### Qwen（通义千问）
```json
{
  "provider": "qwencode",
  "baseUrl": "https://coding.dashscope.aliyuncs.com/v1",
  "apiKey": "sk-sp-645687cbbd854d2ab15251e5086e5ac5",
  "models": [
    "qwen3-max-2026-01-23",
    "qwen3-coder-plus"
  ],
  "status": "⚠️ 需测试API是否正常"
}
```

---

## 💬 消息渠道配置

### 企业微信
```json
{
  "channel": "wecom",
  "corpId": "wwf684d252386fc0b6",
  "agentId": "1000002",
  "token": "Dl5b2jStSsNPF67RzsHhdq2",
  "encodingAESKey": "UFRkrE4sHzfD9q2qQoX38liGSrQ9FHpwjg3VQB4056G",
  "status": "✅ 已配置"
}
```

### 钉钉
```json
{
  "channel": "ddingtalk",
  "status": "✅ 已安装"
}
```

### QQ
```json
{
  "channel": "qqbot",
  "status": "✅ 已安装"
}
```

---

## 🔧 其他配置

### QVeris（动态工具）
```json
{
  "env": {
    "QVERIS_API_KEY": "sk-P1hVbGE5ZZZKE9yUFM3d2HMRW-sxHpPWxcTBkstVYZI"
  },
  "status": "✅ 已配置"
}
```

### OpenClaw Gateway
```json
{
  "port": 18789,
  "token": "4cc12d150634a0f0d70f66c4f9f0e7cc7238ff07250de3e3",
  "status": "✅ 已配置"
}
```

---

## 🌐 代理配置

### HTTP代理
```json
{
  "server": "http://127.0.0.1:13128",
  "status": "⚠️ 小红书被IP检测拦截",
  "note": "180.172.33.19（上海电信）被标记为风险IP"
}
```

### 建议
- 小红书：建议使用本地浏览器或更换代理IP
- 其他服务：代理正常

---

## 📦 子代理配置

### 子代理规则
```yaml
主模型: MiniMax-M2.1
子代理模型: qwen/qwen3
并行策略: 复杂任务优先并行
```

### 用途
- 数据分析任务
- 搜索任务
- 需要并行的复杂任务

---

## 🎯 使用建议

### 1. 模型选择
- **日常对话**: MiniMax（主模型）
- **代码任务**: Qwen3 Coder
- **长文本**: Kimi-k2.5

### 2. 消息渠道
- **个人消息**: 企业微信
- **群组消息**: 钉钉/QQ
- **紧急通知**: 多渠道同时

### 3. 代理使用
- ✅ 正常服务: 使用代理
- ❌ 小红书: 代理IP被标记，建议本地访问或更换IP

---

## 📝 API测试命令

### 测试MiniMax
```bash
curl -X POST https://api.minimaxi.com/anthropic/v1/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-cp-urIBOUm3ibSFf3B6i1vQc6mC7fTqtItyFpqLa7KH6K8VNue3YPh5A3x2oqHYMuXRTXsWDheWA1giq3V4jCNOn2qSW1im2jN_z0BVoiB2R2gnBb_tweRvnxM" \
  -d '{"model": "MiniMax-M2.1", "messages": [{"role": "user", "content": "Hello"}]}'
```

### 测试QVeris
```bash
curl -X POST https://api.qveris.ai/v1/tools \
  -H "Authorization: Bearer sk-P1hVbGE5ZZZKE9yUFM3d2HMRW-sxHpPWxcTBkstVYZI"
```

---

## ⚠️ 待解决

### 小红书IP限制
- 代理IP被小红书标记为风险IP (180.172.33.19)
- 建议: 更换代理IP或本地浏览器访问

---

## ✅ 已解决问题

- [x] MiniMax配置
- [x] 企业微信配置
- [x] 钉钉配置
- [x] QQ配置
- [x] QVeris配置
- [x] 子代理配置
- [x] OpenClaw Gateway配置

