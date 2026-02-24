---
name: minimax-coding-plan
description: MiniMax Coding Plan MCP 工具集，提供网络搜索和图片理解功能。当用户需要搜索网络信息或分析图片内容时使用此技能。
---

# MiniMax Coding Plan

基于 MiniMax Coding Plan API 的工具集，提供网络搜索和图片理解功能。

## 工具

### 1. web_search - 网络搜索

搜索网络获取信息。使用 MiniMax 文本模型基于知识库回答问题。

**使用方法：**
```bash
python3 /root/.openclaw/workspace/skills/minimax-coding-plan/scripts/mcp_tools.py search "搜索关键词"
```

**返回：** 详细的搜索结果和回答。

### 2. understand_image - 图片理解

分析图片内容。支持 HTTP/HTTPS URL 和本地文件路径。

**使用方法：**
```bash
python3 /root/.openclaw/workspace/skills/minimax-coding-plan/scripts/mcp_tools.py image "图片问题" <图片路径或URL>
```

**参数：**
- 图片问题：对图片的提问或分析要求
- 图片路径：本地文件路径或 HTTP/HTTPS URL

**支持格式：** JPEG、PNG、GIF、WebP（最大 20MB）

## API Key

API Key 已配置在脚本中：`sk-cp-cNPUFSRoGGC6p_O4sOjA8sb0FPtWSW5uI8whb71wbqTQBc0isgtbIw9Mj8_f4kcQtNSjWqCs-60rl54ZJiBp2IwZPMeIQQOxCPJ2UVd9DQ3F1ZToRMBnnNU`

## 使用示例

### 网络搜索
```
用户：搜索 Python 异步编程教程
→ 执行：python3 .../mcp_tools.py search "Python 异步编程教程"
```

### 图片理解
```
用户：分析这张图片里的内容
→ 执行：python3 .../mcp_tools.py image "这张图片里有什么？" /path/to/image.jpg

用户：描述这个图片
→ 执行：python3 .../mcp_tools.py image "描述这张图片" https://example.com/image.png
```

## 注意事项

- 脚本会自动清除代理设置，确保直连 MiniMax API
- 图片理解支持本地文件和 URL 两种方式
- 网络搜索返回的是基于模型知识库的回答
