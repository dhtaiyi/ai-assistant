#!/bin/bash
# 微信公众号快捷发布脚本

# 用法: publish-wechat.sh "标题" "内容文件"

TITLE="$1"
CONTENT_FILE="$2"

if [ -z "$TITLE" ] || [ -z "$CONTENT_FILE" ]; then
    echo "用法: publish-wechat.sh '标题' '内容文件'"
    echo ""
    echo "示例:"
    echo "  publish-wechat.sh '我的文章' article.txt"
    exit 1
fi

# 检查环境变量
if [ -z "$WECHAT_APPID" ]; then
    echo "⚠️ 请设置 WECHAT_APPID 环境变量"
    echo "export WECHAT_APPID='your_appid'"
    exit 1
fi

if [ -z "$WECHAT_APPSECRET" ]; then
    echo "⚠️ 请设置 WECHAT_APPSECRET 环境变量"
    echo "export WECHAT_APPSECRET='your_appsecret'"
    exit 1
fi

# 读取内容
CONTENT=$(cat "$CONTENT_FILE")

echo "📤 准备发布文章..."
echo "标题: $TITLE"
echo "内容长度: ${#CONTENT} 字符"

# 执行发布
python3 /root/.openclaw/workspace/skills/wechat-mp-publisher/wechat_mp_publisher.py \
    --title "$TITLE" \
    --content "$CONTENT"

echo ""
echo "✅ 发布完成! 请登录微信公众平台完成发布。"
