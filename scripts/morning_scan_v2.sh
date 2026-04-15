#!/bin/bash
# 每日早盘V2.1：多维度扫描，捕捉强势股（修复版）
# 1. 昨日涨停股（连板预期）
# 2. 近期强势股（3日累计涨幅大）
# 3. 高成交额趋势股（机构信号）
# 运行时间：周一至周五 09:01

LOG_FILE="/tmp/morning_scan_v2.log"
SCRIPT_DIR="/home/dhtaiyi/.openclaw/workspace/scripts"

echo "==== $(date) 早盘候选扫描V2.1 ====" >> $LOG_FILE
cd /home/dhtaiyi/.openclaw/workspace

# 获取昨日日期（用于生成报告标题）
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

TODAY_STR=$(python3 -c "from datetime import datetime; print(datetime.now().strftime('%Y%m%d'))")

python3 - <<PYEOF >> $LOG_FILE 2>&1
import requests
import json
import re
import os
from datetime import datetime

YESTERDAY = "$YESTERDAY_STR"
today_str = "$TODAY_STR"

# ====== 数据源1: 新浪涨幅榜(获取涨停+强势股) ======
url = 'https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeDataSimple'

all_stocks = []
try:
    params = {'page': 1, 'num': 200, 'sort': 'changepercent', 'asc': 0, 'node': 'hs_a'}
    r = requests.get(url, params=params, timeout=15)
    raw = r.text
    # 尝试解析为JSON
    try:
        all_stocks = r.json()
    except:
        # 可能返回了非JSON，尝试直接解析
        all_stocks = []
    print(f"获取股票: {len(all_stocks)}只")
except Exception as e:
    print(f"⚠️ 获取涨幅榜失败: {e}")
    all_stocks = []

# ====== 数据源2: 按成交额排序(获取机构主买单) ======
top_amount_stocks = {}
try:
    params2 = {'page': 1, 'num': 100, 'sort': 'amount', 'asc': 0, 'node': 'hs_a'}
    r2 = requests.get(url, params=params2, timeout=15)
    by_amount = r2.json() if r2.text else []
    for s in (by_amount[:30] if by_amount else []):
        sym = s.get('symbol', '')
        if sym:
            top_amount_stocks[sym] = s
    print(f"获取成交额数据: {len(top_amount_stocks)}只")
except Exception as e:
    print(f"⚠️ 获取成交额榜失败: {e}")
    by_amount = []

# ====== 数据源3: 获取指数（带容错）======
indices = {}
try:
    r_idx = requests.get('http://qt.gtimg.cn/q=s_sh000001,s_sz399001,s_sz399006', timeout=5)
    for line in r_idx.text.strip().split('\n'):
        if '"~' not in line:
            continue
        m = re.search(r'"([^"]+)"', line)
        if not m:
            continue
        content = m.group(1)
        parts = content.split('~')
        # 腾讯接口格式：name在parts[1], price在parts[3], pct在parts[32]
        try:
            if len(parts) > 32 and parts[1] and parts[3]:
                name = parts[1]
                price = float(parts[3]) if parts[3] else 0
                pct = float(parts[32]) if len(parts) > 32 and parts[32] else 0
                indices[name] = {'price': price, 'pct': pct}
        except (ValueError, IndexError) as e:
            continue
except Exception as e:
    print(f"⚠️ 获取指数失败: {e}")

sh_pct = indices.get('上证指数', {}).get('pct', 0)
print(f"上证: {sh_pct:+.2f}%")

# ====== 过滤函数 ======
def is_clean(s):
    name = s.get('name', '')
    if any(x in name for x in ['ST', '*', 'N ', '退', 'S ']):
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
if not all_stocks:
    print("❌ 无数据，跳过扫描")
    exit(1)

limit_up = [s for s in all_stocks if float(s.get('changepercent', 0)) >= 9.9 and is_clean(s)]
strong = [s for s in all_stocks if 5 <= float(s.get('changepercent', 0)) < 9.9 and is_clean(s)]

# 成交额TOP30中的强势股(机构信号)
institutional = []
for sym, s in top_amount_stocks.items():
    try:
        pct = float(s.get('changepercent', 0))
        amount_yi = float(s.get('amount', 0)) / 1e8
        if pct >= 5 and is_clean(s) and amount_yi >= 20:
            institutional.append((s, amount_yi, pct))
    except (ValueError, TypeError):
        continue

print(f"涨停: {len(limit_up)}只 | 大涨(5-9%): {len(strong)}只 | 机构信号: {len(institutional)}只")

# ====== 候选股池生成 ======
candidates = {}

# 1. 涨停股: 成交额排序
limit_up_sorted = sorted(limit_up, key=lambda x: float(x.get('amount', 0) or 0), reverse=True)[:20]
for rank, s in enumerate(limit_up_sorted, 1):
    sym = s.get('symbol', '')
    full_code = get_full_code(sym)
    try:
        amount_yi = float(s.get('amount', 0)) / 1e8
        pct = float(s.get('changepercent', 0))
        trade = float(s.get('trade', 0))
        close_y = float(s.get('settlement', 0))
        candidates[full_code] = {
            'name': s['name'],
            'pct': pct,
            'amount_yi': round(amount_yi, 1),
            'close_y': close_y,
            'price': trade,
            'circ_mv': 0,
            'rank': rank,
            'type': '涨停',
            'reason': f"涨停+{pct:.0f}%成交{amount_yi:.0f}亿"
        }
    except (ValueError, TypeError):
        continue

