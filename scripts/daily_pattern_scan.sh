#!/bin/bash
# 每日图形扫描 - 收盘后自动运行
# 输出报告到 stock-patterns/daily_report/

DATE=$(date +%Y%m%d)
OUTDIR="/home/dhtaiyi/.openclaw/workspace/stock-patterns/daily_report"
LOG="/tmp/daily_pattern_scan.log"

mkdir -p "$OUTDIR"

echo "[$(date)] 开始每日图形扫描" >> "$LOG"
python3 /home/dhtaiyi/.openclaw/workspace/scripts/daily_pattern_scan.py > "$OUTDIR/${DATE}.md" 2>&1
echo "[$(date)] 完成，报告: $OUTDIR/${DATE}.md" >> "$LOG"
