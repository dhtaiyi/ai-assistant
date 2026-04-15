# OpenClaw 模型状态报告

## 🔀 OpenClaw Switch 已安装

### 安装位置
- 目录: `/home/dhtaiyi/.openclaw/workspace/openclaw-switch/`
- 脚本: `scripts/openclaw-switch.sh`

### 功能
- ✅ 查看当前模型状态
- ✅ 列出所有可用模型
- ✅ 一键切换模型
- ✅ 查看Fallback链
- ✅ 安全修改配置（避免格式错误）

---

## 📊 当前模型状态

### ✅ 已切换到 Qwen3 Max
- **主模型**: qwencode/qwen3-max-2026-01-23
- **状态**: 正常 ✅
- **API**: 正常响应

### ⚠️ 有问题的模型
1. **Kimi (Moonshot)** - 认证失败
   - 原因: API Key可能过期或无效
   - 建议: 重新获取有效的API Key

2. **MiniMax** - 404错误  
   - 原因: API端点格式可能不正确
   - 建议: 检查MiniMax API文档

### ✅ 正常工作的模型
1. **Qwen3 Max** - 正常
2. **智谱AI** - 正常（图片分析）

---

## 🔧 可用模型列表

```
1. MiniMax M2.1              (minimax/MiniMax-M2.1)        ❌ 需修复
2. MiniMax M2.1 Lightning   (minimax/MiniMax-M2.1-lightning) ❌ 需修复
3. MiniMax M2                (minimax/MiniMax-M2)            ❌ 需修复
4. Kimi K2 Thinking         (moonshot/kimi-k2-thinking)      ❌ 需修复
5. Kimi K2 Thinking Turbo  (moonshot/kimi-k2-thinking-turbo) ❌ 需修复
6. Kimi K2.5               (moonshot/kimi-k2.5)             ❌ 需修复
7. Moonshot V1 128K        (moonshot/moonshot-v1-128k)       ❌ 需修复
8. Qwen3 Max               (qwencode/qwen3-max-2026-01-23)  ✅ 正常
9. Qwen3 Coder Plus        (qwencode/qwen3-coder-plus)       ✅ 正常
```

---

## 🚀 使用方法

### 查看状态
```bash
cd /home/dhtaiyi/.openclaw/workspace/openclaw-switch
bash scripts/openclaw-switch.sh status
```

### 列出模型
```bash
bash scripts/openclaw-switch.sh list
```

### 切换模型
```bash
bash scripts/openclaw-switch.sh switch 编号
```

### 查看Fallback
```bash
bash scripts/openclaw-switch.sh fallback
```

---

## 💡 建议

1. **当前**: 使用 Qwen3 Max 作为主模型
2. **修复**: 重新配置 Kimi 和 MiniMax API Key
3. **备用**: 使用智谱AI进行图片分析

---

## 📁 相关文件

- 配置文件: `/home/dhtaiyi/.openclaw/openclaw.json`
- 切换工具: `/home/dhtaiyi/.openclaw/workspace/openclaw-switch/`
- 状态报告: `/home/dhtaiyi/.openclaw/workspace/API_STATUS.md`
