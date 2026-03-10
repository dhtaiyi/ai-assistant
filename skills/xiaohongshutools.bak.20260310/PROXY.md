# 代理配置

## NAS 代理信息

需要配置代理让小红书技能通过家里网络访问，防止被检测为机房 IP。

### 方式一：HTTP 代理
```
HTTP_PROXY=http://<NAS-IP>:7890
HTTPS_PROXY=http://<NAS-IP>:7890
```

### 方式二：SOCKS5 代理
```
SOCKS_PROXY=socks5://<NAS-IP>:7891
```

## 使用方法

在运行需要代理的技能时，设置环境变量：

```bash
export HTTP_PROXY=http://192.168.x.x:7890
export HTTPS_PROXY=http://192.168.x.x:7890
```

## 常用代理端口

- 7890: HTTP/HTTPS 代理
- 7891: SOCKS5 代理
- 1080: 常用 SOCKS 端口

## 在 Python 脚本中使用代理

```python
import os
os.environ['HTTP_PROXY'] = 'http://192.168.x.x:7890'
os.environ['HTTPS_PROXY'] = 'http://192.168.x.x:7890'

import requests
requests.get('https://...')  # 自动使用代理
```
