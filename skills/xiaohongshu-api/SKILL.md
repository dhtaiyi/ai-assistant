# xiaohongshu-api

小红书 HTTP API 技能封装。直接调用 xiaohongshu-mcp 的 REST API 接口。

## 功能

- ✅ 检查登录状态
- ✅ 发布图文内容
- ✅ 发布视频内容
- ✅ 获取推荐列表
- ✅ 搜索内容
- ✅ 获取帖子详情
- ✅ 发表评论
- ✅ 获取用户信息

## 配置

**MCP 服务器地址**: http://127.0.0.1:18060

## 使用方法

```bash
# 检查登录状态
python3 xiaohongshu-api.py check-login

# 发布图文
python3 xiaohongshu-api.py publish "标题" "内容" "图片路径1,图片路径2"

# 搜索内容
python3 xiaohongshu-api.py search "关键词"

# 获取推荐列表
python3 xiaohongshu-api.py feeds
```

## 详细文档

查看 `README.md` 了解所有功能。
