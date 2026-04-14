#!/home/dhtaiyi/.conda/envs/openclaw/bin/python3
"""批量转录股票课程视频"""

import subprocess
import os
import sys

COURSES_DIR = "/home/dhtaiyi/.openclaw/workspace/stock-courses"
TMP_DIR = "/tmp"

# Chapter 1 videos (14 files)
ch1_videos = [
    "1.1-主力行为逻辑.mp4",
    "1.2-盘口的重要性以及组成.mp4",
    "1.3-夹板盘的目的及运用.mp4",
    "1.4-压单、托单的目的及运用.mp4",
    "1.5-吃货盘口的典型特征.mp4",
    "1.6-出货盘口的典型特征.mp4",
    "1.7-拆单及对敲的目的及识别.mp4",
    "1.8-如何识别分时结构洗盘.mp4",
    "1.9-识别跌停出货及跌停吃货.mp4",
    "1.10-识别涨停出货及涨停吃货.mp4",
    "1.11-黄白线的关系及初步运用.mp4",
    "1.12-龙虎榜的简单运用.mp4",
    "1.13-集合竞价-集合竞价原理.mp4",
    "1.14-集合竞价-集合竟价在热门股中的运用.mp4",
]

# Chapter 2 videos (36 files)
ch2_videos = [
    "2.1-股价结构及常用辅助线.mp4",
    "2.2-大阳线(一)-意义.mp4",
    "2.3-大阳线(一)一字涨停;实体涨停;推土机大阳线;有影线性质的大阳线;尾盘大阳线.mp4",
    "2.4-大阳线(二)-大阳线启动的有效性.mp4",
    "2.5-大阳线(五)-下降趋势的大阳线.mp4",
    "2.6-大阳线(四)-箱体中大阳线.mp4",
    "2.7-大阳线(五)-多头趋势中的大阳线.mp4",
    "2.8-大阴线(一）-出货阶段的大阴线.mp4",
    "2.9-大阴线（二）-加速赶底大阴线的特征+箱体破位的阴线技术条件.mp4",
    "2.10-大阴线(三）-多头趋势中的大阴线+假阴线的逻辑+调整阴线.mp4",
    "2.11-加速K线和极小线及缺口.mp4",
    "2.12-几种典型的股价结构(一)-黄昏之星+晨星结构+仙人指路.mp4",
    "2.13-几种典型的股价结构(二)-扩散+收敛+旗型++二低点.mp4",
    "2.14-标志性K线形态-高浪线型+高分歧线型+高滞涨线型.mp4",
]

# Add remaining chapter 2 files from download
ch2_dir = f"{COURSES_DIR}/ch2"
for f in sorted(os.listdir(ch2_dir)):
    if f.endswith('.mp4') and f not in ch2_videos:
        ch2_videos.append(f)

def transcribe_video(video_path, txt_path):
    """转录单个视频"""
    if os.path.exists(txt_path):
        size = os.path.getsize(txt_path)
        if size > 1000:  # Skip if already transcribed
            print(f"  已存在，跳过: {os.path.basename(txt_path)}")
            return True
    
    video_name = os.path.basename(video_path)
    print(f"  转录中: {video_name}")
    
    # Extract audio
    audio_path = f"{TMP_DIR}/audio_{os.getpid()}.wav"
    try:
        subprocess.run([
            'ffmpeg', '-i', video_path,
            '-vn', '-acodec', 'pcm_s16le',
            '-ar', '16000', '-ac', '1',
            audio_path, '-y'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=600)
        
        # Transcribe
        result = subprocess.run([
            'python3', '-c',
            f'''
from faster_whisper import WhisperModel
model = WhisperModel("medium", device="cuda", compute_type="int8")
segments, info = model.transcribe("{audio_path}", language="zh", beam_size=5)
with open("{txt_path}", "w", encoding="utf-8") as f:
    for segment in segments:
        f.write(f"[{{segment.start:.1f}}s - {{segment.end:.1f}}s] {{segment.text.strip()}}\\n")
print("转录完成")
'''
        ], capture_output=True, text=True, timeout=7200)
        
        os.remove(audio_path)
        return True
        
    except Exception as e:
        print(f"  错误: {e}")
        if os.path.exists(audio_path):
            os.remove(audio_path)
        return False

def main():
    print("=" * 50)
    print("开始批量转录股票课程")
    print("=" * 50)
    
    # Process Chapter 1
    print("\n📚 第一章 - 交易的'术'")
    ch1_dir = f"{COURSES_DIR}/ch1"
    for i, video in enumerate(ch1_videos):
        video_path = f"{ch1_dir}/{video}"
        txt_path = f"{ch1_dir}/{video.replace('.mp4', '.txt')}"
        if os.path.exists(video_path):
            print(f"[{i+1}/{len(ch1_videos)}]")
            transcribe_video(video_path, txt_path)
    
    # Process Chapter 2
    print("\n📚 第二章 - 交易的'形'")
    ch2_dir = f"{COURSES_DIR}/ch2"
    for i, video in enumerate(ch2_videos):
        video_path = f"{ch2_dir}/{video}"
        txt_path = f"{ch2_dir}/{video.replace('.mp4', '.txt')}"
        if os.path.exists(video_path):
            print(f"[{i+1}/{len(ch2_videos)}]")
            transcribe_video(video_path, txt_path)
    
    print("\n" + "=" * 50)
    print("🎉 全部转录完成!")
    print("=" * 50)

if __name__ == '__main__':
    main()
