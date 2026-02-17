#!/bin/bash

# 图片自动下载和分类存储脚本
# 按 关键词/日期/图片 格式存放

set -e

# 配置
IMAGE_DIR="/root/.openclaw/workspace/images"
ZHIPU_DIR="$IMAGE_DIR/zhipu"

# 帮助
help() {
    cat << EOF
╔═══════════════════════════════════════════════╗
║  图片自动分类下载                           ║
╚═══════════════════════════════════════════════╝

用法: save-image <关键词> <图片URL> [平台]

参数:
  关键词     图片描述/标签
  图片URL    生成的图片链接
  平台       zhipu|openai|qwen (默认: zhipu)

示例:
  save-image "小女孩和猫" "https://xxx.com/img.png"
  save-image "赛博朋克" "https://xxx.com/img.png" openai

功能:
  - 自动按 关键词/日期/图片.png 格式存放
  - 自动清理过期文件
  - 记录生成日志

EOF
}

# 下载图片
download_image() {
    local keyword="$1"
    local url="$2"
    local platform="${3:-zhipu}"
    
    # 清理关键词（保留中文，移除特殊字符）
    local clean_keyword=$(echo "$prompt" | sed 's/[/\\?*|<>:"]//g' | tr -d '\n' | xargs | cut -c1-30)
    
    # 创建目录: 平台/关键词/日期/
    local date_dir=$(date +%Y-%m-%d)
    local save_dir="$IMAGE_DIR/$platform/$clean_keyword/$date_dir"
    mkdir -p "$save_dir"
    
    # 生成文件名
    local timestamp=$(date +%H%M%S)
    local filename="img_${timestamp}.png"
    local filepath="$save_dir/$filename"
    
    # 下载
    echo "🔗 URL: $url"
    echo "📁 保存到: $filepath"
    
    if curl -sL -o "$filepath" "$url"; then
        echo "✅ 下载成功!"
        
        # 创建软链接（最新图片）
        local latest_link="$IMAGE_DIR/$platform/latest.png"
        rm -f "$latest_link"
        ln -s "$filepath" "$latest_link"
        
        # 记录日志
        local log_file="$IMAGE_DIR/$platform/history.log"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] $clean_keyword - $filename - $url" >> "$log_file"
        
        echo ""
        echo "📂 目录结构:"
        ls -la "$save_dir"
        
    else
        echo "❌ 下载失败"
        return 1
    fi
}

# 查看历史
history() {
    local platform="${1:-zhipu}"
    local log_file="$IMAGE_DIR/$platform/history.log"
    
    if [ -f "$log_file" ]; then
        echo "=== $platform 图片历史 ==="
        tail -20 "$log_file"
    else
        echo "无历史记录"
    fi
}

# 清理过期文件
cleanup() {
    local days="${1:-7}"
    
    echo "=== 清理 $days 天前的文件 ==="
    find "$IMAGE_DIR" -name "*.png" -mtime +$days -delete
    echo "✅ 清理完成"
}

# 主逻辑
main() {
    case "$1" in
        help|--help|-h|"")
            help
            ;;
        history|hist)
            history "$2"
            ;;
        cleanup|clean)
            cleanup "$2"
            ;;
        *)
            if [ -z "$1" ] || [ -z "$2" ]; then
                help
            else
                download_image "$1" "$2" "$3"
            fi
            ;;
    esac
}

main "$@"
