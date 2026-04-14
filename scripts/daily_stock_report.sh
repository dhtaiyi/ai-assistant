#!/bin/bash
# 每日股票复盘自动生成脚本
# 执行时间: 每天 17:00 (股市收盘后)

cd /home/dhtaiyi/.openclaw/workspace

# 生成当日复盘报告
REPORT=$(python3 scripts/stock_analyzer.py 2>&1)

# 保存报告
DATE=$(date +%Y%m%d)
echo "$REPORT" > /home/dhtaiyi/.openclaw/workspace/stock-analysis/report_text_${DATE}.txt

# 输出报告内容供发送
echo "$REPORT"
