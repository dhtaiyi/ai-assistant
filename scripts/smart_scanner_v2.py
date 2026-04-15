#!/usr/bin/env python3
"""
智能综合扫描器 V3 - 问财增强版
==============================================
整合功能：
1. 实时市场扫描（涨幅榜+成交额）
2. 妖股潜力评分（成交额+涨幅+振幅+开板）
3. 板块题材检测（问财官方涨停原因）
4. 连板晋级追踪（1板→2板→3板）
5. 首板战法买点A量化
6. 养家心法综合提示

核心评分体系（100分）：
- 成交额得分（40分）
- 涨幅得分（25分）
- 振幅得分（20分）
- 连板/跟风得分（15分）

V3新增：
- 问财涨停原因替代SECTOR_MAP
- 官方涨停原因自动识别主线板块
==============================================
"""
import requests
import json
import re
import os
import subprocess
import time
from datetime import datetime
from collections import defaultdict

LOG_FILE = "/tmp/smart_scanner.log"

# 问财配置
IWENCAI_SKILL = os.path.expanduser("~/.openclaw/workspace/skills/问财选A股/scripts/cli.py")
IWENCAI_API_KEY = os.environ.get(
    "IWENCAI_API_KEY",
    "sk-proj-01-NAItJumXGkKAe1Ha8v-rPenhNjrfud7CDgoY0DEAymigKrbbZSIwxhjOQG5RrqWytp8AZApOyf4RsS-q5d2FbyTbPZAYJC262Vbgthv9IizhxH3W-5a2kNpR3ifa0nAobbl6NQ"
)

# 问财涨停原因缓存
_iwencai_reasons = {}
_iwencai_cache_time = 0
_REASON_TTL = 300  # 5分钟

def get_iwencai_reasons() -> dict:
    """获取问财涨停原因映射（带缓存）"""
    global _iwencai_reasons, _iwencai_cache_time
    now = time.time()
    if _iwencai_reasons and (now - _iwencai_cache_time) < _REASON_TTL:
        return _iwencai_reasons
    try:
        cmd = ["python3", IWENCAI_SKILL,
               "--query", "今日涨停股票，按成交额排序",
               "--limit", "100", "--api-key", IWENCAI_API_KEY]
        env = os.environ.copy()
        env["IWENCAI_BASE_URL"] = "https://openapi.iwencai.com"
        env["IWENCAI_API_KEY"] = IWENCAI_API_KEY
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, env=env)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if data.get("success"):
                _iwencai_reasons = {}
                for s in data.get("datas", []):
                    code_raw = s.get("股票代码", "")
                    code = code_raw.upper().replace(".SZ", "").replace(".SH", "")
                    prefix = "sz" if "SZ" in code_raw else "sh"
                    norm = prefix + code
                    reason = s.get("涨停原因[20260415]", "") or ""
                    _iwencai_reasons[norm] = reason
                _iwencai_cache_time = now
                print(f"   [问财] 涨停原因缓存: {len(_iwencai_reasons)}只")
    except Exception as e:
        print(f"   [问财] 涨停原因获取失败: {e}")
    return _iwencai_reasons

LOG_FILE = "/tmp/smart_scanner.log"

# ===== 股票→板块映射 =====
SECTOR_MAP = {
    # AI/算力
    '寒武纪': 'AI算力', '协创数据': 'AI算力', '工业富联': 'AI算力', '沐曦股份': 'AI算力',
    '壁仞科技': 'AI算力', '长芯博创': 'AI算力', '中安科': 'AI算力',
    # 光模块/光通信
    '剑桥科技': '光模块', '光迅科技': '光模块', '中际旭创': '光模块', '新易盛': '光模块',
    '天孚通信': '光模块', '华工科技': '光模块', '华盛昌': '光模块',
    # 存储/半导体
    '佰维存储': '存储', '兆易创新': '存储', '江波龙': '存储', '德明利': '存储',
    # PCB/电子
    '沪电股份': 'PCB', '鹏鼎控股': 'PCB', '胜宏科技': 'PCB', '东山精密': '精密制造',
    # 军工
    '神剑股份': '军工', '西部材料': '军工',
    # 医药/健康
    '博瑞医药': '医药', '华人健康': '医药', '健信超导': '医药',
    '瑞康医药': '医药流通', '金陵药业': '中药', '沃华医药': '中药',
    # 新能源/储能
    '宁德时代': '新能源车', '亿纬锂能': '电池', '阳光电源': '储能',
    '圣阳股份': '储能', '中恒电气': '储能/电力',
    # 消费
    '天邦食品': '消费', '居然智家': '消费', '来伊份': '食品',
    # 锂电/矿产
    '盛新锂能': '锂矿', '西藏城投': '锂矿', '国城矿业': '锂矿', '大中矿业': '锂矿',
    '天齐锂业': '锂矿', '赣锋锂业': '锂矿',
    # 机器人/AI应用
    '柯力传感': '传感器', '巨力索具': '通用设备', '利通电子': '电子',
    '长信科技': '电子', '奥尼电子': '电子', '大族激光': '激光设备',
    # 连板龙头
    '华远控股': '地产/重组', '长源东谷': '汽车零部件',
    '嘉博创': '算力', '中嘉博创': '算力',
    # 其他科技
    '飞沃科技': 'AI应用', '琏升科技': 'AI应用', '宏景科技': 'AI应用',
    '顺灏股份': '电子', '豫能控股': '电力', '中国西电': '电力',
    '宏和科技': '电子', '博云新材': '材料',
}

