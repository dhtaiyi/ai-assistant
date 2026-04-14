#!/usr/bin/env python3
"""
分钟级盯盘工具 v1.0
监控涨停股开板/炸板/封单变化
用法：python3 minute_monitor.py
"""

import requests
import time
import sys
from datetime import datetime

# 重点盯的股票
WATCH_STOCKS = {
    "汇源通信": "sz000586",
    "通鼎互联": "sz002491",
    "金陵药业": "sz000919",
    "益佰制药": "sh600594",
    "中安科": "sh600654",
    "东山精密": "sz002384",
    "光迅科技": "sz002281",
    "长飞光纤": "sh601869",
    "长芯博创": "sz300548",
}

TENcent_HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_minute_data(codes):
    """每分钟拉取腾讯实时数据"""
    url = "http://qt.gtimg.cn/q=" + ",".join(codes)
    r = requests.get(url, timeout=10)
    result = {}
    for line in r.text.strip().split("\n"):
        if "=" not in line:
            continue
        code = line.split("=")[0].replace("v_", "")
        p = line.split("~")
        if len(p) < 33:
            continue
        name = p[1]
        price = float(p[3]) if p[3] else 0
        prev_close = float(p[4]) if p[4] else 0
        pct = float(p[32]) if p[32] else 0
        amount = float(p[37]) / 1e8 if p[37] else 0
        result[code] = {
            "name": name,
            "price": price,
            "prev_close": prev_close,
            "pct": pct,
            "amount": amount,
        }
    return result

def main():
    print("分钟盯盘 v1.0 | 重点监控炸板/开板/封单")
    print("注意：9:30-15:00 运行效果最佳，收盘后数据仅供参考")
    print("按Ctrl+C停止\n")
    
    while True:
        try:
            data = get_minute_data(list(WATCH_STOCKS.values()))
            
            now = datetime.now().strftime("%H:%M")
            
            # 检测异常
            alerts = []
            for name, info in data.items():
                pct = info["pct"]
                price = info["price"]
                
                # 检测炸板（涨停股涨幅<9.5%）
                if pct < 9.5 and pct > 0:
                    alerts.append(("WARN", "%s %.1f%%" % (name, pct)))
                # 检测涨停（之前未涨停的突然涨停）
                elif pct >= 9.9:
                    alerts.append(("ZT", "%s +%.1f%%" % (name, pct)))
            
            # 输出
            if alerts:
                print("[%s] %s" % (now, " | ".join(["[%s]%s" % a for a in alerts]))
            else:
                print("[%s] 正常" % now)
            
            time.sleep(30)
        except KeyboardInterrupt:
            print("\n停止盯盘")
            break
        except Exception as e:
            print("Error:", e)
            time.sleep(10)

if __name__ == "__main__":
    main()
