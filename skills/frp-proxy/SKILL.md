# FRP 代理管理技能

> 管理家里 NAS 的 FRP 代理服务，实现远程访问家里网络

## 架构

```
☁️ 云服务器 (129.211.82.60)
    │
    └── frps (systemd) - 端口 8080
              │
              ▼ (FRP 隧道)
    🏠 家里 NAS (frpc-visitor Docker)
              │
              ▼
    🏠 家里 PC (小小雨 OpenClaw Gateway :18789)
```

## 管理命令

### FRP 服务端 (frps)

```bash
# 查看状态
systemctl status frps

# 启动/停止/重启
systemctl start frps
systemctl stop frps
systemctl restart frps

# 查看日志
tail -f /var/log/frps.log
```

### FRP 客户端 (frpc-visitor Docker)

```bash
# 查看状态
docker ps | grep frpc

# 查看日志
docker logs frpc-visitor --tail 20
docker logs frpc-visitor -f

# 重启
docker restart frpc-visitor
```

### 健康检查

```bash
# 手动检查
/usr/local/bin/check-frp.sh

# 查看监控日志
tail -f /var/log/frp-check.log
```

## 访问家里服务

通过云服务器访问家里的服务：

| 服务 | 地址 |
|------|------|
| 小小雨 Gateway | http://129.211.82.60:8080 |
| 小小雨 Dashboard | http://129.211.82.60:8080 (如配置) |

## 状态检查

检查 FRP 服务状态：

```bash
echo "=== FRP 状态汇总 ===" && \
systemctl is-active frps && echo "frps: 运行中" || echo "frps: 停止" && \
docker inspect -f '{{.State.Status}}' frpc-visitor 2>/dev/null && echo "frpc-visitor: 运行中" || echo "frpc-visitor: 停止"
```

---

*记住：云服务器上的小雨通过这个 FRP 隧道可以访问家里的小小雨～*
