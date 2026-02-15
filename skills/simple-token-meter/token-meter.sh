#!/bin/bash

# 简单Token用量追踪 - 简洁版
# 追踪OpenClaw会话的Token使用情况

# 颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     🪙 OpenClaw Token用量追踪     ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════╝${NC}"
echo ""

# 检查会话目录
SESSION_DIR="/root/.openclaw/agents"
if [ ! -d "$SESSION_DIR" ]; then
    echo -e "${YELLOW}⚠️ 未找到会话目录${NC}"
    exit 0
fi

# 统计变量
total_input=0
total_output=0
total_cache_read=0
total_cache_write=0
session_count=0
found_data=false

echo -e "${BLUE}📂 分析会话...${NC}"
echo ""

# 查找并统计所有会话
for file in $(find "$SESSION_DIR" -name "*.jsonl" -type f 2>/dev/null); do
    # 提取使用情况
    input=$(grep -oP '"input"\s*:\s*[0-9]+' "$file" 2>/dev/null | grep -oP '[0-9]+' | awk '{sum+=$1} END {print sum+0}')
    output=$(grep -oP '"output"\s*:\s*[0-9]+' "$file" 2>/dev/null | grep -oP '[0-9]+' | awk '{sum+=$1} END {print sum+0}')
    cache_read=$(grep -oP '"cacheRead"\s*:\s*[0-9]+' "$file" 2>/dev/null | grep -oP '[0-9]+' | awk '{sum+=$1} END {print sum+0}')
    cache_write=$(grep -oP '"cacheWrite"\s*:\s*[0-9]+' "$file" 2>/dev/null | grep -oP '[0-9]+' | awk '{sum+=$1} END {print sum+0}')
    model=$(grep -oP '"modelId"\s*:\s*"\K[^"]+' "$file" 2>/dev/null | head -1)
    
    if [ -n "$input" ] && [ "$input" -gt 0 ]; then
        found_data=true
        session_count=$((session_count + 1))
        total_input=$((total_input + input))
        total_output=$((total_output + output))
        total_cache_read=$((total_cache_read + cache_read))
        total_cache_write=$((total_cache_write + cache_write))
        
        # 显示
        short_file=$(basename "$file" | cut -c1-32)
        short_model=$(echo "$model" | cut -c1-14)
        printf "  %-32s %s 📥%'d 📤%'d\n" "$short_file" "$short_model" "$input" "$output"
    fi
done

echo ""
echo -e "${GREEN}✅ 分析完成！${NC}"
echo ""

# 显示汇总
echo -e "${BLUE}📊 Token用量汇总${NC}"
echo "═════════════════════════════════════════"

if [ "$found_data" = true ]; then
    total_tokens=$((total_input + total_output))
    all_tokens=$((total_tokens + total_cache_read + total_cache_write))
    
    echo -e "  📁 会话数:        ${session_count}"
    echo -e "  📥 输入Token:    ${total_input}"
    echo -e "  📤 输出Token:    ${total_output}"
    echo -e "  🔁 缓存读取:      ${total_cache_read}"
    echo -e "  💾 缓存写入:      ${total_cache_write}"
    echo -e "  ─────────────────────────────────"
    echo -e "  🔢 总会话Token:  ${total_tokens}"
    echo -e "  🏁 全部Token:    ${all_tokens}"
    echo ""
    
    echo -e "${GREEN}💡 提示${NC}"
    echo "─────────────────────────────────────"
    echo -e "  • 输入Token: 发送给AI的提示词"
    echo -e "  • 输出Token: AI生成的回答"
    echo -e "  • 缓存读取: 复用之前缓存的数据（省💰）"
    echo -e "  • 缓存写入: 创建新的缓存内容"
    echo ""
    echo -e "${YELLOW}📍 查看详细用量:${NC}"
    echo "  • MiniMax: https://platform.minimax.io/user-center/basic-information"
    echo "  • Kimi: https://platform.moonshot.ai/console/billing"
    echo "  • Qwen: https://dashscope.console.aliyun.com/usage/summary"
else
    echo -e "  ${YELLOW}暂无会话数据${NC}"
    echo ""
    echo -e "${CYAN}💡 开始对话后会自动追踪用量${NC}"
fi

echo ""
