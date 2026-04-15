#!/bin/bash

# AI图片分析脚本
# 用法: ./analyze-image.sh <图片路径> [提示词]

IMAGE_PATH="$1"
PROMPT="${2:-Describe what you see in this image in detail}"

if [ -z "$IMAGE_PATH" ]; then
    echo "用法: $0 <图片路径> [提示词]"
    echo "示例: $0 screenshot.png"
    echo "示例: $0 photo.jpg '分析这张图片的内容'"
    exit 1
fi

if [ ! -f "$IMAGE_PATH" ]; then
    echo "错误: 文件不存在: $IMAGE_PATH"
    exit 1
fi

# 检查API密钥
if [ -z "$OPENAI_API_KEY" ]; then
    echo "错误: 未配置 OPENAI_API_KEY"
    echo "请设置: export OPENAI_API_KEY='your_api_key'"
    exit 1
fi

# 转换为base64
IMAGE_BASE64=$(base64 -w 0 "$IMAGE_PATH")

# 调用OpenAI API
echo "🔍 正在分析图片..."
echo ""

curl -s -X POST "https://api.openai.com/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-4o",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "'"$PROMPT"'"
          },
          {
            "type": "image_url",
            "image_url": {
              "url": "data:image/jpeg;base64,'"$IMAGE_BASE64"'"
            }
          }
        ]
      }
    ],
    "max_tokens": 1000
  }' | jq -r '.choices[0].message.content' 2>/dev/null

echo ""
echo "✅ 分析完成"
