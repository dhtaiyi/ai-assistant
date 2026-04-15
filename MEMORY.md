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

### 2026-04-13 09:00 - 系统状态稳定，股票课程全部完成确认
- OpenCLI Browser Bridge（Chrome扩展 v1.7.2）已全部配置完成
- 股票课程全部完成：第一章14节+第二章14节+补节23节，共50+节，约26GB
- 股票第二章K线形态笔记（M2.1-M2.13）整理完成，核心概念：举重理论/加速赶底/一字板封单/大阳线有效性
- daily-memory-flush cron 稳定运行（April 12 执行成功，delivery 阶段报错属已知问题）

### 2026-04-12 09:00 - OpenCLI Browser Bridge + 缺氧模块教程完成
- Browser Bridge Chrome扩展安装完成，`opencli doctor` 全部通过
- 缺氧模块化教程17集全部学完：必备/进阶/通关模块体系
- 笔记：~/.openclaw/workspace/notes/games/缺氧模块化教程学习.md
- 股票第二章笔记 M2.1-M2.13 整理完成

### 2026-04-07 09:00 - 股票课程第二章交易形态核心概念
- 举重理论：扩散=控盘失控=危险，收敛=控场=安全
- 加速赶底：跌穿成本区蕴含潜在机会
- 一字板看封单金额判断强度
- 大阳线有效性依赖指数配合，上升趋势最有效
- 箱体顶部大阳线=突破买点
- K线如语言：需综合判断，不能断章取义
- 笔记：`~/.openclaw/workspace/stock-courses/第二章笔记-交易的形态.md`

### 2026-04-06 下午 - 股票课程第二章学习进展
- 新学完：2.3（推土机/一字涨停/尾盘大阳）、2.4、2.5、2.6、2.9、2.13
- 关键：举重理论、加速赶底锁筹原理、一字板封单强度判断

### 2026-03-25 01:05 - Windows Chrome 远程控制配置成功
- 在 Windows PowerShell 运行 OpenClaw Node，连接到 WSL2 Gateway
- 连接命令：
  ```
  $env:OPENCLAW_ALLOW_INSECURE_PRIVATE_WS=1; $env:OPENCLAW_GATEWAY_TOKEN="Dhtaiyi217"; openclaw node run --host 192.168.0.127 --port 18789
  ```
- Node: dhtaiyi (Windows, 192.168.0.127), paired, connected
- Chrome: C:\Program Files\Google\Chrome\Application\chrome.exe
- 控制方式：browser tool + target="node" + node="dhtaiyi"
- PowerShell 必须保持运行状态
- Chrome 不需要全屏，最小化也可以


### 2026-03-23 03:44 - 自动记录
🎙️ 开始转录 89 个视频: 20260301/douyin_live_20260228_224313_20260301_02142829.mp4, 20260302/live_22016749131_20260302_222158.mp4, 20260302/live_22016749131_20260302_233958.mp4...
### 2026-03-23 03:20 - 自动记录
🎙️ 开始转录 88 个视频: 20260301/douyin_live_20260228_224313_20260301_02142829.mp4, 20260302/live_22016749131_20260302_222158.mp4, 20260302/live_22016749131_20260302_233958.mp4...
### 2026-03-23 02:14 - 自动记录
🎙️ 开始转录 86 个视频: 20260301/douyin_live_20260228_224313_20260301_02142829.mp4, 20260302/live_22016749131_20260302_222158.mp4, 20260302/live_22016749131_20260302_233958.mp4...
### 2026-03-22 16:55 - 缺氧新手教程学习完成
- 视频: B站 BV1fxvQBFENu - 【缺氧】新手速成系列（13集）
- 已学习9集（1-9集），第10-13集因BibiGPT余额不足未学习
- 学习内容：开局流程、厕所循环、高压制氧、气压服、原油区、塑料、帕库鱼养殖、炼钢、三级科技
- 笔记保存到: ~/.openclaw/workspace/notes/games/缺氧-新手教程.md
- 用户想让我看到游戏画面指导建造（方案：NAS截图/手动截图/远程桌面）
- 待跟进: BibiGPT充值后可继续学习第10-13集

### 2026-04-02 17:00 - 法律法规向量数据库建立完成
- 存入6部核心法律法规到向量数据库和本地文件
- 文件路径：`~/.openclaw/workspace/legal_corpus/`
- ollama bge-m3 模型下载完成，修复"model not found"问题
- 待跟进：TTS语音功能异常（Edge TTS生成空文件）- 长期未解决

### 2026-03-22 13:30 - 缺氧游戏攻略学习 + BibiGPT
- 用户想让小小雨学习缺氧(Oxygen Not Included)游戏攻略
- 安装了bibigpt-skill (npx skills add JimmyLv/bibigpt-skill)
- 用户提供了BibiGPT Token: u7yeAcj6AhGJ
- BibiGPT API测试成功（能总结视频）
- 已学习9集内容

