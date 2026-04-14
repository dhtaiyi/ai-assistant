#!/bin/bash
# 自动发送已转录文件到服务器脚本
# 用途：在转录完成后发送已转录的视频文件名给服务器

VIDEO_DIR="/mnt/f/Program Files/WeGame/dhtaiyi/openclaw douyin work"
API_URL="https://www.kunkunkuntest.cloud/interaction/transcribed-files"

echo "========================================"
echo "开始检查已转录文件..."
echo "========================================"

# 切换到视频目录
cd "$VIDEO_DIR" || exit 1

# 找出所有视频文件（只保留原始直播文件，不包括douyin_live前缀和segment开头的）
video_files=$(ls *.mp4 *.flv 2>/dev/null | grep -v "^douyin_live_" | grep -v "^segment_")

if [ -z "$video_files" ]; then
    echo "没有找到视频文件"
    exit 0
fi

# 转换为JSON数组
files_json="["
first=true
for f in $video_files; do
    # 检查是否有对应的txt文件（表示已转录）
    base="${f%.*}"
    txt_file="${base}.txt"
    if [ -f "$txt_file" ]; then
        if [ "$first" = true ]; then
            first=false
        else
            files_json+=","
        fi
        files_json+="\"$f\""
    fi
done
files_json+="]"

if [ "$files_json" = "[]" ]; then
    echo "没有已转录的文件"
    exit 0
fi

echo "已转录文件: $files_json"

# 发送到服务器
response=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d "{\"action\": \"report\", \"files\": $files_json}")

echo "服务器回复: $response"

# 发送飞书通知
if command -v openclaw &> /dev/null; then
    openclaw message send --target ou_04add8ebe219f09799570c70e3cdc732 \
        --message "✅ 已转录文件已通知服务器删除！\n\n文件列表: $(echo $files_json | tr -d '[]\"')"
fi

echo "========================================"
echo "完成！"
echo "========================================"
