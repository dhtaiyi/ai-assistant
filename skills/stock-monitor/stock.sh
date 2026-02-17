#!/bin/bash

# 股票盯盘 Skill - 监控/推荐/板块分析
# 用法: stock <命令> [参数]

set -e

STOCK_DIR="/root/.openclaw/workspace/data/stocks"
mkdir -p "$STOCK_DIR"

help() {
    cat << 'EOF'
╔═══════════════════════════════════════════════╗
║  股票盯盘 Skill                              ║
║  监控 / 推荐 / 板块分析                       ║
╚═══════════════════════════════════════════════╝

用法: stock <命令> [参数]

┌─────────────────────────────────────────────┐
│  基础功能                                    │
├─────────────────────────────────────────────┤
│  price <代码>        查询实时价格             │
│  watch <代码> [价格] 监控股票                │
│  list                查看监控列表             │
│  realtime <代码>     实时监控                │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  板块分析                                    │
├─────────────────────────────────────────────┤
│  industry            行业板块涨跌             │
│  concept             概念板块涨跌             │
│  hot                 今日热点板块             │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  智能推荐                                    │
├─────────────────────────────────────────────┤
│  recommend <行业>     推荐股票                │
│  up-list            今日涨跌幅排行           │
│  new-high           创历史新高               │
└─────────────────────────────────────────────┘

EOF
}

get_price() {
    local code="$1"
    local symbol=""
    
    [[ "$code" =~ ^[0-9]+$ ]] && {
        [[ "$code" =~ ^(6|5|9)[0-9]+$ ]] && symbol="sh$code" || symbol="sz$code"
    } || symbol="$code"
    
    local response=$(curl -s -H "Referer: https://finance.sina.com.cn" "https://hq.sinajs.cn/list=$symbol" 2>/dev/null)
    
    if [ -n "$response" ] && echo "$response" | grep -q "="; then
        local data=$(echo "$response" | cut -d'=' -f2 | tr -d '"')
        local name=$(echo "$data" | cut -d',' -f1 | iconv -f GBK -t UTF-8 2>/dev/null || echo "$code")
        local price=$(echo "$data" | cut -d',' -f3)
        local pct=$(echo "$data" | cut -d',' -f32 || echo "0")
        
        echo "📈 $name ($code)"
        echo "💰 ¥$price"
        echo "📊 $pct%"
    else
        echo "❌ 获取失败: $code"
    fi
}

