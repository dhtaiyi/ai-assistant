#!/bin/bash
# 每日股票早报生成器
# 自动运行市场扫描+板块分析+连板追踪
# 输出到 ~/.openclaw/workspace/stock-learning/daily_brief_YYYYMMDD.md

DATE=$(date +%Y%m%d)
OUTPUT="$HOME/.openclaw/workspace/stock-learning/daily_brief_$(date +%Y%m%d).md"

echo "生成每日股票早报: $DATE"
echo "输出: $OUTPUT"

# 运行扫描
cd $HOME/.openclaw/workspace/scripts

# 生成报告
{
    echo "# 每日股票早报 $(date '+%Y-%m-%d')"
    echo ""
    echo "生成时间: $(date '+%H:%M:%S')"
    echo "---"
    echo ""
    echo "## 一、市场全景"
    python3 market_scanner.py 2>/dev/null | grep -v "^$"
    echo ""
    echo "## 二、板块热点"
    python3 sector_scanner.py 2>/dev/null | grep -v "^$"
    echo ""
    echo "## 三、连板追踪"
    python3 lianban_tracker.py 2>/dev/null | grep -v "^$"
    echo ""
    echo "---"
    echo "*由小小雨自动生成*"
} > "$OUTPUT"

echo "早报已保存到: $OUTPUT"
cat "$OUTPUT"