def is_trading():
    now = datetime.now().time()
    return (time(9, 30) <= now <= time(11, 30)) or (time(13, 0) <= now <= time(15, 0))

def is_clean_stock(s):
    name = s.get('name', '')
    if any(x in name for x in ['ST', '*ST', 'N ', '退', 'S ']):
        return False
    if s.get('symbol', '').startswith('bj'):
        return False
    return True

def get_full_code(symbol):
    code = symbol.replace('sz', '').replace('sh', '')
    prefix = 'sz' if symbol.startswith('sz') else 'sh'
    return prefix + code

def get_sector(name, code=None, reasons=None):
    # 优先用问财官方涨停原因
    if reasons and code:
        reason = reasons.get(code.lower(), "")
        if reason:
            return reason.split("+")[0].split("(")[0].strip()
    # 降级：SECTOR_MAP
    if name in SECTOR_MAP:
        return SECTOR_MAP[name]
    # 关键词匹配
    for kw, sec in [
        ('医药', '医药'), ('医疗', '医药'), ('健康', '医药'),
        ('光模块', '光模块'), ('光通信', '光模块'),
        ('AI', 'AI'), ('算力', 'AI算力'), ('智能', 'AI'),
        ('锂', '锂电'), ('能源', '新能源'),
        ('军工', '军工'), ('国防', '军工'),
        ('芯片', '半导体'), ('半导体', '半导体'),
        ('消费', '消费'), ('食品', '消费'),
    ]:
        if kw in name:
            return sec
    return '其他'


def scan():
    # 先获取问财涨停原因
    reasons = get_iwencai_reasons()

    url = 'https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeDataSimple'
    
    # 获取涨幅TOP200
    try:
        r1 = requests.get(url, params={
            'page': 1, 'num': 200,
            'sort': 'changepercent', 'asc': 0,
            'node': 'hs_a'
        }, timeout=10)
        all_stocks = r1.json()
    except Exception as e:
        print(f"❌ 涨幅榜获取失败: {e}")
        return

    # 获取成交额TOP100
    try:
        r2 = requests.get(url, params={
            'page': 1, 'num': 100,
            'sort': 'amount', 'asc': 0,
            'node': 'hs_a'
        }, timeout=10)
        by_amount = r2.json()
    except:
        by_amount = []

    # 成交额字典
    amount_dict = {}
    for s in (by_amount or []):
        sym = s.get('symbol', '')
        try:
            amount_dict[sym] = float(s.get('amount', 0)) / 1e8
        except:
            pass

    # 指数
    indices = {}
    try:
        r_idx = requests.get('http://qt.gtimg.cn/q=s_sh000001,s_sz399001,s_sz399006', timeout=5)
        for line in r_idx.text.strip().split('\n'):
            if '"' not in line:
                continue
            m = re.search(r'=\s*"([^"]+)"', line)
            if not m:
                continue
            parts = m.group(1).split('~')
            try:
                if len(parts) > 5 and parts[1]:
                    name = parts[1]
                    price = float(parts[3]) if parts[3] else 0
                    pct = float(parts[5]) if parts[5] else 0
                    indices[name] = {'price': price, 'pct': pct}
            except:
                continue
    except:
        pass

    # 分类
    limit_up = [s for s in all_stocks if float(s.get('changepercent', 0)) >= 9.5 and is_clean_stock(s)]
    strong = [s for s in all_stocks if 5 <= float(s.get('changepercent', 0)) < 9.5 and is_clean_stock(s)]

    return all_stocks, limit_up, strong, amount_dict, indices, reasons