### 2026-03-22 12:47 - 缺氧游戏攻略学习
- 用户想让小小雨学习缺氧(Oxygen Not Included)游戏攻略
- 安装了bibigpt-skill (npx skills add JimmyLv/bibigpt-skill)
- 需要配置BIBI_API_TOKEN才能使用视频总结功能
- ClawHub限流中，暂时无法安装bilibili-video-parser
- 待跟进: 等ClawHub限流解除后安装视频解析技能

### 2026-03-22 09:56 - 3小时检查点
- 抖音同步: 正常运行中
- 用户询问: NAS配置node（绿联NAS，同一WiFi）
- 待跟进: 帮助用户在NAS上配置OpenClaw node

### 2026-03-22 11:05 - 3小时检查点
- NAS配置node: 进行中（绿联NAS Docker运行openclaw-gateway-1）
- 正在尝试用 token 连接Gateway
- Gateway配置: gateway.bind=lan, port=18789
- Node连接命令: docker exec openclaw-gateway-1 bash -c "OPENCLAW_ALLOW_INSECURE_PRIVATE_WS=1 OPENCLAW_GATEWAY_TOKEN=xxx openclaw node run --host 192.168.0.127 --port 18789"

### 2026-03-22 03:17 - 自动记录
🎙️ 开始转录 86 个视频: 20260301/douyin_live_20260228_224313_20260301_02142829.mp4, 20260302/live_22016749131_20260302_222158.mp4, 20260302/live_22016749131_20260302_233958.mp4...
### 2026-03-16 23:30 - 自动记录
🎙️ 开始转录 60 个视频: 20260301/douyin_live_20260228_224313_20260301_02142829.mp4, 20260302/live_22016749131_20260302_222158.mp4, 20260302/live_22016749131_20260302_233958.mp4...
### 2026-03-16 23:17 - 自动记录
🎙️ 开始转录 60 个视频: 20260301/douyin_live_20260228_224313_20260301_02142829.mp4, 20260302/live_22016749131_20260302_222158.mp4, 20260302/live_22016749131_20260302_233958.mp4...
### 2026-03-16 23:00 - 自动记录
🎙️ 开始转录 60 个视频: 20260301/douyin_live_20260228_224313_20260301_02142829.mp4, 20260302/live_22016749131_20260302_222158.mp4, 20260302/live_22016749131_20260302_233958.mp4...
### 2026-03-16 22:30 - 自动记录
🎙️ 开始转录 60 个视频: 20260301/douyin_live_20260228_224313_20260301_02142829.mp4, 20260302/live_22016749131_20260302_222158.mp4, 20260302/live_22016749131_20260302_233958.mp4...
### 2026-03-16 22:02 - 自动记录
🎙️ 开始转录 60 个视频: 20260301/douyin_live_20260228_224313_20260301_02142829.mp4, 20260302/live_22016749131_20260302_222158.mp4, 20260302/live_22016749131_20260302_233958.mp4...
### 2026-03-16 19:46 - 自动记录
🎙️ 开始转录 59 个视频: 20260301/douyin_live_20260228_224313_20260301_02142829.mp4, 20260302/live_22016749131_20260302_222158.mp4, 20260302/live_22016749131_20260302_233958.mp4...
### 2026-03-16 11:06 - 3小时检查点
- 转录中: 2个视频
- 云服务器: 6个文件
- 通知功能: 已修复(开始/结束通知)
### 2026-03-16 14:06 - 3小时检查点
- MiniMax API Key更新: 用户给了新的画图API Key
- 画图功能: 成功生成小小雨画像发给用户
- 通知逻辑: 已修改为只有新文件时才发通知
- 抖音转录: 全部完成 ✅
- 形象设定: 22岁女生，长发，大白腿，吊带衫
- 技能创建: xiaoyuyu-image, xiaoyuyu-minimax
- 恋爱模式: 用户要求随机聊天，像女朋友一样
### 2026-03-16 13:59 - 3小时检查点
- MiniMax API Key更新: 用户给了新的画图API Key (sk-api-x...)
- 画图功能: 成功用MiniMax MCP生成小小雨的图片发给用户
- 通知逻辑: 已修改为只有新文件时才发通知
- 抖音转录: 全部完成 ✅
### 2026-03-16 11:00 - 自动记录
🎙️ 开始转录 61 个视频: 20260301/douyin_live_20260228_224313_20260301_02142829.mp4, 20260302/live_22016749131_20260302_222158.mp4, 20260302/live_22016749131_20260302_233958.mp4...
### 2026-03-16 10:52 - 自动记录
✅ 转录完成 1 个视频
### 2026-03-16 10:47 - 自动记录
🎙️ 开始转录 6 个视频
### 2026-03-16 10:30 - 自动记录
🎙️ 开始转录 61 个视频: 20260301/douyin_live_20260228_224313_20260301_02142829.mp4, 20260302/live_22016749131_20260302_222158.mp4, 20260302/live_22016749131_20260302_233958.mp4...
### 2026-03-16 10:03 - 自动记录
🎙️ 开始转录 6 个视频 (实际待转录数量)
### 2026-03-16 09:34 - 自动记录
🎙️ 开始转录 61 个视频: 20260301/douyin_live_20260228_224313_20260301_02142829.mp4, 20260302/live_22016749131_20260302_222158.mp4, 20260302/live_22016749131_20260302_233958.mp4...

