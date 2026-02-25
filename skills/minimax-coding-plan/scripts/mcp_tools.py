#!/usr/bin/env python3
"""
MiniMax Coding Plan MCP 工具
提供 web_search 和 understand_image 功能
"""

import os
import sys
import json
import base64

# 清除代理设置，确保直连
for key in list(os.environ.keys()):
    if 'proxy' in key.lower():
        del os.environ[key]

import requests
from urllib.parse import quote

# API 配置
API_KEY = "sk-cp-cNPUFSRoGGC6p_O4sOjA8sb0FPtWSW5uI8whb71wbqTQBc0isgtbIw9Mj8_f4kcQtNSjWqCs-60rl54ZJiBp2IwZPMeIQQOxCPJ2UVd9DQ3F1ZToRMBnnNU"
API_HOST = "https://api.minimaxi.com"

def web_search(query: str) -> str:
    """
    网络搜索功能
    使用 MiniMax 文本模型模拟搜索（基于内置知识）
    """
    url = f"{API_HOST}/v1/text/chatcompletion_v2"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "abab6.5s-chat",
        "messages": [
            {
                "role": "system",
                "content": "你是一个专业的网络搜索助手。当用户询问问题时，给出准确、全面、有用的信息。如果不知道某个具体信息，请明确说明。"
            },
            {
                "role": "user",
                "content": f"请搜索并回答以下问题：{query}\n\n请提供详细、准确的回答，包括相关来源信息（如果知道的话）。"
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            return content
        else:
            return f"搜索失败: {result}"
    except Exception as e:
        return f"搜索出错: {str(e)}"


def understand_image(prompt: str, image_path: str) -> str:
    """
    图片理解功能
    使用 MiniMax 视觉模型分析图片
    """
    # 检查图片是 URL 还是本地文件
    if image_path.startswith("http://") or image_path.startswith("https://"):
        # URL 图片
        image_url = image_path
        image_data = None
    else:
        # 本地文件，读取并转为 base64
        try:
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")
            image_url = None
        except Exception as e:
            return f"读取图片失败: {str(e)}"
    
    url = f"{API_HOST}/v1/text/chatcompletion_v2"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 构建消息
    if image_url:
        # 使用 URL
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    else:
        # 使用 base64
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data}"
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    
    payload = {
        "model": "abab6.5s-chat",  # 使用支持视觉的模型
        "messages": messages
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            return content
        else:
            return f"图片理解失败: {result}"
    except Exception as e:
        return f"图片理解出错: {str(e)}"


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  web_search: python3 script.py search <query>")
        print("  understand_image: python3 script.py image <prompt> <image_path_or_url>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "search":
        if len(sys.argv) < 3:
            print("Usage: python3 script.py search <query>")
            sys.exit(1)
        query = sys.argv[2]
        print(web_search(query))
    
    elif command == "image":
        if len(sys.argv) < 4:
            print("Usage: python3 script.py image <prompt> <image_path_or_url>")
            sys.exit(1)
        prompt = sys.argv[2]
        image_path = sys.argv[3]
        print(understand_image(prompt, image_path))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
