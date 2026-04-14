#!/bin/bash
# 每日收盘后：更新候选股池 + 同步到突破监控列表
# 运行时间：周一至周五 15:10

SCRIPT_DIR="/home/dhtaiyi/.openclaw/workspace/scripts"
LOG_FILE="/tmp/candidate_update.log"

echo "==== $(date) 候选股池更新 ====" >> $LOG_FILE

cd /home/dhtaiyi/.openclaw/workspace

# 1. 更新候选股池
python3 ${SCRIPT_DIR}/update_candidates.py --auto >> $LOG_FILE 2>&1

# 2. 获取最新候选文件
CANDIDATE_FILE=$(ls -t ${SCRIPT_DIR}/../stock-patterns/candidates/*.json 2>/dev/null | head -1)
if [ -f "$CANDIDATE_FILE" ]; then
    echo "候选文件: $CANDIDATE_FILE" >> $LOG_FILE
    
    # 3. 同步top5到breakthrough_alert.py的WATCH_STOCKS
    python3 - <<EOF >> $LOG_FILE 2>&1
import json
import os
import re

candidate_file = "$CANDIDATE_FILE"
alert_file = "${SCRIPT_DIR}/breakthrough_alert.py"

with open(candidate_file) as f:
    candidates = json.load(f)

# 取评分最高的前5只
top5 = sorted(candidates.items(), key=lambda x: x[1].get('score', 0), reverse=True)[:5]

# 生成新的WATCH_STOCKS字典
new_watch = {}
for code, info in top5:
    resist = info.get('high', info.get('price', 0))
    if resist == 0:
        resist = info.get('close_today', info.get('close_y', 0)) * 1.1
    new_watch[code] = {
        "name": info['name'],
        "resist": round(resist, 2),
        "reason": info.get('reason', '')[:30]
    }

print("Top5候选股:")
for code, v in new_watch.items():
    print(f"  {code} {v['name']} 阻力{v['resist']}")

# 读取现有文件
with open(alert_file) as f:
    content = f.read()

# 替换WATCH_STOCKS部分
import ast
pattern = r'^WATCH_STOCKS = \{.*?\n\}'
replacement = 'WATCH_STOCKS = ' + json.dumps(new_watch, ensure_ascii=False, indent=4)

new_content = re.sub(pattern, replacement, content, count=1, flags=re.MULTILINE | re.DOTALL)

with open(alert_file, 'w') as f:
    f.write(new_content)

print(f"✅ 已同步{len(new_watch)}只到breakthrough_alert.py")
EOF
else
    echo "未找到候选文件" >> $LOG_FILE
fi

echo "==== 完成 ====" >> $LOG_FILE
