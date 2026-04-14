#!/home/dhtaiyi/.conda/envs/openclaw/bin/python3
"""GPU加速批量转录"""
import subprocess
import os
import sys

# 激活conda环境
subprocess.run(['bash', '-c', 'source ~/anaconda3/etc/profile.d/conda.sh && conda activate openclaw'], check=True)

from faster_whisper import WhisperModel

COURSES_DIR = "/home/dhtaiyi/.openclaw/workspace/stock-courses"
TMP_DIR = "/tmp"

print("🚀 加载GPU模型...")
model = WhisperModel("large-v3", device="cuda", compute_type="int8")
print("✅ 模型加载完成！")

def transcribe_video(video_path, txt_path):
    if os.path.exists(txt_path):
        size = os.path.getsize(txt_path)
        if size > 1000:
            print(f"  已存在，跳过: {os.path.basename(txt_path)}")
            return True
    
    video_name = os.path.basename(video_path)
    print(f"  转录: {video_name}", flush=True)
    
    try:
        segments, info = model.transcribe(video_path, language="zh", beam_size=5)
        count = 0
        with open(txt_path, "w", encoding="utf-8") as f:
            for seg in segments:
                f.write(f"[{seg.start:.1f}s - {seg.end:.1f}s] {seg.text.strip()}\n")
                count += 1
        print(f"  ✅ 完成! {count}段")
        return True
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return False

# 转录第一章剩余视频
print("\n📚 第一章剩余视频...")
ch1_dir = f"{COURSES_DIR}/ch1"
ch1_done = ["1.1", "1.2", "1.3", "1.4"]

for f in sorted(os.listdir(ch1_dir)):
    if not f.endswith('.mp4'):
        continue
    # 检查是否已完成
    done = False
    for d in ch1_done:
        if d in f:
            done = True
            break
    if done:
        continue
    
    video_path = f"{ch1_dir}/{f}"
    txt_path = f"{ch1_dir}/{f.replace('.mp4', '.txt')}"
    transcribe_video(video_path, txt_path)

# 转录第二章所有视频
print("\n📚 第二章视频...")
ch2_dir = f"{COURSES_DIR}/ch2"

for f in sorted(os.listdir(ch2_dir)):
    if not f.endswith('.mp4'):
        continue
    video_path = f"{ch2_dir}/{f}"
    txt_path = f"{ch2_dir}/{f.replace('.mp4', '.txt')}"
    transcribe_video(video_path, txt_path)

print("\n🎉 全部完成!")