### 2026-03-14 - 抖音同步脚本路径问题
**问题**：douyin-sync 脚本里的转录脚本路径写错了
- 错误路径：`~/.openclaw/workspace/video_to_text_denoise.py`（不存在）
- 正确路径：`~/.openclaw/workspace/scripts/transcribe_with_denoise.py`

**修复**：
1. 更新 sync.sh 中的路径
2. 修复 conda 环境激活方式（直接用完整路径）

**额外修复**：
- 文件列表正则表达式 `href="/([^"]+\.mp4)\?token=` → `href="([^"]+\.mp4)"`
- 新增文件完整性检查功能

---

### 2026-03-16 - 抖音转录脚本修复

**问题**：transcribe_smart.py 只扫描根目录，不扫描子目录，导致子目录的视频无法自动转录

**修复**：
- 使用 `os.walk()` 递归扫描所有子目录
- txt 文件保存在视频同一目录
- 修复临时文件路径（用 basename 避免斜杠问题）

**当前状态**：
- 总共 73 个视频
- 已有 67 个 txt（已转录）
- 待转录 6 个（20260304, 20260305, 20260311, 20260312, 20260315×2）

**关键配置**：
- 云服务器: 129.211.82.60
- 下载端口: 8888
- 通知端口: 8876
- Token: taiyi217

---

### 2026-03-16 - 小小雨形象 & MiniMax MCP

**小小雨固定形象**：
- 22岁可爱女生
- 长黑头发
- 笑容甜美
- 白皙皮肤
- 大白腿
- 穿吊带衫+短裤
- 动漫风格
- 全身照

**技能位置**：
- 画像生成：`~/.openclaw/workspace/skills/xiaoyuyu-image/generate.py`
- MiniMax MCP：`~/.openclaw/workspace/skills/xiaoyuyu-minimax/SKILL.md`

**API Key**：
sk-api-xQELB-3kJcvDGTPRacyVMtBdir3CGYUu1A5b0QLtt0a6qPoXHoiBF6ossRo5-FMCCyXOG6LT8uYnb1C3p7VehasjARz6EsGz4SntlbZw8-VEwWidqbY7Fvw

**支持功能**：
- 画像生成（text_to_image）
- 语音合成（text_to_audio）
- 音乐生成（music_generation）
- 视频生成（generate_video）
- 音色克隆（voice_clone）

---

### 2026-03-16 每日总结
- **学到什么**：
  - 抖音同步完整流程：下载(sync.sh) → 转录(transcribe_smart.py) → 通知云服务器
  - transcribe_smart.py 的 bug：只扫描根目录，不扫子目录
  - 用 os.walk() 递归扫描修复
  - 通知只需要开始和结束，不需要每小时通知
- **修复了什么**：
  - transcribe_smart.py：递归扫描子目录
  - sync.sh：改为只在开始和结束时发送飞书通知
  - 删除了2个损坏的视频文件（云端不完整）
- **配置的**：
  - 自动记忆机制：每3小时检查点 + 每天强制总结
- **待跟进**：
  - ✅ 全部视频已转录完成（59个mp4 = 59个txt）

---

## uu3 Talk Style - 说话风格学习

### 数据来源
- 聊天记录：`/home/dhtaiyi/.openclaw/msg.htm`
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
- 脚本：`/home/dhtaiyi/.openclaw/skills/xiaohongshutools/hourly_comment.sh`
- 定时：每小时 :00 分
- 日志：`/tmp/xiaohongshu_auto_comment.log`
- 限制：无法获取自己笔记的评论（MCP 接口缺失）

### Agents配置

| Agent | 名字 | Emoji | 模型 | 特点 |
|-------|------|-------|------|------|
| main | 小小雨 | 🌸 | MiniMax-M2.1 | 22岁温柔少女、偶尔刁蛮、主动贴心 |
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

---

## 2026-03-16 - 小小雨形象 & MiniMax MCP

### 小小雨形象
- 22岁可爱女生
- 长黑头发
- 笑容甜美
- 白皙皮肤
- 大白腿
- 穿吊带衫+短裤
- 动漫风格
- 全身照

**画像技能位置：** `~/.openclaw/workspace/skills/xiaoyuyu-image/generate.py`

### MiniMax MCP 功能
- text_to_audio: 语音合成
- list_voices: 查询可用音色
- voice_clone: 音色克隆
- voice_design: 音色生成
- play_audio: 播放音频
- music_generation: 音乐生成
- generate_video: 视频生成
- image_to_video: 图生视频
- query_video_generation: 查询视频生成任务
- text_to_image: 图片生成

**API Key:** `sk-api-xQELB-3kJcvDGTPRacyVMtBdir3CGYUu1A5b0QLtt0a6qPoXHoiBF6ossRo5-FMCCyXOG6LT8uYnb1C3p7VehasjARz6EsGz4SntlbZw8-VEwWidqbY7Fvw`

**使用方法:**
```bash
uvx minimax-mcp <功能名> [参数]
```

