# 智谱AI API 配置指南

## 🎯 概述

智谱AI（ZhipuAI）提供免费的图片理解API，使用 GLM-4V 模型。

## 📝 申请步骤

### 1. 注册账号
- 访问: https://open.bigmodel.cn/
- 注册智谱AI账号

### 2. 创建API Key
1. 登录后进入控制台
2. 点击「API密钥管理」
3. 点击「创建新密钥」
4. 复制保存 API Key

### 3. 获取免费额度
- 新用户通常有免费调用额度
- 查看剩余额度: 控制台 → 调用统计

## 🔧 配置步骤

### 临时配置（当前会话）
```bash
export ZHIPU_API_KEY="your_api_key_here"
```

### 永久配置
```bash
# 添加到环境变量
echo 'export ZHIPU_API_KEY="your_api_key_here"' >> ~/.bashrc

# 立即生效
source ~/.bashrc
```

### 验证配置
```bash
# 检查是否配置成功
echo ${ZHIPU_API_KEY:0:10}...
```

## 🚀 使用方法

### 基本用法
```bash
/root/.openclaw/workspace/analyze-image-zhipu.sh photo.jpg
```

### 自定义提示词
```bash
/root/.openclaw/workspace/analyze-image-zhipu.sh screenshot.png "详细分析这张图片的内容"
```

### 英文分析
```bash
/root/.openclaw/workspace/analyze-image-zhipu.sh image.png "Describe this image in detail"
```

## 📊 功能特性

| 功能 | 支持 |
|------|------|
| 图片描述 | ✅ |
| 文字识别 | ✅ |
| 物体识别 | ✅ |
| 场景理解 | ✅ |
| 多语言 | ✅ |

## 📁 相关脚本

- `/root/.openclaw/workspace/analyze-image-zhipu.sh` - 智谱AI版本
- `/root/.openclaw/workspace/analyze-image.sh` - OpenAI版本（如有API Key）

## 💡 提示

1. **图片格式**: 支持 JPG, PNG, GIF, WebP
2. **图片大小**: 建议小于 5MB
3. **调用限制**: 遵守免费额度政策
4. **网络**: 需要能访问 api.open.bigmodel.cn

## ❓ 常见问题

Q: API调用失败？
A: 检查 API Key 是否正确，网络是否可访问

Q: 返回错误？
A: 查看错误信息，检查图片格式和大小

Q: 免费额度用完？
A: 登录控制台查看，或购买付费套餐

## 📞 帮助

- 官方文档: https://open.bigmodel.cn/dev/howuse/introduction
- API调试: https://open.bigmodel.cn/dev/howuse/debug
- 控制台: https://open.bigmodel.cn/

---

**配置完成后，运行脚本即可分析图片！**