def analyze_candidates(all_stocks, limit_up, strong, amount_dict, indices, reasons=None):
    """综合评分所有候选股"""
    candidates = []
    
    for s in (limit_up + strong):
        sym = s.get('symbol', '')
        try:
            pct = float(s.get('changepercent', 0))
            trade = float(s.get('trade', 0))
            high = float(s.get('high', 0))
            open_p = float(s.get('open', 0))
            amount = float(s.get("amount", 0)) / 1e8 if float(s.get("amount", 0)) > 0 else amount_dict.get(sym, 0)
            close_y = float(s.get('settlement', 0))
            
            if not trade or not close_y:
                continue
            
            name = s.get('name', '')
            sym = s.get('symbol', '')
            sector = get_sector(name, sym, reasons)
            
            # 振幅
            amplitude = (high - close_y) / close_y * 100 if close_y > 0 else 0
            
            # ===== 综合评分（100分）=====
            # 成交额（40分）
            amount_score = min(40, amount * 0.8)
            
            # 涨幅（25分）
            pct_score = min(25, pct * 1.5)
            
            # 振幅（20分）
            amp_score = min(20, amplitude * 2)
            
            # 连板/跟风（15分）
            # 涨停加分，但一字板没机会
            if pct >= 9.5:
                if open_p < trade:  # 开板=有分歧=有机会
                    lianban_score = 15
                elif amount >= 10:   # 成交额大=主力参与
                    lianban_score = 12
                else:
                    lianban_score = 8
            else:
                lianban_score = 5
            
            total_score = amount_score + pct_score + amp_score + lianban_score
            
            candidates.append({
                'name': name,
                'code': get_full_code(sym),
                'pct': pct,
                'amount': amount,
                'amplitude': round(amplitude, 1),
                'score': round(total_score, 1),
                'type': '涨停' if pct >= 9.5 else '强势',
                'sector': sector,
                'price': trade,
                'high': high,
                'open': open_p,
                'amount_score': round(amount_score, 1),
                'pct_score': round(pct_score, 1),
                'amp_score': round(amp_score, 1),
                'lianban_score': round(lianban_score, 1),
            })
        except:
            continue
    
    candidates.sort(key=lambda x: x['score'], reverse=True)
    return candidates


def detect_sectors(limit_up, amount_dict, reasons=None):
    """检测板块主题"""
    sector_count = defaultdict(list)
    for s in limit_up:
        name = s.get('name', '')
        sym = s.get('symbol', '')
        sector = get_sector(name, sym, reasons)
        amount = float(s.get("amount", 0)) / 1e8 if float(s.get("amount", 0)) > 0 else amount_dict.get(sym, 0)
        pct = float(s.get('changepercent', 0))
        sector_count[sector].append({
            'name': name, 'pct': pct, 'amount': amount,
            'code': get_full_code(sym)
        })
    
    sector_strength = {}
    for sector, members in sector_count.items():
        total_amount = sum(m['amount'] for m in members)
        strength = len(members) * 10 + total_amount * 0.1
        sector_strength[sector] = {
            'count': len(members),
            'total_amount': round(total_amount, 1),
            'strength': round(strength, 1),
            'members': sorted(members, key=lambda x: x['amount'], reverse=True)[:3]
        }
    
    return sector_strength


