# MiniMax MCP 技能

本技能提供 MiniMax 强大的文生音频、文生图、文生视频、音乐生成等功能。

## 可用工具

| 工具 | 功能 |
|------|------|
| text_to_audio | 文字转语音 |
| list_voices | 列出所有可用音色 |
| voice_clone | 克隆语音 |
| voice_design | 用文字描述生成声音 |
| generate_video | 文生视频 |
| text_to_image | 文生图 |
| query_video_generation | 查询视频生成状态 |
| music_generation | 音乐生成 |

## 环境变量

需要配置以下环境变量：
- `MINIMAX_API_KEY`: MiniMax API Key
- `MINIMAX_API_HOST`: API 地址（国内 https://api.minimaxi.com，全球 https://api.minimax.io）

## 使用方法

### 文字转语音
```python
# 使用方法
text_to_audio(
    text="要转换的文字",
    voice_id="male-qn-qingse",  # 可选音色
    speed=1.0,  # 语速 0.5-2.0
    emotion="happy"  # 情绪 happy/sad/angry/fearful/disgusted/surprised/neutral
)
```

### 列出所有音色
```python
list_voices()
```

### 语音克隆
```python
voice_clone(
    audio_file_path="/path/to/audio.wav",
    reference_text="音频对应的文字"
)
```

### 声音设计
```python
voice_design(
    prompt="描述想要的声音特点，如：温柔的女声，略带磁性"
)
```

### 文生视频
```python
generate_video(
    prompt="视频描述",
    model="hailuo-01"或"hailuo-02",  # 可选
    duration=6,  # 6或10秒
    resolution="768p"或"1080p"
)
```

### 文生图
```python
text_to_image(
    prompt="图片描述"
)
```

### 查询视频生成状态
```python
query_video_generation(
    task_id="视频生成任务的task_id"
)
```

### 音乐生成
```python
music_generation(
    prompt="音乐风格描述",
    lyrics="歌词内容"
)
```

## 配置 MCP

确保 MCP 配置正确：
```json
{
  "mcpServers": {
    "minimax": {
      "command": "/usr/local/python3.12/bin/minimax-mcp",
      "env": {
        "MINIMAX_API_KEY": "your-api-key",
        "MINIMAX_API_HOST": "https://api.minimaxi.com"
      }
    }
  }
}
```

## 注意事项

- 使用这些工具可能产生费用
- 确保 API Key 和 API Host 地区匹配
- 视频生成是异步的，需要用 task_id 查询结果
