#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import base64
import json
import os
import urllib.request
import urllib.error

def analyze_image(image_path, prompt=None):
    """使用智谱AI分析图片"""
    
    if not os.path.exists(image_path):
        print(f"错误: 文件不存在: {image_path}")
        return
    
    api_key = os.environ.get('ZHIPU_API_KEY')
    if not api_key:
        print("错误: 未配置 ZHIPU_API_KEY")
        print("请设置: export ZHIPU_API_KEY='your_api_key'")
        return
    
    # 默认提示词
    if not prompt:
        prompt = "请详细描述这张图片的内容"
    
    # 读取图片并编码
    with open(image_path, 'rb') as f:
        image_base64 = base64.b64encode(f.read()).decode('utf-8')
    
    # 确定MIME类型
    ext = image_path.split('.')[-1].lower()
    mime_types = {
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'gif': 'image/gif',
        'webp': 'image/webp'
    }
    mime_type = mime_types.get(ext, 'image/jpeg')
    
    # 构建请求
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    
    data = {
        "model": "glm-4v",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 1000
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    print(f"🔍 正在分析图片...")
    print()
    
    try:
        req = urllib.request.Request(
            url=url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if 'choices' in result:
                content = result['choices'][0]['message']['content']
                print(content)
                print()
                print("✅ 分析完成")
            else:
                print(f"错误: {result}")
                
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"HTTP错误: {e.code}")
        print(error_body)
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 analyze-image-zhipu.py <图片路径> [提示词]")
        print("示例: python3 analyze-image-zhipu.py photo.jpg")
        print("示例: python3 analyze-image-zhipu.py photo.jpg '分析这张图片'")
        sys.exit(1)
    
    image_path = sys.argv[1]
    prompt = sys.argv[2] if len(sys.argv) > 2 else None
    
    analyze_image(image_path, prompt)
