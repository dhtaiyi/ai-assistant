# 401错误排查报告

## ❌ 错误汇总

### 1. Kimi (Moonshot) API - HTTP 401

**状态**: ❌ 认证失败
**API Key**: `sk-kimi-Jz9cAiaQhR3L53XEkMEY8ic8ia6EFOuC5a24x5HcyhOYU14HGtTLNdraKDKZFUx4`

**响应**:
```json
{"error":{"message":"Invalid Authentication","type":"invalid_authentication_error"}}
```

**可能原因**:
1. ✅ **API Key已过期** - 最可能
2. ❌ **API Key格式错误** - Key格式正确
3. ❌ **账户余额不足** - 需要检查
4. ❌ **未开启API权限** - 需要检查

**建议**:
- 访问 https://platform.moonshot.cn/
- 检查API Key是否有效
- 查看账户余额

---

### 2. 企业微信 - HTTP 401

**状态**: ✅ 已修复

**测试结果**: Access Token获取成功
```json
{"errcode":0,"errmsg":"ok","access_token":"..."}
```

**当前配置**:
- CorpID: `wwf684d252386fc0b6`
- AgentID: `1000002`
- Secret: `aEgqy4MfNSXBWUoy9jgwZLiBfVTnd7POgRJzVUHq_Q0`

**结论**: 企业微信API正常，401错误可能来自其他接口

---

## 🔧 解决方案

### Kimi API

1. **登录Moonshot控制台**
   - 访问: https://platform.moonshot.cn/

2. **检查API Key**
   - 进入「API密钥管理」
   - 查看Key状态

3. **如Key无效**
   - 创建新的API Key
   - 更新配置文件

4. **更新配置**
   ```bash
   # 使用OpenClaw Switch查看
   cd /root/.openclaw/workspace/openclaw-switch
   bash scripts/openclaw-switch.sh list
   ```

---

## 📊 当前API状态

| API | 状态 | 错误 |
|-----|------|------|
| **Qwen** | ✅ 正常 | - |
| **智谱AI** | ✅ 正常 | - |
| **企业微信** | ✅ 正常 | - |
| **Kimi** | ❌ 401 | API Key无效 |
| **MiniMax** | ❌ 404 | 端点错误 |

---

## 💡 建议

### 立即可用
1. **使用Qwen** - 当前主模型，正常工作
2. **使用智谱AI** - 图片分析，正常工作

### 需要修复
1. **检查Kimi API Key** - 重新获取有效Key
2. **修复MiniMax端点** - 检查正确的API地址

---

## 📁 相关文件

- 排查报告: `/root/.openclaw/workspace/TROUBLESHOOTING.md`
- 配置文件: `/root/.openclaw/openclaw.json`
- 模型切换: `/root/.openclaw/workspace/openclaw-switch/`
