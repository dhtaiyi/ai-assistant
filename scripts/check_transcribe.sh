#!/bin/bash

# 检测转录是否成功

VIDEO_DIR="/mnt/f/Program Files/WeGame/dhtaiyi/openclaw douyin work"

echo "========== 转录检测 =========="

# 获取所有视频文件
videos=$(ls "$VIDEO_DIR"/*.flv "$VIDEO_DIR"/*.mp4 2>/dev/null)

total=0
success=0
failed=0

for video in $videos; do
    filename=$(basename "$video")
    basename="${filename%.*}"
    txt_file="$VIDEO_DIR/$basename.txt"
    
    ((total++))
    
    if [ -f "$txt_file" ]; then
        size=$(stat -c%s "$txt_file" 2>/dev/null)
        if [ "$size" -gt 100 ]; then
            echo "✅ $basename.txt - 已完成 ($size bytes)"
            ((success++))
        else
            echo "❌ $basename.txt - 文件太小，可能失败 ($size bytes)"
            ((failed++))
        fi
    else
        echo "⏳ $filename - 未转录"
    fi
done

echo ""
echo "========== 统计 =========="
echo "总计: $total"
echo "完成: $success"
echo "失败/未完成: $failed"
