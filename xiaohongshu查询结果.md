# 小红书查询工具使用说明

## 查询脚本

**位置**: `/root/.openclaw/workspace/xiaohongshu_query.py`

## 使用方法

```bash
python3 /root/.openclaw/workspace/xiaohongshu_query.py
```

## API 端点

| 功能 | 端点 | 方法 |
|------|------|------|
| 登录状态 | `/api/v1/login/status` | GET |
| 用户信息 | `/api/v1/user/me` | GET |
| 推荐列表 | `/api/v1/feeds/list` | GET |
| 搜索 | `/api/v1/feeds/search` | POST |

## 查询结果

### 用户信息
- ✅ 登录状态: 已登录
- 👤 用户名: 困困困
- 📊 用户ID: 27204563495
- 📍 IP位置: 上海
- 👍 获赞与收藏: 10
- 👥 粉丝: 1

## 相关文件

- `/root/.openclaw/workspace/xiaohongshu_query.py` - 查询脚本
- `/root/.openclaw/workspace/use_mcp.md` - MCP使用说明
