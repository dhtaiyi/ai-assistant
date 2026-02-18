# 股票数据服务 - 直接对接系统

## 系统架构

```
你的Windows电脑 (数据获取)
    ↓ HTTP API (localhost:8080)
SSH 隧道
    ↓
我 (服务器) ← 直接调用 → 你电脑
```

## 文件说明

| 文件 | 功能 |
|------|------|
| `stock_api.py` | 数据服务主程序 |
| `ssh_tunnel.bat` | SSH隧道脚本 |
| `start.bat` | 启动器 |

## 安装步骤

### 1. 安装依赖

```bash
pip install akshare flask
```

### 2. 下载文件

把以下文件下载到你电脑：
- `stock_api.py`
- `ssh_tunnel.bat`
- `start.bat`

### 3. 启动服务

**方式A：使用启动器**
```bash
start.bat
```

**方式B：手动启动**
```bash
python stock_api.py
```

### 4. 建立SSH隧道

```bash
ssh_tunnel.bat
```

输入：
- 服务器IP
- 用户名（默认root）

## 我如何调用

在服务器上，我可以直接调用你电脑的API：

```bash
# 获取大盘行情
curl http://localhost/market

# 获取行业板块
curl http://localhost/industry

# 获取概念板块
curl http://localhost/concept

# 个股详情 (替换600519)
curl http://localhost/stock/600519

# 板块内个股 (替换"券商概念")
curl http://localhost/industry/stocks/券商概念

# 联动分析
curl http://localhost/analysis

# 同步率分析 (替换"券商概念")
curl http://localhost/sync/券商概念
```

## API接口说明

| 接口 | 说明 | 示例 |
|------|------|------|
| `/` | 服务状态 | `curl http://localhost` |
| `/market` | 大盘行情 | `curl http://localhost/market` |
| `/industry` | 行业板块 | `curl http://localhost/industry` |
| `/concept` | 概念板块 | `curl http://localhost/concept` |
| `/stock/<code>` | 个股详情 | `curl http://localhost/stock/600519` |
| `/industry/stocks/<板块>` | 板块个股 | `curl http://localhost/industry/stocks/券商概念` |
| `/analysis` | 联动分析 | `curl http://localhost/analysis` |
| `/sync/<板块>` | 同步率分析 | `curl http://localhost/sync/券商概念` |

## 使用场景

### 场景1：查看板块联动

```bash
# 券商板块同步率分析
curl http://localhost/sync/券商概念

# 返回：
# - 板块内有多少只股票
# - 同步率（涨跌幅方向一致的比例）
# - 平均涨跌幅
# - 涨幅最大的5只
# - 跌幅最大的5只
```

### 场景2：板块内个股

```bash
# 新能源板块个股
curl http://localhost/industry/stocks/新能源

# 返回：
# - 板块内所有股票
# - 实时价格、涨跌幅
# - 成交量
```

### 场景3：全市场联动

```bash
# 获取全市场联动分析
curl http://localhost/analysis

# 返回：
# - 上涨/下跌/平盘数量
# - 涨幅最大的板块TOP5
# - 跌幅最大的板块TOP5
```

## 注意事项

1. **保持窗口打开** - 服务和隧道窗口都要保持打开
2. **网络稳定** - 确保网络连接稳定
3. **防火墙** - 允许8080端口
4. **SSH连接** - 需要有效的服务器SSH访问

## 故障排除

### 问题1：连接超时
- 检查服务是否启动
- 检查SSH隧道是否建立
- 检查服务器IP是否正确

### 问题2：数据获取失败
- 检查网络连接
- akshare可能有临时故障
- 稍后重试

### 问题3：API返回空
- 板块名称可能不匹配
- 检查板块名称是否正确

## 示例输出

```json
{
  "status": "ok",
  "industry": "券商概念",
  "total_stocks": 48,
  "sync_rate": 75.5,
  "direction": "上涨",
  "avg_pct": 3.25,
  "std_pct": 2.15,
  "statistics": {
    "up_more_2": 30,
    "down_more_2": 5,
    "flat": 13
  },
  "top_up": [
    {"代码": "600519", "名称": "贵州茅台", "最新价": 1500.00, "涨跌幅": 5.23},
    ...
  ],
  "top_down": [
    {"代码": "000001", "名称": "平安银行", "最新价": 12.50, "涨跌幅": -2.15},
    ...
  ]
}
```

## 下一步

1. 告诉我你的服务器IP
2. 我创建远程监控脚本
3. 定时获取数据并分析