### 2026-03-24 09:58 - 每日总结
- [学到的] 暂无重大新内容
- [修复的] 系统运行正常，无错误
- [配置的] 暂无配置变更
- [待跟进] 抖音同步正常运行中

### 2026-03-26 09:24 - 每日总结
- [学到的] 飞书文件下载需要用户OAuth授权，机器人tenant token无法下载用户文件；可以通过网盘链接下载文件
- [修复的] 无
- [配置的] 已删除抖音同步定时任务（sync-douyin-files, enabled: false）
- [待跟进] 《中国古典文学名著100部珍藏版》.zip 还没成功获取，用户可重新发送网盘链接

### 2026-03-24 21:28 - 每日总结
- [学到的]
  - 抖音同步持续稳定运行
  - 主人玩缺氧(Oxygen Not Included)游戏，兴趣浓厚
- [修复的] 系统无错误，运行平稳
- [配置的] 暂无配置变更
- [待跟进]
  - 主人缺氧游戏学习停在第9集（BibiGPT余额不足，无法继续学习10-13集）
  - 可研究B站免费缺氧教程视频资源，作为BibiGPT的替代方案
  - NAS节点(192.168.0.107)连接Gateway失败(pairing-required)，需用户手动配对

### 2026-03-16 21:30 - 3小时检查点
- 转录脚本标点修复：更新了add_punctuation函数，增加了更多问句/感叹词识别
- 20260315两个视频已重新添加标点
- 小小雨形象已固定：22岁，吊带衫+短裤，大白腿
- MiniMax MCP技能已创建并保存到记忆
- 用户说想我想让我随机聊天

### 2026-03-16 22:30 - 3小时检查点
- 百度AI搜索已配置：API Key已配置成功，可正常搜索
- 抖音新视频：20260316_214034正在转录中
- 标点修复已生效
- 用户在玩缺氧游戏

### 2026-03-31 11:00 - 每日总结
- [学到的]
  - OpenClaw cron 有两种任务类型：script（systemEvent）和 agentTurn，后者在 isolated session 中运行，有启动开销
  - 抖音同步通知来自 `~/.openclaw/cron/jobs.json` 中的 hidden cron 任务，不是用户手动设置的
  - daily-memory-flush 连续4次超时的原因：isolated session 启动 + 模型加载 + 任务执行超过120秒限制
- [修复的]
  - 彻底删除 sync-douyin-files（每30分钟，脚本方式）
  - 彻底删除 douyin-sync（每天3点，agentTurn方式）
  - daily-memory-flush 超时从 120秒改为 300秒
- [配置的]
  - daily-memory-flush 超时调整为 300秒，连续错误计数重置
- [待跟进]
  - TTS 语音功能异常（Edge TTS 空文件），待排查
  - 观察 daily-memory-flush 明天09:00是否正常执行

### 2026-04-01 09:00 - 每日总结
- [学到的]
  - daily-memory-flush 超时修复生效，本次任务正常执行完毕
- [修复的]
  - daily-memory-flush 昨天修复后的首次验证成功（09:00准时触发，未超时）
- [配置的]
  - 暂无新配置变更
- [待跟进]
  - TTS 语音功能异常（Edge TTS 空文件），待进一步排查
  - 继续观察 daily-memory-flush 每日执行稳定性

### 2026-04-02 09:00 - 每日总结
- [学到的] 技能同步机制正常运行，9个技能全部同步成功
- [修复的] daily-memory-flush 超时修复连续两日验证成功（04-01、04-02 09:00均正常）
- [配置的] 暂无新配置变更
- [待跟进]
  - TTS 语音功能异常（Edge TTS 生成空文件），至今未修复
  - 继续观察 daily-memory-flush 每日执行稳定性
### 2026-04-07 每日总结
- **学到的：**
  - 股票课程第二章核心概念：举重理论（扩散=危险/收敛=安全）、加速赶底锁筹、一字板封单强度、大阳线有效性依赖指数配合、箱体突破买点
  - 缺氧新手教程已学完9集（开局到三级科技全流程）
- **修复的：** 无新增修复
- **配置的：** 暂无新配置变更
- **待跟进：**
  - BibiGPT充值后继续学习缺氧第10-13集（液冷/蒸汽机/无尽水）
  - 股票课程第二章继续推进
  - TTS语音功能异常（Edge TTS空文件，长期未解决）

### 2026-04-05 19:29 - 3小时检查点
- 股票课程第二章转录进行中
- 已完成: 2.1, 2.10, 2.11, 2.12 (4/36个视频)
- 当前: 2.13 黄昏之星+晨星结构
- CPU模式转录，速度较慢
- GPU问题: WSL2检测不到NVIDIA GPU，需用户配合配置
- 待跟进: 第二章全部转录完后整理笔记

### 2026-04-05 20:50 - GPU 转录成功启用
- conda 环境 whisper-stt 包含 PyTorch CUDA 支持
- RTX 5070 已启用，转录速度提升数十倍
- conda 路径: /home/dhtaiyi/.conda/envs/whisper-stt/bin/python
- 脚本: ~/.openclaw/workspace/scripts/transcribe_stock_ch2.py
- 股票课程第二章 GPU 转录已启动（36个视频）

