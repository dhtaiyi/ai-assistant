#!/bin/bash

# 智谱 AI Skill - 对话/识图/生图/生视频
# API Key: bd1e2312f8bc4539ae2ae2645905576d.RISv3Rf49m3C3tCG
# 用法: zhipu <命令> [参数]

set -e

# 配置
ZHIPU_API_KEY="${ZHIPU_API_KEY:-bd1e2312f8bc4539ae2ae2645905576d.RISv3Rf49m3C3tCG}"
BASE_URL="https://open.bigmodel.cn/api/paas/v3/model-api"

# 日志
log() {
    echo "[$(date '+%H:%M:%S')] $1"
}

# 帮助
help() {
    cat << EOF
╔═══════════════════════════════════════════════════════╗
║  智谱 AI Skill                                      ║
║  对话 / 识图 / 生图 / 生视频                         ║
╚═══════════════════════════════════════════════════════╝

用法: zhipu <命令> [参数]

命令:
  chat <问题>        对话 (chatglm_turbo)
  vision <图片>      识图 (glm-4v)
  image <提示词>     文生图 (cogview-3)
  video <提示词>     文生视频 (cogvideo)
  test               测试所有功能
  help               显示帮助

示例:
  zhipu chat "你好"
  zhipu vision "https://xxx.com/img.jpg"
  zhipu image "一只可爱的猫"
  zhipu video "一只猫在跑"

前置配置:
  export ZHIPU_API_KEY="bd1e2312f8bc..."

EOF
}

# 对话
chat() {
    local prompt="$*"
    
    if [ -z "$prompt" ]; then
        echo "用法: zhipu chat <问题>"
        return 1
    fi
    
    log "对话中..."
    
    local response=$(curl -s -X POST "$BASE_URL/chatglm_turbo/invoke" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $ZHIPU_API_KEY" \
      -d "{\"prompt\": \"$prompt\"}")
    
    if echo "$response" | grep -q '"success":true'; then
        local result=$(echo "$response" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['data']['choices'][0]['content'])" 2>/dev/null)
        echo "✅ $result"
    else
        echo "❌ 失败: $response"
    fi
}

# 识图 (Vision)
vision() {
    local image_url="$1"
    local prompt="${2:-描述这张图片}"
    
    if [ -z "$image_url" ]; then
        echo "用法: zhipu vision <图片URL> [问题]"
        echo "示例: zhipu vision https://xxx.com/img.jpg 这图里有什么"
        return 1
    fi
    
    log "识图中..."
    
    local response=$(curl -s -X POST "$BASE_URL/glm-4v/invoke" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $ZHIPU_API_KEY" \
      -d "{\"prompt\": \"$prompt\", \"image_url\": \"$image_url\"}")
    
    if echo "$response" | grep -q '"success":true'; then
        local result=$(echo "$response" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['data']['choices'][0]['content'])" 2>/dev/null)
        echo "✅ $result"
    else
        echo "❌ 失败: $response"
    fi
}

# 文生图
image() {
    local prompt="$*"
    
    if [ -z "$prompt" ]; then
        echo "用法: zhipu image <提示词>"
        return 1
    fi
    
    log "生成图像中..."
    
    local response=$(curl -s -X POST "$BASE_URL/cogview-3/invoke" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $ZHIPU_API_KEY" \
      -d "{\"prompt\": \"$prompt\"}")
    
    if echo "$response" | grep -q '"success":true'; then
        local url=$(echo "$response" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['data']['image_links'][0]['url'])" 2>/dev/null)
        echo "✅ 生成成功!"
        echo "🔗 $url"
        echo ""
        echo "📥 自动下载到分类目录..."
        /root/.openclaw/workspace/scripts/save-image.sh "$prompt" "$url" zhipu
    else
        echo "❌ 失败: $response"
    fi
}

# 文生视频 (异步)
video() {
    local prompt="$*"
    
    if [ -z "$prompt" ]; then
        echo "用法: zhipu video <提示词>"
        return 1
    fi
    
    log "生成视频中... (首次可能需要 1-2 分钟)"
    
    # 提交任务
    local task=$(curl -s -X POST "$BASE_URL/cogvideo/async/invoke" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $ZHIPU_API_KEY" \
      -d "{\"prompt\": \"$prompt\"}")
    
    if echo "$task" | grep -q '"success":true'; then
        local task_id=$(echo "$task" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['data']['task_id'])" 2>/dev/null)
        echo "✅ 任务已提交: $task_id"
        echo "🔄 等待生成..."
        
        # 轮询结果 (最多 120 秒)
        local count=0
        while [ $count -lt 60 ]; do
            sleep 2
            count=$((count + 1))
            
            local result=$(curl -s -X GET "$BASE_URL/cogvideo/async/$task_id" \
              -H "Authorization: Bearer $ZHIPU_API_KEY")
            
            if echo "$result" | grep -q '"task_status":"SUCCESS"'; then
                local url=$(echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['data']['video_info'][0]['video_url'])" 2>/dev/null)
                echo "✅ 生成成功!"
                echo "🔗 $url"
                return 0
            elif echo "$result" | grep -q '"task_status":"FAILED"'; then
                echo "❌ 生成失败: $result"
                return 1
            fi
            
            echo -n "."
        done
        
        echo ""
        echo "⏰ 超时，请稍后查询: zhipu video-status $task_id"
        
    else
        echo "❌ 提交失败: $task"
    fi
}

# 测试所有功能
test_all() {
    echo "╔═══════════════════════════════════════════════╗"
    echo "║  智谱 AI 功能测试                             ║"
    echo "╚═══════════════════════════════════════════════╝"
    echo ""
    
    echo "1. 对话测试:"
    local response=$(curl -s -X POST "$BASE_URL/chatglm_turbo/invoke" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $ZHIPU_API_KEY" \
      -d '{"prompt": "hi"}')
    if echo "$response" | grep -q '"success":true'; then
        echo "✅ 对话: $(echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['choices'][0]['content'][:50])" 2>/dev/null)"
    else
        echo "❌ 对话失败"
    fi
    
    echo ""
    echo "2. 文生图测试:"
    local img_response=$(curl -s -X POST "$BASE_URL/cogview-3/invoke" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $ZHIPU_API_KEY" \
      -d '{"prompt": "一只猫"}')
    if echo "$img_response" | grep -q '"success":true'; then
        echo "✅ 文生图: 成功"
    else
        echo "❌ 文生图失败"
    fi
    
    echo ""
    echo "✅ 测试完成"
}

# 主逻辑
main() {
    case "$1" in
        chat|talk)
            shift
            chat "$@"
            ;;
        vision|see|recognize)
            shift
            vision "$@"
            ;;
        image|img|pic)
            shift
            image "$@"
            ;;
        video|animate)
            shift
            video "$@"
            ;;
        test|check)
            test_all
            ;;
        help|--help|-h|"")
            help
            ;;
        *)
            help
            ;;
    esac
}

main "$@"
