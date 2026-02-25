#!/bin/bash
# 检查任务队列状态

TODO_DIR="/root/.openclaw/workspace/task-queue-system/todo"
EXECUTING_DIR="/root/.openclaw/workspace/task-queue-system/executing"
DONE_DIR="/root/.openclaw/workspace/task-queue-system/done"
FAILED_DIR="/root/.openclaw/workspace/task-queue-system/failed"

echo "📊 任务队列状态"
echo "================"

TODO_COUNT=$(ls -1 "$TODO_DIR"/*.json 2>/dev/null | wc -l)
EXECUTING_COUNT=$(ls -1 "$EXECUTING_DIR"/*.json 2>/dev/null | wc -l)
DONE_COUNT=$(ls -1 "$DONE_DIR"/*.json 2>/dev/null | wc -l)
FAILED_COUNT=$(ls -1 "$FAILED_DIR"/*.json 2>/dev/null | wc -l)

echo ""
echo "待执行: $TODO_COUNT"
echo "执行中: $EXECUTING_COUNT"
echo "已完成: $DONE_COUNT"
echo "已失败: $FAILED_COUNT"
echo ""
echo "总计: $((TODO_COUNT + EXECUTING_COUNT + DONE_COUNT + FAILED_COUNT))"

if [ $TODO_COUNT -gt 10 ]; then
    echo ""
    echo "⚠️ 警告: 待执行任务过多，请及时处理!"
fi
