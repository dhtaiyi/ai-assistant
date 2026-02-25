# 获取的 EvoMap 胶囊

## 胶囊 1: Feishu Doc 错误修复
- **Asset ID**: sha256:22e00475cc06d59c44f55beb3a623f43c347ac39f1342e62bce5cfcd5593a63c
- **GDI**: 61.9
- **置信度**: 0.92
- **成功次数**: 45 次
- **触发**: FeishuDocError, 400BadRequest, append_action_failure
- **修复内容**: 
  - 添加输入清理 (sanitizeMarkdown + validateBlocks)
  - 自动从 write 降级到 append
- **影响范围**: 2 个文件，45 行代码

## 胶囊 2: Feishu 消息降级发送
- **Asset ID**: sha256:6d2b5224c9858a6b9610e9c065254f385d5a055e4d6789eaa061f0f9053ae9f4
- **GDI**: 60.85
- **置信度**: 0.91
- **触发**: FeishuFormatError, markdown_render_failed, card_send_rejected
- **修复内容**: 
  - Feishu 消息降级链：富文本 → 交互卡片 → 纯文本
  - 自动检测格式错误并重试
- **影响范围**: 1 个文件

---

获取时间：2026-02-25
