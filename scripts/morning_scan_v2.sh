#!/bin/bash
# 每日早盘V2：多维度扫描，捕捉强势股
# 1. 昨日涨停股（连板预期）
# 2. 近期强势股（3日累计涨幅大）
# 3. 高成交额趋势股（机构信号）
# 运行时间：周一至周五 09:00

LOG_FILE="/tmp/morning_scan_v2.log"
SCRIPT_DIR="/home/dhtaiyi/.openclaw/workspace/scripts"

echo "==== $(date) 早盘候选扫描V2 ====" >> $LOG_FILE
cd /home/dhtaiyi/.openclaw/workspace

# 获取昨日日期
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

python3 - <<PYEOF >> $LOG_FILE 2>&1
import requests
import json
import re
import os
from datetime import datetime

YESTERDAY = "$YESTERDAY_STR"
today_str = datetime.now().strftime('%Y%m%d')

# ====== 数据源1: 新浪涨幅榜(获取涨停+强势股) ======
url = 'https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeDataSimple'

# 获取涨幅前200（含涨停）
params = {'page': 1, 'num': 200, 'sort': 'changepercent', 'asc': 0, 'node': 'hs_a'}
r = requests.get(url, params=params, timeout=10)
all_stocks = r.json()
print(f"获取股票: {len(all_stocks)}只")

# ====== 数据源2: 按成交额排序(获取机构主买单) ======
params2 = {'page': 1, 'num': 100, 'sort': 'amount', 'asc': 0, 'node': 'hs_a'}
r2 = requests.get(url, params=params2, timeout=10)
by_amount = r2.json()
top_amount_stocks = {s['symbol']: s for s in by_amount[:30]}

# ====== 数据源3: 获取指数 ======
r_idx = requests.get('http://qt.gtimg.cn/q=s_sh000001,s_sz399001,s_sz399006', timeout=5)
indices = {}
for line in r_idx.text.strip().split('\n'):
    if '"~' not in line:
        continue
    # 格式: v_s_sh000001="1~上证指数~000001~4026.63~38.07~0.95~..."
    m = re.search(r'"([^"]+)"', line)
    if not m:
        continue
    content = m.group(1)
    parts = content.split('~')
    if len(parts) > 4:
        name = parts[1]
        price = float(parts[3]) if parts[3] else 0
        change = float(parts[4]) if parts[4] else 0
        indices[name] = {'price': price, 'pct': change}

sh_pct = indices.get('上证指数', {}).get('pct', 0)
print(f"上证: {sh_pct:+.2f}%")

# ====== 过滤函数 ======
def is_clean(s):
    name = s.get('name', '')
    if any(x in name for x in ['ST', '*', 'N ', '退']):
        return False
    code = s.get('symbol', '')
    # 过滤北交所
    if code.startswith('bj'):
        return False
    return True

def get_full_code(symbol):
    code = symbol.replace('sz', '').replace('sh', '')
    prefix = 'sz' if symbol.startswith('sz') else 'sh'
    return prefix + code

# ====== 分类 ======
limit_up = [s for s in all_stocks if float(s.get('changepercent', 0)) >= 9.9 and is_clean(s)]
strong = [s for s in all_stocks if 5 <= float(s.get('changepercent', 0)) < 9.9 and is_clean(s)]

# 成交额TOP30中的强势股(机构信号)
institutional = []
for sym, s in top_amount_stocks.items():
    pct = float(s.get('changepercent', 0))
    amount_yi = float(s.get('amount', 0)) / 1e8
    if pct >= 5 and is_clean(s) and amount_yi >= 20:
        institutional.append((s, amount_yi, pct))

print(f"涨停: {len(limit_up)}只 | 大涨(5-9%): {len(strong)}只 | 机构信号: {len(institutional)}只")

# ====== 候选股池生成 ======
candidates = {}

# 1. 涨停股: 成交额排序
limit_up_sorted = sorted(limit_up, key=lambda x: float(x.get('amount', 0)), reverse=True)[:20]
for rank, s in enumerate(limit_up_sorted, 1):
    sym = s.get('symbol', '')
    full_code = get_full_code(sym)
    amount_yi = float(s.get('amount', 0)) / 1e8
    pct = float(s.get('changepercent', 0))
    trade = float(s.get('trade', 0))
    candidates[full_code] = {
        'name': s['name'],
        'pct': pct,
        'amount_yi': round(amount_yi, 1),
        'close_y': float(s.get('settlement', 0)),
        'price': trade,
        'circ_mv': 0,
        'rank': rank,
        'type': '涨停',
        'reason': f"涨停+{pct:.0f}%成交{amount_yi:.0f}亿"
    }

