#!/bin/bash

# 系统健康检查任务 - 自动修复版
# 检查关键服务和进程，如果异常则自动修复

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> /root/.openclaw/workspace/logs/health-check.log
}

echo -e "${CYAN}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║       🌸 系统健康检查任务监控 🌸              ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════╝${NC}"
echo ""
echo "检查时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# ========== 检查变量 ==========
all_ok=true
need_restart=false

# ========== 1. 检查关键端口 ==========
echo -e "${BLUE}📡 检查网络服务${NC}"
echo "─────────────────────────────────────────────"

# Port 3000 (Harmony AI)
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/ | grep -q "200"; then
    echo -e "  🌐 Port 3000 (网页):    ✅ 正常"
else
    echo -e "  🌐 Port 3000 (网页):    ❌ 异常 - 尝试重启..."
    log "Port 3000 异常，尝试重启服务器"
    cd /root/.openclaw/workspace/harmony-ai-app/Server
    pkill -f "node src/index.js" 2>/dev/null
    sleep 2
    nohup node src/index.js > /tmp/harmony.log 2>&1 &
    sleep 3
    
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/ | grep -q "200"; then
        echo -e "  🌐 Port 3000 (网页):    ✅ 已自动重启"
        log "Port 3000 已自动重启"
    else
        echo -e "  🌐 Port 3000 (网页):    ❌ 重启失败"
        log "Port 3000 重启失败"
        all_ok=false
    fi
fi

# Port 18789 (OpenClaw Gateway)
if curl -s -o /dev/null -w "%{http_code}" http://localhost:18789/api/health 2>/dev/null | grep -q "200"; then
    echo -e "  🦞 Port 18789 (Gateway): ✅ 正常"
else
    echo -e "  🦞 Port 18789 (Gateway): ⚠️ 异常"
    log "Gateway 异常"
fi

echo ""

# ========== 2. 检查关键进程 ==========
echo -e "${BLUE}📊 检查关键进程${NC}"
echo "─────────────────────────────────────────────"

# Node.js 服务器
if ps aux | grep -v grep | grep -q "node.*index.js"; then
    pid=$(ps aux | grep -v grep | grep "node.*index.js" | awk '{print $2}' | head -1)
    echo -e "  📄 Node.js 服务器:     ✅ 运行中 (PID: $pid)"
else
    echo -e "  📄 Node.js 服务器:     ❌ 未运行 - 尝试启动..."
    log "Node.js 服务器未运行，尝试启动"
    cd /root/.openclaw/workspace/harmony-ai-app/Server
    nohup node src/index.js > /tmp/harmony.log 2>&1 &
    sleep 3
    
    if ps aux | grep -v grep | grep -q "node.*index.js"; then
        pid=$(ps aux | grep -v grep | grep "node.*index.js" | awk '{print $2}' | head -1)
        echo -e "  📄 Node.js 服务器:     ✅ 已自动启动 (PID: $pid)"
        log "Node.js 已自动启动"
    else
        echo -e "  📄 Node.js 服务器:     ❌ 启动失败"
        log "Node.js 启动失败"
        all_ok=false
    fi
fi

# OpenClaw Gateway
if ps aux | grep -v grep | grep -q "openclaw-gateway"; then
    pid=$(ps aux | grep -v grep | grep "openclaw-gateway" | awk '{print $2}' | head -1)
    echo -e "  🦞 OpenClaw Gateway:   ✅ 运行中 (PID: $pid)"
else
    echo -e "  🦞 OpenClaw Gateway:   ⚠️ 未运行 (需要手动启动)"
    log "Gateway 未运行"
fi

echo ""

# ========== 3. 检查Cron任务 ==========
echo -e "${BLUE}⏰ Cron任务数量: $(crontab -l 2>/dev/null | grep -v "^#" | grep -c "[^*]") 个${NC}"
echo ""

# ========== 4. 系统资源 ==========
echo -e "${BLUE}💻 系统资源状态${NC}"
echo "─────────────────────────────────────────────"

load=$(uptime | awk -F'load average: ' '{print $2}')
echo -e "  📊 CPU 负载:           $load"

mem=$(free -h | awk '/^Mem:/ {printf "已用: %s / 总计: %s", $3, $2}')
echo -e "  🧠 内存使用:           $mem"

disk=$(df -h / | awk 'NR==2 {printf "已用: %s / 总计: %s (%s)", $3, $2, $5}')
echo -e "  💾 磁盘使用:           $disk"

echo ""

# ========== 总结 ==========
echo -e "${CYAN}═══════════════════════════════════════════════${NC}"
echo ""

if [ "$all_ok" = true ]; then
    echo -e "${GREEN}✅ 所有关键服务和进程都正常运行！${NC}"
    echo -e "${GREEN}🔒 自动修复功能已启用${NC}"
else
    echo -e "${RED}⚠️ 发现问题！已尝试自动修复${NC}"
    echo -e "${YELLOW}请检查日志: /root/.openclaw/workspace/logs/health-check.log${NC}"
fi

echo ""
echo -e "${GREEN}💡 检查完成${NC}"
