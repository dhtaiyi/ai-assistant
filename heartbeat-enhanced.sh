#!/bin/bash

# 增强版心跳监控脚本 - 检测 OpenClaw 完整状态
# 检测项目：进程、WeCom API、消息通道、网关状态
# 频率：每5分钟

set -e

# 配置
LOG_DIR="/root/.openclaw/workspace/logs"
LOG_FILE="$LOG_DIR/heartbeat-enhanced.log"
ALERT_LOG="$LOG_DIR/heartbeat-alerts.log"
PID_FILE="/root/.openclaw/workspace/logs/heartbeat-enhanced.pid"
LAST_MSG_FILE="/root/.openclaw/workspace/logs/last-message-time.txt"

# 告警配置（设置你的联系方式）
ALERT_ENABLED=true
ALERT_WEBHOOK=""  # 例如：https://your-webhook-url.com
ALERT_EMAIL=""    # 例如：admin@example.com

# 时间戳
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
DATE=$(date "+%Y-%m-%d")

# 日志函数
log() {
    echo "[$TIMESTAMP] $1" >> "$LOG_FILE"
    echo "[$TIMESTAMP] $1"
}

alert() {
    local msg="[$TIMESTAMP] ALERT: $1"
    echo "$msg" >> "$LOG_FILE"
    echo "$msg" >> "$ALERT_LOG"
    
    if [ "$ALERT_ENABLED" = true ]; then
        # Webhook 告警（如果配置了）
        if [ -n "$ALERT_WEBHOOK" ]; then
            curl -s -X POST "$ALERT_WEBHOOK" \
                -H "Content-Type: application/json" \
                -d "{\"text\": \"OpenClaw Heartbeat Alert: $1\"}" \
                >> "$LOG_FILE" 2>&1 || true
        fi
        
        # 这里可以添加邮件、短信等告警方式
    fi
}

# 检查是否正在运行（防止重复执行）
check_pid() {
    if [ -f "$PID_FILE" ]; then
        OLD_PID=$(cat "$PID_FILE")
        if kill -0 "$OLD_PID" 2>/dev/null; then
            log "WARN: 另一个实例正在运行 (PID: $OLD_PID)，退出"
            exit 1
        fi
        log "WARN: 发现残留 PID 文件，清除"
        rm -f "$PID_FILE"
    fi
    echo $$ > "$PID_FILE"
}

# 1. 检查进程状态
check_process() {
    local pid=$(pgrep -f "openclaw-gateway" 2>/dev/null | head -1)
    if [ -n "$pid" ]; then
        echo "RUNNING:$pid"
        return 0
    else
        echo "DOWN"
        return 1
    fi
}

# 2. 检查网关可达性
check_gateway() {
    local response=$(curl -s -o /dev/null -w "%{http_code}" \
        --connect-timeout 5 \
        --max-time 10 \
        "http://127.0.0.1:18789/health" 2>/dev/null)
    
    if [ "$response" = "200" ] || [ "$response" = "000" ]; then
        # 000 通常表示连接成功但服务返回非标准响应
        echo "REACHABLE"
        return 0
    else
        echo "UNREACHABLE:$response"
        return 1
    fi
}

# 3. 检查 WeCom 通道状态
check_wecom_status() {
    local status=$(openclaw channel status wecom 2>/dev/null | grep -o "OK\|ERROR\|SETUP" | head -1)
    if [ "$status" = "OK" ]; then
        echo "OK"
        return 0
    else
        echo "$status"
        return 1
    fi
}

# 4. 检查最近消息时间（关键：检测是否断联）
check_last_message() {
    local last_time=""
    
    # 从日志获取最近消息时间
    if [ -f "$LOG_FILE" ]; then
        last_time=$(grep -E "inbound|outbound" "$LOG_FILE" 2>/dev/null | tail -1 | grep -oP "\d{4}-\d{2}-\d{2} \d{2}:\d{2}" || echo "")
    fi
    
    # 检查 OpenClaw 主日志
    if [ -z "$last_time" ] && [ -f "/tmp/openclaw/openclaw-$DATE.log" ]; then
        last_time=$(grep -E "inbound.*wecom" "/tmp/openclaw/openclaw-$DATE.log" 2>/dev/null | tail -1 | grep -oP "\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}" || echo "")
    fi
    
    # 如果有最近消息记录
    if [ -n "$last_time" ]; then
        echo "$last_time"
        return 0
    else
        echo "UNKNOWN"
        return 1
    fi
}

