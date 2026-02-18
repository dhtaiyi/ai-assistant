#!/bin/bash
# 添加任务到队列

TASK_FILE="/root/.openclaw/workspace/task-queue-system/todo/queue.json"

if [ -z "$1" ]; then
    echo "用法: add-task.sh <任务内容>"
    echo "示例: add-task.sh '创建小红书笔记'"
    exit 1
fi

# 生成任务ID
TASK_ID=$(date +%Y%m%d%H%M%S)

# 创建任务JSON
TASK_JSON=$(cat << EOF
{
    "id": "$TASK_ID",
    "content": "$1",
    "priority": "${2:-3}",
    "created_at": "$(date -Iseconds)",
    "status": "pending"
}
EOF
)

# 添加到队列
echo "$TASK_JSON" >> "$TASK_FILE"

echo "✅ 任务已添加: $TASK_ID"
echo "内容: $1"
echo "优先级: ${2:-3}"
