# 企业微信401错误诊断报告

## ✅ 测试结果

| API接口 | 状态 | 错误码 |
|---------|------|--------|
| Access Token | ✅ 正常 | 0 |
| 发送消息 | ✅ 正常 | 0 |
| 获取部门 | ✅ 正常 | 0 |
| 用户列表 | ✅ 正常 | 0 |
| 客户列表 | ⚠️ 需权限 | 40058 |

---

## 🔍 结论

**基础API权限正常！** 消息发送、部门查询、用户查询都可以正常工作。

---

## 💡 401错误可能原因

### 1. 特定回调接口
企业微信的回调验证使用不同的认证机制，可能在验证签名时失败。

### 2. 高级API权限不足
客户群发、客户联系等高级功能可能需要额外权限。

### 3. openclaw-wecom扩展问题
版本2026.2.5可能存在特定场景的bug。

---

## 🔧 解决方案

### 方案1: 检查企业微信应用权限

1. 登录企业微信后台
2. 进入「应用管理」→「OpenClaw」
3. 检查以下权限：
   - ✅ 发送消息 - 已开启
   - ❓ 读取客户联系 - 需要开启
   - ❓ 客户群发 - 需要权限
   - ✅ 查看通讯录 - 已开启

### 方案2: 检查IP白名单

1. 企业微信后台 → 「我的企业」→「通讯录同步」
2. 添加服务器IP到白名单
   - 当前IP: `129.211.82.60`

### 方案3: 更新扩展

```bash
cd /root/.openclaw/extensions/wecom
git pull
npm install
```

### 方案4: 重启OpenClaw

```bash
pkill -HUP openclaw
```

---

## 📊 当前配置

```json
{
  "corpId": "wwf684d252386fc0b6",
  "agentId": "1000002",
  "token": "Dl5b2jStSsNPF67RzsHhdq2",
  "encodingAESKey": "UFRkrE4sHzfD9q2qQoX38liGSrQ9FHpwjg3VQB4056G"
}
```

---

## 🎯 下一步

1. **检查应用权限** - 确保所有API权限已开启
2. **添加IP白名单** - 添加服务器IP
3. **重启OpenClaw** - 清除临时状态
4. **查看扩展日志** - 定位具体错误位置

---

## 📁 相关文件

- 测试脚本: `/root/.openclaw/workspace/test-wecom.sh`
- 诊断报告: `/root/.openclaw/workspace/WECHAT_ERROR_FIX.md`
