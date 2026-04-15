#!/usr/bin/env python3
"""
集合竞价监控 V1.0
===============
每个交易日9:25运行，筛选竞价强势股并推送飞书

条件一（竞价强势）：
  竞价匹配金额 > 2000万
  竞价涨幅 > 0
  非ST

条件二（高开接力）：
  高开 > 5%（今开 > 昨收 * 1.05）
  非ST / 非新股
  竞价匹配金额 > 2000万

用法：
  python3 auction_monitor.py
"""

import json, os, re, sys, time, subprocess, urllib.request
from datetime import datetime
from pathlib import Path

# ─── 配置 ────────────────────────────────────────────────────────────────────
HIST_DIR = Path("/home/dhtaiyi/.openclaw/workspace/stock-data/auction")
os.makedirs(HIST_DIR, exist_ok=True)
FEISHU_USER = "ou_04add8ebe219f09799570c70e3cdc732"

IWENCAI_SKILL = os.path.expanduser("~/.openclaw/workspace/skills/问财选A股/scripts/cli.py")
IWENCAI_KEY = os.environ.get(
    "IWENCAI_API_KEY",
    "sk-proj-01-NAItJumXGkKAe1Ha8v-rPenhNjrfud7CDgoY0DEAymigKrbbZSIwxhjOQG5RrqWytp8AZApOyf4RsS-q5d2FbyTbPZAYJC262Vbgthv9IizhxH3W-5a2kNpR3ifa0nAobbl6NQ"
)

# ─── 问财查询 ────────────────────────────────────────────────────────────────
def iwencai_query(query: str, limit: int = 200) -> list:
    today_key = datetime.now().strftime("%Y%m%d")
    try:
        cmd = ["python3", IWENCAI_SKILL,
               "--query", query, "--limit", str(limit), "--api-key", IWENCAI_KEY]
        env = os.environ.copy()
        env["IWENCAI_BASE_URL"] = "https://openapi.iwencai.com"
        env["IWENCAI_API_KEY"] = IWENCAI_KEY
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60, env=env)
        if r.returncode == 0:
            data = json.loads(r.stdout)
            if data.get("success"):
                # 动态替换日期后缀
                results = []
                for s in data.get("datas", []):
                    row = {}
                    for k, v in s.items():
                        if today_key in k:
                            row[k.replace(today_key, "{TODAY}")] = v
                        else:
                            row[k] = v
                    # 统一用{TODAY}做key方便后面取
                    results.append(row)
                return results
    except Exception as e:
        print(f"[问财] 查询失败: {e}")
    return []

# ─── 昨收价（腾讯） ────────────────────────────────────────────────────────
def get_prev_close(codes: list) -> dict:
    """批量获取昨收价和今开价，返回 {norm_code: (prev_close, today_open)}"""
    if not codes:
        return {}
    batch = ",".join(codes)
    try:
        r = urllib.request.urlopen(f"http://qt.gtimg.cn/q={batch}", timeout=10)
        text = r.read().decode("gbk", errors="replace")
        result = {}
        for line in text.strip().split("\n"):
            m = re.search(r'="([^"]+)"', line)
            if not m:
                continue
            parts = m.group(1).split("~")
            # 批量接口：parts[0]=版本, parts[1]=名称, parts[2]=代码, parts[4]=昨收, parts[5]=今开
            if len(parts) > 5 and parts[2]:
                code_only = parts[2]  # 如 "300750"
                # 匹配回 norm_code 格式
                for nc in codes:
                    if nc.replace("sz", "").replace("sh", "") == code_only:
                        try:
                            result[nc] = (float(parts[4]), float(parts[5]))
                        except:
                            pass
                        break
        return result
    except Exception as e:
        print(f"[腾讯] 昨收价失败: {e}")
        return {}

# ─── 工具 ────────────────────────────────────────────────────────────────
def norm_code(code_raw: str) -> str:
    """统一转换为 sz300750 / sh600000"""
    code = code_raw.upper()
    if ".SZ" in code:
        return ("sz" + code.replace(".SZ", "")).lower()
    elif ".SH" in code:
        return ("sh" + code.replace(".SH", "")).lower()
    elif ".BJ" in code:
        return ("bj" + code.replace(".BJ", "")).lower()
    return code.lower()

def is_clean(name: str, code_raw: str = "") -> bool:
    """非ST/非新股"""
    if not name:
        return False
    if any(x in name for x in ["ST", "*ST", "N\t", "退", "S "]):
        return False
    # 过滤明显新股特征
    if name.startswith("N "):
        return False
    # 北交所代码43/83/87开头，且无历史K线的
    code = code_raw.upper().replace(".SZ","").replace(".SH","").replace(".BJ","")
    if code.startswith("43") or code.startswith("83") or code.startswith("87"):
        # 北交所有些也是老股，放行
        pass
    return True

