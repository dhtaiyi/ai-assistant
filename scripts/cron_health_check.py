#!/usr/bin/env python3
"""Cron健康检查"""
import json, os, time
from datetime import datetime

JOBS_PATH = "/home/dhtaiyi/.openclaw/cron/jobs.json"
RUNS_DIR = "/home/dhtaiyi/.openclaw/cron/runs"

def main():
    with open(JOBS_PATH) as f:
        jobs = json.load(f).get('jobs', [])
    enabled = [j for j in jobs if j.get('enabled', True)]
    disabled = [j for j in jobs if not j.get('enabled', True)]
    
    recent_count = 0
    if os.path.exists(RUNS_DIR):
        cutoff = time.time() - 86400
        for fn in os.listdir(RUNS_DIR):
            fpath = os.path.join(RUNS_DIR, fn)
            if fn.endswith('.jsonl') and os.path.getmtime(fpath) > cutoff:
                recent_count += 1
    
    ts = datetime.now().strftime('%Y-%m-%d %H:%M')
    print("=== Cron健康检查 %s ===" % ts)
    print("总:%d 启用:%d 禁用:%d" % (len(jobs), len(enabled), len(disabled)))
    print("今日运行:%d个" % recent_count)
    
    if disabled:
        print("\n已禁用任务:")
        for j in disabled:
            print("  - %s | %s" % (j.get('name','?'), j.get('schedule',{}).get('expr','?')))
    else:
        print("\n全部正常，无禁用任务")

if __name__ == "__main__":
    main()
