#!/bin/bash

# Kimi CLI Skill for OpenClaw
# 基于官方文档: https://www.kimi.com/code/docs/kimi-cli/guides/getting-started.html
# 用法: kimi-code <命令> [参数]

set -e

# 配置
KIMI_CONFIG_DIR="${HOME}/.kimi"
KIMI_LOG_FILE="/tmp/kimi-skill.log"

# 日志
log() {
    echo "[$(date '+%H:%M:%S')] $1" | tee -a "$KIMI_LOG_FILE"
}

# 帮助
help() {
    cat << EOF
╔═══════════════════════════════════════════════════════════╗
║  Kimi CLI Skill for OpenClaw                               ║
║  官方文档: https://www.kimi.com/code/docs/kimi-cli/        ║
╚═══════════════════════════════════════════════════════════╝

📦 安装
   uv tool install --python 3.13 kimi-cli

🚀 快速开始
   1. 运行: kimi
   2. 输入: /login
   3. 选择平台 (推荐 Kimi Code)
   4. OAuth 授权

📖 使用方式
   kimi-code status        # 检查状态
   kimi-code test          # 测试连接
   kimi-code chat "问题"   # 对话
   kimi-code exec "命令"   # 执行命令
   kimi-code setup        # 配置向导

🛠️ 常用命令 (在 kimi 交互模式中)
   /login    登录/配置 API
   /help     查看帮助
   /init     分析项目生成 AGENTS.md
   /exit     退出

📝 示例
   kimi-code chat "用 Python 写快速排序"
   kimi-code exec "git status"

EOF
}

# 检查 Kimi CLI
check_kimi() {
    if ! command -v kimi &> /dev/null; then
        echo "❌ Kimi CLI 未安装"
        echo ""
        echo "安装方法:"
        echo "  uv tool install --python 3.13 kimi-cli"
        return 1
    fi
    echo "✅ Kimi CLI: $(kimi --version 2>&1)"
}

# 检查配置
check_config() {
    if [ ! -f "$KIMI_CONFIG_DIR/config.toml" ]; then
        echo "❌ 未配置 (config.toml 不存在)"
        echo ""
        echo "配置方法:"
        echo "  1. 运行: kimi"
        echo "  2. 输入: /login"
        echo "  3. 选择 Kimi Code 平台"
        echo "  4. OAuth 授权"
        return 1
    fi
    echo "✅ 已配置: $KIMI_CONFIG_DIR/config.toml"
}

# 测试连接
test_connection() {
    log "测试 Kimi CLI 连接..."
    
    # 测试配置是否有效
    local test_result=$(timeout 20 kimi --print --yolo --prompt "hi" 2>&1)
    
    if echo "$test_result" | grep -qi "LLM not set\|Error\|error\|401\|403"; then
        echo "❌ 连接失败"
        echo "$test_result" | head -5
        return 1
    fi
    
    echo "✅ 连接成功"
}

# 对话
chat() {
    local prompt="$*"
    
    if [ -z "$prompt" ]; then
        echo "用法: kimi-code chat <问题>"
        echo ""
        echo "示例:"
        echo "  kimi-code chat '用 Python 写快速排序'"
        return 1
    fi
    
    log "对话: $prompt"
    echo "---"
    
    timeout 120 kimi --print --yolo --prompt "$prompt" 2>&1
}

# 执行命令
exec_cmd() {
    local cmd="$*"
    
    if [ -z "$cmd" ]; then
        echo "用法: kimi-code exec <命令>"
        echo ""
        echo "示例:"
        echo "  kimi-code exec 'git status'"
        echo "  kimi-code exec 'ls -la'"
        return 1
    fi
    
    log "执行: $cmd"
    echo "---"
    
    timeout 120 kimi --print --yolo --prompt "执行命令: $cmd" 2>&1
}

# 配置向导
setup_wizard() {
    echo "╔════════════════════════════════════════════════════╗"
    echo "║  Kimi CLI 配置向导                                  ║"
    echo "╚════════════════════════════════════════════════════╝"
    echo ""
    echo "步骤:"
    echo ""
    echo "1️⃣  启动 Kimi CLI"
    echo "   /root/.local/bin/kimi"
    echo ""
    echo "2️⃣  输入配置命令"
    echo "   /login"
    echo ""
    echo "3️⃣  选择平台"
    echo "   1. Kimi Code (推荐 - OAuth 自动授权)"
    echo "   2. Moonshot AI (中国)"
    echo "   3. Moonshot AI (全球)"
    echo ""
    echo "4️⃣  OAuth 授权"
    echo "   - 选择 Kimi Code 后会自动打开浏览器"
    echo "   - 登录你的 Kimi 账号"
    echo ""
    echo "5️⃣  开始使用"
    echo "   帮我用 Python 写一个快速排序"
    echo ""
}

# 查看配置
show_config() {
    echo "╔════════════════════════════════════════════════════╗"
    echo "║  Kimi CLI 状态                                      ║"
    echo "╚════════════════════════════════════════════════════╝"
    echo ""
    
    check_kimi
    echo ""
    check_config
    echo ""
    
    if [ -f "$KIMI_CONFIG_DIR/config.toml" ]; then
        echo "配置文件内容:"
        echo "---"
        cat "$KIMI_CONFIG_DIR/config.toml"
        echo "---"
    fi
}

# 主逻辑
main() {
    mkdir -p "$KIMI_CONFIG_DIR"
    
    case "$1" in
        status|check)
            show_config
            ;;
        test)
            check_kimi
            echo ""
            check_config
            echo ""
            test_connection
            ;;
        chat|ask)
            shift
            if [ -z "$1" ]; then
                help
            else
                check_kimi && chat "$@"
            fi
            ;;
        exec|run|command)
            shift
            if [ -z "$1" ]; then
                help
            else
                check_kimi && exec_cmd "$@"
            fi
            ;;
        setup|config)
            setup_wizard
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