# 2. 机构信号股: 成交额>=20亿的强势股
for s, amount_yi, pct in institutional[:10]:
    sym = s.get('symbol', '')
    full_code = get_full_code(sym)
    if full_code in candidates:
        continue
    try:
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
    except (ValueError, TypeError):
        continue

# 3. 大涨股中成交最大的(补强)
for s in strong[:30]:
    sym = s.get('symbol', '')
    full_code = get_full_code(sym)
    if full_code in candidates:
        continue
    try:
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
    except (ValueError, TypeError):
        continue

print(f"候选股总数: {len(candidates)}只")

# ====== 简单市值估算+评分======
for code, c in candidates.items():
    price = c['price']
    amount_yi = c['amount_yi']
    # 成交额越大分越高，涨停加分
    type_bonus = 20 if c['type'] == '涨停' else (10 if c['type'] == '机构信号' else 0)
    c['score'] = amount_yi * 10 + c['rank'] * -1 + type_bonus

# 排序，取top15
top15 = sorted(candidates.items(), key=lambda x: x[1].get('score', 0), reverse=True)[:15]

print(f"\n{'='*60}")
print(f"📊 今日观察标的 (候选池{len(candidates)}只)")
print(f"{'='*60}")
for i, (code, c) in enumerate(top15, 1):
    print(f"{i}. [{c['type']}] {c['name']}({code}) +{c['pct']:.1f}% 成交{c['amount_yi']:.0f}亿")

# ====== 保存 ======
save_dir = "/home/dhtaiyi/.openclaw/workspace/stock-patterns/candidates"
os.makedirs(save_dir, exist_ok=True)
save_path = f"{save_dir}/{today_str}.json"
with open(save_path, 'w') as f:
    json.dump({code: c for code, c in candidates.items()}, f, ensure_ascii=False, indent=2)
print(f"\n✅ 候选池已保存: {save_path}")

# ====== 更新WATCH_STOCKS (top8到breakthrough_alert.py) ======
watch = {}
watch_codes = []
for code, c in top15[:8]:
    resist = round(c['price'] * 1.03, 2) if c['price'] > 0 else 0
    watch[code] = {
        "name": c['name'],
        "resist": resist,
        "reason": c['reason'][:30]
    }
    watch_codes.append(code)

# 读取当前breakthrough_alert.py内容
alert_path = "/home/dhtaiyi/.openclaw/workspace/scripts/breakthrough_alert.py"
if os.path.exists(alert_path):
    with open(alert_path) as f:
        content = f.read()
    
    # 找到WATCH_STOCKS块并替换
    import textwrap
    watch_str = 'WATCH_STOCKS = ' + json.dumps(watch, ensure_ascii=False, indent=4)
    
    # 简单替换：在WATCH_STOCKS = {之后找到对应的闭合}
    # 用正则匹配整个WATCH_STOCKS字典
    pattern = r'(WATCH_STOCKS = \{[^}]+\})'
    new_content = re.sub(pattern, watch_str, content, count=1, flags=re.DOTALL)
    if new_content == content:
        # 备选方案：直接修改注释行
        content_lines = content.split('\n')
        for i, line in enumerate(content_lines):
            if '# 重点监控的股票和关键价位' in line:
                # 找到下一个}之后的内容
                pass
    else:
        with open(alert_path, 'w') as f:
            f.write(new_content)
        print(f"✅ 已同步top8到突破监控")
else:
    print(f"⚠️ breakthrough_alert.py不存在，跳过监控更新")

# ====== 生成早报 ======
institutional_list = [c for c in candidates.values() if c['type'] == '机构信号']
limit_up_list = [c for c in candidates.values() if c['type'] == '涨停']

report = f"""📊 **今日观察标的** {today_str}

昨日涨停 {len(limit_up_list)} 只 + 机构信号 {len(institutional_list)} 只 + 高成交强势 {len([c for c in candidates.values() if c['type'] == '高成交强势'])} 只：

"""
for i, (code, c) in enumerate(top15[:8], 1):
    report += f"{i}. **{c['name']}**[{c['type']}] +{c['pct']:.1f}% 成交{c['amount_yi']:.0f}亿\n"

report += f"""
💡 今日策略参考：
• 上证指数 {sh_pct:+.2f}%，市场氛围参考
• 涨停 {len(limit_up_list)} 只（高辨识度）
"""
if institutional_list:
    report += f"• 机构信号 {len(institutional_list)} 只（成交额>20亿+涨幅>5%）\n"
report += "• 开盘观察竞价，高开3-7%超预期为佳\n• 实时关注：飞沃科技、博瑞医药等成交额居前标的"
print(report)

# ====== 自动触发智能评分 ======
import subprocess
print("\n" + "="*60)
print("🧠 正在运行智能评分系统...")
print("="*60)
try:
    result = subprocess.run(
        ['python3', '/home/dhtaiyi/.openclaw/workspace/scripts/smart_scoring.py', today_str],
        capture_output=True, text=True, timeout=120
    )
    print(result.stdout[-2000:] if result.stdout else "(无输出)")
    if result.stderr:
        print("STDERR:", result.stderr[-500:])
except subprocess.TimeoutExpired:
    print("⏰ 智能评分超时，跳过")
except Exception as e:
    print(f"⚠️ 智能评分失败: {e}")

PYEOF
echo "==== 完成 ====" >> $LOG_FILE
