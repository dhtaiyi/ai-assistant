#!/usr/bin/env python3
"""
API Key 测试工具 - 支持多个模型提供商
用法: python3 test-api-key.py --provider <provider> --api-key <key>

支持的 provider:
  - minimax      MiniMax API
  - moonshot     Moonshot AI (Kimi 标准版)
  - kimi-code    Kimi Code (编程专用)
  - qwen         阿里 Qwen
  - zhipu        智谱 AI
"""

import argparse
import json
import requests
import sys
from datetime import datetime

# 配置
PROVIDERS = {
    "minimax": {
        "url": "https://api.minimaxi.com/v1/chat/completions",
        "model": "MiniMax-M2.1",
        "auth_type": "Bearer"
    },
    "moonshot": {
        "url": "https://api.moonshot.cn/v1/chat/completions",
        "model": "moonshot-v1-128k",
        "auth_type": "Bearer"
    },
    "kimi-code": {
        "url": "https://api.kimi.com/coding/v1/chat/completions",
        "model": "kimi-for-coding",
        "auth_type": "Bearer"
    },
    "qwen": {
        "url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
        "model": "qwen-turbo",
        "auth_type": "Bearer",
        "headers": {"Content-Type": "application/json"}
    },
    "zhipu": {
        "url": "https://open.bigmodel.cn/api/paas/v3/model-api/chatglm_turbo",
        "model": "chatglm_turbo",
        "auth_type": "Bearer"
    }
}

def test_minimax(url, api_key, model):
    """测试 MiniMax"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 10
    }
    
    response = requests.post(url, headers=headers, json=data, timeout=20)
    return response

def test_moonshot(url, api_key, model):
    """测试 Moonshot/Kimi"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 10
    }
    
    response = requests.post(url, headers=headers, json=data, timeout=20)
    return response

def test_kimi_code(url, api_key, model):
    """测试 Kimi Code (编程专用)"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": "def hello():\n    return 'hello'"}],
        "max_tokens": 50
    }
    
    response = requests.post(url, headers=headers, json=data, timeout=20)
    return response

def test_qwen(url, api_key, model):
    """测试 Qwen"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "input": {"messages": [{"role": "user", "content": "hi"}]},
        "parameters": {"max_tokens": 10}
    }
    
    response = requests.post(url, headers=headers, json=data, timeout=20)
    return response

def test_zhipu(url, api_key, model):
    """测试智谱 AI"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 10
    }
    
    response = requests.post(url, headers=headers, json=data, timeout=20)
    return response

def main():
    parser = argparse.ArgumentParser(description="API Key 测试工具")
    parser.add_argument("--provider", "-p", required=True, 
                       choices=["minimax", "moonshot", "kimi-code", "qwen", "zhipu"],
                       help="API 提供商")
    parser.add_argument("--api-key", "-k", required=True, help="API Key")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    provider_config = PROVIDERS[args.provider]
    url = provider_config["url"]
    model = provider_config["model"]
    
    print("=" * 60)
    print(f"  API Key 测试: {args.provider.upper()}")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n📡 端点: {url}")
    print(f"🔑 模型: {model}")
    print(f"🔐 Key: {args.api_key[:10]}...{args.api_key[-5:]}")
    print("-" * 60)
    
    # 根据提供商选择测试方法
    test_func = {
        "minimax": test_minimax,
        "moonshot": test_moonshot,
        "kimi-code": test_kimi_code,
        "qwen": test_qwen,
        "zhipu": test_zhipu
    }[args.provider]
    
    try:
        print("\n⏳ 测试中...")
        response = test_func(url, args.api_key, model)
        
        # 解析结果
        status_code = response.status_code
        try:
            result = response.json()
        except:
            result = {"raw": response.text}
        
        print(f"\n📊 状态码: {status_code}")
        print("-" * 60)
        
        if status_code == 200:
            print("✅ 成功!")
            if "choices" in result:
                print(f"💬 回复: {result['choices'][0]['message']['content'][:100]}")
            elif "output" in result:
                print(f"💬 回复: {result['output']['text'][:100]}")
        else:
            print("❌ 失败!")
            if "error" in result:
                err = result["error"]
                print(f"   类型: {err.get('type', 'unknown')}")
                print(f"   消息: {err.get('message', str(err))}")
            elif "error" in result:
                print(f"   错误: {result['error']}")
            else:
                print(f"   原始响应: {str(result)[:200]}")
        
        # 详细输出
        if args.verbose:
            print("\n" + "=" * 60)
            print("📋 完整响应:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        print("\n" + "=" * 60)
        
    except requests.exceptions.Timeout:
        print("❌ 错误: 请求超时")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 未预期错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