# 5. 测试消息发送（可选：发送测试消息到监控群）
test_message_send() {
    # 仅在检测到异常时执行
    local test_result=$(curl -s -o /dev/null -w "%{http_code}" \
        --connect-timeout 5 \
        --max-time 10 \
        "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=wwf684d252386fc0b6" 2>/dev/null)
    
    if [ "$test_result" = "200" ]; then
        echo "SENDABLE"
        return 0
    else
        echo "UNSENDABLE:$test_result"
        return 1
    fi
}

# 自动恢复
auto_recover() {
    log "INFO: 尝试自动恢复..."
    
    # 1. 重启网关
    log "ACTION: 重启 openclaw-gateway..."
    pkill -f "openclaw-gateway" 2>/dev/null || true
    sleep 2
    
    # 重新启动
    cd /root/.openclaw/workspace
    nohup npx openclaw gateway start >> "$LOG_FILE" 2>&1 &
    sleep 5
    
    # 2. 验证恢复
    local new_status=$(check_process)
    if [[ "$new_status" == RUNNING:* ]]; then
        log "SUCCESS: 自动恢复成功"
        alert "OpenClaw 自动恢复成功"
        return 0
    else
        log "FAIL: 自动恢复失败，需要手动干预"
        alert "OpenClaw 自动恢复失败，请检查系统"
        return 1
    fi
}

# 主检测流程
main() {
    check_pid
    
    log "========== 开始增强心跳检测 =========="
    
    # 状态收集
    PROCESS_STATUS=$(check_process)
    GATEWAY_STATUS=$(check_gateway)
    WECOM_STATUS=$(check_wecom_status)
    LAST_MSG=$(check_last_message)
    
    # 记录状态
    log "PROCESS: $PROCESS_STATUS"
    log "GATEWAY: $GATEWAY_STATUS"
    log "WECOM: $WECOM_STATUS"
    log "LAST_MESSAGE: $LAST_MSG"
    
    # 判断健康状态
    HEALTHY=true
    ISSUES=""
    
    if [[ "$PROCESS_STATUS" != RUNNING:* ]]; then
        HEALTHY=false
        ISSUES="$ISSUES PROCESS_DOWN;"
        alert "进程不存在，尝试恢复"
        auto_recover
    fi
    
    if [[ "$GATEWAY_STATUS" != REACHABLE ]]; then
        HEALTHY=false
        ISSUES="$ISSUES GATEWAY_UNREACHABLE;"
        alert "网关不可达: $GATEWAY_STATUS"
    fi
    
    if [[ "$WECOM_STATUS" != "OK" ]]; then
        HEALTHY=false
        ISSUES="$ISSUES WECOM_ERROR($WECOM_STATUS);"
        alert "WeCom 通道异常: $WECOM_STATUS"
    fi
    
    # 检查消息新鲜度（超过30分钟视为异常）
    if [ "$LAST_MSG" != "UNKNOWN" ] && [ -n "$LAST_MSG" ]; then
        local msg_ts=$(date -d "$LAST_MSG" +%s 2>/dev/null || echo 0)
        local now_ts=$(date +%s)
        local diff=$((now_ts - msg_ts))
        
        if [ $diff -gt 1800 ]; then  # 30分钟
            HEALTHY=false
            ISSUES="$ISSUES MESSAGE_STALE(${diff}s);"
            alert "消息通道可能断联，最后消息: ${diff}秒前"
        fi
    fi
    
    # 输出最终结果
    if [ "$HEALTHY" = true ]; then
        log "STATUS: HEALTHY - 所有检测通过"
    else
        log "STATUS: UNHEALTHY - 问题: $ISSUES"
    fi
    
    log "========== 检测完成 =========="
    
    # 清理 PID
    rm -f "$PID_FILE"
}

# 执行
main "$@"
