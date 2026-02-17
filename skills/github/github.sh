#!/bin/bash

API="https://api.github.com"

case "$1" in
    search)
        query=$2
        echo "🔍 搜索仓库: $query"
        curl -s "${API}/search/repositories?q=${query}&per_page=10" | \
            jq -r '.items[] | "⭐ \(.stargazers_count) | ★ \(.full_name)\n  📝 \(.description)\n"' | head -20
        ;;
    info)
        repo=$2
        echo "📊 仓库信息: $repo"
        curl -s "${API}/repos/${repo}" | jq '{名称: .full_name, 描述: .description, ⭐: .stargazers_count, 🔀: .forks_count, 👀: .watchers_count, 📅创建于: .created_at, 🔗: .html_url}'
        ;;
    issues)
        repo=$2
        echo "📋 Issues: $repo"
        curl -s "${API}/repos/${repo}/issues?state=open&per_page=10" | \
            jq -r '.[] | "● #\(.number) \(.title)\n  👤 \(.user.login) | 💬 \(.comments) 评论\n"' | head -30
        ;;
    trending)
        echo "🔥 今日趋势仓库"
        today=$(date +%Y-%m-%d)
        curl -s "${API}/search/repositories?q=created:>${today}&sort=stars&order=desc&per_page=10" | \
            jq -r '.items[] | "⭐ \(.stargazers_count) | ★ \(.full_name)\n  📝 \(.description)\n"' | head -40
        ;;
    files)
        repo=$2
        path=${3:-""}
        echo "📁 文件列表: $repo/$path"
        curl -s "${API}/repos/${repo}/contents/${path}" | \
            jq -r '.[] | if .type == "dir" then "📁 \(.name)/" else "📄 \(.name)" end' | head -20
        ;;
    *)
        echo "GitHub 工具"
        echo ""
        echo "用法: github.sh <命令> [参数]"
        echo ""
        echo "命令:"
        echo "  search <关键词>   - 搜索仓库"
        echo "  info <owner/repo> - 仓库信息"
        echo "  issues <owner/repo> - Issues"
        echo "  trending         - 今日趋势"
        echo "  files <owner/repo> [path] - 文件列表"
        ;;
esac
