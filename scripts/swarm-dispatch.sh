#!/bin/bash
# Swarm 任务分解器 - 多 Agent 并行执行
# 使用：./swarm-dispatch.sh "任务描述"

TASK="$1"

echo "🌸 Swarm 任务分解器启动..."
echo "任务：$TASK"
echo ""

# 任务类型判断
if [[ "$TASK" =~ (分析 | 研究 | 调研 | 报告|data|research|analyze) ]]; then
    TYPE="research"
    AGENT="诗诗"
    echo "📊 任务类型：研究型 → 分配给诗诗"
elif [[ "$TASK" =~ (代码 | 开发 | 实现 | 自动化|code|dev|implement|automate) ]]; then
    TYPE="development"
    AGENT="小 u"
    echo "💻 任务类型：开发型 → 分配给小 u"
elif [[ "$TASK" =~ (对比 | 方案 | 决策|compare|option|decision) ]]; then
    TYPE="analysis"
    AGENT="诗诗"
    echo "📈 任务类型：分析型 → 分配给诗诗"
else
    TYPE="generic"
    AGENT="小雨"
    echo "💬 任务类型：通用型 → 小雨处理"
fi

echo ""
echo "=== 任务分发 ==="
echo "类型：$TYPE"
echo "代理：$AGENT"
echo "时间：$(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 记录到日志
echo "- [$(date '+%Y-%m-%d %H:%M:%S')] [$TYPE] $TASK → $AGENT" >> /root/.openclaw/workspace/memory/swarm-task-log.md

echo "✅ 任务已分发"
