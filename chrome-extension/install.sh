#!/bin/bash
# 小红书助手 - Chrome 插件安装脚本

echo "========================================"
echo "    🌸 小红书助手 - 安装脚本"
echo "========================================"
echo ""

# 检查 Chrome 是否安装
if [ ! -d "$HOME/.config/google-chrome/Default/Extensions" ]; then
    echo "⚠️  未检测到 Chrome 浏览器"
    echo "   请先安装 Chrome: https://www.google.com/chrome/"
    exit 1
fi

# 获取扩展目录
EXTENSION_DIR="$HOME/.config/google-chrome/Default/Extensions/xiaohongshu-assistant"
mkdir -p "$EXTENSION_DIR"

# 创建版本目录（使用当前日期作为版本号）
VERSION=$(date +%Y%m%d)
EXTENSION_PATH="$EXTENSION_DIR/$VERSION"

# 复制文件
echo "📦 正在安装插件..."
cp -r /root/.openclaw/workspace/chrome-extension/* "$EXTENSION_PATH/"

echo "✅ 安装完成！"
echo ""
echo "📁 安装位置: $EXTENSION_PATH"
echo ""

# 打开 Chrome 扩展页面
echo "🔗 下一步："
echo "   1. 打开 Chrome"
echo "   2. 地址栏输入: chrome://extensions/"
echo "   3. 找到「小红书助手」"
echo "   4. 点击「详情」→「扩展程序选项」"
echo "   5. 确保「允许访问文件网址」已开启"
echo ""

# 提示创建图标
if [ ! -f "$EXTENSION_PATH/icons/icon16.png" ]; then
    echo "⚠️  提示：图标文件不存在"
    echo "   请创建以下PNG图片："
    echo "   - $EXTENSION_PATH/icons/icon16.png (16x16)"
    echo "   - $EXTENSION_PATH/icons/icon48.png (48x48)"
    echo "   - $EXTENSION_PATH/icons/icon128.png (128x128)"
fi

echo ""
echo "========================================"
echo "    🎉 安装成功！"
echo "========================================"
