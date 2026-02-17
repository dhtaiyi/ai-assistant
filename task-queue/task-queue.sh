#!/bin/bash
# 任务队列管理系统

QUEUE_DIR="/root/.openclaw/workspace/task-queue"
LOG_FILE="$QUEUE_DIR/queue.log"
PROCESSED_FILE="$QUEUE_DIR/processed.log"
FAILED_FILE="$QUEUE_DIR/failed.log"

# 添加任务到队列
add_task() {
    local task="$1"
    local priority="${2:-normal}"
    echo "$(date '+%Y-%m-%d %H:%M:%S')|$priority|$task" >> "$QUEUE_DIR/queue.txt"
    echo "✅ 任务已添加: $task"
}

# 处理队列
process_queue() {
    if [ ! -f "$QUEUE_DIR/queue.txt" ]; then
        echo "📭 队列为空"
        return
    fi
    
    while IFS='|' read -r timestamp priority task; do
        if [ -n "$task" ]; then
            echo "🔄 处理任务: $task"
            if eval "$task" >> "$LOG_FILE" 2>&1; then
                echo "$(date '+%Y-%m-%d %H:%M:%S')|SUCCESS|$task" >> "$PROCESSED_FILE"
            else
                echo "$(date '+%Y-%m-%d %H:%M:%S')|FAILED|$task" >> "$FAILED_FILE"
            fi
        fi
    done < "$QUEUE_DIR/queue.txt"
    
    # 清空队列
    > "$QUEUE_DIR/queue.txt"
}

# 显示队列状态
status() {
    echo "📋 任务队列状态"
    echo "待处理: $(wc -l < "$QUEUE_DIR/queue.txt" 2>/dev/null || echo 0)"
    echo "已完成: $(wc -l < "$PROCESSED_FILE" 2>/dev/null || echo 0)"
    echo "失败: $(wc -l < "$FAILED_FILE" 2>/dev/null || echo 0)"
}

case "$1" in
    add)
        add_task "$2" "$3"
        ;;
    process)
        process_queue
        ;;
    status)
        status
        ;;
    *)
        echo "用法: $0 {add|process|status}"
        ;;
esac
