#!/bin/bash
# OpenClaw 全量同步脚本

echo "🔄 正在同步全部文件到GitHub..."

cd /home/dhtaiyi/.openclaw/workspace

# 添加所有重要文件（跳过pycache和敏感文件）
git add \
    *.md \
    *.json \
    AGENTS.md \
    IDENTITY.md \
    USER.md \
    SOUL.md \
    TOOLS.md \
    HEARTBEAT.md \
    MEMORY.md \
    openclaw-switch \
    skills/ \
    memory/ \
    ! -path "**/__pycache__/**" \
    ! -name "evomap_cookies.txt" \
    2>/dev/null

# 检查是否有新内容
if git status -s | grep -q "^.M\|^A "; then
    echo "📝 提交中..."
    git commit -m "sync: $(date '+%Y-%m-%d %H:%M') - 全量同步
    
- 更新配置和记忆
- 同步技能文件
- 记录每日进展"
    
    echo "🚀 推送到GitHub..."
    git push origin master
    
    echo "✅ 同步完成！"
else
    echo "ℹ️  没有新内容需要同步"
fi