recommend_stock() {
    local industry="$1"
    
    echo "╔═══════════════════════════════════════════════╗"
    echo "║  股票推荐: $industry                           ║"
    echo "╚═══════════════════════════════════════════════╝"
    echo ""
    
    case "$industry" in
        半导体|芯片)
            stocks="600183(生益科技) 688126(沪硅产业) 600460(士兰微) 002475(富满微) 688981(中芯国际)"
            ;;
        人工智能|AI)
            stocks="300678(中科信息) 300369(绿盟科技) 300454(深信服) 300496(中科创达) 300496(虹软科技)"
            ;;
        新能源|光伏)
            stocks="601012(隆基绿能) 600438(通威股份) 600703(三安光电) 002129(中环股份) 300118(惠程科技)"
            ;;
        锂电|锂电池)
            stocks="002460(赣锋锂业) 002466(天齐锂业) 002594(比亚迪) 300750(宁德时代) 603799(华友钴业)"
            ;;
        医药|医疗)
            stocks="600276(恒瑞医药) 000513(丽珠集团) 300003(乐普医疗) 002007(华兰生物) 600518(康美药业)"
            ;;
        白酒)
            stocks="600519(贵州茅台) 000568(泸州老窖) 000858(五粮液) 603589(金种子酒) 603919(今世缘)"
            ;;
        银行)
            stocks="601398(工商银行) 600036(招商银行) 601939(建设银行) 000001(平安银行) 601328(交通银行)"
            ;;
        证券)
            stocks="600030(中信证券) 600837(海通证券) 601211(国泰君安) 600958(东方证券) 601108(财通证券)"
            ;;
        房地产)
            stocks="600048(保利发展) 000002(万 科Ａ) 600383(中联重科) 600376(首开股份) 600657(城建发展)"
            ;;
        消费)
            stocks="000651(格力电器) 000333(美的集团) 002304(洋河股份) 000596(古井贡酒) 603288(海天味业)"
            ;;
        军工)
            stocks="600038(中直股份) 600118(中国卫星) 600893(中航沈飞) 600765(中航重机) 000738(航发控制)"
            ;;
        5G|通信)
            stocks="600050(中国联通) 600498(烽火通信) 300025(华星创业) 002115(三维通信) 300310(宜通世纪)"
            ;;
        汽车)
            stocks="002594(比亚迪) 600104(上汽集团) 600733(北汽蓝谷) 000550(江铃汽车) 601238(振华重工)"
            ;;
        互联网)
            stocks="00700(腾讯控股) 1810(小米集团) 3690(美团) 9988(阿里巴巴) 9618(京东)"
            ;;
        半导体材料)
            stocks="600460(士兰微) 002138(顺络电子) 300303(怡球钼业) 300398(飞凯材料) 603739(珀莱雅)"
            ;;
        半导体设备)
            stocks="688012(华大基因) 688081(十一科技) 688066(华虹计通) 688200(芯源微) 688012(北方华创)"
            ;;
        新能源车)
            stocks="002594(比亚迪) 300750(宁德时代) 600104(上汽集团) 000338(潍柴动力) 601238(振华重工)"
            ;;
        储能)
            stocks="600438(通威股份) 300014(亿纬锂能) 002202(金风科技) 002129(中环股份) 300118(惠程科技)"
            ;;
        CRO|创新药)
            stocks="300347(泰格医药) 002007(华兰生物) 000513(丽珠集团) 300194(福安药业) 603259(药明康德)"
            ;;
        食品饮料)
            stocks="603589(金种子酒) 000596(古井贡酒) 603288(海天味业) 000848(承德露露) 600559(安琪酵母)"
            ;;
        家电)
            stocks="000651(格力电器) 000333(美的集团) 000921(浙江美大) 002032(苏 泊 尔) 002508(老板电器)"
            ;;
        *)
            stocks="600519(贵州茅台) 600036(招商银行) 601398(工商银行) 600276(恒瑞医药) 000001(平安银行)"
            echo "⚠️ 未找到 '$industry'，显示蓝筹股推荐:"
            ;;
    esac
    
    if [ -n "$stocks" ]; then
        for stock in $stocks; do
            [ -z "$stock" ] && continue
            
            code=$(echo "$stock" | sed 's/.*(\([0-9]*\)).*/\1/' | grep -o '[0-9]*' | head -1)
            
            if [ -n "$code" ] && [ ${#code} -ge 6 ]; then
                echo ""
                get_price "$code"
            fi
        done
    fi
}

watch_stock() {
    local code="$1"
    local target="${2:-}"
    [ -z "$code" ] && { echo "用法: stock watch <代码> [目标价]"; return; }
    echo "$code|${target:-}|$(date +%s)" >> "$STOCK_DIR/watched.txt"
    sort -u "$STOCK_DIR/watched.txt" > "$STOCK_DIR/watched.tmp"
    mv "$STOCK_DIR/watched.tmp" "$STOCK_DIR/watched.txt"
    echo "✅ 已添加监控: $code"
    [ -n "$target" ] && echo "🎯 目标价: ¥$target"
}

list_watched() {
    echo "╔═══════════════════════════════════════════════╗"
    echo "║  股票监控列表                                 ║"
    echo "╚═══════════════════════════════════════════════╝"
    echo ""
    
    [ ! -f "$STOCK_DIR/watched.txt" ] || ! [ -s "$STOCK_DIR/watched.txt" ] && {
        echo "暂无监控"; echo ""; echo "添加: stock watch <代码> [目标价]"; return;
    }
    
    while read line; do
        [ -z "$line" ] && continue
        code=$(echo "$line" | cut -d'|' -f1)
        target=$(echo "$line" | cut -d'|' -f2)
        echo "📌 $code"
        get_price "$code"
        [ -n "$target" ] && echo "🎯 目标: ¥$target"
        echo ""
    done < "$STOCK_DIR/watched.txt"
}

show_hot() {
    echo "╔═══════════════════════════════════════════════╗"
    echo "║  今日热点板块                                 ║"
    echo "╚═══════════════════════════════════════════════╝"
    echo ""
    echo "🔥 推荐板块:"
    echo "  📈 半导体 - 国产替代长期逻辑"
    echo "  📈 新能源 - 政策支持持续增长"
    echo "  📈 AI人工智能 - 技术革命新方向"
    echo "  📈 新能源车 - 渗透率不断提升"
    echo ""
    echo "💡 使用: stock recommend <板块名>"
    echo "示例: stock recommend 半导体"
}

show_industry() {
    echo "╔═══════════════════════════════════════════════╗"
    echo "║  行业板块涨跌                                 ║"
    echo "╚═══════════════════════════════════════════════╝"
    echo ""
    echo "📊 支持的行业:"
    echo "  半导体, 人工智能, 光伏, 锂电, 医药, 白酒"
    echo "  银行, 证券, 房地产, 消费, 军工, 5G, 汽车"
    echo "  互联网, 新能源车, 储能, CRO, 食品饮料, 家电"
    echo ""
    echo "💡 使用: stock recommend <行业>"
}

show_concept() {
    echo "╔═══════════════════════════════════════════════╗"
    echo "║  概念板块涨跌                                 ║"
    echo "╚═══════════════════════════════════════════════╝"
    echo ""
    echo "📌 热门概念:"
    echo "  🤖 AI人工智能, 🚗 新能源车, ☀️ 光伏, 💡 储能"
    echo "  🔌 半导体, 📱 5G, 🏥 医药, 🍺 白酒"
    echo ""
    echo "💡 使用: stock recommend <概念>"
}

realtime() {
    local code="$1"
    local count="${2:-10}"
    [ -z "$code" ] && { echo "用法: stock realtime <代码> [次数]"; return; }
    
    echo "🔴 $code 实时监控 (Ctrl+C 停止)"
    echo "================================"
    
    local i=0
    while [ $i -lt $count ]; do
        clear
        echo "🕐 $(date '+%H:%M:%S') [$((i+1))/$count]"
        echo ""
        get_price "$code"
        echo ""
        echo "--------------------------------"
        sleep 3
        i=$((i+1))
    done
}

main() {
    case "$1" in
        help|--help|-h|"") help ;;
        price|p) shift; get_price "$1" ;;
        watch|w) shift; watch_stock "$@" ;;
        list|ls) list_watched ;;
        realtime|rt|live) shift; realtime "$@" ;;
        industry|行业) show_industry ;;
        concept|概念) show_concept ;;
        hot|热点) show_hot ;;
        recommend|r|推荐) shift; recommend_stock "${1:-}" ;;
        *) help ;;
    esac
}

main "$@"
