#!/bin/bash

# ===========================================
# OpenClaw 系统全面优化脚本
# ===========================================

LOG_DIR="/root/.openclaw/workspace/logs"
BACKUP_DIR="/root/.openclaw/backups"
MAX_LOG_DAYS=7
MAX_BACKUP_DAYS=30
DISK_WARNING=80
MEMORY_WARNING=80
LOAD_WARNING=5

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ===========================================
# 1. 性能优化
# ===========================================
optimize_performance() {
    log "🚀 优化系统性能..."
    
    # 清理内存缓存
    sync
    echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || warn "无法清理缓存（需要root权限）"
    
    # 优化Swappiness
    sysctl vm.swappiness=10 2>/dev/null || warn "无法修改swappiness"
    
    # 清理临时文件
    rm -rf /tmp/*.log /tmp/*.tmp 2>/dev/null
    
    log "✅ 性能优化完成"
}

# ===========================================
# 2. 日志管理
# ===========================================
manage_logs() {
    log "📋 清理旧日志..."
    
    # 清理日志文件
    find "$LOG_DIR" -name "*.log" -mtime +$MAX_LOG_DAYS -delete 2>/dev/null
    find /root/.openclaw/workspace -name "*.pyc" -delete 2>/dev/null
    find /root/.openclaw/workspace -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
    
    # 清理Docker（如果有）
    docker system prune -f 2>/dev/null || warn "Docker清理失败"
    
    log "✅ 日志清理完成（保留$MAX_LOG_DAYS天）"
}

# ===========================================
# 3. 监控告警
# ===========================================
monitor_health() {
    log "🔍 系统健康检查..."
    
    # 检查磁盘空间
    DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ $DISK_USAGE -gt $DISK_WARNING ]; then
        warn "⚠️ 磁盘使用率: ${DISK_USAGE}%"
    else
        log "✅ 磁盘使用率: ${DISK_USAGE}%"
    fi
    
    # 检查内存
    MEM_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100}')
    if [ $MEM_USAGE -gt $MEMORY_WARNING ]; then
        warn "⚠️ 内存使用率: ${MEM_USAGE}%"
    else
        log "✅ 内存使用率: ${MEM_USAGE}%"
    fi
    
    # 检查负载
    LOAD=$(uptime | awk -f <(echo '{print $NF}'))
    LOAD_INT=$(echo $LOAD | cut -d. -f1)
    if [ $LOAD_INT -gt $LOAD_WARNING ]; then
        warn "⚠️ 系统负载: $LOAD"
    else
        log "✅ 系统负载: $LOAD"
    fi
    
    # 检查OpenClaw进程
    if pgrep -f "openclaw" > /dev/null; then
        log "✅ OpenClaw 运行中"
    else
        warn "⚠️ OpenClaw 未运行"
    fi
}

# ===========================================
# 4. 备份管理
# ===========================================
manage_backups() {
    log "💾 清理旧备份..."
    
    # 清理旧备份
    find "$BACKUP_DIR" -mtime +$MAX_BACKUP_DAYS -delete 2>/dev/null
    
    # 保留最近的日志
    ls -lh "$LOG_DIR"/*.log 2>/dev/null | tail -5
    
    log "✅ 备份管理完成（保留$MAX_BACKUP_DAYS天）"
}

# ===========================================
# 5. 系统状态报告
# ===========================================
report_status() {
    log "📊 系统状态报告"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🖥️  系统信息"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    uptime
    echo ""
    echo "💾 内存使用"
    free -h | grep -E "^Mem|^Swap"
    echo ""
    echo "📦 磁盘使用"
    df -h | grep -E "^/dev/|Filesystem" | head -5
    echo ""
    echo "🌐 网络状态"
    curl -s https://api.ipify.org 2>/dev/null && echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# ===========================================
# 6. 自动更新检查
# ===========================================
check_updates() {
    log "🔄 检查更新..."
    
    # 检查Node.js更新
    CURRENT_NODE=$(node -v 2>/dev/null | cut -d'v' -f2)
    log "Node.js版本: $CURRENT_NODE"
    
    # 检查Python更新
    CURRENT_PYTHON=$(python3 --version 2>&1)
    log "Python版本: $CURRENT_PYTHON"
    
    log "✅ 更新检查完成"
}

# ===========================================
# 主程序
# ===========================================
main() {
    echo "╔════════════════════════════════════╗"
    echo "║   OpenClaw 系统优化器 v1.0        ║"
    echo "╚════════════════════════════════════╝"
    echo ""
    
    report_status
    echo ""
    optimize_performance
    echo ""
    manage_logs
    echo ""
    manage_backups
    echo ""
    monitor_health
    echo ""
    check_updates
    
    echo ""
    echo "╔════════════════════════════════════╗"
    echo "║   ✅ 系统优化完成！               ║"
    echo "╚════════════════════════════════════╝"
}

# 运行主程序
main
