# ⚡ OpenClaw 快捷命令手册

## 📁 常用脚本位置

```
/home/dhtaiyi/.openclaw/workspace/
├── 小红书工具
│   ├── xiaohongshu-tool.py          # 主工具箱（搜索+发贴）
│   ├── xiaohongshu-publish-now.py   # 发贴脚本
│   ├── xiaohongshu-save-now.py      # Cookie保存工具
│   └── xiaohongshu-creator-cookies.json  # Cookie文件
│
├── 系统监控
│   ├── system-monitor.sh            # 系统监控（每小时）
│   ├── system-optimizer.sh          # 系统优化（每天4点）
│   ├── heartbeat-monitor.sh         # 心跳监控（每5分钟）
│   ├── backup-system.sh             # 备份（每天3点）
│   └── daily-summary.sh             # 日报（每天23点）
│
└── 工具脚本
    ├── analyze-image-zhipu.py       # 智谱AI图像分析
    ├── safe-edit.sh                 # 安全编辑（带备份）
    └── openclaw-switch/            # 模型切换工具
```

---

## 🚀 日常操作命令

### 小红书操作
```bash
# 保存Cookie
python3 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-save-now.py "粘贴的Cookie"

# 发贴（需要有效Cookie）
python3 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-publish-now.py

# 搜索内容
python3 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-tool.py search "关键词"
```

### 系统状态
```bash
# 查看OpenClaw状态
openclaw status

# 查看系统监控
cat /home/dhtaiyi/.openclaw/workspace/logs/monitor.log | tail -20

# 查看心跳
cat /home/dhtaiyi/.openclaw/workspace/logs/heartbeat.log | tail -10
```

### 模型切换
```bash
# 查看当前模型
openclaw-switch status

# 切换模型
openclaw-switch switch <模型名>

# 查看可用模型
openclaw-switch list
```

---

## 🔧 开发调试命令

### 测试API
```bash
# 测试MiniMax
curl -X POST "https://api.minimaxi.com/anthropic/v1/messages" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-cp-..." \
  -d '{"model": "MiniMax-M2.1", "messages": [{"role": "user", "content": "Hi"}]}'

# 测试Qwen
curl -X POST "https://coding.dashscope.aliyuncs.com/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-sp-..." \
  -d '{"model": "qwen3-max-2026-01-23", "messages": [{"role": "user", "content": "Hi"}]}'

# 测试QVeris
cd /home/dhtaiyi/.openclaw/workspace/skills/qveris
python3 scripts/qveris_tool.py search "天气"
```

---

## 📊 监控和维护

### 查看日志
```bash
# 实时监控日志
tail -f /home/dhtaiyi/.openclaw/workspace/logs/monitor.log

# 查看错误
grep -i error /home/dhtaiyi/.openclaw/workspace/logs/*.log | tail -20

# 查看今天的活动
grep "2026-02-13" /home/dhtaiyi/.openclaw/workspace/logs/*.log | tail -30
```

### 手动执行任务
```bash
# 手动系统监控
bash /home/dhtaiyi/.openclaw/workspace/system-monitor.sh

# 手动备份
bash /home/dhtaiyi/.openclaw/workspace/backup-system.sh

# 手动优化
bash /home/dhtaiyi/.openclaw/workspace/system-optimizer.sh

# 刷新小红书Cookie
bash /home/dhtaiyi/.openclaw/workspace/xiaohongshu-cron-refresh.sh
```

---

## 💡 常用技巧

### 快速搜索
```bash
# 在日志中搜索
grep "关键词" /home/dhtaiyi/.openclaw/workspace/logs/*.log

# 在配置中搜索
grep -r "keyword" /home/dhtaiyi/.openclaw/openclaw.json
```

### 文件管理
```bash
# 安全编辑（带备份）
bash /home/dhtaiyi/.openclaw/workspace/safe-edit.sh <文件路径>

# 查看大文件
ls -lh /home/dhtaiyi/.openclaw/workspace/*.py | sort -k5 -h | tail -10
```

### 进程管理
```bash
# 查看OpenClaw进程
ps aux | grep openclaw

# 重启OpenClaw
openclaw gateway restart
```

---

## ⚠️ 常见问题

### 小红书发贴失败
1. 检查Cookie是否过期
2. 检查IP是否被拦截
3. 重新保存Cookie后重试

### API调用失败
1. 检查API Key是否正确
2. 检查网络连接
3. 查看错误日志

### 系统监控告警
1. 查看monitor.log了解详情
2. 检查磁盘、内存使用
3. 重启相关服务

---

## 📝 快速参考

| 操作 | 命令 |
|------|------|
| 保存Cookie | `python3 xiaohongshu-save-now.py "cookie"` |
| 发贴 | `python3 xiaohongshu-publish-now.py` |
| 搜索 | `python3 xiaohongshu-tool.py search "关键词"` |
| 查看状态 | `openclaw status` |
| 切换模型 | `openclaw-switch switch <模型>` |
| 查看日志 | `tail -f logs/monitor.log` |
| 系统监控 | `bash system-monitor.sh` |

