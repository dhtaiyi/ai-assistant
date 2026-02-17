# 图像生成 Skill

支持多个平台的 AI 图像生成。

## 支持的平台

| 平台 | 命令 | 备注 |
|------|------|------|
| OpenAI DALL-E | `openai` | 需要 OpenAI API Key |
| 通义万相 | `qwen` | 需要阿里云 API Key |
| 百度文心一言 | `baidu` | 需要百度 AI API Key |

## 使用方式

```bash
# OpenAI DALL-E 3
image-gen openai "一只可爱的猫在草地上"

# 通义万相
image-gen qwen "现代城市夜景，赛博朋克风格"

# 百度文心一言
image-gen baidu "山水画，秋天风景"

# 测试连接
image-gen test
```

## 前置配置

### OpenAI

```bash
export OPENAI_API_KEY="sk-..."
```

### 通义万相 (阿里云)

```bash
export QWEN_API_KEY="sk-..."
```

### 百度文心一言

```bash
export BAIDU_API_KEY="..."
export BAIDU_SECRET_KEY="..."
```

## 示例

```bash
# 生成一只猫
image-gen openai "A cute cat sitting on grass, photorealistic"

# 生成风景图
image-gen qwen "日落海滩，热带风情"
```

## 文件位置

```
/root/.openclaw/workspace/skills/image-generator/
├── SKILL.md
└── image-gen.sh
```

## 注意事项

- 需要各平台的 **API Key**
- 部分平台需要 **充值** 才能使用
- 生成图片需要几秒到几十秒
- 图片 URL 有时效性，请及时保存
