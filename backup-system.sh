#!/bin/bash

# OpenClaw 备份脚本
# 功能：备份所有核心数据和配置

BACKUP_DIR="/root/.openclaw/backups"
DATE=$(date +%Y%m%d)
TIME=$(date +%H%M%S)
BACKUP_PATH="$BACKUP_DIR/$DATE/$TIME"

# 创建目录
mkdir -p "$BACKUP_PATH"

# 备份清单
echo "🔄 开始备份..."

# 1. 核心配置
cp /root/.openclaw/openclaw.json "$BACKUP_PATH/openclaw.json" 2>/dev/null

# 2. 工作空间数据
cp -r /root/.openclaw/workspace/MEMORY.md "$BACKUP_PATH/" 2>/dev/null
cp -r /root/.openclaw/workspace/AGENTS.md "$BACKUP_PATH/" 2>/dev/null
cp -r /root/.openclaw/workspace/SOUL.md "$BACKUP_PATH/" 2>/dev/null
cp -r /root/.openclaw/workspace/TOOLS.md "$BACKUP_PATH/" 2>/dev/null
cp -r /root/.openclaw/workspace/USER.md "$BACKUP_PATH/" 2>/dev/null
cp -r /root/.openclaw/workspace/IDENTITY.md "$BACKUP_PATH/" 2>/dev/null

# 3. 记忆数据
cp -r /root/.openclaw/workspace/memory "$BACKUP_PATH/" 2>/dev/null

# 4. 技能配置
cp -r /root/.openclaw/workspace/skills "$BACKUP_PATH/" 2>/dev/null

# 5. 系统服务配置
cp /etc/systemd/system/openclaw.service "$BACKUP_PATH/" 2>/dev/null

# 生成备份清单
cat > "$BACKUP_PATH/manifest.txt" << MANIFEST
Backup Date: $(date)
Backup Path: $BACKUP_PATH
Files:
$(ls -la "$BACKUP_PATH" 2>/dev/null | grep -v "^total\|^d\|manifest")
MANIFEST

# 压缩备份（可选）
# tar -czf "$BACKUP_PATH.tar.gz" -C "$BACKUP_DIR/$DATE" "$TIME" && rm -rf "$BACKUP_DIR/$DATE/$TIME"

# 输出结果
echo "✅ 备份完成: $BACKUP_PATH"
echo "📁 备份大小: $(du -sh "$BACKUP_PATH" 2>/dev/null | cut -f1)"
echo "📊 备份数量: $(find "$BACKUP_PATH" -type f 2>/dev/null | wc -l) 个文件"

# 清理旧备份（保留30天）
find "$BACKUP_DIR" -type d -mtime +30 -exec rm -rf {} \; 2>/dev/null
echo "🧹 已清理30天前的旧备份"
