#!/usr/bin/env python3
"""
小红书代理配置脚本
用于设置代理环境变量，让小红书技能通过 NAS 代理访问网络

默认使用 FRP 代理: 127.0.0.1:13128 (通过家庭宽带访问)
如果需要直接连接 NAS，可以使用环境变量覆盖
"""
import os
import sys

# FRP 代理配置（默认）
# 流量通过: 本机 -> FRP 隧道 -> NAS Squid -> 家庭宽带
FRP_PROXY_HOST = os.environ.get("FRP_PROXY_HOST", "127.0.0.1")
FRP_PROXY_PORT = os.environ.get("FRP_PROXY_PORT", "13128")

# NAS 代理配置（备用，如果 FRP 不可用）
NAS_IP = os.environ.get("NAS_PROXY_IP", "10.0.0.4")
NAS_PROXY_PORT = os.environ.get("NAS_PROXY_PORT", "7890")

# 选择代理模式: "frp" 或 "nas"
PROXY_MODE = os.environ.get("XHS_PROXY_MODE", "frp")

def get_proxy_url():
    """获取当前代理 URL"""
    if PROXY_MODE == "frp":
        return f"http://{FRP_PROXY_HOST}:{FRP_PROXY_PORT}"
    else:
        return f"http://{NAS_IP}:{NAS_PROXY_PORT}"

# HTTP/HTTPS 代理
PROXY_URL = get_proxy_url()
HTTP_PROXY = PROXY_URL
HTTPS_PROXY = PROXY_URL

def enable_proxy():
    """启用代理"""
    os.environ['HTTP_PROXY'] = HTTP_PROXY
    os.environ['HTTPS_PROXY'] = HTTPS_PROXY
    os.environ['http_proxy'] = HTTP_PROXY
    os.environ['https_proxy'] = HTTPS_PROXY
    print(f"✅ 代理已启用: {HTTP_PROXY}")
    print(f"   模式: {'FRP (家庭宽带)' if PROXY_MODE == 'frp' else 'NAS 直连'}")

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
        'https': HTTPS_PROXY,
        'mode': PROXY_MODE
    }

def test_proxy():
    """测试代理是否可用"""
    import urllib.request
    import urllib.error
    
    test_url = "https://www.xiaohongshu.com/"
    proxy_handler = urllib.request.ProxyHandler({
        'http': HTTP_PROXY,
        'https': HTTPS_PROXY
    })
    
    try:
        req = urllib.request.Request(test_url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        opener = urllib.request.build_opener(proxy_handler)
        response = opener.open(req, timeout=10)
        print(f"✅ 代理测试成功! 状态码: {response.status}")
        return True
    except urllib.error.URLError as e:
        print(f"❌ 代理测试失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 代理测试失败: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "enable":
            enable_proxy()
        elif sys.argv[1] == "disable":
            disable_proxy()
        elif sys.argv[1] == "status":
            print(f"当前代理: {HTTP_PROXY}")
            print(f"代理模式: {'FRP (家庭宽带)' if PROXY_MODE == 'frp' else 'NAS 直连'}")
        elif sys.argv[1] == "test":
            test_proxy()
        elif sys.argv[1] == "mode":
            if len(sys.argv) > 2:
                print(f"切换代理模式: {sys.argv[2]}")
                print("请设置环境变量 XHS_PROXY_MODE 再运行")
            else:
                print(f"当前模式: {PROXY_MODE}")
                print("可用模式: frp (默认), nas")
        else:
            print(f"未知命令: {sys.argv[1]}")
    else:
        print(f"小红书代理配置:")
        print(f"  代理地址: {HTTP_PROXY}")
        print(f"  代理模式: {'FRP (家庭宽带)' if PROXY_MODE == 'frp' else 'NAS 直连'}")
        print(f"\n用法: python proxy_config.py [enable|disable|status|test]")
