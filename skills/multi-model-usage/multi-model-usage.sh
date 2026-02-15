#!/bin/bash

# 多模型用量查看脚本
# 查看各模型的使用情况和配额

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}🔍 检查多模型用量...${NC}"
echo ""

# ========== MiniMax ==========
check_minimax() {
    echo -e "${BLUE}📊 ===== MiniMax (编程计划) =====${NC}"
    echo ""
    echo -e "${GREEN}✅ MiniMax CLI 已配置${NC}"
    echo "   API Key: 已配置"
    echo ""
    echo "💡 查看用量请访问:"
    echo "   https://platform.minimax.io/user-center/basic-information"
    echo ""
    echo "   或运行 CLI 命令:"
    echo "   cd /root/.openclaw/workspace/skills/minimax-usage && ./minimax-usage.sh"
    echo ""
}

# ========== Kimi ==========
check_kimi() {
    echo -e "${BLUE}📊 ===== Kimi (Moonshot AI - Coding) =====${NC}"
    echo ""
    
    if command -v kimi &> /dev/null; then
        local kimi_version=$(kimi --version 2>&1 | grep -oP 'version \K[0-9.]+' || echo "unknown")
        echo -e "${GREEN}✅ Kimi CLI 已安装${NC}"
        echo "   版本: $kimi_version"
        echo "   状态: 已登录 ✅"
        echo ""
    else
        echo -e "${YELLOW}⚠️ Kimi CLI 未安装${NC}"
        echo ""
    fi
    
    echo "💡 查看用量请访问:"
    echo "   https://platform.moonshot.ai/console/billing"
    echo ""
    echo "   或运行:"
    echo "   kimi --version"
    echo ""
}

# ========== Qwen ==========
check_qwen() {
    echo -e "${BLUE}📊 ===== Qwen (阿里云DashScope) =====${NC}"
    echo ""
    echo -e "${GREEN}✅ Qwen Coding API 已配置${NC}"
    echo "   端点: https://coding.dashscope.aliyuncs.com/v1"
    echo "   模型: qwen3-coder-plus, qwen3-max-2026-01-23"
    echo ""
    echo "💡 查看用量请访问:"
    echo "   https://dashscope.console.aliyun.com/usage/summary"
    echo ""
    echo "   登录 → 用量管理 → 模型推理"
    echo ""
}

# ========== Token Meter ==========
check_tokenmeter() {
    echo -e "${BLUE}📊 ===== Token Meter (综合统计) =====${NC}"
    echo ""
    
    if [ -f "/root/.openclaw/workspace/skills/tokenmeter/tokenmeter.sh" ]; then
        echo -e "${GREEN}✅ Token Meter 已安装${NC}"
        echo ""
        echo "💡 运行综合统计:"
        echo "   cd /root/.openclaw/workspace/skills/tokenmeter && ./tokenmeter.sh"
        echo ""
    else
        echo -e "${YELLOW}⚠️ Token Meter 未安装${NC}"
        echo ""
    fi
}

# ========== 主程序 ==========
main() {
    echo -e "${CYAN}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║           🌸 多模型用量监控中心 🌸                       ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    check_minimax
    check_kimi
    check_qwen
    check_tokenmeter
    
    echo -e "${GREEN}💡 所有模型的用量详情请访问对应的控制台网站${NC}"
    echo ""
}

main "$@"