# 2. 机构信号股: 成交额>=30亿的强势股
for s, amount_yi, pct in institutional[:10]:
    sym = s.get('symbol', '')
    full_code = get_full_code(sym)
    if full_code in candidates:
        continue
    trade = float(s.get('trade', 0))
    candidates[full_code] = {
        'name': s['name'],
        'pct': pct,
        'amount_yi': round(amount_yi, 1),
        'close_y': float(s.get('settlement', 0)),
        'price': trade,
        'circ_mv': 0,
        'rank': 0,
        'type': '机构信号',
        'reason': f"强势+{pct:.0f}%成交{amount_yi:.0f}亿[机构]"
    }

# 3. 大涨股中成交最大的(补强)
for s in strong[:30]:
    sym = s.get('symbol', '')
    full_code = get_full_code(sym)
    if full_code in candidates:
        continue
    amount_yi = float(s.get('amount', 0)) / 1e8
    if amount_yi >= 15:
        pct = float(s.get('changepercent', 0))
        candidates[full_code] = {
            'name': s['name'],
            'pct': pct,
            'amount_yi': round(amount_yi, 1),
            'close_y': float(s.get('settlement', 0)),
            'price': float(s.get('trade', 0)),
            'circ_mv': 0,
            'rank': 0,
            'type': '高成交强势',
            'reason': f"+{pct:.0f}%成交{amount_yi:.0f}亿"
        }

# ====== 简单市值估算（用收盘价*假设股本估算）======
# 流通市值估算：假设流通股本=总股本，用成交额/换手率估算
for code, c in candidates.items():
    price = c['price']
    amount_yi = c['amount_yi']
    # 换手率 ≈ 成交额/(股价*总股本) → 假设换手率3%，反推股本
    # 这里简化：用成交额排名给一个虚拟市值
    c['score'] = amount_yi * 10 + c['rank'] * -1  # 成交额为主

# 排序，取top10
top10 = sorted(candidates.items(), key=lambda x: x[1].get('score', 0), reverse=True)[:10]

print(f"\n{'='*60}")
print(f"📊 今日观察标的 (候选池{len(candidates)}只)")
print(f"{'='*60}")
for i, (code, c) in enumerate(top10, 1):
    print(f"{i}. [{c['type']}] {c['name']}({code}) +{c['pct']:.1f}% 成交{c['amount_yi']:.0f}亿")

# ====== 保存 ======
save_path = f"/home/dhtaiyi/.openclaw/workspace/stock-patterns/candidates/{today_str}.json"
os.makedirs(os.path.dirname(save_path), exist_ok=True)
with open(save_path, 'w') as f:
    json.dump({code: c for code, c in candidates.items()}, f, ensure_ascii=False, indent=2)
print(f"\n✅ 候选池已保存: {save_path}")

# ====== 更新WATCH_STOCKS (top5) ======
watch = {}
for code, c in top10[:5]:
    resist = round(c['price'] * 1.03, 2)
    watch[code] = {
        "name": c['name'],
        "resist": resist,
        "reason": c['reason'][:30]
    }

with open("/home/dhtaiyi/.openclaw/workspace/scripts/breakthrough_alert.py") as f:
    content = f.read()

pattern = r'^WATCH_STOCKS = \{.*?\n\}'
replacement = 'WATCH_STOCKS = ' + json.dumps(watch, ensure_ascii=False, indent=4)
new_content = re.sub(pattern, replacement, content, count=1, flags=re.MULTILINE | re.DOTALL)

with open("/home/dhtaiyi/.openclaw/workspace/scripts/breakthrough_alert.py", 'w') as f:
    f.write(new_content)
print(f"✅ 已同步top5到突破监控")

# ====== 生成早报 ======
institutional_list = [c for c in candidates.values() if c['type'] == '机构信号']
limit_up_list = [c for c in candidates.values() if c['type'] == '涨停']

report = f"""📊 **今日观察标的** {YESTERDAY}

昨日涨停 {len(limit_up_list)} 只 + 高成交强势股 {len(candidates)-len(limit_up_list)} 只：

"""
for i, (code, c) in enumerate(top10[:8], 1):
    report += f"{i}. **{c['name']}**[{c['type']}] +{c['pct']:.1f}% 成交{c['amount_yi']:.0f}亿\n"

report += f"""
💡 今日策略参考：
• 上证指数 {sh_pct:+.2f}%，市场氛围参考
• 涨停 {len(limit_up_list)} 只（高辨识度）
"""
if institutional_list:
    report += f"• 机构信号 {len(institutional_list)} 只（成交额>20亿+涨幅>5%）\n"
report += "• 开盘观察竞价，高开3-7%超预期为佳"
print(report)

# ====== 自动触发智能评分 ======
import subprocess
print("\n" + "="*60)
print("🧠 正在运行智能评分系统...")
print("="*60)
result = subprocess.run(
    ['python3', '/home/dhtaiyi/.openclaw/workspace/scripts/smart_scoring.py', today_str],
    capture_output=True, text=True, timeout=120
)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr[:500])

PYEOF
echo "==== 完成 ====" >> $LOG_FILE
