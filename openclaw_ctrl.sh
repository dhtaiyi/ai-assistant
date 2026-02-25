#!/bin/bash
# OpenClaw 本地控制脚本

# 配置
GATEWAY_PORT=18789
WORKSPACE=/root/.openclaw/workspace

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 帮助信息
show_help() {
    echo -e "${BLUE}🌸 OpenClaw 本地控制脚本${NC}"
    echo ""
    echo "用法: $0 <命令> [参数]"
    echo ""
    echo "命令:"
    echo "  status          查看Gateway状态"
    echo "  sessions        列出所有会话"
    echo "  send <消息>     发送消息到主会话"
    echo "  logs [行数]     查看日志 (默认20行)"
    echo "  restart         重启Gateway"
    echo "  browser         浏览器状态"
    echo "  help           显示帮助"
    echo ""
    echo "示例:"
    echo "  $0 status"
    echo "  $0 sessions"
    echo "  $0 send 'Hello from CLI'"
    echo "  $0 logs 50"
    echo "  $0 restart"
}

# 查看状态
cmd_status() {
    echo -e "${BLUE}📊 Gateway 状态${NC}"
    echo "----------------------------------------"
    openclaw gateway status
}

# 会话列表
cmd_sessions() {
    echo -e "${BLUE}📋 会话列表${NC}"
    echo "----------------------------------------"
    openclaw sessions --json | python3 -m json.tool 2>/dev/null || openclaw sessions
}

# 发送消息
cmd_send() {
    local message="$1"
    if [ -z "$message" ]; then
        message="Hello from CLI - $(date)"
    fi
    
    echo -e "${BLUE}📤 发送消息${NC}"
    echo "----------------------------------------"
    echo "消息: $message"
    
    # 获取主会话ID
    local session_id=$(openclaw sessions --json 2>/dev/null | python3 -c "
import json, sys
data = json.load(sys.stdin)
for s in data.get('sessions', []):
    if 'agent:main:main' in s.get('key', ''):
        print(s.get('sessionId', ''))
        break
" 2>/dev/null)
    
    if [ -n "$session_id" ]; then
        openclaw agent --session-id "$session_id" --message "$message"
        echo -e "${GREEN}✅ 消息已发送${NC}"
    else
        echo -e "${RED}❌ 未找到主会话${NC}"
    fi
}

# 查看日志
cmd_logs() {
    local lines=${1:-20}
    echo -e "${BLUE}📜 Gateway 日志 (最近${lines}行)${NC}"
    echo "----------------------------------------"
    openclaw logs --tail $lines 2>/dev/null || echo "无法获取日志"
}

# 重启Gateway
cmd_restart() {
    echo -e "${YELLOW}🔄 重启Gateway${NC}"
    echo "----------------------------------------"
    openclaw gateway restart
    echo -e "${YELLOW}⏳ 等待Gateway重新启动...${NC}"
    sleep 3
    cmd_status
}

# 浏览器状态
cmd_browser() {
    echo -e "${BLUE}🌐 浏览器状态${NC}"
    echo "----------------------------------------"
    openclaw browser status 2>/dev/null || echo "浏览器未运行或不支持"
}

# 主函数
main() {
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi
    
    local command="$1"
    shift
    
    case "$command" in
        status)
            cmd_status
            ;;
        sessions)
            cmd_sessions
            ;;
        send)
            cmd_send "$@"
            ;;
        logs)
            cmd_logs "$@"
            ;;
        restart)
            cmd_restart
            ;;
        browser)
            cmd_browser
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}❌ 未知命令: $command${NC}"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
