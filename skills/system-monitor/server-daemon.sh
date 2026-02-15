#!/bin/bash

# 服务器守护进程 - 自动监控并重启
# 确保 Node.js 服务器持续运行

PROCESS_NAME="node src/index.js"
PORT=3000
LOG_FILE="/root/.openclaw/workspace/logs/daemon-monitor.log"
MAX_RESTARTS=5
RESTART_COOLDOWN=60  # 60秒内最多重启5次

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

check_port() {
    netstat -tlnp 2>/dev/null | grep -q ":$PORT " || ss -tlnp | grep -q ":$PORT "
}

get_pid() {
    ps aux | grep "$PROCESS_NAME" | grep -v grep | awk '{print $2}' | head -1
}

start_server() {
    cd /root/.openclaw/workspace/harmony-ai-app/Server
    nohup node src/index.js > /tmp/harmony.log 2>&1 &
    sleep 3
    
    if check_port; then
        log "✅ 服务器启动成功"
        return 0
    else
        log "❌ 服务器启动失败"
        return 1
    fi
}

stop_server() {
    pid=$(get_pid)
    if [ -n "$pid" ]; then
        kill "$pid" 2>/dev/null
        sleep 2
        log "已停止服务器 (PID: $pid)"
    fi
}

restart_server() {
    log "🔄 重启服务器..."
    stop_server
    start_server
}

# 主监控循环
main() {
    log "🚀 守护进程启动"
    log "监控进程: $PROCESS_NAME"
    log "监控端口: $PORT"
    
    restart_count=0
    last_restart_time=0
    
    while true; do
        sleep 30  # 每30秒检查一次
        
        # 检查端口是否监听
        if ! check_port; then
            log "⚠️ 端口 $PORT 未监听，尝试重启..."
            
            current_time=$(date +%s)
            
            # 检查重启频率
            if [ $((current_time - last_restart_time)) -lt $RESTART_COOLDOWN ]; then
                restart_count=$((restart_count + 1))
            else
                restart_count=1
                last_restart_time=$current_time
            fi
            
            if [ $restart_count -gt $MAX_RESTARTS ]; then
                log "❌ 30分钟内重启超过 $MAX_RESTARTS 次，停止自动恢复"
                log "请手动检查系统问题"
                exit 1
            fi
            
            # 尝试重启
            restart_server
        fi
        
        # 检查进程是否存活
        pid=$(get_pid)
        if [ -z "$pid" ]; then
            log "⚠️ 进程不存在，尝试启动..."
            start_server
        fi
    done
}

# 如果直接运行，执行主程序
if [ "$1" = "--daemon" ]; then
    main
else
    # 前台运行模式
    log "🔍 前台模式启动监控"
    main
fi
