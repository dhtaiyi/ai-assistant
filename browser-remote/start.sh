#!/bin/bash
# OpenClaw 远程浏览器控制 - 快速启动

echo "========================================"
echo "  OpenClaw 远程浏览器控制"
echo "========================================"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 需要安装 Python 3"
    exit 1
fi

# 检查依赖
echo "📦 检查依赖..."
pip install requests --quiet 2>/dev/null

echo "✅ 依赖检查完成"
echo ""

# 检查Chrome扩展
EXTENSION_DIR="$(pwd)/browser-remote"
if [ ! -d "$EXTENSION_DIR" ]; then
    echo "❌ 未找到扩展目录: $EXTENSION_DIR"
    exit 1
fi

echo "========================================"
echo "  启动选项"
echo "========================================"
echo ""
echo "  1. 启动服务器 (后台运行)"
echo "  2. 测试连接"
echo "  3. 运行示例"
echo "  4. 查看帮助"
echo ""
echo "========================================"

read -p "请选择 [1-4]: " choice

case $choice in
    1)
        echo ""
        echo "🚀 启动服务器..."
        python3 "$EXTENSION_DIR/server.py"
        ;;
    2)
        echo ""
        echo "🔍 测试连接..."
        python3 -c "
from browser_remote import RemoteBrowser
browser = RemoteBrowser()
result = browser.status()
import json
print(json.dumps(result, indent=2, ensure_ascii=False))
"
        ;;
    3)
        echo ""
        echo "📝 运行示例..."
        python3 "$EXTENSION_DIR/client.py"
        ;;
    4)
        cat "$EXTENSION_DIR/README.md"
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac
