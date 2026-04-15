# OpenClaw 系统优化指南

## 📁 优化脚本

### 1. 系统优化器 (system-optimizer.sh)
- **功能**: 性能优化、日志清理、备份管理、健康检查
- **自动执行**: 每天凌晨4点
- **手动运行**: `/home/dhtaiyi/.openclaw/workspace/system-optimizer.sh`
- **日志**: `/home/dhtaiyi/.openclaw/workspace/logs/optimizer.log`

### 2. 系统监控器 (system-monitor.sh)
- **功能**: 磁盘、内存、CPU、负载、服务、网络监控
- **自动执行**: 每小时
- **手动运行**: `/home/dhtaiyi/.openclaw/workspace/system-monitor.sh`
- **日志**: `/home/dhtaiyi/.openclaw/workspace/logs/monitor.log`

## ⚙️ 告警配置 (可选)

### Telegram告警
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"
```

### Slack告警
```bash
export SLACK_WEBHOOK="https://hooks.slack.com/services/xxx"
```

### 邮件告警
```bash
export EMAIL_ALERT="your@email.com"
```

## 📊 监控阈值

| 项目 | 警告 | 严重 |
|------|------|------|
| 磁盘 | 80% | 90% |
| 内存 | 80% | 90% |
| CPU | 70% | 90% |
| 负载 | 3 | 5 |

## 🧹 自动化任务

```bash
# 查看定时任务
crontab -l

# 任务列表
0 4 * * * /home/dhtaiyi/.openclaw/workspace/system-optimizer.sh    # 每天优化
0 * * * * /home/dhtaiyi/.openclaw/workspace/system-monitor.sh       # 每小时监控
*/5 * * * * /home/dhtaiyi/.openclaw/workspace/heartbeat-monitor.sh # 心跳监控
0 3 * * * /home/dhtaiyi/.openclaw/workspace/backup-system.sh       # 自动备份
0 23 * * * /home/dhtaiyi/.openclaw/workspace/daily-summary.sh      # 日报总结
```

## 🔧 手动优化

```bash
# 立即优化
/home/dhtaiyi/.openclaw/workspace/system-optimizer.sh

# 立即监控
/home/dhtaiyi/.openclaw/workspace/system-monitor.sh

# 查看系统状态
openclaw status

# 查看日志
tail -f /home/dhtaiyi/.openclaw/workspace/logs/heartbeat.log
```

## 📈 性能优化项

1. **内存缓存清理**: 自动清理PageCache
2. **Swappiness优化**: 设置为10，优先使用内存
3. **临时文件清理**: 定期清理tmp目录
4. **日志轮转**: 保留7天日志
5. **备份清理**: 保留30天备份

## 💡 最佳实践

1. **定期检查**: 每周查看监控报告
2. **及时响应**: 收到告警后及时处理
3. **定期优化**: 让自动任务处理日常维护
4. **日志分析**: 关注错误日志和警告

## 🆘 故障排除

### 磁盘空间不足
```bash
# 查找大文件
du -sh /home/dhtaiyi/.openclaw/workspace/* | sort -hr | head -10

# 清理Docker
docker system prune -a -f
```

### 内存不足
```bash
# 查看内存使用
free -h

# 清理缓存
sync && echo 3 > /proc/sys/vm/drop_caches
```

### 服务宕机
```bash
# 重启OpenClaw
openclaw restart

# 检查状态
openclaw status
```
