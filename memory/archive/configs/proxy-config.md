# 代理配置文档

## NAS SOCKS5/HTTP代理

### 代理服务器信息
| 属性 | 值 |
|------|-----|
| NAS地址 | 10.0.0.15 |
| 公网IP | 129.211.82.60 |
| SOCKS5端口 | 1080 |
| HTTP端口 | 13128 |
| 用户名 | xiaoyu |
| 密码 | socks5pass123 |

### 使用方式

**SOCKS5代理（推荐）：**
```
socks5://xiaoyu:socks5pass123@10.0.0.15:1080
```

**HTTP代理：**
```
http://10.0.0.15:13128
```

### Playwright配置示例
```python
proxy = {
    "server": "socks5://xiaoyu:socks5pass123@10.0.0.15:1080"
}
browser = p.chromium.launch(
    headless=True,
    proxy=proxy
)
```

### curl使用示例
```bash
# SOCKS5
curl -x socks5://xiaoyu:socks5pass123@10.0.0.15:1080 https://example.com

# HTTP
curl -x http://10.0.0.15:13128 https://example.com
```

### 注意事项
- 同花顺(10jqka.com.cn)会封锁NAS公网IP，需要换其他网站或使用其他代理
- 百度、京东等普通网站可以正常访问

### 相关文件
- virtual-browser.py - 虚拟浏览器，已配置默认代理