def yangjia_hints(candidates, sector_strength, limit_up, strong, indices):
    """养家心法综合提示"""
    hints = []
    lu_count = len(limit_up)
    strong_count = len(strong)
    
    sh_pct = indices.get('上证指数', {}).get('pct', 0)
    
    # 主线判断
    sorted_sectors = sorted(sector_strength.items(), key=lambda x: x[1]['strength'], reverse=True)
    main_themes = [(s, i) for s, i in sorted_sectors if i['count'] >= 2]
    
    # 指数分析
    if sh_pct >= 0.5:
        hints.append(("✅", f"指数上涨{sh_pct:+.2f}%，多头占优"))
    elif sh_pct <= -0.5:
        hints.append(("⚠️", f"指数下跌{sh_pct:+.2f}%，谨慎操作"))
    
    # 主线
    if main_themes:
        top_sector, top_info = main_themes[0]
        hints.append(("👑", f"主线明确: {top_sector}（{top_info['count']}只涨停）"))
        hints.append(("→", f"跟龙头！重点关注: {', '.join(m['name'] for m in top_info['members'][:2])}"))
    elif lu_count >= 30:
        hints.append(("🔥", f"无明确主线，但涨停家数多({lu_count}只)，行情活跃"))
    
    # 仓位建议
    if lu_count >= 50:
        hints.append(("🎯", "仓位8-9成，积极参与"))
    elif lu_count >= 30:
        hints.append(("🎯", "仓位5-7成，轻仓参与"))
    else:
        hints.append(("🎯", "仓位1-3成，极轻仓练习"))
    
    # 危险信号
    st_count = sum(1 for s in limit_up if 'ST' in s.get('name', ''))
    if st_count > lu_count * 0.3:
        hints.append(("🚨", f"ST股占比过高({st_count}/{lu_count})，谨慎！"))
    
    # 买点信号
    buy_a_candidates = [c for c in candidates if 
                        3 <= c['pct'] <= 9.5 and 
                        c['amount'] >= 5 and 
                        c['amplitude'] > 2]
    if buy_a_candidates:
        top_buy = buy_a_candidates[0]
        hints.append(("🔔", f"买点A信号: {top_buy['name']}(+{top_buy['pct']:.1f}%,成交{top_buy['amount']:.0f}亿)"))
    
    return hints


