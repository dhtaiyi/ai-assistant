#!/bin/bash

# 智谱AI图片分析脚本

IMAGE_PATH="$1"
PROMPT="${2:-请详细描述这张图片的内容}"

if [ -z "$IMAGE_PATH" ]; then
    echo "用法: $0 <图片路径> [提示词]"
    exit 1
fi

if [ ! -f "$IMAGE_PATH" ]; then
    echo "错误: 文件不存在: $IMAGE_PATH"
    exit 1
fi

if [ -z "$ZHIPU_API_KEY" ]; then
    echo "错误: 未配置 ZHIPU_API_KEY"
    exit 1
fi

# 获取文件扩展名
EXT="${IMAGE_PATH##*.}"
MIME_TYPE="image/jpeg"
case $EXT in
    png) MIME_TYPE="image/png" ;;
    jpg|JPEG) MIME_TYPE="image/jpeg" ;;
    gif) MIME_TYPE="image/gif" ;;
    webp) MIME_TYPE="image/webp" ;;
esac

# 转换为base64
IMAGE_BASE64=$(base64 -w 0 "$IMAGE_PATH")

echo "🔍 正在分析图片..."
echo ""

# 调用智谱AI API
curl -s -X POST "https://open.bigmodel.cn/api/paas/v4/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ZHIPU_API_KEY" \
  -d "{
    \"model\": \"glm-4v\",
    \"messages\": [
      {
        \"role\": \"user\",
        \"content\": [
          {
            \"type\": \"text\",
            \"text\": \"$PROMPT\"
          },
          {
            \"type\": \"image_url\",
            \"image_url\": {
              \"url\": \"data:$MIME_TYPE;base64,$IMAGE_BASE64\"
            }
          }
        ]
      }
    ],
    \"max_tokens\": 1000
  }" | jq -r '.choices[0].message.content' 2>/dev/null

echo ""
echo "✅ 分析完成"
