#!/usr/bin/env python3
"""
飞书语音条发送脚本
用法: python3 feishu_voice.py <音频文件路径>
"""
import requests
import os
import json

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

def upload_file(token, file_path):
    """上传音频文件"""
    url = "https://open.feishu.cn/open-apis/im/v1/files"
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f)}
        # 重要：用 opus 类型！
        data = {'file_type': 'opus'}
        resp = requests.post(url, headers=headers, files=files, data=data)
        result = resp.json()
        
        if result.get("code") == 0:
            return result["data"]["file_key"]
        else:
            raise Exception(f"上传文件失败: {result}")

def send_voice(token, file_key):
    """发送语音条"""
    url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    data = {
        "receive_id": USER_ID,
        "msg_type": "audio",
        "content": json.dumps({"file_key": file_key})
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
    
    print("获取token中...")
    token = get_token()
    
    print(f"上传文件: {file_path}")
    file_key = upload_file(token, file_path)
    print(f"文件key: {file_key}")
    
    print("发送语音条...")
    send_voice(token, file_key)
    print("✅ 语音条发送成功!")

if __name__ == "__main__":
    main()