def main():
    print(f"\n{'='*70}")
    print(f"🧠 智能综合扫描器 V2 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*70}")
    
    all_stocks, limit_up, strong, amount_dict, indices, reasons = scan()
    
    if not all_stocks:
        print("❌ 数据获取失败")
        return
    
    sh_pct = indices.get('上证指数', {}).get('pct', 0)
    sz_pct = indices.get('深证成指', {}).get('pct', 0)
    cy_pct = indices.get('创业板指', {}).get('pct', 0)
    
    print(f"\n📊 市场概况")
    print(f"  涨停: {len(limit_up)}只 | 强势(5-9%): {len(strong)}只")
    print(f"  上证 {indices.get('上证指数',{}).get('price','?')} ({sh_pct:+.2f}%)")
    print(f"  深证 {indices.get('深证成指',{}).get('price','?')} ({sz_pct:+.2f}%)")
    print(f"  创业板 {indices.get('创业板指',{}).get('price','?')} ({cy_pct:+.2f}%)")
    
    # 综合评分
    candidates = analyze_candidates(all_stocks, limit_up, strong, amount_dict, indices)
    
    # 板块检测
    sector_strength = detect_sectors(limit_up, amount_dict, reasons)
    sorted_sectors = sorted(sector_strength.items(), key=lambda x: x[1]['strength'], reverse=True)
    
    # ===== 1. 妖股潜力 TOP15 =====
    print(f"\n{'─'*70}")
    print(f"🔥 妖股潜力 TOP15（综合评分）:")
    print(f"{'─'*70}")
    print(f"  {'股票':12s} {'代码':10s} {'涨幅':>6s} {'成交':>6s} {'振幅':>5s} {'评分':>5s} {'所属板块':10s}")
    print(f"  {'─'*60}")
    
    for i, c in enumerate(candidates[:15], 1):
        amp_mark = "⚡" if c['amplitude'] > 5 else "  "
        board_mark = "🔓" if c['open'] < c['high'] and c['pct'] >= 9.5 else "  "
        sector_tag = c['sector'][:8]
        print(f"  {board_mark}{amp_mark}{i:2d}.{c['name'][:10]:12s} {c['code']:10s} "
              f"+{c['pct']:5.1f}% {c['amount']:5.0f}亿 {c['amplitude']:5.1f}% {c['score']:5.0f} {sector_tag}")
    
    # ===== 2. 板块主线 =====
    print(f"\n{'─'*70}")
    print(f"💎 主线题材TOP5:")
    print(f"{'─'*70}")
    
    main_themes = [(s, i) for s, i in sorted_sectors if i['count'] >= 2]
    
    if main_themes:
        for sector, info in main_themes[:5]:
            print(f"  👑 {sector}: {info['count']}只涨停 {info['total_amount']:.0f}亿成交")
            for m in info['members'][:2]:
                print(f"      → {m['name']}(+{m['pct']:.1f}%) {m['amount']:.0f}亿")
    else:
        print("  （暂无明确主线，混沌期）")
    
    # ===== 3. 买点机会 =====
    print(f"\n{'─'*70}")
    print(f"🎯 买点机会扫描:")
    print(f"{'─'*70}")
    
    opportunities = []
    for c in candidates:
        # 买点A: 首板战法（涨幅3-9.5%，成交5亿+，振幅>2%）
        if 3 <= c['pct'] <= 9.5 and c['amount'] >= 5 and c['amplitude'] > 2:
            opportunities.append(('买点A 首板战法', c))
        # 买点B: 开板回封（涨停已开板，成交大）
        if c['pct'] >= 9.5 and c['open'] < c['high'] and c['amount'] >= 10:
            opportunities.append(('买点B 开板回封', c))
        # 买点C: 跟风（主线内滞涨）
        if main_themes and c['pct'] < 9.5 and c['pct'] >= 5:
            sector = c['sector']
            if sector in sector_strength and sector_strength[sector]['count'] >= 2:
                opportunities.append(('跟风机会', c))
    
    shown_types = set()
    for op_type, c in opportunities[:8]:
        if op_type not in shown_types:
            print(f"  ✅ {op_type}: {c['name']}({c['code']}) "
                  f"+{c['pct']:.1f}% 成交{c['amount']:.0f}亿 评分{c['score']:.0f}")
            shown_types.add(op_type)
    
    if not opportunities:
        print("  （暂无明显买点，等回调或确认）")
    
    # ===== 4. 养家心法提示 =====
    print(f"\n{'─'*70}")
    print(f"💡 养家心法综合提示:")
    print(f"{'─'*70}")
    
    hints = yangjia_hints(candidates, sector_strength, limit_up, strong, indices)
    for icon, text in hints:
        print(f"  {icon} {text}")
    
    # ===== 5. 危险信号 =====
    danger = [c for c in candidates if c['pct'] >= 9.5 and c['amount'] < 1]
    if danger:
        print(f"\n  🚨 缩量涨停（小心！成交<1亿）:")
        for c in danger[:3]:
            print(f"      {c['name']} 成交{c['amount']:.1f}亿 ⚠️")
    
    # ===== 保存 =====
    today_str = datetime.now().strftime('%Y%m%d')
    save_dir = "/home/dhtaiyi/.openclaw/workspace/stock-data/realtime"
    os.makedirs(save_dir, exist_ok=True)
    save_path = f"{save_dir}/{today_str}_smart.json"
    
    with open(save_path, 'w') as f:
        json.dump({
            'time': datetime.now().isoformat(),
            'indices': indices,
            'limit_up_count': len(limit_up),
            'strong_count': len(strong),
            'top15': candidates[:15],
            'sectors': {k: v for k, v in sorted_sectors[:10]},
            'main_themes': [(s, i['count'], i['total_amount']) for s, i in main_themes[:5]],
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 综合扫描已保存: {save_path}")
    
    return candidates[:8]


if __name__ == "__main__":
    print(f"智能综合扫描器 V2 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    main()


# ===== 单独运行入口 =====
if __name__ == "__main__":
    import sys
    print(f"智能综合扫描器 V2 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    top5 = main()
    
    if top5 and len(sys.argv) > 1 and sys.argv[1] == '--update-watch':
        # 更新watch列表
        watch = {}
        for c in top5[:8]:
            resist = round(c['price'] * 1.03, 2)
            watch[c['code']] = {
                "name": c['name'],
                "resist": resist,
                "reason": f"{c['type']}+{c['pct']:.0f}%|{c['score']}分|{c['sector'][:4]}"
            }
        
        alert_path = "/home/dhtaiyi/.openclaw/workspace/scripts/breakthrough_alert.py"
        if os.path.exists(alert_path):
            with open(alert_path) as f:
                content = f.read()
            watch_str = 'WATCH_STOCKS = ' + json.dumps(watch, ensure_ascii=False, indent=4)
            import re as _re
            pattern = r'WATCH_STOCKS = \{[\s\S]*?\n\}'
            new_content = _re.sub(pattern, watch_str + '\n', content)
            with open(alert_path, 'w') as f:
                f.write(new_content)
            print(f"\n✅ 已同步TOP{len(watch)}到突破监控")
