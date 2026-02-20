# 小红书工具代理配置

## 当前代理配置

代理地址: `http://localhost:13128`

## 使用方法

### 方法1: 环境变量
```bash
export http_proxy=http://localhost:13128
export https_proxy=http://localhost:13128
```

### 方法2: Python代码
```python
import os
os.environ['http_proxy'] = 'http://localhost:13128'
os.environ['https_proxy'] = 'http://localhost:13128'
```

### 方法3: 直接在Session中使用
```python
session = XHS_Session(proxy_url='http://localhost:13128')
```

## NAS代理说明

- 代理类型: Squid HTTP Proxy
- 端口: 13128
- 通过FRP内网穿透连接到NAS
- 可以访问小红书、百度等网站
