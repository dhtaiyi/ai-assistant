#!/bin/bash
# 每日连板股票记录脚本
# 每天收盘后自动记录连板梯队数据

OUTPUT_DIR="/home/dhtaiyi/.openclaw/workspace/stock-data/daily-boards"
mkdir -p "$OUTPUT_DIR"

TODAY=$(date +%Y%m%d)
TODAY_DISPLAY=$(date +"%Y年%m月%d日")
LOG_FILE="$OUTPUT_DIR/${TODAY}.md"

echo "=== 获取今日连板数据 ==="

# 使用MX搜索获取连板信息
export MX_APIKEY="mkt__bGBVbyVyWGlJi1PS8r_gJLSNmmd6-1gIDweArbPs6I"
RESULT=$(python3 ~/.openclaw/skills/mx-search/mx_search.py "A股连板梯队涨停股" /home/dhtaiyi/.openclaw/workspace/mx_data/output/ 2>&1)

# 获取新浪涨停股数据
ZHUANGTING=$(curl -s -H "Referer: https://finance.sina.com.cn" "https://hq.sinajs.cn/list=s_sh000001" 2>/dev/null)

# 生成报告
cat > "$LOG_FILE" << REPORT
# 📊 每日连板股票记录 - ${TODAY_DISPLAY}

## 📈 今日市场概况

（由系统自动记录）

## 🔥 涨停板分析

\`\`\`
${RESULT}
\`\`\`

## 📝 记录时间

生成时间: $(date +"%Y-%m-%d %H:%M:%S")

---
*由小小雨自动记录 🌸*
REPORT

echo "✅ 今日记录已保存: $LOG_FILE"

# 同时追加到汇总文件
SUMMARY_FILE="$OUTPUT_DIR/summary.md"
if [ ! -f "$SUMMARY_FILE" ]; then
    echo "# 📊 连板股票月度汇总" > "$SUMMARY_FILE"
fi

echo "" >> "$SUMMARY_FILE"
echo "## ${TODAY_DISPLAY}" >> "$SUMMARY_FILE"
echo '- ['"${TODAY}"']('"$TODAY".md') 记录完成' >> "$SUMMARY_FILE"

echo "✅ 汇总已更新: $SUMMARY_FILE"
