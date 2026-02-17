# 🎉 小红书工具箱 - 完整功能总结

## ✅ 已实现功能

### 1. 搜索功能 ✅
- 关键词搜索
- 内容提取
- 结果保存（JSON格式）

### 2. Cookie管理 ✅
- Cookie保存
- 自动刷新
- 状态监控
- 有效期管理

### 3. 自动化 ✅
- 定时任务
- 守护进程
- 系统服务（可选）

---

## 📁 完整文件列表

```
/root/.openclaw/workspace/
├── xiaohongshu-tool.py              # 🎯 集成工具箱（推荐）
├── xiaohongshu-cookie-manager.py    # 🔧 Cookie管理器
├── xiaohongshu-save-cookies.py      # 💾 Cookie保存工具
├── xiaohongshu-cookies.json        # 📦 Cookie存储文件
├── xiaohongshu-results.json         # 📊 搜索结果
├── xiaohongshu-cookie.log          # 📝 日志文件
├── XIAOHONGSHU_COMPLETE.md         # 📖 本文档
└── XIAOHONGSHU_COOKIE.md          # 📋 Cookie管理文档
```

---

## 🚀 快速使用指南

### 第一步：获取Cookie

**方法1：控制台（最快）**
```javascript
// 浏览器打开小红书并登录
// F12 → Console
copy(document.cookie);
```

**方法2：书签脚本**
```bash
python3 /root/.openclaw/workspace/xiaohongshu-save-cookies.py
# 按提示创建书签
```

### 第二步：保存Cookie

```bash
# 保存Cookie
python3 /root/.openclaw/workspace/xiaohongshu-tool.py save "粘贴的Cookie"

# 查看状态
python3 /root/.openclaw/workspace/xiaohongshu-tool.py status
```

### 第三步：开始搜索

```bash
# 搜索单个关键词
python3 /root/.openclaw/workspace/xiaohongshu-tool.py search 穿搭

# 搜索多个关键词
python3 /root/.openclaw/workspace/xiaohongshu-tool.py search 穿搭 美妆 美食 健身

# 查看结果
cat /root/.openclaw/workspace/xiaohongshu-results.json
```

---

## 📋 详细命令

### Cookie管理
```bash
# 查看Cookie状态
python3 /root/.openclaw/workspace/xiaohongshu-tool.py status

# 保存Cookie
python3 /root/.openclaw/workspace/xiaohongshu-tool.py save "Cookie字符串"

# 刷新Cookie
python3 /root/.openclaw/workspace/xiaohongshu-cookie-manager.py refresh

# 启动自动刷新
python3 /root/.openclaw/workspace/xiaohongshu-cookie-manager.py monitor
```

### 搜索功能
```bash
# 搜索
python3 /root/.openclaw/workspace/xiaohongshu-tool.py search 穿搭

# 搜索多个
python3 /root/.openclaw/workspace/xiaohongshu-tool.py search 穿搭 美妆 美食
```

### 帮助
```bash
python3 /root/.openclaw/workspace/xiaohongshu-tool.py help
```

---

## ⏰ 自动刷新设置（推荐）

### 设置定时任务
```bash
# 编辑crontab
crontab -e

# 添加每6小时自动刷新
0 */6 * * * /usr/bin/python3 /root/.openclaw/workspace/xiaohongshu-cookie-manager.py refresh
```

### 验证设置
```bash
# 查看cron任务
crontab -l
```

---

## 📊 Cookie有效期

| 状态 | 建议 |
|------|------|
| < 6小时 | ✅ 最佳 |
| 6-24小时 | ⚠️ 建议刷新 |
| > 24小时 | ❌ 需要更新 |

---

## 🔧 故障排除

### 问题1：Cookie无效
```bash
# 检查状态
python3 /root/.openclaw/workspace/xiaohongshu-tool.py status

# 重新保存
python3 /root/.openclaw/workspace/xiaohongshu-tool.py save "新Cookie"
```

### 问题2：搜索失败
```bash
# 1. 检查Cookie
python3 /root/.openclaw/workspace/xiaohongshu-tool.py status

# 2. 刷新Cookie
python3 /root/.openclaw/workspace/xiaohongshu-cookie-manager.py refresh

# 3. 重新搜索
python3 /root/.openclaw/workspace/xiaohongshu-tool.py search 穿搭
```

### 问题3：查看日志
```bash
tail -f /root/.openclaw/workspace/xiaohongshu-cookie.log
```

---

## 💡 使用建议

### 日常使用
1. **定期检查Cookie状态** - 每周一次
2. **设置定时刷新** - 自动保持有效
3. **搜索前确认** - 确保Cookie有效

### 备份重要
```bash
# 备份Cookie
cp /root/.openclaw/workspace/xiaohongshu-cookies.json /backup/xiaohongshu-cookies.json

# 恢复Cookie
cp /backup/xiaohongshu-cookies.json /root/.openclaw/workspace/xiaohongshu-cookies.json
```

---

## 🎯 高级功能

### 多账号支持（扩展）
```python
# 修改代码支持多个Cookie
{
  "account1": { cookies, saved_at },
  "account2": { cookies, saved_at }
}
```

### 数据持久化
```python
# 保存到数据库
import sqlite3

conn = sqlite3.connect('xiaohongshu.db')
conn.execute('''CREATE TABLE cookies
    (account TEXT, cookie TEXT, saved_at TEXT)''')
```

### Web界面
```bash
# 启动简单Web服务器
python3 -m http.server 8000
# 访问 http://localhost:8000
```

---

## 📈 技术架构

```
浏览器（获取Cookie）
    ↓
保存到JSON文件
    ↓
定时任务（自动刷新）
    ↓
搜索时读取Cookie
    ↓
Playwright执行搜索
    ↓
保存结果到JSON
```

---

## ✅ 成功标准

- [x] Cookie可以长期保存
- [x] 自动刷新保持有效
- [x] 搜索功能正常工作
- [x] 结果正确保存
- [x] 日志记录完整

---

## 🎓 总结

**小红书工具箱已完整实现**：

✅ **搜索功能** - 关键词搜索，内容提取
✅ **Cookie管理** - 保存、刷新、监控
✅ **自动化** - 定时任务、守护进程
✅ **易用性** - 简单命令，一键操作

**下一步扩展**：
- 多账号支持
- 数据持久化
- Web界面
- API接口

---

**🎯 使用愉快！**

