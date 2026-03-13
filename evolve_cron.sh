#!/bin/bash
# 小雨自我进化定时任务
# 每天早上 9:00 自动运行

cd /root/.openclaw/workspace
python3 xiaoyu_evolver.py >> /tmp/evolve.log 2>&1
