#!/bin/bash
# ============================================================
# 晚盘综合分析链路 - 收盘后一键运行
# 整合：涨停采集 → 候选池更新 → 图形扫描 → 智能评分 → 买点分析
# ============================================================
LOG="/tmp/evening_pipeline.log"
DATE=$(date +%Y%m%d)

echo "[$(date)] === 晚盘综合分析开始 ===" >> $LOG

SCRIPT_DIR="/home/dhtaiyi/.openclaw/workspace/scripts"

# Step 1: 采集涨停历史
echo "Step 1: 涨停历史采集..." >> $LOG
bash ${SCRIPT_DIR}/collect_limitup.sh >> $LOG 2>&1

# Step 2: 图形扫描
echo "Step 2: 图形扫描..." >> $LOG
python3 ${SCRIPT_DIR}/daily_pattern_scan.py >> ${SCRIPT_DIR}/../stock-patterns/daily_report/${DATE}.md 2>&1

# Step 3: 候选池更新
echo "Step 3: 候选池更新..." >> $LOG
bash ${SCRIPT_DIR}/daily_candidate_update.sh >> $LOG 2>&1

# Step 4: 智能评分
echo "Step 4: 智能评分..." >> $LOG
python3 ${SCRIPT_DIR}/smart_scoring.py $DATE >> $LOG 2>&1

# Step 5: 买点分析
echo "Step 5: 买点分析..." >> $LOG
python3 ${SCRIPT_DIR}/buy_point_analyzer.py $DATE >> ${SCRIPT_DIR}/../stock-patterns/daily_report/buy_point_${DATE}.md 2>&1

# Step 6: 市场情绪回顾
echo "Step 6: 市场情绪..." >> $LOG
python3 ${SCRIPT_DIR}/market_sentiment.py >> $LOG 2>&1

echo "[$(date)] === 晚盘综合分析完成 ===" >> $LOG

# 生成最终报告摘要
python3 - <<'PYEOF' >> $LOG 2>&1
import json
from datetime import datetime

date_str = "$DATE"

# 读取评分结果
try:
    with open(f'/home/dhtaiyi/.openclaw/workspace/stock-patterns/candidates/scored_{date_str}.json') as f:
        scored = json.load(f)
    print(f"\n{'='*60}")
    print(f"📊 今日综合评分 TOP5")
    print(f"{'='*60}")
    for i, s in enumerate(scored[:5], 1):
        print(f"{i}. **{s['name']}**({s['code']}) 评分:{s['total_score']}")
        print(f"   涨幅{s['pct']:+.1f}% | 3日+{s['gain3d']:+.1f}% | 振幅{s['amplitude']:.1f}%")
except:
    pass

# 读取买点分析
try:
    with open(f'/home/dhtaiyi/.openclaw/workspace/stock-patterns/daily_report/buy_point_{date_str}.md') as f:
        content = f.read()
    buy_points = [l for l in content.split('\n') if '买点' in l or '🚨' in l]
    if buy_points:
        print(f"\n{'='*60}")
        print(f"🎯 买点信号")
        print(f"{'='*60}")
        for bp in buy_points[:5]:
            print(bp)
except:
    pass

# 读取情绪结果
try:
    with open('/tmp/sentiment_result.json') as f:
        sent = json.load(f)
    print(f"\n{'='*60}")
    print(f"🌡️ 今日市场情绪")
    print(f"{'='*60}")
    print(f"情绪: {sent['sentiment']}")
    print(f"策略: {sent['strategy']}")
    print(f"操作: {sent['action']}")
except:
    pass

print(f"\n✅ 晚盘分析完成 - {datetime.now().strftime('%H:%M:%S')}")
PYEOF

echo "==== 晚盘链路完成 ===" >> $LOG
