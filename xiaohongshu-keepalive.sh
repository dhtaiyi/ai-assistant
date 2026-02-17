#!/bin/bash

# 小红书保持登录状态脚本
# 使用保存的 Cookie 恢复登录并保持浏览器打开

echo "🚀 启动小红书（恢复登录状态）..."
echo ""

# 检查 Cookie 文件
if [ ! -f "/root/.openclaw/workspace/xiaohongshu-cookies.json" ]; then
    echo "❌ 未找到 Cookie 文件"
    echo "请先登录一次以保存 Cookie"
    exit 1
fi

echo "📂 发现 Cookie 文件: xiaohongshu-cookies.json"
echo ""

# 启动 Node.js 脚本
cd /root/.openclaw/workspace

# 使用 nohup 在后台运行
nohup node xiaohongshu-keepalive.js > /root/.openclaw/workspace/xiaohongshu-keepalive.log 2>&1 &

echo "✅ 后台进程已启动"
echo "📄 日志文件: xiaohongshu-keepalive.log"
echo ""
echo "检查状态："
ps aux | grep xiaohongshu-keepalive | grep -v grep
