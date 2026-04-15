#!/bin/bash
# 小红书Cookie自动刷新
# 运行时间: 每6小时

/usr/bin/python3 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-cookie-manager.py refresh >> /home/dhtaiyi/.openclaw/workspace/xiaohongshu-cron.log 2>&1