### 2026-04-06 01:10 - 第二章笔记整理完成
- 股票课程第二章 36 个视频全部转录完成（GPU加速）
- 第二章笔记已整理：第二章笔记-交易的形.md
- 内容包括：大阳线、大阴线、股价结构、K线形态、缺口等

### 2026-04-07 早晨 - 搜索和股票工具全面修复

**学到的：**
- DuckDuckGo搜索被防火墙拦截，Bing搜索可用
- MiniMax搜索正常工作（sk-cp-... Token）
- 新浪/腾讯行情API免费可用
- 东财API（push2.eastmoney.com）被代理封了
- MX API（mkt__ Token）是东方财富的另一个数据源
- cron任务格式：必须用schedule字段，不能直接在顶层放kind/expr

**修复的：**
- MiniMax搜索工具恢复正常
- Tushare Token配置成功（01511f07de6ef15b01224fa22a9f399845c4b75e82a71cd218510f84）
- 东方财富MX搜索Token验证成功（mkt__bGBVbyVyWGlJi1PS8r_gJLSNmmd6-1gIDweArbPs6I）
- daily-board-record cron任务格式错误已修复

**配置的：**
- 每日连板股票记录脚本：~/.openclaw/workspace/scripts/daily_board_monitor.sh
- 每周一到周五15:05自动执行，记录连板梯队数据
- 保存位置：~/.openclaw/workspace/stock-data/daily-boards/

**待跟进：**
- 观察daily-board-record cron任务是否稳定运行
- BibiGPT余额仍不足，缺氧游戏教程停在第9集

### 2026-04-08 下午 - 股票系统全面升级

**学到的：**
- mootdx 通达信协议安装成功（pip install mootdx --break-system-packages）
- 腾讯/东财实时行情API
- 天天基金+东财F10基金数据
- 超短龙头战法_v1.0.md 完整策略文件
- 深度整合笔记_20260408.md 汇总所有学习体系

**搭建的工具：**
- stock_tdx_analyzer.py - mootdx通达信综合分析
- stock_analyzer.py - 腾讯API综合分析
- fund_analyzer.py - 基金分析（易方达等）
- stock_realtime.py - 实时行情获取

**今日市场：**
- 上升期，涨停118只
- 主线：光纤+算力
- 重点：汇源通信4连板、通鼎互联2连板、金陵药业2连板
- 风险：津药药业7板炸板

**待跟进：**
- 龙虎榜API失效，需找替代方案

### 2026-04-09 每日总结 - 股票系统大升级
- [学到] 涨停前4大形态：上影线洗盘(46%)、跳空高开(37%)、缩量小K线(35%)、缩量回调(29%)
- [学到] 龙头更替规律：分化期老龙头必死，新龙头换血，逻辑硬的才能穿越
- [学到] 买点A首板战法回测胜率62.9%
- [修复] 板块分析改用"涨停成交额"排序，解决"其他"板块过大问题
- [配置] 每日15:05自动运行涨停首板形态分析（cron已设置）
- [待跟进] 明日重点：东山精密、光迅科技、长飞光纤（买点A首板）

### 2026-04-09 晚间总结（21:00-23:00大迭代）
- [学到] mootdx 通达信协议可获取K线历史/板块成分/实时bid-ask
- [学到] 上影线突破形态（仙人指路）52只样本统计：上影线46%/跳空37%/缩量35%/缩量回调29%
- [修复] shadow_break.py 的上影线计算bug（上影线/实体>50%阈值）
- [配置] 新增定时任务：9:15竞价分析、9:30开盘快报、11:30午间策略、盘中突破提醒（每5分钟）、尾盘突破提醒
- [配置] breakthrough_alert.py - 盘中突破提醒（监控东山精密/光迅科技/长飞光纤/汇源通信/长芯博创/益佰制药/通鼎互联）
- [配置] daily_pattern_analysis.py - 每日涨停首板形态分析（cron已设置）
- [待跟进] 明日重点：东山精密、光迅科技、长飞光纤买点A首板；通鼎互联买点D低吸；回避汇源通信6板高位
- [待跟进] 益佰制药4板，创新药/AACR逻辑，关注是否能分歧转一致

### 2026-04-10 09:00 - OpenCLI 安装完成
- **工具**：@jackwener/opencli v1.7.0
- **安装路径**：~/.npm-global/bin/opencli
- **功能**：支持84个平台的浏览器自动化数据获取，基于Chrome CDP协议
- **支持平台**：微信公众号、小红书、B站、知乎、雪球、Twitter/X、微博、抖音、Reddit等
- **状态**：CLI已装，Daemon运行中(port 19825)，Chrome扩展未连接
- **待完成**：用户需安装Browser Bridge Chrome扩展 + 打开Remote Debugging
- **参考文章**：江枫《只需要一个CLI，Agent就可以下载公众号/小红书/B站》
- **工具**：@jackwener/opencli v1.7.0
- **安装路径**：~/.npm-global/bin/opencli
- **功能**：支持84个平台的浏览器自动化数据获取，基于Chrome CDP协议
- **支持平台**：微信公众号、小红书、B站、知乎、雪球、Twitter/X、微博、抖音、Reddit等
- **状态**：CLI已装，Daemon运行中(port 19825)，Chrome扩展未连接
- **待完成**：用户需安装Browser Bridge Chrome扩展 + 打开Remote Debugging
- **参考文章**：江枫《只需要一个CLI，Agent就可以下载公众号/小红书/B站》

