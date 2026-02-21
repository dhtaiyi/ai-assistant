# 小红书AI生图发布工作流

## 完整流程

### 1. 用智谱AI生成图片
```bash
ZHIPU_KEY="bd1e2312f8bc4539ae2ae2645905576d.RISv3Rf49m3C3tCG"

curl -s "https://open.bigmodel.cn/api/paas/v4/images/generations" \
  -H "Authorization: Bearer $ZHIPU_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "cogview-3",
    "prompt": "你的图片描述",
    "size": "1024x1024"
  }'
```

### 2. 下载图片到宿主机
```bash
IMAGE_URL="获取到的图片URL"
curl -s -L "$IMAGE_URL" -o /root/.openclaw/workspace/ai_generated_image.png
```

### 3. 复制图片到MCP容器
```bash
# 容器ID
CONTAINER_ID="009d90717581"

docker cp /root/.openclaw/workspace/ai_generated_image.png \
  $CONTAINER_ID:/tmp/xiaohongshu_images/ai_image.jpg
```

### 4. 用MCP发布笔记
```bash
# 获取session
SESSION_ID=$(curl -s --noproxy '*' -c /tmp/xhs.txt -i -X POST http://127.0.0.1:18060/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' 2>&1 | grep -i "Mcp-Session-Id:" | awk '{print $2}' | tr -d '\r')

# 发布
curl -s --noproxy '*' -X POST http://127.0.0.1:18060/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "publish_content",
      "arguments": {
        "title": "标题",
        "content": "正文内容",
        "images": ["/tmp/xiaohongshu_images/ai_image.jpg"],
        "tags": ["标签1", "标签2"]
      }
    }
  }'
```

---

## 关键注意事项

### ⚠️ 代理问题
- MCP容器配置了HTTP代理：`HTTP_PROXY=http://host.docker.internal:13128`
- 代理无法访问内网地址（172.17.0.x, 10.x.x.x）
- **解决方案**：用 `docker cp` 直接复制文件到容器，不要用HTTP服务器

### 📝 MCP容器信息
- 容器ID: `009d90717581`
- MCP端口: `18060`
- 图片目录: `/tmp/xiaohongshu_images/`

### 🔑 智谱AI配置
- API Key: `bd1e2312f8bc4539ae2ae2645905576d.RISv3Rf49m3C3tCG`
- 端点: `https://open.bigmodel.cn/api/paas/v4/images/generations`
- 模型: `cogview-3`

---

## 自动化脚本

参考: `/root/.openclaw/workspace/xiaohongshu_publish.py`
