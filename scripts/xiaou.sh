#!/bin/bash
# 和小 u 直接对话

export PATH="$HOME/.local/bin:$PATH"

echo "╔════════════════════════════════════════╗"
echo "║     💻 小 u 代码助手 - 直接对话        ║"
echo "╚════════════════════════════════════════╝"
echo ""

if [ -n "$1" ]; then
    # 有参数则直接执行
    echo "小 u：好哒主人！马上处理～"
    echo ""
    kimi -w "$1"
else
    # 无参数在当前目录启动
    echo "小 u：主人好呀～今天想让我帮你写什么代码呢？💻✨"
    echo ""
    kimi
fi
