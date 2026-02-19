#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 图片生成器 - 自动生成并提供下载链接
"""

import requests
import os
from datetime import datetime

# 智谱API配置
API_KEY = os.environ.get("ZHIPU_API_KEY", "")

# 图片提示词库
IMAGE_PROMPTS = {
    "worker": {
        "filename": "xiaohongshu_cover_worker.png",
        "prompt": "A young professional woman happily leaving work, bright modern office background, sunset through windows, AI assistant interface on phone, minimal modern style, warm bright colors, flat illustration"
    },
    "creator": {
        "filename": "xiaohongshu_cover_creator.png", 
        "prompt": "Beautiful content creator working at pink desk, AI assistant on laptop, social media analytics dashboard visible, warm cozy atmosphere, Xiaohongshu aesthetic, soft lighting"
    },
    "tech": {
        "filename": "xiaohongshu_cover_tech.png",
        "prompt": "Futuristic AI interface displaying multiple AI model logos, smart technology core, blue tech colors, minimalist design, glowing elements, modern flat style"
    },
    "xiaohongshu_post": {
        "filename": "xiaohongshu_post_content.png",
        "prompt": "AI assistant helping with content creation, smartphone screen showing Xiaohongshu app interface, creating posts with AI assistance, warm friendly atmosphere, modern minimal style"
    }
}

def generate_image(prompt, filename):
    """生成图片并保存"""
    
    url = "https://open.bigmodel.cn/api/paas/v4/images/generations"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "cogview-3",
        "prompt": prompt,
        "size": "1024x1024"
    }
    
    print(f"🎨 正在生成: {filename}")
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        result = response.json()
        
        if "data" in result and len(result["data"]) > 0:
            image_url = result["data"][0]["url"]
            
            # 下载图片
            img_response = requests.get(image_url)
            
            filepath = f"/root/.openclaw/workspace/{filename}"
            with open(filepath, "wb") as f:
                f.write(img_response.content)
            
            print(f"✅ 已保存: {filepath}")
            return filepath
        else:
            print(f"❌ 生成失败: {result}")
            return None
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None

def main():
    """生成所有配图"""
    
    print("=" * 60)
    print("    🎨 OpenClaw 图片生成器")
    print("=" * 60)
    print()
    
    generated = []
    
    for key, info in IMAGE_PROMPTS.items():
        filepath = generate_image(info["prompt"], info["filename"])
        if filepath:
            generated.append({
                "name": key,
                "filepath": filepath,
                "filename": info["filename"]
            })
        print()
    
    # 生成下载脚本
    if generated:
        print("=" * 60)
        print("    📦 生成下载脚本")
        print("=" * 60)
        print()
        
        with open("/root/.openclaw/workspace/download_images.sh", "w") as f:
            f.write("#!/bin/bash\n")
            f.write("# OpenClaw 图片下载脚本\n")
            f.write("# 生成时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n")
            
            for img in generated:
                f.write(f"# {img['name']}\n")
                f.write(f"# 下载: {img['filename']}\n")
                f.write(f"scp root@你的服务器IP:{img['filepath']} ./\n\n")
        
        os.chmod("/root/.openclaw/workspace/download_images.sh", 0o755)
        
        print("✅ 下载脚本已创建: /root/.openclaw/workspace/download_images.sh")
        print()
    
    # 输出总结
    print("=" * 60)
    print("    ✅ 图片生成完成")
    print("=" * 60)
    print()
    
    print("📁 已生成的图片:")
    for img in generated:
        print(f"  - {img['filename']} ({img['filepath']})")
    
    print()
    print("🔗 下载所有图片:")
    print(f"  bash {os.path.abspath('/root/.openclaw/workspace/download_images.sh')}")
    print()
    
    print("=" * 60)

if __name__ == "__main__":
    main()
