#!/bin/bash
# 小红书保持登录状态脚本

LOG_FILE="/root/.openclaw/workspace/logs/xiaohongshu-keepalive.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> $LOG_FILE
}

log "检查登录状态..."

# 检查 MCP 服务是否运行
if ! docker ps | grep -q xiaohongshu-mcp; then
    log "MCP 容器未运行，重启中..."
    docker restart xiaohongshu-mcp
    sleep 5
fi

# 检查登录状态
STATUS=$(curl -s http://127.0.0.1:18060/api/v1/login/status 2>/dev/null)
if echo $STATUS | grep -q '"is_logged_in":true'; then
    log "登录状态正常"
    
    # 备份 Cookie
    docker cp xiaohongshu-mcp:/tmp/cookies.json /root/.openclaw/workspace/xiaohongshu-mcp/cookies/cookies.json 2>/dev/null
    log "Cookie 已备份"
else
    log "警告：登录状态异常"
    echo $STATUS
fi
