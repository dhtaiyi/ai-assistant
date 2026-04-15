#!/usr/bin/env python3
"""
视频转文字 - 使用 faster-whisper (GPU 加速)
用法: python3 video_to_text.py <视频文件路径> [模型大小]
"""

import sys
import os
import tempfile

# 设置 CUDA 库路径（必须在导入 faster_whisper 之前）
os.environ['LD_LIBRARY_PATH'] = '/usr/local/lib/ollama/cuda_v12:/usr/local/lib/ollama/mlx_cuda_v13:' + os.environ.get('LD_LIBRARY_PATH', '')

import subprocess

# 检查 faster-whisper
try:
    from faster_whisper import WhisperModel
except ImportError:
    print("❌ faster-whisper 未安装，请运行: pip install faster-whisper")
    sys.exit(1)

def extract_audio(video_path, audio_path):
    """使用 ffmpeg 从视频提取音频"""
    # 先提取原始音频，再转换
    tmp_audio = audio_path.replace('.wav', '_raw.m4a')
    cmd1 = [
        'ffmpeg', '-i', video_path,
        '-vn', '-acodec', 'aac',
        '-y', tmp_audio
    ]
    result = subprocess.run(cmd1, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ 音频提取失败: {result.stderr}")
        return False
    
    # 转换为 wav
    cmd2 = [
        'ffmpeg', '-i', tmp_audio,
        '-vn', '-acodec', 'pcm_s16le',
        '-ar', '16000', '-ac', '1',
        '-y', audio_path
    ]
    result = subprocess.run(cmd2, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ 音频转换失败: {result.stderr}")
        return False
    
    # 清理临时文件
    if os.path.exists(tmp_audio):
        os.remove(tmp_audio)
    
    return True

def transcribe(audio_path, model_size="medium"):
    """使用 faster-whisper 转写（GPU 加速）"""
    print(f"🚀 加载模型: {model_size}...")
    
    # 优先使用 GPU CUDA
    try:
        model = WhisperModel(model_size, device="cuda", compute_type="int8")
        print("✅ 使用 GPU (CUDA float16) 加速")
    except Exception as e:
        print(f"⚠️  GPU 加载失败: {e}")
        print("⚠️  使用 CPU 模式...")
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
    
    print("📝 转写中...")
    segments, info = model.transcribe(audio_path, language="zh")
    
    print(f"🎤 检测到语言: {info.language} (概率: {info.language_probability:.2f})")
    
    results = []
    for segment in segments:
        results.append({
            'start': segment.start,
            'end': segment.end,
            'text': segment.text.strip()
        })
    
    return results

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\n可用模型: tiny, base, small, medium, large-v2, large-v3")
        print("您已缓存的模型: base, medium")
        print("\n示例:")
        print("  python3 video_to_text.py /path/to/video.mp4")
        print("  python3 video_to_text.py /path/to/video.mp4 base")
        sys.exit(1)
    
    video_path = sys.argv[1]
    model_size = sys.argv[2] if len(sys.argv) > 2 else "medium"
    
    if not os.path.exists(video_path):
        print(f"❌ 文件不存在: {video_path}")
        sys.exit(1)
    
    # 创建临时音频文件
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        audio_path = tmp.name
    
    try:
        print(f"📹 视频: {video_path}")
        print(f"📦 模型: {model_size}")
        
        # 提取音频
        print("🎵 提取音频...")
        if not extract_audio(video_path, audio_path):
            sys.exit(1)
        
        # 转写
        results = transcribe(audio_path, model_size)
        
        # 输出结果
        print("\n" + "="*50)
        print("📄 转写结果:")
        print("="*50)
        
        full_text = ""
        for r in results:
            full_text += r['text'] + " "
            print(f"[{r['start']:.1f}s -> {r['end']:.1f}s] {r['text']}")
        
        # 保存到文件
        output_path = os.path.splitext(video_path)[0] + '.txt'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_text.strip())
        
        print(f"\n✅ 已保存到: {output_path}")
        
    finally:
        # 清理临时文件
        if os.path.exists(audio_path):
            os.remove(audio_path)

if __name__ == "__main__":
    main()
