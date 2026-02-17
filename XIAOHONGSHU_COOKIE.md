# 🎯 小红书Cookie长期管理方案

## 概述

实现Cookie的自动保存、定期刷新和长期有效性管理。

---

## 📁 工具文件

| 文件 | 功能 | 说明 |
|------|------|------|
| `xiaohongshu-cookie-manager.py` | Cookie管理器 | 自动刷新、状态检查 |
| `xiaohongshu-save-cookies.py` | Cookie保存工具 | 从浏览器获取Cookie |
| `xiaohongshu-tool.py` | 集成工具箱 | 搜索+Cookie管理 |
| `xiaohongshu-cookies.json` | Cookie存储 | JSON格式保存 |

---

## 🚀 快速开始

### 步骤1：获取Cookie

**方法A：使用书签脚本**
```bash
# 生成书签脚本
python3 /root/.openclaw/workspace/xiaohongshu-save-cookies.py

# 复制生成的JavaScript代码
# 创建浏览器书签
# 访问小红书并登录
# 点击书签复制Cookie
```

**方法B：控制台命令**
```javascript
// 浏览器F12 → Console
copy(document.cookie);
```

**方法C：手动提供**
```bash
# 复制Cookie字符串
python3 /root/.openclaw/workspace/xiaohongshu-tool.py save "a1=xxx; web_session=xxx; ..."
```

### 步骤2：查看Cookie状态
```bash
python3 /root/.openclaw/workspace/xiaohongshu-tool.py status
```

### 步骤3：开始搜索
```bash
python3 /root/.openclaw/workspace/xiaohongshu-tool.py search 穿搭 美妆 美食
```

---

## 📋 工具使用

### 1. Cookie管理器
```bash
# 查看状态
python3 /root/.openclaw/workspace/xiaohongshu-cookie-manager.py status

# 刷新Cookie
python3 /root/.openclaw/workspace/xiaohongshu-cookie-manager.py refresh

# 启动自动刷新守护进程
python3 /root/.openclaw/workspace/xiaohongshu-cookie-manager.py monitor
```

### 2. Cookie保存工具
```bash
# 生成书签脚本
python3 /root/.openclaw/workspace/xiaohongshu-save-cookies.py

# 直接保存
python3 /root/.openclaw/workspace/xiaohongshu-save-cookies.py "Cookie字符串"
```

### 3. 集成工具箱
```bash
# 查看状态
python3 /root/.openclaw/workspace/xiaohongshu-tool.py status

# 保存Cookie
python3 /root/.openclaw/workspace/xiaohongshu-tool.py save "Cookie字符串"

# 搜索
python3 /root/.openclaw/workspace/xiaohongshu-tool.py search 穿搭

# 搜索多个
python3 /root/.openclaw/workspace/xiaohongshu-tool.py search 穿搭 美妆 美食 健身
```

---

## ⏰ 自动刷新方案

### 方案1：定时任务（推荐）

创建cron定时任务：
```bash
# 编辑crontab
crontab -e

# 添加定时刷新（每6小时）
0 */6 * * * /usr/bin/python3 /root/.openclaw/workspace/xiaohongshu-cookie-manager.py refresh
```

### 方案2：守护进程模式
```bash
# 启动自动刷新（前台运行）
python3 /root/.openclaw/workspace/xiaohongshu-cookie-manager.py monitor

# 后台运行
nohup python3 /root/.openclaw/workspace/xiaohongshu-cookie-manager.py monitor > /tmp/xiaohongshu-monitor.log 2>&1 &
```

### 方案3：系统服务（高级）

创建systemd服务：
```ini
# /etc/systemd/system/xiaohongshu-cookie.service
[Unit]
Description=XiaoHongShu Cookie Auto-Refresh

[Service]
Type=simple
User=root
ExecStart=/usr/bin/python3 /root/.openclaw/workspace/xiaohongshu-cookie-manager.py monitor
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 启用服务
systemctl enable xiaohongshu-cookie
systemctl start xiaohongshu-cookie
```

---

## 📊 Cookie有效期

| 状态 | 有效期 | 说明 |
|------|--------|------|
| 新Cookie | 24小时 | 小红书默认有效期 |
| 刷新后 | +24小时 | 每次访问延长有效期 |
| 建议刷新 | <6小时 | 超过6小时建议刷新 |
| 可能失效 | >24小时 | 建议立即刷新 |

---

## 🔄 刷新策略

### 智能刷新
```python
# 刷新间隔
REFRESH_INTERVAL = 6 * 3600  # 每6小时

# 检查阈值
NEEDS_REFRESH = elapsed > REFRESH_INTERVAL
```

### 手动刷新时机
1. **搜索失败时** - 尝试刷新Cookie
2. **定期刷新** - 每6小时自动刷新
3. **手动触发** - 发现问题时手动刷新

---

## 💾 Cookie存储

### 文件格式
```json
{
  "cookies": {
    "a1": "xxx",
    "web_session": "xxx",
    "webId": "xxx"
  },
  "saved_at": "2026-02-12T23:00:00.000000",
  "expires_at": "2026-02-13T23:00:00.000000"
}
```

### 安全建议
1. **设置权限**
   ```bash
   chmod 600 /root/.openclaw/workspace/xiaohongshu-cookies.json
   ```

2. **定期备份**
   ```bash
   # 备份Cookie
   cp /root/.openclaw/workspace/xiaohongshu-cookies.json /backup/xiaohongshu-cookies.json
   ```

3. **监控日志**
   ```bash
   tail -f /root/.openclaw/workspace/xiaohongshu-cookie.log
   ```

---

## 🔧 常见问题

### Q1: Cookie过期怎么办？
A: 使用书签脚本或控制台获取新Cookie，然后：
```bash
python3 /root/.openclaw/workspace/xiaohongshu-tool.py save "新Cookie"
```

### Q2: 如何知道Cookie是否有效？
A: 查看状态：
```bash
python3 /root/.openclaw/workspace/xiaohongshu-tool.py status
```

### Q3: 搜索失败怎么办？
A: 按顺序排查：
1. 检查Cookie状态
2. 刷新Cookie
3. 重新搜索

### Q4: 可以同时保存多个Cookie吗？
A: 当前版本支持单个Cookie，如需多个可以扩展保存为：
```json
{
  "default": { cookies, saved_at },
  "account2": { cookies, saved_at }
}
```

---

## 🎯 最佳实践

1. **定期刷新**
   - 设置定时任务自动刷新
   - 建议每6小时刷新一次

2. **监控状态**
   - 使用status命令定期检查
   - 设置告警（可选）

3. **备份重要**
   - 定期备份Cookie文件
   - 记录保存时间

4. **及时更新**
   - 发现搜索失败立即刷新
   - 长期不使用时也定期刷新

---

## 📈 流程图

```
获取Cookie
    ↓
保存到文件
    ↓
定期刷新（每6小时）
    ↓
检查有效期
    ↓
├─ 有效 → 使用搜索
│
└─ 失效 → 重新获取
         ↓
       保存并使用
```

---

## ✅ 检查清单

- [ ] Cookie已保存
- [ ] 可以查看状态
- [ ] 定时任务已设置（可选）
- [ ] 搜索功能正常
- [ ] 日志文件可访问