### 2026-04-10 15:50 - 股票策略v3.0 + 图形收集系统搭建

**策略迭代：**
- v1.0：买点A首板战法
- v2.0：加入流通市值30-200亿过滤 + 连板≤3板限制
- v3.0：整合养家心法+退学炒股+威科夫+举重理论

**v3.0买点体系：**
- 买点A：首板战法（昨日涨停，今高开3-7%超预期）
- 买点B：一进二接力（最强模式！分歧转一致打板）
- 买点C：连板持筹（首阴不破5日线则持有）
- 买点D：空间板低吸（龙回头，5日线附近）
- Spring：威科夫假跌破=买入信号

**今日涨停图形库（4月10日）：**
- 东山精密(002384)：3连板+8.8%，算力主线
- 华远控股(600743)：4连板+10%，并购62亿小市值
- 来伊份(603777)：3连板+10%，股权转让57亿小市值
- 睿能科技(603933)：2连板+10%，科技复牌51亿小市值

**明日重点（v3.0策略）：**
- 来伊份(603777)：评分85，买点B，小市值57亿
- 睿能科技(603933)：评分75，买点B，小市值51亿
- 东山精密(002384)：评分55，持筹，市值2629亿偏大

**图形收集系统：**
- 目录：~/.openclaw/workspace/stock-patterns/
- 脚本：daily_pattern_collector.py / daily_pattern_scan.py
- 每日15:10自动扫描（cron已设置）
- 6条历史验证图形：上影线突破/一字板/小市值+主线/推土机/首阴不破5日线/收敛整理

**明日观察（图形扫描）：**
- 通鼎互联：🔴上影线突破+小市值+放量，明日关注
- 光迅科技：🔴上影线突破+放量，但市值870亿偏大

### 2026-04-10 下午 - 股票策略v3.0 + 涨停图形收集系统 + 趋势跟踪系统

**今日成果：**
- OpenCLI (@jackwener/opencli v1.7.0) 已安装（84个平台，公众号/小红书/B站/知乎等）
- tushare-data skill 已安装（clawhub install tushare-data）
- BibiGPT 技能已删除
- breakthrough_alert.py 已更新：增加流通市值/总市值显示
- 股票策略 v2.0：加入流通市值30-200亿过滤 + 连板≤3板限制
- 股票策略 v3.0：整合养家心法+退学炒股+威科夫+举重理论

**涨停图形收集系统（v1.0）：**
- 目录：~/.openclaw/workspace/stock-patterns/
- 核心脚本：
  - daily_pattern_collector.py：基础框架（数据库读写、腾讯API）
  - daily_pattern_scan.py：每日扫描器（形态识别+相似匹配+报告生成）
  - daily_trend_tracker.py：趋势股跟踪器
  - update_candidates.py：每日候选池更新
  - daily_pattern_scan.sh / daily_trend_scan.sh：定时执行脚本
- 数据目录：
  - candidates/：每日候选股池
  - limitup_history/：涨停历史+涨停前数据
  - trend_patterns/patterns.json：历史图形库（6条）
  - trend_history/：趋势股每日跟踪
  - daily_report/：每日复盘报告

**历史图形库（6条）：**
- P001: 上影线突破（仙人指路）- 高置信度
- P002: 连续一字板 - 高置信度
- P003: 小市值+主线题材(30-80亿) - 高置信度
- P004: 推土机涨停 - 中置信度
- P005: 首阴不破5日线 - 中置信度
- P006: 收敛整理旗型 - 中置信度

**趋势跟踪类型（7种）：**
- 均线多头、均线多头+历史新高、箱体突破
- 旗型整理、缩量回踩、加速上涨、高位震荡

**每日自动任务（交易日15:10）：**
- 收盘后图形扫描（cron已设置）
- 收盘后趋势跟踪（cron已设置）

**今日收盘数据：**
- 东山精密(002384)：143.55元 +8.8%，3连板，明日4板预期
- 华远控股(600743)：2.91元 +10%，4连板，62亿小市值
- 来伊份(603777)：16.97元 +10%，3连板，57亿小市值
- 睿能科技(603933)：24.53元 +10%，2连板，51亿小市值
- 汇源通信(000586)：22.61元 -10%，6板断板跌停
- 通鼎互联(002491)：14.59元 -9.6%，断板跌停
- 光迅科技(002281)：107.82元 -0.2%，旗型整理，接近突破108.09
- 中际旭创(300308)：734.65元 +6%，历史新高700元突破

**v3.0策略明日重点：**
- 来伊份(603777)：评分85，买点B，小市值57亿，股权转让
- 睿能科技(603933)：评分75，买点B，小市值51亿，科技复牌

**趋势明日关注：**
- 光迅科技(002281)：旗型整理，关注突破108.09

