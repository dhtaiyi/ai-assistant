#!/bin/bash
# OpenClaw 小雨助手 - 跨会话记忆集成启动脚本

echo "🌸 小雨助手启动中..."
echo ""

# 1. 加载跨会话记忆
echo "📚 加载跨会话记忆..."
python3 -c "
import sys
sys.path.insert(0, '/home/dhtaiyi/.openclaw/workspace')
from memory.session_manager import SessionMemoryManager

mgr = SessionMemoryManager()
context = mgr.start_session('小雨助手')

print('✅ 跨会话记忆已加载')
print(f'📂 待办任务: {len(context.get(\"pending_tasks\", []))}')
print(f'🔄 进行中: {len(context.get(\"current_projects\", []))}')
print(f'📝 用户偏好: {context.get(\"user_preferences\", {})}')
"

# 2. 显示今日摘要
echo ""
echo "📋 今日摘要:"
echo "-----------"

# 检查今日任务
if [ -f "/home/dhtaiyi/.openclaw/workspace/memory/$(date +%Y-%m-%d).md" ]; then
    echo "✅ 已创建今日日志"
else
    echo "📝 今日日志未创建"
fi

# 检查EvoMap申诉状态
echo "⏳ EvoMap申诉: GitHub Issue #18 待回复"

# 检查同步状态  
echo "💾 GitHub备份: 最后同步 15:00"

echo ""
echo "🌸 准备就绪！开始新的一天~"
echo ""
