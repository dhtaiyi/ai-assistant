#!/usr/bin/env python3
"""
飞书语音条发送脚本 - 修复版
关键：上传和发送时都要传 duration（毫秒）！
用法: python3 feishu_voice.py <音频文件路径>
"""
import requests
import os
import json
import subprocess

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
        raise Exception(f"获取token失败: {result}")

def get_duration(file_path):
    """获取音频时长（毫秒）"""
    try:
        result = subprocess.run(
            ["ffprobe", "-i", file_path, "-show_entries", "format=duration", 
             "-of", "default=noprint_wrappers=1:nokey=1"],
            capture_output=True, text=True, timeout=10
        )
        duration = float(result.stdout.strip())
        return int(duration * 1000)  # 转换为毫秒
    except Exception as e:
        print(f"获取时长失败: {e}")
        return 0

def upload_file(token, file_path):
    """上传音频文件（带duration！）"""
    url = "https://open.feishu.cn/open-apis/im/v1/files"
    headers = {"Authorization": f"Bearer {token}"}
    
    duration = get_duration(file_path)
    print(f"音频时长: {duration}ms ({duration/1000:.2f}秒)")
    
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f)}
        # 关键：上传时要在metadata里加duration！
        data = {
            'file_type': 'opus',
            'file_name': os.path.basename(file_path),
            'duration': str(duration)  # 毫秒！
        }
        resp = requests.post(url, headers=headers, files=files, data=data)
        result = resp.json()
        
        if result.get("code") == 0:
            return result["data"]["file_key"], duration
        else:
            raise Exception(f"上传文件失败: {result}")

def send_voice(token, file_key, duration):
    """发送语音条（带duration！）"""
    url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    # 关键：发送时也要传duration！
    content = {
        "file_key": file_key,
        "duration": duration  # 毫秒！
    }
    
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
        raise Exception(f"发送失败: {result}")

def main():
    if len(os.sys.argv) < 2:
        print("用法: python3 feishu_voice.py <音频文件路径>")
        os.sys.exit(1)
    
    file_path = os.sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        os.sys.exit(1)
    
    print(f"处理文件: {file_path}")
    print("获取token中...")
    token = get_token()
    
    print(f"上传文件...")
    file_key, duration = upload_file(token, file_path)
    print(f"文件key: {file_key}")
    
    print("发送语音条...")
    send_voice(token, file_key, duration)
    print("✅ 语音条发送成功!")

if __name__ == "__main__":
    main()