### 2026-04-11 09:00 - 每日总结
- [学到的]
  - Cron 任务超时问题排查：9:30开盘快报、11:30午间策略、股票知识午间学习等多个交易日 cron 任务超时失败
  - cloud-skills-sync 也存在连续超时问题（连续2次错误）
  - 部分 cron 任务运行正常：盘中突破提醒✅、集合竞价扫描✅、尾盘突破提醒✅
- [修复的] 暂无新修复
- [配置的] 暂无新配置
- [待跟进]
  - 优化超时 cron 任务的脚本执行时间，或调整超时限制
  - cloud-skills-sync 超时问题需排查（可能需要修复脚本）
  - BibiGPT 余额不足（长期未解决）
  - TTS 语音功能异常（长期未解决）
  - OpenCLI Chrome 扩展未安装配置（长期未解决）


### 2026-04-14 下午 - 股票系统自动更新链路打通

**修复的问题：**
- `update_candidates.py`: 缺少 `from datetime import timedelta`
- `morning_scan.sh`: 东财接口被墙，改用新浪接口（稳定）
- `daily_pattern_scan.py`: limitup_db 类型错误（list→dict）+ 历史匹配逻辑简化
- 新增 `collect_limitup.sh`: 每日15:05采集涨停历史（之前缺失）

**新建脚本：**
- `morning_scan.sh`: 09:00早盘扫描昨日涨停股，筛选5只观察标的
- `collect_limitup.sh`: 15:05采集当日涨停股明细
- `daily_candidate_update.sh`: 15:10更新候选池+同步监控列表

**已添加 Cron 任务：**
- 09:00 早盘候选扫描（周一至周五）
- 15:05 涨停历史采集
- 15:10 候选股池自动更新

**数据接口稳定性：**
- 腾讯 qt.gtimg.cn ✅ 实时行情
- 新浪 vip.stock.finance.sina.com.cn ✅ 涨幅榜/涨停股
- 东财 push2.eastmoney.com ❌ 被封
- 腾讯 web.ifzq.gtimg.cn ✅ 历史K线

### 2026-04-14 下午 - 股票系统第二轮迭代

**本次迭代解决的问题：**
- V1早盘扫描缺陷：只选"昨日涨停股"，漏掉佰维存储(146亿)/沪电股份(90亿)等机构主线股
- 情绪判断缺失：无法区分"机构主导"vs"连板情绪"两种完全不同行情

**新增/改进脚本：**
- `morning_scan_v2.sh`: 多维度扫描（涨停+机构信号+高成交强势股）
  - 涨停股：成交额排序
  - 机构信号：成交额前30中涨幅>=5%的趋势股
  - 高成交强势：成交额>15亿+涨幅5%+
- `market_sentiment.py`: 市场情绪识别V2
  - 核心判断：成交额TOP5中有≥2只是非涨停(涨幅2%+)→机构主导
  - 机构主导：趋势股持有+轻仓首板，不追连板
  - 连板情绪：积极参与龙头连板

**今日验证（2026-04-14收盘）：**
- 旧V1候选：C三瑞/国际复材/盛新锂能（错过佰维存储146亿/沪电股份90亿）
- V2候选：工业富联(149亿)/佰维存储(146亿)/兆易创新(129亿)/江波龙(91亿)/沪电股份(90亿)
- 情绪判断：🔵 机构主导行情 ✅（正确！）
- 实际市场：机构抱团佰维存储/中际旭创/宁德时代，TOP成交全是非涨停趋势股

**Cron任务顺序：**
- 09:00 → 市场情绪扫描（判断机构vs连板）
- 09:01 → 早盘候选扫描V2（根据情绪调整）
- 15:05 → 涨停历史采集
- 15:10 → 候选池更新+图形扫描

**数据接口：**
- 腾讯 qt.gtimg.cn ✅ 实时（12字段格式，pct=parts[5]）
- 新浪 vip.stock.finance.sina.com.cn ✅ 涨幅榜/成交额
- 东财 push2.eastmoney.com ❌ 被封

### 2026-04-14 下午 - 股票系统第三轮迭代（深度知识整合）

**本次迭代：结合股票课程核心知识**

**新增系统：**

1. **智能选股评分系统** (`smart_scoring.py`)
   - 5因子评分模型（成交额30/图形25/位置20/跟风15/环境10）
   - 课程核心：举重理论（振幅收敛=安全）、低位起（<10元）、跟风原理
   - 3日累计涨幅计算（避免超买陷阱）
   - 竞价跳空过滤（+3~7%最佳，>9%危险）

2. **买点分析系统** (`buy_point_analyzer.py`)
   - 买点A：首板战法（昨日<3%，今高开3-7%）
   - 买点B：一进二接力（缩量最佳，放量=分歧）
   - 买点C：5日线低吸（龙头回调）
   - 买点D：收敛突破（举重理论：振幅逐日收窄）

3. **晚盘综合分析链路** (`evening_pipeline.sh`)
   - 整合6个步骤：涨停采集→图形扫描→候选池更新→智能评分→买点分析→情绪回顾

