#!/bin/bash

# 每日自动总结脚本
# 功能：自动总结当天的对话，提取偏好、习惯、目标等

SUMMARY_FILE="/root/.openclaw/workspace/memory/$(date +%Y-%m-%d).md"
LOG_FILE="/root/.openclaw/workspace/logs/daily-summary.log"

echo "$(date '+%Y-%m-%d %H:%M:%S') - 开始生成每日总结" >> "$LOG_FILE"

# 检查今日是否有对话记录
TODAY_DIR="/root/.openclaw/agents/main/sessions/$(date +%Y%m%d)*"
TEMP_COUNT=$(ls -d $TODAY_DIR 2>/dev/null | wc -l)

if [ "$TEMP_COUNT" -eq 0 ]; then
    echo "今日无对话记录" >> "$LOG_FILE"
    exit 0
fi

# 提取今日对话主题（简化版本）
TOPICS=""
KEYWORDS=""

# 检查是否有关键词出现
if grep -r "股票\|交易\|分析" $TODAY_DIR 2>/dev/null | head -1 > /dev/null; then
    TOPICS="${TOPICS}金融分析 "
fi

if grep -r "搜索\|查询\|查找" $TODAY_DIR 2>/dev/null | head -1 > /dev/null; then
    TOPICS="${TOPICS}信息检索 "
fi

# 生成简单总结
cat > "$SUMMARY_FILE" << SUMMARY
# $(date +%Y-%m-%d) - 每日总结

## 日期
$(date '+%Y-%m-%d %H:%M UTC')

## 对话统计
- 对话会话数: $TEMP_COUNT

## 主题
$TOPICS

## 系统变化
$(tail -20 "$LOG_FILE" 2>/dev/null | grep -v "^\[" | head -3 || echo "无重大变化")

## 备注
SUMMARY

echo "$(date '+%Y-%m-%d %H:%M:%S') - 总结已生成: $SUMMARY_FILE" >> "$LOG_FILE"
echo "✅ 每日总结已生成: $SUMMARY_FILE"
