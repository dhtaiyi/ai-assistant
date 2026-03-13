#!/usr/bin/env python3
"""
飞书语音条发送脚本 - 测试版
测试不同的file_type和发送方式
"""
import requests
import os
import json
import sys

# 飞书应用凭证
APP_ID = "cli_a9295e013c785bc0"
APP_SECRET = "SFDeXXVozEoSrELeiTlHsbWc0xufJaMg"

# 用户ID (主人)
USER_ID = "ou_fe4883cdfedd67ada203863e28b4b73c"

def get_token():
    """获取 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
    result = resp.json()
    
    if result.get("code") == 0:
        return result["tenant_access_token"]
    else:
        print(f"❌ 获取token失败: {result}")
        sys.exit(1)

def upload_file(token, file_path, file_type):
    """上传音频文件"""
    url = "https://open.feishu.cn/open-apis/im/v1/files"
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f)}
        data = {'file_type': file_type}
        resp = requests.post(url, headers=headers, files=files, data=data)
        result = resp.json()
        
        if result.get("code") == 0:
            return result["data"]["file_key"]
        else:
            print(f"❌ 上传失败 (type={file_type}): {result}")
            return None

def send_voice(token, file_key, duration=None):
    """发送语音条"""
    url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    # 构建content，包含duration
    content = {"file_key": file_key}
    if duration:
        content["duration"] = duration
    
    data = {
        "receive_id": USER_ID,
        "msg_type": "audio",
        "content": json.dumps(content)
    }
    
    resp = requests.post(url, headers=headers, json=data)
    result = resp.json()
    
    if result.get("code") == 0:
        return True
    else:
        print(f"❌ 发送失败: {result}")
        return False

def main():
    if len(sys.argv) < 2:
        print("用法: python3 test_feishu_voice.py <音频文件路径>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        sys.exit(1)
    
    print(f"🔬 测试飞书语音发送...")
    print(f"📁 文件: {file_path}")
    
    # 获取token
    print("\n1. 获取token...")
    token = get_token()
    print("✅ token获取成功")
    
    # 测试不同的file_type
    file_types = ["opus", "mp3", "wav", "amr", "aac"]
    
    for file_type in file_types:
        print(f"\n2. 测试 file_type={file_type}...")
        file_key = upload_file(token, file_path, file_type)
        
        if file_key:
            print(f"   ✅ 上传成功, file_key: {file_key}")
            
            # 尝试发送
            print(f"   发送语音消息...")
            if send_voice(token, file_key):
                print(f"   ✅ 发送成功!")
                break
        else:
            print(f"   ❌ 上传失败")

if __name__ == "__main__":
    main()
