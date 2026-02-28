#!/bin/bash
# ClawHub Skill 定时同步脚本
# 添加到 crontab: 0 2 * * * /root/.openclaw/workspace/scripts/auto-sync-clawhub.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/tmp/clawhub-sync-$(date +%Y%m%d).log"

echo "🔄 开始同步 ClawHub Skill ($(date))" | tee -a "$LOG_FILE"

# 执行同步
python3 "$SCRIPT_DIR/sync-clawhub-skills.py" 2>&1 | tee -a "$LOG_FILE"

# 检查新 skill
SYNC_INDEX="$SCRIPT_DIR/../memory/clawhub-sync-index.json"
if [ -f "$SYNC_INDEX" ]; then
    NEW_COUNT=$(python3 -c "import json; d=json.load(open('$SYNC_INDEX')); print(d['not_installed'])")
    echo "📊 发现 $NEW_COUNT 个未安装的 skill" | tee -a "$LOG_FILE"
fi

echo "✅ 同步完成 ($(date))" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
