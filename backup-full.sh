#!/bin/bash

BACKUP_DIR="/root/.openclaw/backups"
DATE=$(date +%Y%m%d)
TIME=$(date +%H%M%S)
BACKUP_NAME="full-$DATE-$TIME"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"
BACKUP_FILE="$BACKUP_DIR/$BACKUP_NAME.tar.gz"

echo "========================================"
echo "    💾 OpenClaw 完整备份"
echo "    $DATE $TIME"
echo "========================================"

mkdir -p "$BACKUP_PATH"

echo ""
echo "📦 开始备份..."

# 1. 核心配置
cp /root/.openclaw/openclaw.json "$BACKUP_PATH/"

# 2. 工作空间核心文件
cp /root/.openclaw/workspace/*.md "$BACKUP_PATH/" 2>/dev/null
cp /root/.openclaw/workspace/*.json "$BACKUP_PATH/" 2>/dev/null

# 3. 记忆数据
cp -r /root/.openclaw/workspace/memory "$BACKUP_PATH/" 2>/dev/null

# 4. 技能配置
cp -r /root/.openclaw/workspace/skills "$BACKUP_PATH/" 2>/dev/null

# 5. 笔记
cp -r /root/.openclaw/workspace/notes "$BACKUP_PATH/" 2>/dev/null

# 6. 脚本
cp -r /root/.openclaw/workspace/scripts "$BACKUP_PATH/" 2>/dev/null

# 7. 备份记录
cp -r /root/.openclaw/workspace/backup "$BACKUP_PATH/" 2>/dev/null

# 8. 数据
cp -r /root/.openclaw/workspace/data "$BACKUP_PATH/" 2>/dev/null

# 9. 会话记录
mkdir -p "$BACKUP_PATH/sessions"
cp /root/.openclaw/agents/main/sessions/*.jsonl "$BACKUP_PATH/sessions/" 2>/dev/null
cp /root/.openclaw/agents/main/sessions/sessions.json "$BACKUP_PATH/sessions/" 2>/dev/null

# 10. 代理配置
mkdir -p "$BACKUP_PATH/agents"
cp -r /root/.openclaw/agents/main "$BACKUP_PATH/agents/" 2>/dev/null
cp -r /root/.openclaw/agents/xiaoyu "$BACKUP_PATH/agents/" 2>/dev/null
cp -r /root/.openclaw/agents/shishi "$BACKUP_PATH/agents/" 2>/dev/null

# 11. 日志文件
mkdir -p "$BACKUP_PATH/logs"
cp /root/.openclaw/logs/*.log "$BACKUP_PATH/logs/" 2>/dev/null
cp /root/.openclaw/workspace/logs/*.log "$BACKUP_PATH/logs/" 2>/dev/null

# 12. OpenClaw 配置
cp -r /root/.openclaw/.claw* "$BACKUP_PATH/" 2>/dev/null

# 13. 清单
cat > "$BACKUP_PATH/manifest.txt" << EOF
========================================
OpenClaw 完整备份清单
========================================
备份时间: $DATE $TIME
文件数: $(find "$BACKUP_PATH" -type f 2>/dev/null | wc -l)
EOF

# 14. 压缩
echo ""
echo "📦 压缩备份..."
cd "$BACKUP_DIR"
tar -czf "$BACKUP_NAME.tar.gz" "$BACKUP_NAME" 2>&1
rm -rf "$BACKUP_PATH"

BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
FILE_COUNT=$(tar -tzf "$BACKUP_FILE" | wc -l)

echo ""
echo "========================================"
echo "    ✅ 完整备份完成"
echo "========================================"
echo ""
echo "📦 文件: $BACKUP_FILE"
echo "📊 大小: $BACKUP_SIZE"
echo "📁 数量: $FILE_COUNT"
echo ""
echo "🧹 清理旧备份 (30天)..."
find "$BACKUP_DIR" -name "full-*.tar.gz" -mtime +30 -delete 2>/dev/null
echo "✅ 完成！"