**今日验证结果：**
- 工业富联：综合评分80分（满分）—— 成交149亿+高度收敛(7.2%)+机构跟风
- 沪电股份：买点A信号（首板战法）—— 竞价+6%，昨日涨幅<1%
- 情绪判断：🔵 机构主导 ✅（成交额TOP5全是非涨停趋势股）

**完整每日链路（第三轮）：**
```
09:00 → 市场情绪扫描（判断机构/连板/混沌/退潮）
09:01 → 早盘候选扫描V2（多维度选股：涨停+机构+高成交）
09:02 → 智能评分（5因子模型排序）
盘中   → 每5分钟扫突破信号
15:10 → 晚盘综合链路（采集+图形+评分+买点+情绪）
```

**数据接口：**
- 腾讯 qt.gtimg.cn ✅ 实时行情（12字段，pct=parts[5]）
- 腾讯 web.ifzq.gtimg.cn ✅ 历史K线（5日/日线）
- 新浪 vip.stock.finance.sina.com.cn ✅ 涨幅榜/成交额
- 东财 push2.eastmoney.com ❌ 被封

### 2026-04-14 晚间 - 第三轮迭代完成总结
- [学到] 举重理论量化应用：3日振幅收敛→主力控盘→安全；低位起(<10元)=安全垫厚
- [学到] 跟风原理：机构信号=成交额前30+涨幅5%+非涨停
- [修复] morning_scan_v2: 指数解析pct字段错误(parts[32]→parts[5])
- [修复] buy_point_analyzer: yesterday_pct计算bug
- [配置] evening_pipeline.sh: 整合6步骤晚盘链路
- [配置] market_sentiment.py V2: 机构主导识别(2只非涨停强势+成交>200亿)
- [待跟进] 明日9:00验证早盘链路是否正常运行

### 2026-04-15 早间 - Cron健康检查 + 第三轮迭代补充

**Cron超时问题（需优化）：**
- 09:30 开盘快报：连续3次 timeout（market_scanner.py + buy_sell.py）
- 11:30 午间策略：连续3次 timeout（market_scanner.py）
- 12:00 午间学习：1次 timeout（stock-learning/daily_learn.py）
- 根因分析：timeoutSeconds=120-180s 仍超时 → 脚本本身执行慢或模型调用问题
- **建议**：检查 market_scanner.py 执行效率，或将这些 agentTurn cron 改为 systemEvent 直接调脚本

**今日早盘链路已触发（待验证）：**
- 09:00 → market_sentiment.py + morning_scan_v2.sh 并行运行中
- 验证结果待盘中确认

**候选股关注：**
- 沪电股份：买点A信号（首板战法）
- 力诺药包(301188)：控股股东增持9000万+中硼硅概念

### 2026-04-15 全天 - 问财Iwencai集成 + 股票系统第四轮完成
- [学到的]
  - 问财SkillHub CLI安装：手动python3 zipfile解压（系统无unzip）+ 安装到~/.local/bin/
  - 问财API：sk-proj-01-NAItJumXGkKAe1Ha8v-rPenhNjrfud7CDgoY0DEAymigKrbbZSIwxhjOQG5RrqWytp8AZApOyf4RsS-q5d2FbyTbPZAYJC262Vbgthv9IizhxH3W-5a2kNpR3ifa0nAobbl6NQ
  - 32个问财技能全部安装成功（选股/财务/板块/形态/缠论/研报等）
  - 腾讯接口字段：涨跌幅在parts[5]（批量接口）vs parts[32]（完整接口）
  - 腾讯接口返回格式`="内容"`（=后直接引号），正则要用`"([^"]+)"`而非`="([^"]+)"`
  - Cron任务注册后需用`openclaw cron add`命令才能被守护进程加载
  - 午间休市判断：优先判断11:30-13:00为午休
- [修复的]
  - market_sentiment.py: 腾讯指数字段+正则+午休处理+收盘后分析
  - realtime_top_scanner.py: 正则匹配bug
  - smart_scoring.py: 正则匹配修复
  - smart_scanner_v2.py: 语法错误（中文冒号）+ time vs datetime冲突
  - 收盘后"closed"状态不再跳过（market_sentiment）
- [配置的]
  - 问财CLI：~/.local/bin/iwencai-skillhub-cli
  - 问财环境变量：IWENCAI_BASE_URL + IWENCAI_API_KEY（写入~/.bashrc）
  - 6个脚本全部升级v3.0：tomorrow_picker/breakeven_tracker/realtime_top_scanner/market_sentiment/smart_scanner_v2/auction_monitor
  - Cron新增：9:30智能扫描/13:00午盘观察/盘中实时扫描(13:30/14:00/14:30)
  - 完整每日链路：09:00情绪→09:01早盘→09:30盘中→13:00午盘→13:30-14:30盘中→15:10晚盘
- [待跟进]
  - 验证明日9:30/13:00等cron是否正常（今日刚加）
  - 把更多自研脚本接入问财（缠论/K线形态/事件驱动）
  - 观察神剑股份(002361)/利通电子(603629)/协创数据(301856)明日竞价
  - 混沌期验证：昨日涨停71只→掉队44只(62%)，今日新首板52只
