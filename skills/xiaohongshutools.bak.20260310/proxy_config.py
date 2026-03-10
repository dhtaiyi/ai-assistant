#!/usr/bin/env python3
"""
小红书代理配置脚本
用于设置代理环境变量，让小红书技能通过 NAS 代理访问网络
"""
import os
import sys

# 代理配置 - 需要根据你的 NAS IP 地址修改
# NAS_IP = "192.168.x.x"  # 替换为你的 NAS 内网 IP
NAS_IP = os.environ.get("NAS_PROXY_IP", "10.0.0.4")  # 默认 NAS IP
PROXY_PORT = os.environ.get("NAS_PROXY_PORT", "7890")

# HTTP/HTTPS 代理
HTTP_PROXY = f"http://{NAS_IP}:{PROXY_PORT}"
HTTPS_PROXY = f"http://{NAS_IP}:{PROXY_PORT}"

def enable_proxy():
    """启用代理"""
    os.environ['HTTP_PROXY'] = HTTP_PROXY
    os.environ['HTTPS_PROXY'] = HTTPS_PROXY
    os.environ['http_proxy'] = HTTP_PROXY
    os.environ['https_proxy'] = HTTPS_PROXY
    print(f"✅ 代理已启用: {HTTP_PROXY}")

def disable_proxy():
    """禁用代理"""
    os.environ.pop('HTTP_PROXY', None)
    os.environ.pop('HTTPS_PROXY', None)
    os.environ.pop('http_proxy', None)
    os.environ.pop('https_proxy', None)
    print("❌ 代理已禁用")

def get_proxy():
    """获取代理配置"""
    return {
        'http': HTTP_PROXY,
        'https': HTTPS_PROXY
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "enable":
            enable_proxy()
        elif sys.argv[1] == "disable":
            disable_proxy()
        elif sys.argv[1] == "status":
            print(f"当前代理: {HTTP_PROXY}")
    else:
        print(f"代理配置: {HTTP_PROXY}")
        print("用法: python proxy.py [enable|disable|status]")
