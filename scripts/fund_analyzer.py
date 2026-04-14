#!/usr/bin/env python3
"""
基金分析脚本
功能:
1. 获取基金实时估值 (天天基金网API)
2. 获取历史净值 (东财API)
3. 获取前10大持仓 (东财F10)
"""

import requests
import json
import re
import sys
from datetime import datetime

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://fund.eastmoney.com/'
}

def get_fund_realtime(fund_code):
    """获取基金实时估值"""
    url = f"https://fundgz.1234567.com.cn/js/{fund_code}.js"
    try:
        r = requests.get(url, timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        text = r.text
        if "jsonpgz" in text:
            data_str = text.replace("jsonpgz(", "").rstrip(");")
            return json.loads(data_str)
    except Exception as e:
        print(f"实时估值获取失败: {e}", file=sys.stderr)
    return None


def get_fund_history(fund_code, pagesize=10):
    """获取基金历史净值"""
    url = "https://api.fund.eastmoney.com/f10/lsjz"
    params = {"fundCode": fund_code, "pageIndex": 1, "pageSize": pagesize}
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=8)
        data = r.json()
        if data.get('Data'):
            return data['Data']['LSJZList']
    except Exception as e:
        print(f"历史净值获取失败: {e}", file=sys.stderr)
    return []


def get_fund_holdings(fund_code, year=None, quarter=None):
    """获取基金前10大持仓"""
    url = f"https://fundf10.eastmoney.com/FundArchivesDatas.aspx"
    params = {
        "type": "jjcc",
        "code": fund_code,
        "topline": 10,
        "year": year or "",
        "month": quarter or "",
        "rt": int(datetime.now().timestamp() * 1000)
    }
    try:
        r = requests.get(url, params=params, headers={
            'User-Agent': 'Mozilla/5.0',
            'Referer': f'https://fundf10.eastmoney.com/fundArchivesDatas.aspx?type=jjcc&code={fund_code}'
        }, timeout=10)
        text = r.text
        
        match = re.search(r"var apidata=\{(.*)\}", text, re.DOTALL)
        if match:
            content_match = re.search(r"content:\"(.*?)\"", match.group(1), re.DOTALL)
            if content_match:
                html = content_match.group(1)
                html = html.replace("\\n", "").replace("\\t", "")
                html = html.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("\\\"", '"')
                
                # Parse table rows
                holdings = []
                seen = set()
                rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL)
                for row in rows[:20]:
                    cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
                    if len(cells) >= 4:
                        seq = re.sub(r'<[^>]+>', '', cells[0]).strip()
                        code = re.sub(r'<[^>]+>', '', cells[1]).strip()
                        name = re.sub(r'<[^>]+>', '', cells[2]).strip()
                        pct = cells[6].strip() if len(cells) > 6 else '-'
                        
                        if (code.isdigit() and len(code) == 6 and
                            name and len(name) < 10 and '变动' not in name):
                            if code not in seen and len(holdings) < 10:
                                seen.add(code)
                                holdings.append({"code": code, "name": name, "pct": pct})
                return holdings
    except Exception as e:
        print(f"持仓获取失败: {e}", file=sys.stderr)
    return []


def get_fund_info(fund_code):
    """获取基金基本信息"""
    url = "https://api.fund.eastmoney.com/f10/FundBaseInfo"
    params = {"fundCode": fund_code}
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=8)
        data = r.json()
        if data.get('Data'):
            return data['Data']
    except:
        pass
    rt = get_fund_realtime(fund_code)
    if rt:
        return {"fundcode": rt.get("fundcode"), "name": rt.get("name")}
    return {}


def analyze_fund(fund_code):
    """综合分析基金"""
    result = {
        "code": fund_code,
        "name": "",
        "realtime": None,
        "history": [],
        "holdings": [],
        "analysis": {}
    }
    
    rt = get_fund_realtime(fund_code)
    if rt:
        result["name"] = rt.get("name", "")
        result["realtime"] = rt
    
    result["history"] = get_fund_history(fund_code, 20)
    result["holdings"] = get_fund_holdings(fund_code)
    
    if result["history"]:
        recent_5 = result["history"][:5]
        if len(recent_5) >= 2:
            try:
                first_nav = float(recent_5[-1].get("DWJZ", 0))
                last_nav = float(recent_5[0].get("DWJZ", 0))
                if first_nav > 0:
                    change_5d = (last_nav - first_nav) / first_nav * 100
                    result["analysis"]["recent_5d"] = round(change_5d, 2)
            except:
                pass
    
    if rt:
        try:
            result["analysis"]["today_change"] = float(rt.get("gszzl", "0"))
        except:
            result["analysis"]["today_change"] = 0
    
    return result


def format_fund_report(fund_code):
    """格式化基金报告"""
    result = analyze_fund(fund_code)
    
    lines = []
    lines.append("=" * 50)
    
    name = result.get("name", result.get("code", ""))
    lines.append(f"📊 基金分析报告 - {name} ({fund_code})")
    lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 50)
    
    rt = result.get("realtime")
    if rt:
        lines.append("\n💰 实时估值")
        lines.append(f"  基金名称: {rt.get('name', '')}")
        lines.append(f"  昨日净值: {rt.get('dwjz', '-')}")
        lines.append(f"  今日估算: {rt.get('gsz', '-')}")
        gszzl = rt.get('gszzl', '0')
        try:
            change = float(gszzl)
            emoji = "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
            lines.append(f"  估算涨幅: {emoji} {change:+.2f}%")
        except:
            lines.append(f"  估算涨幅: {gszzl}%")
        lines.append(f"  估算时间: {rt.get('gztime', '-')}")
        lines.append(f"  数据日期: {rt.get('jzrq', '-')}")
    
    history = result.get("history", [])
    if history:
        lines.append(f"\n📈 历史净值 (最近{len(history)}天)")
        for item in history[:5]:
            date = item.get("FSRQ", "")
            nav = item.get("DWJZ", "")
            change = item.get("JZZZL", "0")
            try:
                ch = float(change)
                emoji = "🟢" if ch > 0 else "🔴" if ch < 0 else ""
                lines.append(f"  {date}: 净值={nav} {emoji}{ch:+.2f}%")
            except:
                lines.append(f"  {date}: 净值={nav} {change}%")
    
    analysis = result.get("analysis", {})
    if "recent_5d" in analysis:
        ch5 = analysis["recent_5d"]
        emoji = "🟢" if ch5 > 0 else "🔴" if ch5 < 0 else "⚪"
        lines.append(f"\n📅 近5日表现: {emoji} {ch5:+.2f}%")
    
    holdings = result.get("holdings", [])
    if holdings:
        lines.append(f"\n🏦 前10大持仓")
        for i, h in enumerate(holdings[:10], 1):
            pct = h.get('pct', '-')
            lines.append(f"  {i:2d}. {h['name']} ({h['code']}) 占净值: {pct}")
    else:
        lines.append("\n🏦 持仓数据: 暂无可用")
    
    lines.append("=" * 50)
    return "\n".join(lines)


if __name__ == "__main__":
    codes = sys.argv[1:] if len(sys.argv) > 1 else ["110022"]
    for code in codes:
        print(format_fund_report(code))
        print()
