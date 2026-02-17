# xiaohongshu-api

小红书 HTTP API 技能封装。直接调用 xiaohongshu-mcp 的 REST API 接口，无需 MCP 协议支持。

## 功能列表

✅ **基础功能**
- 检查登录状态
- 获取登录二维码
- 删除 cookies

✅ **内容发布**
- 发布图文内容
- 发布视频内容

✅ **内容获取**
- 获取推荐列表
- 搜索内容
- 获取帖子详情
- 获取用户主页

✅ **互动功能**
- 发表评论
- 回复评论
- 获取当前用户信息

## 快速开始

### 1. 启动 xiaohongshu-mcp

确保 xiaohongshu-mcp 服务已启动：

```bash
docker run -d \
  --name xiaohongshu-mcp \
  -p 18060:18060 \
  -v $(pwd)/cookies:/app/cookies \
  -e HTTP_PROXY=http://127.0.0.1:13128 \
  xpzouying/xiaohongshu-mcp
```

### 2. 安装依赖

```bash
pip install requests
```

### 3. 使用命令行

```bash
# 检查登录状态
python3 xiaohongshu-api.py check-login

# 发布图文
python3 xiaohongshu-api.py publish "标题" "正文内容" "图片1.jpg,图片2.jpg"

# 搜索内容
python3 xiaohongshu-api.py search "关键词"

# 获取推荐列表
python3 xiaohongshu-api.py feeds

# 获取当前用户信息
python3 xiaohongshu-api.py me
```

### 4. 作为模块使用

```python
from xiaohongshu-api import XiaoHongShuAPI

# 创建 API 客户端
api = XiaoHongShuAPI(base_url="http://127.0.0.1:18060")

# 检查登录状态
result = api.check_login()
print(result)

# 发布内容
result = api.publish(
    title="我的标题",
    content="正文内容",
    images=["/path/to/image1.jpg", "/path/to/image2.jpg"]
)
print(result)

# 搜索内容
result = api.search("美食")
print(result)
```

## 命令详解

### 检查登录状态

```bash
python3 xiaohongshu-api.py check-login
```

### 获取登录二维码

```bash
python3 xiaohongshu-api.py qrcode
```

### 发布图文内容

```bash
python3 xiaohongshu-api.py publish "标题" "正文" "图片1.jpg,图片2.jpg"
```

参数说明：
- `title`: 帖子标题（不超过 20 字）
- `content`: 正文内容（不超过 1000 字）
- `images`: 图片路径，使用逗号分隔

### 发布视频内容

```bash
python3 xiaohongshu-api.py publish-video "标题" "描述" "/path/to/video.mp4"
```

### 搜索内容

```bash
python3 xiaohongshu-api.py search "关键词"
```

### 获取推荐列表

```bash
python3 xiaohongshu-api.py feeds
```

### 获取帖子详情

```bash
python3 xiaohongshu-api.py detail "feed_id" "xsec_token"
```

### 发表评论

```bash
python3 xiaohongshu-api.py comment "feed_id" "xsec_token" "评论内容"
```

### 获取当前用户信息

```bash
python3 xiaohongshu-api.py me
```

## API 参考

### XiaoHongShuAPI 类

#### 初始化

```python
api = XiaoHongShuAPI(base_url="http://127.0.0.1:18060")
```

#### 方法列表

| 方法 | 功能 |
|------|------|
| `check_login()` | 检查登录状态 |
| `get_qrcode()` | 获取登录二维码 |
| `delete_cookies()` | 删除 cookies |
| `publish(title, content, images, video=None)` | 发布图文 |
| `publish_video(title, content, video)` | 发布视频 |
| `list_feeds()` | 获取推荐列表 |
| `search(keyword)` | 搜索内容 |
| `get_feed_detail(feed_id, xsec_token)` | 获取帖子详情 |
| `post_comment(feed_id, xsec_token, content)` | 发表评论 |
| `reply_comment(feed_id, xsec_token, comment_id, content)` | 回复评论 |
| `get_user_profile(user_id, xsec_token)` | 获取用户主页 |
| `get_my_profile()` | 获取当前用户信息 |

## 注意事项

1. **登录状态**: 使用前请确保已登录小红书
2. **发布限制**: 
   - 标题不超过 20 字
   - 正文不超过 1000 字
   - 每天建议发布不超过 50 篇
3. **图片路径**: 推荐使用本地绝对路径，避免使用中文路径
4. **Cookie 管理**: 删除 cookies 后需要重新登录

## 相关项目

- [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) - MCP 服务器
- [xiaohongshutools](/root/.openclaw/workspace/skills/xiaohongshutools) - 小红书工具集

## 作者

**OpenClaw** - AI Assistant

## 版本

**Version**: 1.0.0
**最后更新**: 2026-02-17
