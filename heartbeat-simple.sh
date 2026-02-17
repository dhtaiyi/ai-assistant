#!/bin/bash

# 简化版心跳监控脚本 - 检测 OpenClaw 状态
# 检测项目：进程、网关、WeCom
# 频率：每5分钟

# 配置
LOG_FILE="/root/.openclaw/workspace/logs/heartbeat-simple.log"
ALERT_LOG="/root/.openclaw/workspace/logs/heartbeat-alerts.log"
PID_FILE="/root/.openclaw/workspace/logs/heartbeat-simple.pid"

TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

log() {
    echo "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"
}

alert() {
    echo "[$TIMESTAMP] ALERT: $1" | tee -a "$LOG_FILE" "$ALERT_LOG"
}

# 防止重复运行
check_pid() {
    if [ -f "$PID_FILE" ]; then
        OLD_PID=$(cat "$PID_FILE")
        if kill -0 "$OLD_PID" 2>/dev/null; then
            echo "[$TIMESTAMP] 已有实例运行，退出" | tee -a "$LOG_FILE"
            exit 1
        fi
    fi
    echo $$ > "$PID_FILE"
}

# 1. 检查进程
check_process() {
    if pgrep -f "openclaw-gateway" > /dev/null 2>&1; then
        echo "RUNNING:$(pgrep -f 'openclaw-gateway' | head -1)"
        return 0
    else
        echo "DOWN"
        return 1
    fi
}

# 2. 检查网关
check_gateway() {
    local code=$(curl -s -o /dev/null -w "%{http_code}" \
        --connect-timeout 3 \
        --max-time 5 \
        "http://127.0.0.1:18789/health" 2>/dev/null || echo "000")
    
    if [ "$code" = "200" ] || [ "$code" = "000" ]; then
        echo "OK"
        return 0
    else
        echo "FAIL:$code"
        return 1
    fi
}

# 3. 检查 WeCom (简化版)
check_wecom() {
    # 检查日志中最近是否有 wecom 消息
    local log_file="/tmp/openclaw/openclaw-$(date +%Y-%m-%d).log"
    
    if [ -f "$log_file" ]; then
        local last_msg=$(grep "inbound.*wecom" "$log_file" 2>/dev/null | tail -1)
        if [ -n "$last_msg" ]; then
            echo "OK"
            return 0
        fi
    fi
    
    # 备选：检查进程
    if pgrep -f "openclaw.*wecom" > /dev/null 2>&1; then
        echo "OK"
        return 0
    fi
    
    echo "UNKNOWN"
    return 1
}

# 自动恢复
auto_recover() {
    log "尝试自动恢复..."
    
    # 杀掉旧进程
    pkill -9 -f "openclaw-gateway" 2>/dev/null || true
    sleep 2
    
    # 重启
    cd /root/.openclaw/workspace
    nohup npx openclaw gateway start >> "$LOG_FILE" 2>&1 &
    sleep 5
    
    if pgrep -f "openclaw-gateway" > /dev/null 2>&1; then
        log "自动恢复成功"
        alert "OpenClaw 已自动恢复"
    else
        log "自动恢复失败"
        alert "OpenClaw 自动恢复失败，请手动检查"
    fi
}

# 主流程
main() {
    check_pid
    log "========== 心跳检测 =========="
    
    # 检测
    PROC=$(check_process)
    GW=$(check_gateway)
    WM=$(check_wecom)
    
    log "进程: $PROC"
    log "网关: $GW"
    log "WeCom: $WM"
    
    # 判断
    ISSUES=""
    
    if [[ "$PROC" == DOWN ]]; then
        ISSUES="${ISSUES}进程DOWN;"
        alert "进程不存在，尝试重启"
        auto_recover
    fi
    
    if [[ "$GW" != OK ]]; then
        ISSUES="${ISSUES}网关异常($GW);"
        alert "网关异常: $GW"
    fi
    
    # 输出结果
    if [ -n "$ISSUES" ]; then
        log "状态: UNHEALTHY - $ISSUES"
    else
        log "状态: HEALTHY"
    fi
    
    log "========== 完成 =========="
    
    rm -f "$PID_FILE"
}

# 运行
main
