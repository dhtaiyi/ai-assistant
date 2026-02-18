#!/bin/bash
# Tushare 配置脚本

# 请替换为你的 Tushare Token
TUSHARE_TOKEN="your_token_here"

# 写入环境变量文件
echo "export TUSHARE_TOKEN=$TUSHARE_TOKEN" > /root/.openclaw/workspace/.tushare.env

echo "✅ Tushare Token 已配置"
echo ""
echo "配置内容:"
cat /root/.openclaw/workspace/.tushare.env

# 加载配置
source /root/.openclaw/workspace/.tushare.env

echo ""
echo "验证配置:"
echo $TUSHARE_TOKEN | head -c 20
echo "..."
