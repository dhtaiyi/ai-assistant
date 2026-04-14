#!/bin/bash
# 每日趋势跟踪 - 收盘后自动运行
DATE=$(date +%Y%m%d)
OUTDIR="/home/dhtaiyi/.openclaw/workspace/stock-patterns/daily_report"
LOG="/tmp/daily_trend_scan.log"

mkdir -p "$OUTDIR"

echo "[$(date)] 开始趋势跟踪" >> "$LOG"
python3 /home/dhtaiyi/.openclaw/workspace/scripts/daily_trend_tracker.py "$DATE" > "$OUTDIR/${DATE}_trend.md" 2>&1
echo "[$(date)] 完成" >> "$LOG"
