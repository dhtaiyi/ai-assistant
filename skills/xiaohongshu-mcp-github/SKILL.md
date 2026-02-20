# 小红书 MCP 技能 (xiaohongshu-mcp)

## 技能概述

**名称**: xiaohongshu-mcp  
**类型**: MCP (Model Context Protocol) 服务器  
**功能**: 小红书自动化操作  
**作者**: xpzouying  
**仓库**: https://github.com/xpzouying/xiaohongshu-mcp

## 功能特性

### 1. 登录管理
- 检查登录状态
- 登录小红书账号
- Cookie 管理

### 2. 内容发布
- 发布图文内容（支持标题、描述、图片）
- 发布视频内容（支持本地视频文件）
- 图片支持：
  - HTTP/HTTPS 图片链接
  - 本地图片绝对路径（推荐）

### 3. 数据获取
- 获取用户信息
- 获取笔记详情
- 获取主页内容
- 搜索功能

### 4. 互动操作
- 点赞/取消点赞
- 收藏/取消收藏
- 评论功能

## 使用方法

### 前置条件

1. 安装 MCP 客户端
2. 配置 MCP 服务器
3. 登录小红书账号

### 配置文件

```json
{
  "mcpServers": {
    "xiaohongshu": {
      "command": "/path/to/xiaohongshu-mcp",
      "args": ["--port", "18060"]
    }
  }
}
```

### 常用命令

```bash
# 启动服务
./xiaohongshu-mcp --port 18060

# 检查登录状态
curl http://localhost:18060/api/login/status

# 发布图文
curl -X POST http://localhost:18060/api/note/image \
  -H "Content-Type: application/json" \
  -d '{"title": "标题", "content": "内容", "images": ["图片路径"]}'
```

## 安装步骤

### 方式1: Docker 安装（推荐）

```bash
# 拉取镜像
docker pull xpzouying/xiaohongshu-mcp

# 运行容器
docker run -d \
  --name xiaohongshu-mcp \
  -p 18060:18060 \
  -v $(pwd)/cookies:/app/cookies \
  xpzouying/xiaohongshu-mcp
```

### 方式2: 手动安装

```bash
# 克隆仓库
git clone https://github.com/xpzouying/xiaohongshu-mcp.git

# 进入目录
cd xiaohongshu-mcp

# 编译
go build -o xiaohongshu-mcp .

# 运行
./xiaohongshu-mcp --port 18060
```

## 注意事项

1. **登录状态**: 使用前必须先登录
2. **Cookie 管理**: Cookie 文件保存在 `cookies/` 目录
3. **频率限制**: 避免过于频繁的操作
4. **账号安全**: 不要分享 Cookie 文件
5. **公益捐赠**: 项目所有赞赏用于慈善捐赠

## 相关链接

- **项目文档**: [README.md](./README.md)
- **疑难杂症**: [常见问题](https://github.com/xpzouying/xiaohongshu-mcp/issues/56)
- **GitHub**: https://github.com/xpzouying/xiaohongshu-mcp
- **博客**: https://www.haha.ai/xiaohongshu-mcp

## 文件说明

| 文件 | 说明 |
|------|------|
| `xiaohongshu-mcp` | MCP 服务器主程序 |
| `cookies/` | Cookie 保存目录 |
| `README.md` | 详细文档 |
| `docs/` | 文档目录 |

## 常见问题

### Q: 登录失败？
A: 检查 Cookie 是否有效，参考[疑难杂症](https://github.com/xpzouying/xiaohongshu-mcp/issues/56)

### Q: 发布失败？
A: 确保图片路径正确，内容不包含违规词

### Q: 如何更新 Cookie？
A: 删除 `cookies/` 目录下的文件，重新登录

## 版本历史

- v1.0.0: 初始版本
- v1.1.0: 增加视频发布功能
- v1.2.0: 优化登录流程
- v1.3.0: 支持更多互动功能
