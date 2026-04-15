# 🎯 小红书自动化发贴系统

## 概述

实现小红书笔记的自动化发布、定时发布和批量发布功能。

---

## 📁 文件列表

| 文件 | 功能 |
|------|------|
| `xiaohongshu-poster.py` | 自动化发贴系统 |
| `xiaohongshu-posts/` | 发布队列目录 |
| `xiaohongshu-poster.log` | 发贴日志 |

---

## 🚀 快速开始

### 第一步：检查权限

```bash
python3 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-poster.py check
```

这会检查：
- ✅ 是否已登录
- ✅ 是否有创作者资格
- ✅ 能否访问发贴页面

### 第二步：申请创作者资格（如需要）

如果检查显示没有创作者资格：

1. 访问 https://creator.xiaohongshu.com
2. 点击"申请创作者"
3. 满足条件：
   - 实名认证
   - 绑定手机号
   - 粉丝数≥500（或其他条件）
4. 等待审核通过

### 第三步：开始发贴

#### 方式1：立即发布

```bash
python3 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-poster.py post '我的标题' '笔记内容...'
```

#### 方式2：添加到队列

```bash
python3 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-poster.py add '稍后发布' '内容...'
```

#### 方式3：使用模板

```bash
# 创建模板
python3 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-poster.py template

# 编辑模板
vim /home/dhtaiyi/.openclaw/workspace/xiaohongshu-posts/template.json

# 使用模板发布
python3 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-poster.py post '模板标题' '模板内容...'
```

---

## 📋 命令详解

### check - 检查权限

```bash
python3 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-poster.py check
```

输出示例：
```
2026-02-13 00:00:00 - INFO - 🔄 启动浏览器...
2026-02-13 00:00:03 - INFO - 📱 访问创作者平台...
2026-02-13 00:00:06 - INFO - ✅ 有发贴权限
```

### post - 立即发布

```bash
python3 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-poster.py post '标题' '内容'
```

参数：
- `标题` - 笔记标题（必填）
- `内容` - 笔记正文（必填）

示例：
```bash
python3 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-poster.py post \
  '今日穿搭分享' \
  '今天穿了这套，超喜欢！✨'
```

### add - 添加到队列

```bash
python3 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-poster.py add '标题' '内容'
```

与post类似，但添加到发布队列，稍后定时发布。

### list - 查看队列

```bash
python3 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-poster.py list
```

输出示例：
```
1. [pending] 标题1
2. [pending] 标题2
```

### template - 创建模板

```bash
python3 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-poster.py template
```

生成模板文件：`/home/dhtaiyi/.openclaw/workspace/xiaohongshu-posts/template.json`

---

## 📝 内容模板

### 基础模板

```json
{
  "title": "笔记标题",
  "content": "分享内容...\n\n✨ 亮点:\n- 第一点\n\n#话题标签",
  "images": ["/path/to/image.jpg"],
  "publish_time": null
}
```

### 完整模板（带定时）

```json
{
  "title": "定时发布笔记",
  "content": "内容...",
  "images": ["/path/to/1.jpg", "/path/to/2.jpg"],
  "publish_time": "2026-02-14T10:00:00",
  "status": "scheduled"
}
```

---

## ⏰ 定时发布

### 方案1：Cron定时任务

```bash
# 编辑crontab
crontab -e

# 添加定时发布（每天上午10点）
0 10 * * * /usr/bin/python3 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-poster.py post '定时标题' '定时内容'
```

### 方案2：发布队列

```bash
# 添加到队列
python3 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-poster.py add '标题' '内容'

# 设置定时任务处理队列
crontab -e
# 每小时检查一次队列
0 * * * * /usr/bin/python3 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-poster.py process
```

---

## 🔄 批量发布

### 创建批量内容

```bash
# 创建批量发布脚本
cat > /home/dhtaiyi/.openclaw/workspace/xiaohongshu-batch.sh << 'SCRIPT'
#!/bin/bash

TOPICS=("穿搭" "美妆" "美食" "健身" "旅行")

for topic in "${TOPICS[@]}"; do
    python3 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-poster.py post \
      "关于${topic}的分享" \
      "今天分享关于${topic}的内容..." \
      --delay 3600  # 每条间隔1小时
done
SCRIPT

chmod +x /home/dhtaiyi/.openclaw/workspace/xiaohongshu-batch.sh
```

### 使用

```bash
# 运行批量发布
bash /home/dhtaiyi/.openclaw/workspace/xiaohongshu-batch.sh
```

---

## ⚠️ 注意事项

### 1. 创作者资格
- 必须有创作者资格才能发贴
- 需要申请并通过审核

### 2. 内容规范
- 避免敏感词
- 图片需要合规
- 遵守社区规范

### 3. 发布频率
- 建议每天1-3篇
- 避免频繁发布（可能被限流）

### 4. Cookie有效期
- Cookie会过期
- 设置自动刷新
- 定期检查权限

---

## 🔧 常见问题

### Q1: 没有创作者资格？
A: 访问 https://creator.xiaohongshu.com 申请

### Q2: Cookie过期？
A: 刷新Cookie：
```bash
python3 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-cookie-manager.py refresh
```

### Q3: 发布失败？
A: 按顺序排查：
1. 检查权限
2. 刷新Cookie
3. 查看日志

### Q4: 如何查看日志？
```bash
tail -f /home/dhtaiyi/.openclaw/workspace/xiaohongshu-poster.log
```

---

## 📊 发布最佳实践

### 内容策略
1. **标题** - 吸引眼球，包含关键词
2. **封面** - 精美图片，第一印象
3. **内容** - 有价值，有干货
4. **标签** - 相关话题，增加曝光

### 发布频率
| 阶段 | 频率 | 目的 |
|------|------|------|
| 起步期 | 1篇/天 | 养号 |
| 成长期 | 2-3篇/天 | 涨粉 |
| 稳定期 | 1-2篇/天 | 维护 |

### 发布时间
- 早7-9点：通勤时间
- 午12-14点：午休时间
- 晚20-22点：黄金时间
- 周末：全天活跃

---

## 🎯 完整工作流

### 日常发布

```bash
# 1. 检查状态
python3 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-tool.py status

# 2. 发布内容
python3 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-poster.py post '标题' '内容'

# 3. 查看日志
tail -f /home/dhtaiyi/.openclaw/workspace/xiaohongshu-poster.log
```

### 定时发布

```bash
# 1. 设置cron
crontab -e

# 2. 添加定时任务
0 10 * * * /usr/bin/python3 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-poster.py post '早安' '早上好！'

0 20 * * * /usr/bin/python3 /home/dhtaiyi/.openclaw/workspace/xiaohongshu-poster.py post '晚安' '晚安，明天见！'
```

---

## ✅ 成功标准

- [ ] 创作者资格已获取
- [ ] Cookie有效
- [ ] 能成功发布
- [ ] 定时任务已设置
- [ ] 发布日志正常

