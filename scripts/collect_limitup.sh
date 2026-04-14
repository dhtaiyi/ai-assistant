#!/bin/bash
# 每日收盘后采集涨停股历史数据
# 运行时间：周一至周五 15:05（在连板记录之后）

LOG="/tmp/limitup_collect.log"
echo "[$(date)] 开始采集涨停历史" >> $LOG

python3 - <<'PYEOF' >> $LOG 2>&1
import requests
import json
import os
from datetime import datetime

today = datetime.now().strftime('%Y%m%d')
save_dir = '/home/dhtaiyi/.openclaw/workspace/stock-patterns/limitup_history'
os.makedirs(save_dir, exist_ok=True)
save_path = f'{save_dir}/{today}.json'

# 用新浪获取今日涨幅前150（含涨停）
url = 'https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeDataSimple'
params = {'page': 1, 'num': 150, 'sort': 'changepercent', 'asc': 0, 'node': 'hs_a', '_s_r_a': 'page'}
r = requests.get(url, params=params, timeout=10)
stocks = r.json()

# 筛选涨停股
limit_up = [s for s in stocks if float(s.get('changepercent', 0)) >= 9.9]
print(f'今日涨停: {len(limit_up)} 只')

# 补充详细行情：获取每只股票的当日数据
result = []
for s in limit_up:
    code = s.get('symbol', '')
    result.append({
        'code': code,
        'name': s.get('name', ''),
        'pct': float(s.get('changepercent', 0)),
        'price': float(s.get('trade', 0)),
        'close_y': float(s.get('settlement', 0)),
        'open': float(s.get('open', 0)),
        'high': float(s.get('high', 0)),
        'low': float(s.get('low', 0)),
        'amount_yi': round(float(s.get('amount', 0)) / 1e8, 1),
    })

# 保存
with open(save_path, 'w') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(f'✅ 已保存: {save_path}')
PYEOF

echo "[$(date)] 完成" >> $LOG
