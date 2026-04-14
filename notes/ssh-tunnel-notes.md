# SSH tunnel 远程连接配置

## Windows → 云服务器 SSH tunnel

### 命令
```bash
ssh -L 18789:localhost:18789 root@129.211.82.60 -N -f
```
保持后台运行即可。

## 注意
- 视频同步需要 SSH tunnel 保持连接
- 断线后 OpenClaw 通知云服务器需要 tunnel 在线
