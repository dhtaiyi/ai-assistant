#!/bin/bash

# 同步远程网络文件夹到本地
# 每30分钟检查并下载新文件

set -e

# 配置
REMOTE_URL="http://129.211.82.60:8888"
LOCAL_DIR="/mnt/f/Program Files/WeGame/dhtaiyi/openclaw douyin work"
LOG_FILE="/tmp/sync_remote_files.log"
LOCK_FILE="/tmp/sync_remote_files.lock"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 获取远程文件列表
fetch_remote_files() {
    curl -s "$REMOTE_URL/" 2>/dev/null | grep -oP 'href="[^"]+\.(flv|mp4|txt)"' | sed 's/href="//;s/"//g' | grep -v "^\s*$" || true
}

# 获取远程文件大小
get_remote_size() {
    local filename="$1"
    curl -sI "$REMOTE_URL/$filename" 2>/dev/null | grep -i "Content-Length" | awk '{print $2}' | tr -d '\r\n' || echo "0"
}

# 获取本地文件大小
get_local_size() {
    local filepath="$1"
    if [ -f "$filepath" ]; then
        stat -c%s "$filepath" 2>/dev/null || echo "0"
    else
        echo "0"
    fi
}

# 下载文件
download_file() {
    local filename="$1"
    local remote_file="$REMOTE_URL/$filename"
    local local_file="$LOCAL_DIR/$filename"
    
    log "下载: $filename"
    
    # 后台下载 (使用 nohup)
    nohup curl -L -o "$local_file" "$remote_file" >> "$LOG_FILE" 2>&1 &
    
    log "已启动后台下载: $filename"
}

# 检测最近1天的文件
check_recent_files() {
    log "========== 检测最近1天的文件 =========="
    
    # 获取最近1天修改过的本地文件
    recent_files=$(find "$LOCAL_DIR" -type f -mtime -1 -name "*.flv" -o -name "*.mp4" -o -name "*.txt" 2>/dev/null | xargs -I {} basename {})
    
    if [ -z "$recent_files" ]; then
        log "最近1天没有修改过的文件"
        return
    fi
    
    log "最近1天修改过的文件:"
    for file in $recent_files; do
        log "  - $file"
    done
    
    # 获取远程文件列表
    remote_files=$(fetch_remote_files)
    
    log ""
    log "对比结果:"
    mismatched=0
    for local_file in $recent_files; do
        # 检查远程是否存在该文件
        if echo "$remote_files" | grep -q "^$local_file$"; then
            local_size=$(get_local_size "$LOCAL_DIR/$local_file")
            remote_size=$(get_remote_size "$local_file")
            
            if [ "$local_size" -eq "$remote_size" ]; then
                log "✅ $local_file - 完整 ($local_size bytes)"
            else
                log "❌ $local_file - 不完整 (本地: $local_size, 远程: $remote_size)"
                download_file "$local_file"
                ((mismatched++))
            fi
        else
            log "⏭️ $local_file - 远程不存在"
        fi
    done
    
    if [ $mismatched -gt 0 ]; then
        log "共启动 $mismatched 个下载任务"
    fi
    
    log "========== 检测完成 =========="
}

# 同步所有文件
sync_files() {
    log "========== 开始同步文件 =========="
    
    # 检查远程服务器是否可达
    if ! curl -s --connect-timeout 5 "$REMOTE_URL/" > /dev/null 2>&1; then
        log "错误: 无法连接到 $REMOTE_URL"
        exit 1
    fi
    
    # 获取远程文件列表
    remote_files=$(fetch_remote_files)
    
    if [ -z "$remote_files" ]; then
        log "警告: 无法获取远程文件列表"
        exit 1
    fi
    
    # 比对并下载新文件或不完整的文件
    downloaded=0
    for remote_file in $remote_files; do
        local_file="$LOCAL_DIR/$remote_file"
        
        # 获取远程文件大小
        remote_size=$(get_remote_size "$remote_file")
        
        # 获取本地文件大小
        local_size=$(get_local_size "$local_file")
        
        # 检查是否需要下载
        if [ "$local_size" -eq 0 ]; then
            # 文件不存在，下载
            log "新文件: $remote_file (远程: $remote_size bytes)"
            download_file "$remote_file"
            ((downloaded++))
        elif [ "$remote_size" -gt 0 ] && [ "$local_size" -ne "$remote_size" ]; then
            # 文件大小不一致，重新下载
            log "文件不完整: $remote_file (本地: $local_size, 远程: $remote_size bytes)"
            download_file "$remote_file"
            ((downloaded++))
        fi
    done
    
    if [ $downloaded -eq 0 ]; then
        log "没有新文件需要下载"
    else
        log "共启动 $downloaded 个下载任务"
    fi
    
    log "========== 同步完成 =========="
}

# 主逻辑
main() {
    case "${1:-sync}" in
        check)
            check_recent_files
            ;;
        sync|*)
            sync_files
            ;;
    esac
}

# 检查是否已在运行
if [ -f "$LOCK_FILE" ]; then
    pid=$(cat "$LOCK_FILE")
    if kill -0 "$pid" 2>/dev/null; then
        log "任务已在运行中 (PID: $pid)"
        exit 0
    fi
    rm -f "$LOCK_FILE"
fi

# 记录PID
echo $$ > "$LOCK_FILE"

# 执行主逻辑
main "$@"

# 清理锁文件
rm -f "$LOCK_FILE"
