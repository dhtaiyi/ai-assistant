#!/bin/bash

# GitHub 工具脚本
# 支持：搜索仓库、查看信息、获取 Issues

GITHUB_API="https://api.github.com"

case "$1" in
    search)
        # 搜索仓库
        query=$2
        curl -s "${GITHUB_API}/search/repositories?q=${query}&per_page=5" | \
            jq -r '.items[] | "★ \(.full_name)\n  ⭐ \(.stargazers_count) | 📝 \(.description)\n"'
        ;;
    info)
        # 查看仓库信息
        repo=$2
        curl -s "${GITHUB_API}/repos/${repo}" | jq '.'
        ;;
    issues)
        # 查看 Issues
        repo=$2
        curl -s "${GITHUB_API}/repos/${repo}/issues?state=open&per_page=5" | \
            jq -r '.[] | "● #\(.number): \(.title)\n  状态: \(.state) | 评论: \(.comments)\n"'
        ;;
    trending)
        # 今日趋势
        curl -s "${GITHUB_API}/search/repositories?q=created:>$(date +%Y-%m-%d)&sort=stars&order=desc&per_page=5" | \
            jq -r '.items[] | "★ \(.full_name) - ⭐ \(.stargazers_count)\n"'
        ;;
    *)
        echo "GitHub 工具"
        echo ""
        echo "用法: $0 <命令> [参数]"
        echo ""
        echo "命令:"
        echo "  search <关键词>  - 搜索仓库"
        echo "  info <owner/repo> - 查看仓库信息"
        echo "  issues <owner/repo> - 查看 Issues"
        echo "  trending         - 今日趋势仓库"
        ;;
esac