# ─── 主筛选 ───────────────────────────────────────────────────────────────
def run():
    today_key = datetime.now().strftime("%Y%m%d")
    today_disp = datetime.now().strftime("%Y-%m-%d")

    print(f"\n{'='*55}")
    print(f"📋 竞价监控 {today_disp} 9:25")
    print(f"{'='*55}")

    print("\n⏳ 查询问财竞价数据...")
    raw = iwencai_query("今日竞价成交额排名", 300)
    print(f"   问财返回: {len(raw)}只")

    if not raw:
        print("❌ 无数据")
        return

    # 准备批量获取昨收价
    code_list = []
    for s in raw:
        cr = s.get("股票代码", "")
        nc = norm_code(cr)
        if nc.startswith("sz") or nc.startswith("sh"):
            code_list.append(nc)

    prev_map = get_prev_close(code_list)

    cond1, cond2 = [], []
    today_key_tpl = "{TODAY}"

    for s in raw:
        name = s.get("股票简称", "")
        code_raw = s.get("股票代码", "")
        nc = norm_code(code_raw)

        if not is_clean(name, code_raw):
            continue

        # 竞价字段（动态日期key）
        auction_pct = 0.0
        auction_amt = 0.0
        for k, v in s.items():
            if "竞价涨幅" in k and "{TODAY}" in k:
                try:
                    auction_pct = float(v) if v else 0.0
                except:
                    auction_pct = 0.0
            if "竞价匹配金额" in k and "{TODAY}" in k:
                try:
                    auction_amt = float(v) if v else 0.0
                except:
                    auction_amt = 0.0

        # 昨收和今开（腾讯实时接口）
        tc = prev_map.get(nc, (0.0, 0.0))
        prev_close, today_open = tc[0], tc[1]

        # 高开
        gaokai_pct = 0.0
        if prev_close > 0 and today_open > 0:
            gaokai_pct = (today_open - prev_close) / prev_close * 100

        # 条件一：竞价匹配金额>2000万，竞价涨幅>0
        if auction_amt >= 2000 * 10000 and auction_pct > 0:
            cond1.append({
                "name": name,
                "code": nc,
                "auction_pct": auction_pct,
                "auction_amt": auction_amt,
                "gaokai_pct": gaokai_pct,
                "today_open": today_open,
                "prev_close": prev_close,
            })

        # 条件二：高开>5%，竞价匹配金额>2000万
        if gaokai_pct > 5 and auction_amt >= 2000 * 10000:
            cond2.append({
                "name": name,
                "code": nc,
                "auction_pct": auction_pct,
                "auction_amt": auction_amt,
                "gaokai_pct": gaokai_pct,
                "today_open": today_open,
                "prev_close": prev_close,
            })

    # 排序
    cond1.sort(key=lambda x: x["auction_amt"], reverse=True)
    cond2.sort(key=lambda x: x["auction_amt"], reverse=True)

    # 输出
    print(f"\n{'─'*55}")
    print(f"【条件一】竞价强势（金额>2000万 & 涨幅>0）")
    print(f"共 {len(cond1)} 只")
    if cond1:
        print(f"{'代码':<12} {'名称':<10} {'竞价涨幅':>8} {'竞价金额':>10} {'高开':>8}")
        print("-" * 52)
        for s in cond1[:20]:
            print(f"{s['code']:<12} {s['name']:<10} {s['auction_pct']:>+7.2f}% {s['auction_amt']/1e8:>8.1f}亿 {s['gaokai_pct']:>+7.2f}%")
    else:
        print("  （无）")

    print(f"\n{'─'*55}")
    print(f"【条件二】高开接力（高开>5% & 金额>2000万）")
    print(f"共 {len(cond2)} 只")
    if cond2:
        print(f"{'代码':<12} {'名称':<10} {'高开':>8} {'竞价涨幅':>8} {'竞价金额':>10} {'开盘价':>8} {'昨收':>8}")
        print("-" * 68)
        for s in cond2[:20]:
            print(f"{s['code']:<12} {s['name']:<10} {s['gaokai_pct']:>+7.2f}% {s['auction_pct']:>+7.2f}% {s['auction_amt']/1e8:>8.1f}亿 {s['today_open']:>7.2f} {s['prev_close']:>7.2f}")
    else:
        print("  （无）")

    print(f"\n{'='*55}")

    # 保存历史
    record = {
        "date": today_disp,
        "cond1_count": len(cond1),
        "cond2_count": len(cond2),
        "cond1": cond1[:30],
        "cond2": cond2[:30],
    }
    out_path = HIST_DIR / f"{today_key}.json"
    with open(out_path, "w") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    print(f"📁 历史已保存: {out_path}")

    # 飞书推送（静默，打印输出由cron捕获）
    push_lines = [f"📋 竞价监控 {today_disp} 9:25", f"{'─'*40}"]
    push_lines.append(f"\n【条件一】竞价强势（金额>2000万 & 涨幅>0）共{len(cond1)}只")
    for s in cond1[:10]:
        push_lines.append(f"  {s['name']}({s['code']}) 竞价{s['auction_pct']:+.2f}% {s['auction_amt']/1e8:.1f}亿")
    push_lines.append(f"\n【条件二】高开接力（高开>5% & 金额>2000万）共{len(cond2)}只")
    for s in cond2[:10]:
        push_lines.append(f"  {s['name']}({s['code']}) 高开{s['gaokai_pct']:+.2f}% 竞价{s['auction_pct']:+.2f}% {s['auction_amt']/1e8:.1f}亿")
    push_lines.append(f"\n{'='*40}")
    push_text = "\n".join(push_lines)
    print("\n" + push_text)

    return cond1, cond2

# ─── 飞书 ────────────────────────────────────────────────────────────────
def feishu_push(text: str):
    try:
        app_id = "cli_a92923c6a2f99bc0"
        app_secret = "H4CdLHf1NwM1iv3JWzBsfdFFUY8bO4At"
        # 获取token
        token_data = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode()
        req = urllib.request.Request(
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            data=token_data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            token = json.loads(resp.read())["tenant_access_token"]
        # 发消息
        msg_data = json.dumps({
            "receive_id": FEISHU_USER,
            "msg_type": "text",
            "content": {"text": text}
        }).encode()
        msg_req = urllib.request.Request(
            "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id",
            data=msg_data,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
        )
        with urllib.request.urlopen(msg_req, timeout=10) as mr:
            result = json.loads(mr.read())
            if result.get("code") == 0:
                print("✅ 飞书推送成功")
            else:
                print(f"⚠️ 飞书推送失败: {result}")
    except Exception as e:
        print(f"⚠️ 飞书推送异常: {e}")

if __name__ == "__main__":
    run()
