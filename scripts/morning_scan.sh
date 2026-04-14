#!/bin/bash
# 每日早盘：扫描昨日涨停股，筛选观察标的，更新监控列表
# 运行时间：周一至周五 09:00

LOG_FILE="/tmp/morning_scan.log"

echo "==== $(date) 早盘候选扫描 ====" >> $LOG_FILE
cd /home/dhtaiyi/.openclaw/workspace

# 获取昨日日期（交易日在周末会取周五）
YESTERDAY_STR=$(python3 -c "
from datetime import datetime, timedelta
today = datetime.now()
wd = today.weekday()
if wd == 5:
    y = today - timedelta(days=1)
elif wd == 6:
    y = today - timedelta(days=2)
else:
    y = today - timedelta(days=1)
print(y.strftime('%Y%m%d'))
")

echo "昨日日期: $YESTERDAY_STR" >> $LOG_FILE

python3 - <<PYEOF >> $LOG_FILE 2>&1
import requests
import json
import re
import os

YESTERDAY = "$YESTERDAY_STR"

# 从新浪获取涨幅前150只（含涨停）
url = 'https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeDataSimple'
params = {'page': 1, 'num': 150, 'sort': 'changepercent', 'asc': 0, 'node': 'hs_a', 'symbol': '', '_s_r_a': 'page'}
r = requests.get(url, params=params, timeout=10)
stocks = r.json()
print(f"获取到 {len(stocks)} 只股票")

# 筛选涨停股（>=9.9%）
limit_up = [s for s in stocks if float(s.get('changepercent', 0)) >= 9.9]
print(f"涨停股: {len(limit_up)} 只")

# 过滤ST和不合格
def ok_stock(s):
    name = s.get('name', '')
    if 'ST' in name or '*' in name or 'N ' in name:
        return False
    amount = float(s.get('amount', 0))
    amount_yi = amount / 1e8
    if amount_yi < 2:  # 成交额<2亿不要
        return False
    return True

candidates = [s for s in limit_up if ok_stock(s)]
candidates.sort(key=lambda x: float(x.get('amount', 0)), reverse=True)
print(f"初筛候选: {len(candidates)} 只")

print("\n===== 今日观察标的（按成交额排序）=====")
for i, s in enumerate(candidates[:10], 1):
    amount_yi = float(s.get('amount', 0)) / 1e8
    pct = float(s.get('changepercent', 0))
    code = s.get('symbol', '')
    print(f"{i}. {code} {s['name']} +{pct:.1f}% 成交{amount_yi:.0f}亿")

# 取前5只更新监控
top5 = candidates[:5]
watch = {}
for s in top5:
    pct = float(s.get('changepercent', 0))
    amount_yi = float(s.get('amount', 0)) / 1e8
    code = s.get('symbol', '').replace('sz', 'sz').replace('sh', 'sh')
    full_code = code  # sz002463 格式
    resist = round(float(s.get('trade', 0)) * 1.03, 2)
    watch[full_code] = {
        "name": s['name'],
        "resist": resist,
        "reason": f"涨停+{pct:.0f}%成交{amount_yi:.0f}亿"
    }

# 保存候选池
os.makedirs("/home/dhtaiyi/.openclaw/workspace/stock-patterns/candidates", exist_ok=True)
save_data = {}
for s in candidates[:10]:
    code = s.get('symbol', '')
    amount_yi = float(s.get('amount', 0)) / 1e8
    pct = float(s.get('changepercent', 0))
    save_data[code] = {
        'name': s['name'],
        'pct': pct,
        'amount': round(amount_yi, 1),
        'close_y': float(s.get('settlement', 0)),
        'reason': f"涨停+{pct:.0f}%"
    }

with open(f"/home/dhtaiyi/.openclaw/workspace/stock-patterns/candidates/morning_{YESTERDAY}.json", 'w') as f:
    json.dump(save_data, f, ensure_ascii=False, indent=2)

# 更新breakthrough_alert.py
with open("/home/dhtaiyi/.openclaw/workspace/scripts/breakthrough_alert.py") as f:
    content = f.read()

pattern = r'^WATCH_STOCKS = \{.*?\n\}'
replacement = 'WATCH_STOCKS = ' + json.dumps(watch, ensure_ascii=False, indent=4)
new_content = re.sub(pattern, replacement, content, count=1, flags=re.MULTILINE | re.DOTALL)

with open("/home/dhtaiyi/.openclaw/workspace/scripts/breakthrough_alert.py", 'w') as f:
    f.write(new_content)

print(f"\n✅ 已更新 {len(watch)} 只到突破监控列表")

# 生成早报
report = f"""📊 **今日观察标的** {YESTERDAY}

从 {len(limit_up)} 只涨停股中筛选出 {len(candidates)} 只优质标的：

"""
for i, s in enumerate(candidates[:5], 1):
    amount_yi = float(s.get('amount', 0)) / 1e8
    report += f"{i}. **{s['name']}**({s.get('symbol','')}) +{float(s.get('changepercent', 0)):.1f}% 成交{amount_yi:.0f}亿\n"

report += """
💡 今日策略参考：
• 开盘观察竞价强度，高开3-7%超预期为佳
• 优先关注成交额最大的标的
• 指数配合时突破更有效
"""
print(report)
PYEOF

echo "==== 完成 ====" >> $LOG_FILE
