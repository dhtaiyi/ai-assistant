#!/home/dhtaiyi/.conda/envs/openclaw/bin/python3
"""转录股票课程第二章视频"""
import os
import sys

os.environ['HF_HUB_OFFLINE'] = '1'

from faster_whisper import WhisperModel

VIDEO_DIR = "/home/dhtaiyi/.openclaw/workspace/stock-courses/ch2"

print("加载模型中...")
model = WhisperModel("Systran/faster-whisper-medium", device="cuda", compute_type="int8")

videos = [f for f in os.listdir(VIDEO_DIR) if f.endswith('.mp4')]
videos.sort()

for i, video in enumerate(videos, 1):
    base = video.rsplit('.', 1)[0]
    txt_file = os.path.join(VIDEO_DIR, base + ".txt")
    
    if os.path.exists(txt_file) and os.path.getsize(txt_file) > 100:
        print(f"[{i}/{len(videos)}] 跳过(已存在): {video}")
        continue
    
    print(f"[{i}/{len(videos)}] 转录中: {video}")
    try:
        segments, info = model.transcribe(
            os.path.join(VIDEO_DIR, video),
            language='zh',
            vad_filter=True
        )
        
        with open(txt_file, 'w', encoding='utf-8') as out:
            for seg in segments:
                out.write(seg.text + '\n')
        
        print(f"  完成: {video}")
    except Exception as e:
        print(f"  失败: {video} - {e}")

print("=== 全部完成 ===")
