#!/bin/bash

# ===========================================
# OpenClaw 高级系统监控脚本
# ===========================================

# 配置
TELEGRAM_BOT_TOKEN=""
TELEGRAM_CHAT_ID=""
EMAIL_ALERT=""
SLACK_WEBHOOK=""

# 告警阈值
DISK_WARNING=80
DISK_CRITICAL=90
MEMORY_WARNING=80
MEMORY_CRITICAL=90
CPU_WARNING=70
CPU_CRITICAL=90
LOAD_WARNING=3
LOAD_CRITICAL=5

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

send_alert() {
    local title="$1"
    local message="$2"
    
    # Telegram告警
    if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
        curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
            -d "chat_id=$TELEGRAM_CHAT_ID" \
            -d "text=🚨 $title: $message" \
            -d "parse_mode=HTML" > /dev/null
    fi
    
    # Slack告警
    if [ -n "$SLACK_WEBHOOK" ]; then
        curl -s -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"🚨 $title: $message\"}" \
            "$SLACK_WEBHOOK" > /dev/null
    fi
    
    # 邮件告警
    if [ -n "$EMAIL_ALERT" ]; then
        echo "$message" | mail -s "🚨 $title" "$EMAIL_ALERT" 2>/dev/null
    fi
    
    log_warn "告警已发送: $title"
}

check_disk() {
    log_info "检查磁盘..."
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    
    if [ $disk_usage -gt $DISK_CRITICAL ]; then
        send_alert "磁盘严重不足" "使用率: ${disk_usage}%"
        return 1
    elif [ $disk_usage -gt $DISK_WARNING ]; then
        send_alert "磁盘空间警告" "使用率: ${disk_usage}%"
        log_warn "⚠️ 磁盘使用率: ${disk_usage}%"
    else
        log_info "✅ 磁盘正常: ${disk_usage}%"
    fi
}

check_memory() {
    log_info "检查内存..."
    local mem_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100}')
    
    if [ $mem_usage -gt $MEMORY_CRITICAL ]; then
        send_alert "内存严重不足" "使用率: ${mem_usage}%"
        return 1
    elif [ $mem_usage -gt $MEMORY_WARNING ]; then
        send_alert "内存警告" "使用率: ${mem_usage}%"
        log_warn "⚠️ 内存使用率: ${mem_usage}%"
    else
        log_info "✅ 内存正常: ${mem_usage}%"
    fi
}

check_cpu() {
    log_info "检查CPU..."
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
    local cpu_int=$(echo $cpu_usage | cut -d. -f1)
    
    if [ $cpu_int -gt $CPU_CRITICAL ]; then
        send_alert "CPU过载" "使用率: ${cpu_usage}%"
        return 1
    elif [ $cpu_int -gt $CPU_WARNING ]; then
        send_alert "CPU警告" "使用率: ${cpu_usage}%"
        log_warn "⚠️ CPU使用率: ${cpu_usage}%"
    else
        log_info "✅ CPU正常: ${cpu_usage}%"
    fi
}

check_load() {
    log_info "检查系统负载..."
    local load=$(uptime | awk -f <(echo '{print $NF}'))
    local load_int=$(echo $load | cut -d. -f1)
    
    if [ $load_int -gt $LOAD_CRITICAL ]; then
        send_alert "系统负载过高" "负载: $load"
        return 1
    elif [ $load_int -gt $LOAD_WARNING ]; then
        send_alert "系统负载警告" "负载: $load"
        log_warn "⚠️ 系统负载: $load"
    else
        log_info "✅ 负载正常: $load"
    fi
}

check_services() {
    log_info "检查服务状态..."
    
    # 检查OpenClaw
    if pgrep -f "openclaw" > /dev/null; then
        log_info "✅ OpenClaw 运行中"
    else
        send_alert "OpenClaw宕机" "服务未运行"
        log_error "❌ OpenClaw 未运行"
    fi
    
    # 检查关键端口
    local ports=(18789 22 80 443)
    for port in "${ports[@]}"; do
        if netstat -tlnp 2>/dev/null | grep -q ":$port "; then
            log_info "✅ 端口 $port 正常"
        else
            log_warn "⚠️ 端口 $port 未监听"
        fi
    done
}

check_network() {
    log_info "检查网络..."
    
    # 测试外网连接
    if timeout 5 curl -s -I https://www.baidu.com > /dev/null 2>&1; then
        local ip=$(curl -s https://api.ipify.org 2>/dev/null)
        log_info "✅ 网络正常 (IP: $ip)"
    else
        send_alert "网络异常" "无法访问外网"
        log_error "❌ 网络连接失败"
    fi
}

generate_report() {
    echo ""
    echo "╔════════════════════════════════════╗"
    echo "║   📊 OpenClaw 系统监控报告        ║"
    echo "╚════════════════════════════════════╝"
    echo ""
    echo "🕐 时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    echo "🖥️  系统信息"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    uptime
    echo ""
    echo "💾 资源使用"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    free -h | grep -E "^Mem|^Swap"
    echo ""
    echo "📦 磁盘空间"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    df -h | grep -E "^/dev/|Filesystem" | head -3
    echo ""
    echo "🌐 网络"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    curl -s https://api.ipify.org && echo ""
    echo ""
    echo "╔════════════════════════════════════╗"
    echo "║   ✅ 监控完成                      ║"
    echo "╚════════════════════════════════════╝"
}

main() {
    echo "╔════════════════════════════════════╗"
    echo "║   🔍 OpenClaw 系统监控 v1.0       ║"
    echo "╚════════════════════════════════════╝"
    echo ""
    
    generate_report
    echo ""
    
    check_disk
    echo ""
    check_memory
    echo ""
    check_cpu
    echo ""
    check_load
    echo ""
    check_services
    echo ""
    check_network
    
    echo ""
    echo "╔════════════════════════════════════╗"
    echo "║   ✅ 监控检查完成                  ║"
    echo "╚════════════════════════════════════╝"
}

main
