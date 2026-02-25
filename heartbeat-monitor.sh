#!/bin/bash

# 心跳监控脚本 - 检测 openclaw 进程状态
# 作者: OpenClaw
# 用途: 每5分钟检测 openclaw 进程，自动重启宕机进程

LOG_FILE="/root/.openclaw/workspace/logs/heartbeat.log"
SERVICE_NAME="openclaw"

# 获取当前时间戳
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# 写入日志函数
log_message() {
    echo "[$TIMESTAMP] $1" >> "$LOG_FILE"
}

# 检测进程是否存在 (使用 -f 匹配完整命令行)
check_process() {
    if pgrep -f "openclaw-gateway" > /dev/null 2>&1; then
        return 0  # 进程存活
    else
        return 1  # 进程不存在
    fi
}

# 主逻辑
if check_process; then
    STATUS="RUNNING"
    log_message "STATUS: $STATUS - openclaw 进程运行正常"
    echo "[$TIMESTAMP] [RUNNING] openclaw 进程运行正常"
else
    STATUS="DOWN"
    log_message "STATUS: $STATUS - openclaw 进程未运行，尝试重启..."
    echo "[$TIMESTAMP] [DOWN] openclaw 进程未运行，尝试重启..."
    
    # 尝试重启服务
    if systemctl restart "$SERVICE_NAME"; then
        log_message "ACTION: systemctl restart $SERVICE_NAME - 成功"
        echo "[$TIMESTAMP] [RESTARTED] openclaw 服务已重启成功"
        
        # 等待2秒后再次检查
        sleep 2
        if check_process; then
            log_message "VERIFICATION: 重启后进程状态正常"
            echo "[$TIMESTAMP] [VERIFIED] 重启后进程验证通过"
        else
            log_message "ERROR: 重启后进程仍未运行，请手动检查"
            echo "[$TIMESTAMP] [ERROR] 重启后进程验证失败"
        fi
    else
        log_message "ERROR: systemctl restart $SERVICE_NAME - 失败"
        echo "[$TIMESTAMP] [ERROR] openclaw 服务重启失败，请检查 systemctl 状态"
    fi
fi

# 输出控制台日志
echo "[$TIMESTAMP] 检测完成"
