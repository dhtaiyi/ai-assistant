#!/bin/bash

# 简单服务器进程监控
# 每分钟检查，如果停止则自动重启

PID_FILE="/tmp/harmony-server.pid"
LOG_FILE="/root/.openclaw/workspace/logs/server-monitor.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

check_server() {
    # 检查端口是否监听
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/ | grep -q "200"; then
        return 0  # 正常运行
    else
        return 1  # 可能已停止
    fi
}

start_server() {
    cd /root/.openclaw/workspace/harmony-ai-app/Server
    
    # 杀掉旧进程
    pkill -f "node src/index.js" 2>/dev/null
    sleep 1
    
    # 启动新进程
    nohup node src/index.js > /tmp/harmony.log 2>&1 &
    sleep 3
    
    if check_server; then
        log "✅ 服务器启动成功"
        return 0
    else
        log "❌ 服务器启动失败"
        return 1
    fi
}

# 主程序
log "🔍 开始监控服务器状态..."

if check_server; then
    log "✅ 服务器运行正常"
else
    log "⚠️ 服务器未运行，尝试启动..."
    start_server
fi
