#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智谱AI图像生成
"""

import requests
import json
import base64
import os
from datetime import datetime

# 智谱API配置
API_KEY = os.environ.get("ZHIPU_API_KEY", "")

def generate_image(prompt, filename="image.png"):
    """生成图片"""
    
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
    
    print(f"🎨 正在生成图片...")
    print(f"📝 提示词: {prompt[:50]}...")
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        result = response.json()
        
        print(f"📊 API返回: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}")
        
        if "data" in result and len(result["data"]) > 0:
            image_url = result["data"][0]["url"]
            
            # 下载图片
            img_response = requests.get(image_url)
            
            with open(filename, "wb") as f:
                f.write(img_response.content)
            
            print(f"✅ 图片已保存: {filename}")
            return filename
        else:
            print(f"❌ 生成失败: {result}")
            return None
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None

# 测试生成
if __name__ == "__main__":
    # 生成3个图片
    prompts = [
        # 图片1 - 打工人
        "A young professional woman happily leaving work, bright modern office background, sunset through windows, AI assistant interface on phone, minimal modern style, warm bright colors, flat illustration",
        
        # 图片2 - 自媒体
        "Beautiful content creator working at pink desk, AI assistant on laptop, social media analytics dashboard visible, warm cozy atmosphere, Xiaohongshu aesthetic, soft lighting",
        
        # 图片3 - 多模型
        "Futuristic AI interface displaying multiple AI model logos, smart technology core, blue tech colors, minimalist design, glowing elements, modern flat style"
    ]
    
    filenames = [
        "/home/dhtaiyi/.openclaw/workspace/image_worker.png",
        "/home/dhtaiyi/.openclaw/workspace/image_creator.png",
        "/home/dhtaiyi/.openclaw/workspace/image_tech.png"
    ]
    
    for i, (prompt, filename) in enumerate(zip(prompts, filenames), 1):
        print(f"\n{'='*60}")
        print(f"🎨 生成图片 {i}/3")
        print('='*60)
        
        result = generate_image(prompt, filename)
        
        if result:
            print(f"✅ 成功: {result}")
        else:
            print(f"❌ 失败")
