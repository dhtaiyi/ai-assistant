# 智谱 AI Skill

清华智谱AI，对话/识图/生图/生视频全能型。

## API Key

```
bd1e2312f8bc4539ae2ae2645905576d.RISv3Rf49m3C3tCG
```

## 支持的功能

| 功能 | 模型 | 命令 | 状态 |
|------|------|------|------|
| 对话 | chatglm_turbo | `zhipu chat` | ✅ |
| 识图 | glm-4v | `zhipu vision` | ✅ |
| 文生图 | cogview-3 | `zhipu image` | ✅ |
| 文生视频 | cogvideo | `zhipu video` | ✅ |

## 使用方式

```bash
# 对话
zhipu chat "你好，请介绍一下自己"

# 识图 (需要图片 URL)
zhipu vision "https://example.com/image.jpg" "这张图片有什么特点"

# 文生图
zhipu image "一只可爱的橘猫躺在阳光下的草地上"

# 文生视频
zhipu video "一只小猫在草地上跑，4秒"
```

## 测试

```bash
# 测试所有功能
zhipu test
```

## 前置配置

```bash
# 可选：设置自定义 API Key
export ZHIPU_API_KEY="bd1e2312f8bc..."
```

## 注意事项

- 文生视频首次生成可能需要 1-2 分钟
- 视频生成是异步任务，请耐心等待
- 图片 URL 需要是可访问的公网链接

## 文件位置

```
/root/.openclaw/workspace/skills/zhipu-ai/
├── SKILL.md
└── zhipu.sh
```

## 示例

### 对话

```bash
$ zhipu chat "什么是人工智能？"
✅ 人工智能（Artificial Intelligence，简称 AI）是指...
```

### 识图

```bash
$ zhipu vision "https://xxx.com/photo.jpg" "描述这张图"
✅ 这是一张风景照片，展现了...
```

### 文生图

```bash
$ zhipu image "赛博朋克风格的都市夜景"
✅ 生成成功!
🔗 https://maas-watermark-prod.ufileos.com/...
```

### 文生视频

```bash
$ zhipu video "一只猫在跑"
✅ 任务已提交: 202602131558003a1e313efe964d50
🔄 等待生成...
🔗 https://...
```
