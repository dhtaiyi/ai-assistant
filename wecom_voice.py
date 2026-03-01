#!/usr/bin/env python3
"""
企业微信语音条发送脚本
用法: python3 wecom_voice.py <音频文件路径>
"""
import requests
import os
import sys
import subprocess
import tempfile

# 企业微信配置
CORP_ID = "wwf684d252386fc0b6"
CORP_SECRET = "aEgqy4MfNSXBWUoy9jgwZLiBfVTnd7POgRJzVUHq_Q0"
AGENT_ID = "1000002"
USER_ID = "KunKun"  # 困困

def get_token():
    """获取 access_token"""
    url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={CORP_ID}&corpsecret={CORP_SECRET}"
    resp = requests.get(url)
    result = resp.json()
    
    if result.get("errcode") == 0:
        return result["access_token"]
    else:
        raise Exception(f"获取token失败: {result}")

def convert_to_amr(mp3_path):
    """将 MP3 转换为 AMR 格式"""
    # 使用系统的 mp3-to-amr.py 脚本
    cmd = ["python3", "/usr/local/bin/mp3-to-amr.py", mp3_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"AMR转换失败: {result.stderr}")
    
    # 输出文件路径
    amr_path = mp3_path.rsplit(".", 1)[0] + ".amr"
    return amr_path

def upload_voice(token, amr_path):
    """上传语音文件"""
    url = f"https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={token}&type=voice"
    
    with open(amr_path, 'rb') as f:
        files = {'file': ('voice.amr', f)}
        resp = requests.post(url, files=files)
        result = resp.json()
        
        if result.get("errcode") == 0:
            return result["media_id"]
        else:
            raise Exception(f"上传失败: {result}")

def send_voice(token, media_id):
    """发送语音条"""
    url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}"
    
    data = {
        "touser": USER_ID,
        "msgtype": "voice",
        "agentid": AGENT_ID,
        "voice": {"media_id": media_id}
    }
    
    resp = requests.post(url, json=data)
    result = resp.json()
    
    if result.get("errcode") == 0:
        return True
    else:
        raise Exception(f"发送失败: {result}")

def main():
    if len(sys.argv) < 2:
        print("用法: python3 wecom_voice.py <音频文件路径>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        sys.exit(1)
    
    print("获取token中...")
    token = get_token()
    
    print(f"转换音频为AMR格式: {file_path}")
    amr_path = convert_to_amr(file_path)
    print(f"AMR文件: {amr_path}")
    
    print("上传语音文件...")
    media_id = upload_voice(token, amr_path)
    print(f"media_id: {media_id}")
    
    print("发送语音条...")
    send_voice(token, media_id)
    print("✅ 语音条发送成功!")

if __name__ == "__main__":
    main()
