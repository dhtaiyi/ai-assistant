#!/bin/bash
# Git 自动备份脚本 - 每小时执行

REPO_DIR="$HOME/.openclaw/workspace"
LOG_FILE="/tmp/git_backup.log"

cd "$REPO_DIR" || exit 1

# 先更新并添加 submodule
git submodule update --init --recursive 2>> "$LOG_FILE"
git add . 2>> "$LOG_FILE"

# 检查是否有更改
if git diff --staged --quiet; then
    echo "$(date) - No changes to commit" >> "$LOG_FILE"
    exit 0
fi

# 提交更改
TIMESTAMP=$(date '+%Y-%m-%d %H:%M')
git commit -m "auto backup $TIMESTAMP" 2>> "$LOG_FILE"

# 推送到 GitHub
git push origin master 2>> "$LOG_FILE"

echo "$(date) - Backup completed" >> "$LOG_FILE"
