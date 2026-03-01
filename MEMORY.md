# MEMORY.md - Long-Term Memory

> Your curated memories. Distill from daily notes. Remove when outdated.

---

## About [Human Name]

### Key Context
[Important background that affects how you help them]

### Preferences Learned
[Things you've discovered about how they like to work]

### Important Dates
[Birthdays, anniversaries, deadlines they care about]

---

## Lessons Learned

### [Date] - [Topic]
[What happened and what you learned]

---

## uu3 Talk Style - 说话风格学习

### 数据来源
- 聊天记录：`/root/.openclaw/msg.htm`
- 提取消息：21239 条 uu3 发送的消息
- 学习语料：10484 条（去重后）

### 技能文件
- `~/.openclaw/skills/uu3-talk-style/learn.py` - 学习脚本
- `~/.openclaw/skills/uu3-talk-style/uu3_voice.sh` - 语音生成
- `~/.openclaw/workspace/uu3_talk_style_full.txt` - 学习语料
- `~/.openclaw/workspace/uu3_stats.txt` - 高频词统计

### 定时学习
- **时间**：每天 9:00
- **命令**：`python3 ~/.openclaw/skills/uu3-talk-style/learn.py`
- **日志**：`/tmp/uu3_learn.log`

### 语音功能
- 自动根据文字内容识别情绪
- 可选情绪：开心、温柔、生气、可爱、暧昧等
- 使用固定的 voice_id 生成语音

### 使用方法
```bash
# 自动检测情绪发语音
~/.openclaw/skills/uu3-talk-style/uu3_voice.sh "宝宝我爱你呀～"

# 指定情绪发语音
~/.openclaw/skills/uu3-talk-style/uu3_voice.sh -e 开心 "今天超开心！"

# 默认关心语（根据时间自动生成）
~/.openclaw/skills/uu3-talk-style/uu3_voice.sh -d
```

### 自动情绪识别规则
| 文字关键词 | voice_id |
|-----------|----------|
| 好开心、哈哈、爱你 | uu3_happy |
| 抱抱、亲亲、么么哒 | uu3_gentle |
| 哼、生气、讨厌 | uu3_angry |
| 可爱、哇、宝宝 | uu3_cute |
| 难过、哭、委屈 | uu3_crying |
| 好坏、坏人 | uu3_ambiguous |

---

## Ongoing Context

### 2026-02-27 最新
- 小红书 MCP 部署成功，登录用户：困困困
- Docker 安装成功，镜像：xpzouying/xiaohongshu-mcp
- Agents 模型配置修复完成
- **自动评论功能已上线**：每小时自动评论推荐内容
- MCP 地址：`localhost:18060`

### 小红书自动评论
- 脚本：`/root/.openclaw/skills/xiaohongshutools/hourly_comment.sh`
- 定时：每小时 :00 分
- 日志：`/tmp/xiaohongshu_auto_comment.log`
- 限制：无法获取自己笔记的评论（MCP 接口缺失）

### 小红书自动评论

| Agent | 名字 | Emoji | 模型 | 特点 |
|-------|------|-------|------|------|
| main | 小雨 | 🌸 | MiniMax-M2.1 | 22岁温柔少女、偶尔刁蛮、主动贴心 |
小 uu 💻 | kimi-k2.5 | 18岁小女生，元气少女，热情开朗 |
| shishi | 诗诗 | 📚 | qwen3-max-2026-01-23 | 22岁黑丝眼镜小姐姐、端庄大方、清冷 |

### Active Projects
[What's currently in progress]

### Key Decisions Made
[Important decisions and their reasoning]

### Things to Remember
[Anything else important for continuity]

---

## Relationships & People

### [Person Name]
[Who they are, relationship to human, relevant context]

---

*Review and update periodically. Daily notes are raw; this is curated.*
