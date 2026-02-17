#!/bin/bash

# 图像生成 Skill - 支持多个平台
# 用法: image-gen <平台> <提示词> [选项]

set -e

# 配置 - 在这里填入你的 API Key
OPENAI_API_KEY="${OPENAI_API_KEY:-}"
QWEN_API_KEY="${QWEN_API_KEY:-sk-sp-645687cbbd854d2ab15251e5086e5ac5}"
BAIDU_API_KEY="${BAIDU_API_KEY:-}"
BAIDU_SECRET_KEY="${BAIDU_SECRET_KEY:-}"

# 日志
log() {
    echo "[$(date '+%H:%M:%S')] $1"
}

# 帮助
help() {
    cat << EOF
╔═══════════════════════════════════════════════════════╗
║  图像生成 Skill                                       ║
╚═══════════════════════════════════════════════════════╝

用法: image-gen <命令> [参数]

命令:
  openai <提示词>     OpenAI DALL-E 生图
  qwen <提示词>       通义万相生图
  baidu <提示词>      百度文心一言生图
  test                测试各平台连接
  help                显示帮助

示例:
  image-gen openai "一只可爱的猫在草地上"
  image-gen qwen "现代城市夜景，赛博朋克风格"
  image-gen test

前置配置:
  export OPENAI_API_KEY="sk-..."
  export QWEN_API_KEY="sk-..."
  export BAIDU_API_KEY="..."
  export BAIDU_SECRET_KEY="..."

EOF
}

# OpenAI DALL-E 3
gen_openai() {
    local prompt="$*"
    
    if [ -z "$prompt" ]; then
        echo "用法: image-gen openai <提示词>"
        return 1
    fi
    
    if [ -z "$OPENAI_API_KEY" ]; then
        echo "❌ 未设置 OPENAI_API_KEY"
        echo "export OPENAI_API_KEY=\"sk-...\""
        return 1
    fi
    
    log "OpenAI DALL-E 3 生图中..."
    
    local response=$(curl -s -X POST "https://api.openai.com/v1/images/generations" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $OPENAI_API_KEY" \
      -d '{
        "model": "dall-e-3",
        "prompt": "'"$prompt"'",
        "n": 1,
        "size": "1024x1024",
        "quality": "standard"
      }')
    
    if echo "$response" | grep -q "url"; then
        local url=$(echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',[{}])[0].get('url',''))" 2>/dev/null)
        echo "✅ 生成成功!"
        echo "🔗 $url"
    else
        echo "❌ 生成失败"
        echo "$response"
    fi
}

# 通义万相 (Qwen)
gen_qwen() {
    local prompt="$*"
    
    if [ -z "$prompt" ]; then
        echo "用法: image-gen qwen <提示词>"
        return 1
    fi
    
    log "通义万相生图中..."
    
    local response=$(curl -s -X POST "https://dashscope.aliyuncs.com/api/v1/services/aigc/images/generation/generation" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $QWEN_API_KEY" \
      -d '{
        "model": "wanx-v1",
        "input": {
          "prompt": "'"$prompt"'"
        },
        "parameters": {
          "n": 1,
          "size": "1024*1024"
        }
      }')
    
    if echo "$response" | grep -q "output"; then
        local url=$(echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('output',{}).get('task_results',[{}])[0].get('url',''))" 2>/dev/null)
        echo "✅ 生成成功!"
        echo "🔗 $url"
    else
        echo "❌ 生成失败"
        echo "$response"
    fi
}

# 百度文心一言
gen_baidu() {
    local prompt="$*"
    
    if [ -z "$prompt" ]; then
        echo "用法: image-gen baidu <提示词>"
        return 1
    fi
    
    log "百度文心一言生图中..."
    
    # 获取 access_token
    local token=$(curl -s "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=$BAIDU_API_KEY&client_secret=$BAIDU_SECRET_KEY" | \
      python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null)
    
    if [ -z "$token" ]; then
        echo "❌ 获取 token 失败"
        return 1
    fi
    
    local response=$(curl -s -X POST "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/text2image/v2" \
      -H "Content-Type: application/json" \
      -d '{
        "prompt": "'"$prompt"'",
        "size": "1024*1024",
        "n": 1
      }' \
      "?access_token=$token")
    
    if echo "$response" | grep -q "image"; then
        echo "✅ 生成成功!"
        echo "$response" | python3 -c "import sys,json; r=json.load(sys.stdin); print(r.get('data',{}).get('images',[{}])[0].get('image',''))"
    else
        echo "❌ 生成失败"
        echo "$response"
    fi
}

# 测试连接
test_connection() {
    echo "╔═══════════════════════════════════════════════╗"
    echo "║  测试各平台连接                               ║"
    echo "╚═══════════════════════════════════════════════╝"
    echo ""
    
    echo "OpenAI:"
    if [ -n "$OPENAI_API_KEY" ]; then
        echo "✅ Key 已设置"
    else
        echo "❌ 未设置 (export OPENAI_API_KEY=\"sk-...\")"
    fi
    
    echo ""
    echo "通义万相:"
    if [ -n "$QWEN_API_KEY" ]; then
        echo "✅ Key 已设置: ${QWEN_API_KEY:0:10}..."
    else
        echo "❌ 未设置"
    fi
    
    echo ""
    echo "百度文心:"
    if [ -n "$BAIDU_API_KEY" ]; then
        echo "✅ API Key 已设置"
    else
        echo "❌ 未设置 (export BAIDU_API_KEY=\"...\")"
    fi
}

# 主逻辑
main() {
    case "$1" in
        openai|dalle)
            shift
            gen_openai "$@"
            ;;
        qwen|wanxiang)
            shift
            gen_qwen "$@"
            ;;
        baidu|ernie)
            shift
            gen_baidu "$@"
            ;;
        test|check)
            test_connection
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
