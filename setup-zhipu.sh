#!/bin/bash

# 智谱AI API Key 配置脚本

echo "╔════════════════════════════════════╗"
echo "║   🔑 智谱AI API Key 配置      ║"
echo "╚════════════════════════════════════╝"
echo ""

# 读取API Key
read -p "请粘贴你的智谱API Key: " API_KEY

if [ -z "$API_KEY" ]; then
    echo "❌ 错误: API Key不能为空"
    exit 1
fi

# 添加到环境变量
echo "" >> ~/.bashrc
echo "# 智谱AI API Key - $(date)" >> ~/.bashrc
echo "export ZHIPU_API_KEY=\"$API_KEY\"" >> ~/.bashrc

# 立即生效
export ZHIPU_API_KEY="$API_KEY"

echo ""
echo "✅ 配置完成!"
echo ""
echo "API Key: ${API_KEY:0:10}..."
echo ""
echo "📁 已保存到: ~/.bashrc"
echo ""
echo "🔍 验证配置..."
if [ -n "$ZHIPU_API_KEY" ]; then
    echo "✅ 配置成功!"
    echo ""
    echo "🚀 可以使用了:"
    echo "   /root/.openclaw/workspace/analyze-image-zhipu.sh 图片路径"
else
    echo "❌ 配置失败"
fi
