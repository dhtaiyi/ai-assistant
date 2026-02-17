#!/bin/bash

# 安全编辑脚本 - 修改核心文件前自动备份
# 用法: safe-edit.sh <文件路径> <编辑命令>

FILE_PATH="$1"
if [ -z "$FILE_PATH" ]; then
    echo "❌ 用法: safe-edit.sh <文件路径>"
    exit 1
fi

if [ ! -f "$FILE_PATH" ]; then
    echo "❌ 文件不存在: $FILE_PATH"
    exit 1
fi

# 创建备份
BACKUP_DIR="/root/.openclaw/backups/pre-edit"
DATE=$(date +%Y%m%d)
TIME=$(date +%H%M%S)
BACKUP_FILE="$BACKUP_DIR/$(basename $FILE_PATH).$DATE.$TIME.bak"

mkdir -p "$BACKUP_DIR"
cp "$FILE_PATH" "$BACKUP_FILE"

echo "✅ 已备份: $BACKUP_FILE"
echo "📝 现在可以安全编辑: $FILE_PATH"

# 返回备份路径供后续使用
echo "$BACKUP_FILE"
