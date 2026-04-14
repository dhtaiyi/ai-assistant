#!/home/dhtaiyi/.conda/envs/openclaw/bin/python3
"""抖音直播转文字脚本 - 带降噪版"""
import sys
import os
import subprocess
from datetime import datetime

# 离线模式 - 不下载模型
os.environ['HF_HUB_OFFLINE'] = '1'

from faster_whisper import WhisperModel

# 视频文件夹
VIDEO_DIR = "/mnt/f/Program Files/WeGame/dhtaiyi/openclaw douyin work"

# 降噪脚本临时文件
DENOISE_SCRIPT = "/tmp/denoise_script.py"

def send_notification(message):
    """发送飞书通知"""
    try:
        cmd = f'openclaw message send --target ou_04add8ebe219f09799570c70e3cdc732 --message "{message}"'
        subprocess.run(cmd, shell=True, capture_output=True)
    except Exception as e:
        print(f"发送通知失败: {e}")

def get_video_files():
    """获取文件夹中所有需要转录的视频文件"""
    if not os.path.exists(VIDEO_DIR):
        print(f"文件夹不存在: {VIDEO_DIR}")
        return []
    
    video_extensions = ['.flv', '.mp4', '.mp3', '.wav', '.aac', '.m4a']
    videos = []
    
    for f in os.listdir(VIDEO_DIR):
        ext = os.path.splitext(f)[1].lower()
        if ext in video_extensions:
            videos.append(f)
    
    return sorted(videos)

def needs_transcription(video_file):
    """检查是否需要转录（同名的txt文件是否存在）"""
    base_name = os.path.splitext(video_file)[0]
    txt_file = base_name + ".txt"
    txt_path = os.path.join(VIDEO_DIR, txt_file)
    
    # 如果同名txt文件不存在或为空，需要转录
    if not os.path.exists(txt_path):
        return True
    
    # 检查文件是否为空
    if os.path.getsize(txt_path) < 100:
        return True
    
    return False

def extract_audio(video_file):
    """提取音频"""
    video_path = os.path.join(VIDEO_DIR, video_file)
    base_name = os.path.splitext(video_file)[0]
    audio_wav = os.path.join(VIDEO_DIR, f"/tmp/{base_name}_audio.wav")
    
    # 提取音频为16kHz wav
    cmd = f'ffmpeg -i "{video_path}" -vn -ar 16000 -ac 1 -acodec pcm_s16le "{audio_wav}" -y'
    print(f"提取音频...")
    subprocess.run(cmd, shell=True, capture_output=True)
    
    return audio_wav

def denoise_audio(audio_file, output_file):
    """降噪处理"""
    print("降噪处理...")
    
    # 创建降噪脚本
    denoise_script = f'''
import numpy as np
import soundfile as sf
import noisereduce as nr

y, sr = sf.read("{audio_file}")
y_denoised = nr.reduce_noise(y=y, sr=sr, prop_decrease=0.8)
sf.write("{output_file}", y_denoised, sr)
print("降噪完成")
'''
    
    with open(DENOISE_SCRIPT, 'w') as f:
        f.write(denoise_script)
    
    # 运行降噪脚本
    result = subprocess.run(f'python3 {DENOISE_SCRIPT}', shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"降噪失败，使用原文件: {result.stderr}")
        # 如果降噪失败，复制原文件
        subprocess.run(f"cp {audio_file} {output_file}", shell=True)
    else:
        print(result.stdout)
    
    return output_file

def transcribe(audio_file, output_file):
    """转写"""
    print("转写中...")
    
    # 自动检测并使用 GPU（如果可用）
    import ctranslate2
    if ctranslate2.get_cuda_device_count() > 0:
        print(f"🎮 检测到 {ctranslate2.get_cuda_device_count()} 个 CUDA 设备")
        try:
            model = WhisperModel("Systran/faster-whisper-medium", device="cuda", compute_type="float16")
            print("✅ 使用 GPU (CUDA float16) 加速")
        except Exception as e:
            print(f"⚠️ GPU 初始化失败: {e}")
            print("🔄 使用 CPU 模式")
            model = WhisperModel("Systran/faster-whisper-medium", device="cpu", compute_type="float16")
    else:
        print("🔄 使用 CPU 模式 (未检测到 GPU)")
        model = WhisperModel("Systran/faster-whisper-medium", device="cpu", compute_type="float16")
    
    segments, info = model.transcribe(
        audio_file,
        language="zh",
        beam_size=5,
        vad_filter=True
    )
    
    lines = []
    lines.append("="*60)
    lines.append(f"抖音直播转文字 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("="*60)
    lines.append("")
    
    for segment in segments:
        start = segment.start
        text = segment.text.strip()
        
        # 格式化为 时:分:秒
        h = int(start // 3600)
        m = int((start % 3600) // 60)
        s = int(start % 60)
        
        line = f"[{h:02d}:{m:02d}:{s:02d}] {text}"
        lines.append(line)
        print(line)
    
    lines.append("")
    lines.append("="*60)
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    print(f"已保存到: {output_file}")
    return True

def process_video(video_file):
    """处理单个视频文件"""
    base_name = os.path.splitext(video_file)[0]
    txt_file = base_name + ".txt"
    txt_path = os.path.join(VIDEO_DIR, txt_file)
    
    print(f"\n{'='*60}")
    print(f"处理: {video_file}")
    print(f"{'='*60}")
    
    # 提取音频
    audio_file = extract_audio(video_file)
    base_name = os.path.splitext(video_file)[0]
    audio_denoised = os.path.join(VIDEO_DIR, f"/tmp/{base_name}_denoised.wav")
    
    # 降噪
    denoise_audio(audio_file, audio_denoised)
    
    # 转写
    success = transcribe(audio_denoised, txt_path)
    
    # 清理临时文件
    try:
        os.remove(audio_file)
        if os.path.exists(audio_denoised):
            os.remove(audio_denoised)
    except:
        pass
    
    if success:
        print(f"✅ {video_file} -> {txt_file}")
    else:
        print(f"❌ {video_file} 转写失败")
    
    return success

def main():
    print("="*60)
    print("抖音直播转录工具 - 带降噪版")
    print("="*60)
    
    # 获取所有视频文件
    videos = get_video_files()
    
    if not videos:
        print("没有找到视频文件")
        return
    
    print(f"找到 {len(videos)} 个视频文件")
    
    # 统计需要转录的视频数量
    videos_to_process = [v for v in videos if needs_transcription(v)]
    if videos_to_process:
        send_notification(f"🎙️ 开始转录了！共有 {len(videos_to_process)} 个视频待处理～")
    
    # 处理每个需要转录的视频
    processed = 0
    skipped = 0
    
    for video_file in videos:
        if needs_transcription(video_file):
            process_video(video_file)
            processed += 1
        else:
            print(f"⏭️ 跳过 {video_file} (已有txt)")
            skipped += 1
    
    print(f"\n完成! 处理: {processed}, 跳过: {skipped}")
    
    # 发送完成通知
    if processed > 0:
        send_notification(f"✅ 转录完成！共处理了 {processed} 个视频～")
    
    # 发送已转录文件到小雨服务器
    try:
        subprocess.run(['/home/dhtaiyi/.openclaw/workspace/scripts/send_transcribed_to_xiaoyu.sh'], 
                     capture_output=True, text=True, timeout=60)
        print("📤 已通知小雨服务器删除源文件")
    except Exception as e:
        print(f"通知服务器失败: {e}")

if __name__ == '__main__':
    main()
