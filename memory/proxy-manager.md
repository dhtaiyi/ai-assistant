

## Proxy-Manager 使用说明

### 当前状态
- 云服务器出口 IP: 129.211.82.60
- 代理服务运行在 NAS (10.0.0.4)
- FRP SOCKS 代理端口: 13128

### FRP 代理配置

NAS 上的 Squid 通过 FRP 映射到云服务器：
- 代理类型: SOCKS5
- 本地端口: 13128
- 远程访问: localhost:13128

### 使用方法

1. **环境变量方式**:
```bash
export http_proxy=http://localhost:13128
export https_proxy=http://localhost:13128
```

2. **Python 脚本方式**:
```python
from proxy_config import enable_proxy
enable_proxy()
```

### 配置文件位置
- `/root/.openclaw/workspace/proxy.conf`
- `/root/.openclaw/workspace/skills/xiaohongshutools/proxy_config.py`

### 检查代理状态
```bash
curl -x http://localhost:13128 https://api.ipify.org
```

### 注意事项
- 代理需要通过 FRP 连接到家里 NAS
- 如果代理无法访问，检查 NAS 上的代理服务是否正常运行
