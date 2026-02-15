---
name: system-monitor
description: Monitor system health with auto-restart capability. Checks ports, processes, and auto-restarts if stopped.
metadata: {"clawdbot":{"emoji":"🔍"}}
---

# System Monitor Skill

Monitor system health with auto-restart capability.

## Features

- ✅ **Auto-Restart**: Automatically restarts server if stopped
- 🔍 **Health Checks**: Ports, processes, resources
- 📊 **Monitoring**: CPU, Memory, Disk, Cron tasks
- 📝 **Logging**: All checks logged to file

## Files

```
/root/.openclaw/workspace/skills/system-monitor/
├── health-check.sh       # Main health check with auto-restart
├── server-daemon.sh      # Advanced daemon with rate limiting
└── simple-monitor.sh     # Simple process monitor
```

## Usage

```bash
# Manual check (with auto-restart)
./health-check.sh

# Advanced daemon mode
./server-daemon.sh --daemon

# Simple monitor
./simple-monitor.sh
```

## Auto-Restart Behavior

| Scenario | Action |
|----------|--------|
| Port 3000 down | Auto-restart server |
| Process dead | Auto-start server |
| Too many restarts | Stop (prevents loops) |
| Gateway down | Log warning only |

## Cron Schedule

```
# Every minute with auto-restart
* * * * * /root/.openclaw/workspace/skills/system-monitor/health-check.sh

# Every 6 hours
0 */6 * * * /root/.openclaw/workspace/skills/system-monitor/health-check.sh

# Daily report at 8 AM
0 8 * * * /root/.openclaw/workspace/skills/system-monitor/health-check.sh
```

## Logs

- Health checks: `/root/.openclaw/workspace/logs/health-check.log`
- Server daemon: `/root/.openclaw/workspace/logs/daemon.log`
- Server errors: `/tmp/harmony.log`

## What It Monitors

| Check | Description | Auto-Fix |
|-------|-------------|----------|
| Port 3000 | Web server port | ✅ Restart |
| Port 18789 | Gateway port | ⚠️ Log only |
| Node.js process | Server process | ✅ Restart |
| Gateway process | OpenClaw daemon | ⚠️ Log only |
| Cron tasks | Scheduled tasks | 📊 Count |
| CPU load | System load average | 📊 Report |
| Memory | RAM usage | 📊 Report |
| Disk | Disk space | 📊 Report |

## Output Example

```
╔═══════════════════════════════════════════════╗
║       🌸 系统健康检查任务监控 🌸              ║
╚═══════════════════════════════════════════════╝

检查时间: 2026-02-15 23:55:02

📡 检查网络服务
─────────────────────────────────────────────
  🌐 Port 3000 (网页):    ✅ 正常
  🦞 Port 18789 (Gateway): ✅ 正常

📊 检查关键进程
─────────────────────────────────────────────
  📄 Node.js 服务器:     ✅ 运行中 (PID: 805383)
  🦞 OpenClaw Gateway:   ✅ 运行中 (PID: 804874)

⏰ Cron任务数量: 9 个

💻 系统资源状态
─────────────────────────────────────────────
  📊 CPU 负载:           1.55, 1.00, 0.89
  🧠 内存使用:           已用: 2.1Gi / 总计: 7.5Gi
  💾 磁盘使用:           已用: 25G / 总计: 120G (21%)

═══════════════════════════════════════════════

✅ 所有关键服务和进程都正常运行！
🔒 自动修复功能已启用

💡 检查完成
```

## Protection Against Crashes

The system has multiple layers of protection:

1. **Cron Monitor**: Checks every minute
2. **Auto-Restart**: Fixes issues automatically
3. **Rate Limiting**: Max 5 restarts per hour
4. **Logging**: All events recorded

## Commands

```bash
# View recent logs
tail -20 /root/.openclaw/workspace/logs/health-check.log

# Force check
/root/.openclaw/workspace/skills/system-monitor/health-check.sh

# View server status
ps aux | grep "node.*index.js"
```
