# 使用 Claude Code CLI 调用 MCP

## 前提条件

1. 安装 Claude Code CLI
2. 配置 xiaohongshu-mcp MCP 服务器

## 配置方法

### 1. 创建 MCP 配置文件

```bash
mkdir -p ~/.claude
cat > ~/.claude/mcp.json << 'JSON'
{
  "mcpServers": {
    "xiaohongshu": {
      "command": "docker",
      "args": [
        "exec", "-i", "xiaohongshu-mcp",
        "xiaohongshu-mcp", "--port", "18060"
      ],
      "disabled": false
    }
  }
}
JSON
```

### 2. 重启 Claude Code

### 3. 使用 MCP 工具

```bash
# 检查登录状态
claude "check_login_status"

# 获取用户信息  
claude "user_profile with user_id='xxx'"

# 发布内容
claude "publish_content with title='标题', content='内容', images=['path/to/image.jpg']"
```

## 可用工具

- `check_login_status` - 检查登录状态
- `publish_content` - 发布图文
- `publish_with_video` - 发布视频
- `list_feeds` - 获取推荐列表
- `search_feeds` - 搜索内容
- `get_feed_detail` - 获取帖子详情
- `user_profile` - 获取用户信息

## 使用示例

```bash
# 查询登录状态
claude "帮我检查小红书登录状态"

# 查询用户信息
claude "帮我查询小红书用户信息"
```
