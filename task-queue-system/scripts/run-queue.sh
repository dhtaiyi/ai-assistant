#!/bin/bash
# 执行队列任务

TODO_DIR="/root/.openclaw/workspace/task-queue-system/todo"
EXECUTING_DIR="/root/.openclaw/workspace/task-queue-system/executing"
DONE_DIR="/root/.openclaw/workspace/task-queue-system/done"

echo "📋 执行任务队列..."

# 获取第一个任务
TASK_FILE=$(ls -t "$TODO_DIR"/*.json 2>/dev/null | head -1)

if [ -z "$TASK_FILE" ]; then
    echo "✅ 没有待执行任务"
    exit 0
fi

# 移动到执行中
mv "$TASK_FILE" "$EXECUTING_DIR/"

TASK_ID=$(basename "$TASK_FILE" .json)
echo "▶️ 执行任务: $TASK_ID"

# 读取任务内容
CONTENT=$(cat "$EXECUTING_DIR/$TASK_ID.json" | grep '"content"' | cut -d'"' -f4)
echo "内容: $CONTENT"

# TODO: 这里添加实际的执行逻辑

# 模拟执行完成
mv "$EXECUTING_DIR/$TASK_ID.json" "$DONE_DIR/"
echo "✅ 任务完成: $TASK_ID"
