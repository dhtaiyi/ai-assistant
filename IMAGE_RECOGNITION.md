# OpenClaw 图像识别技能指南

## 🎉 已成功安装2个图像识别技能

### 1️⃣ image-ocr - OCR文字识别

**功能**：
- 从图片中提取文字
- 支持多种图片格式（PNG、JPEG、TIFF、BMP）
- 支持多语言（需安装语言包）

**依赖**：
- Tesseract OCR 已安装 ✅
- 版本: 5.3.2

**使用方法**：
```bash
# 提取英文文字
image-ocr "screenshot.png"

# 指定语言
image-ocr "document.jpg" --lang eng

# 中文识别（需要中文包）
image-ocr "chinese.png" --lang chi_sim
```

**安装语言包**：
```bash
# Fedora/RHEL
sudo dnf install tesseract-langpack-*

# 查看可用语言包
dnf search tesseract-langpack
```

---

### 2️⃣ image2prompt - 图片分析生成提示词

**功能**：
- 分析图片内容
- 生成AI绘画提示词
- 支持多种图片类型：
  - 人像 (portrait)
  - 风景 (landscape)
  - 产品 (product)
  - 动物 (animal)
  - 插画 (illustration)

**输出格式**：
- 结构化输出
- 自然语言描述

**使用方法**：
查看技能文件：`/home/dhtaiyi/.openclaw/workspace/skills/image2prompt/SKILL.md`

---

## 📊 当前图像识别技能

| 技能 | 功能 | 状态 |
|------|------|------|
| image-ocr | OCR文字识别 | ✅ 已安装 |
| image2prompt | 图片转提示词 | ✅ 已安装 |

---

## 🚀 快速开始

### 文字识别
```bash
# 简单用法
image-ocr your_image.png

# 带参数
image-ocr document.jpg --lang eng
```

### 图片分析
```bash
# 查看image2prompt使用方法
cat /home/dhtaiyi/.openclaw/workspace/skills/image2prompt/SKILL.md
```

---

## 📚 相关文档

- OpenClaw技能指南: `/home/dhtaiyi/.openclaw/workspace/SKILLS_GUIDE.md`
- 系统优化文档: `/home/dhtaiyi/.openclaw/workspace/OPTIMIZATION.md`

---

**安装时间**: 2026-02-12
**技能数量**: 2个
**总技能数**: 14个
