# A股分析系统使用说明

## 快速开始

### 1. 配置 Tushare Token

```bash
# Linux/Mac
export TUSHARE_TOKEN='your_token_here'

# 添加到 ~/.bashrc
echo "export TUSHARE_TOKEN='your_token_here'" >> ~/.bashrc
```

### 2. 测试安装

```bash
# 测试股票价格
stock price 600519

# 测试日线数据
python scripts/get_stock_daily.py 600519
```

---

## 常用命令速查

### 股票查询

| 命令 | 说明 | 示例 |
|-----|------|-----|
| `stock price 600519` | 查询价格 | 贵州茅台 |
| `stock watch 600519 2000` | 设置监控 | 目标价2000元 |
| `stock list` | 查看监控 | 所有监控股票 |
| `stock realtime AAPL` | 实时行情 | 苹果美股 |

### 板块分析

| 命令 | 说明 |
|-----|------|
| `stock hot` | 今日热点 |
| `stock industry` | 行业板块 |
| `stock concept` | 概念板块 |

### 智能推荐

| 命令 | 说明 |
|-----|------|
| `stock recommend 半导体` | 半导体行业 |
| `stock recommend AI人工智能` | AI人工智能 |
| `stock recommend 新能源` | 新能源 |
| `stock recommend 医药` | 医药行业 |
| `stock recommend 白酒` | 白酒行业 |

### 财务分析

| 脚本 | 说明 |
|-----|------|
| `python scripts/get_stock_daily.py 600519` | 日线行情 |
| `python scripts/get_financial.py 600519` | 财务指标 |
| `python scripts/get_market_hot.py` | 市场热点 |

---

## 脚本使用方法

### 1. 获取日线数据

```bash
# 基本用法
python scripts/get_stock_daily.py 600519

# 指定天数
python scripts/get_stock_daily.py 600519 60

# 输出示例:
# 📈 获取 600519.SH 日线数据...
#
# 最近 5 天数据:
#   trade_date    open    high     low   close        vol
# 0   20250110  2050.0  2080.0  2045.0  2075.0  12345678
# ...
#
# 📊 月度涨跌: +3.25%
```

### 2. 获取财务指标

```bash
python scripts/get_financial.py 600519

# 输出示例:
# 📊 获取 600519.SH 财务指标...
#
# 最近 3 期财务数据:
#     end_date    roe net_profit_ratio gross_profit_margin
# 0   20240930  25.5     48.2            82.5
# ...
#
# 📈 最新指标:
#   ROE: 25.5%
#   净利润率: 48.2%
```

### 3. 获取市场热点

```bash
python scripts/get_market_hot.py

# 输出:
# 🔥 今日热点板块:
# [板块列表]
#
# 🏭 行业板块:
# [行业列表]
```

---

## 常见问题

### Q1: Tushare Token 怎么获取？

1. 访问 https://tushare.pro
2. 注册账号
3. 在个人中心 → API Token
4. 复制 Token

### Q2: 股票代码格式？

| 市场 | 示例 | 说明 |
|------|------|------|
| A股沪市 | 600519.SH | 6开头 |
| A股深市 | 000001.SZ | 0/3开头 |
| 港股 | 00700.HK | 4/5位数字 |
| 美股 | AAPL | 字母 |

### Q3: 数据延迟？

- 实时行情: 延迟15分钟
- 财务数据: T+1更新
- 限制: 免费用户100积分/天

---

## 最佳实践

### 每日复盘流程

```bash
# 1. 查看今日热点
python scripts/get_market_hot.py

# 2. 检查持仓
python scripts/get_stock_daily.py 600519
python scripts/get_stock_daily.py 000001

# 3. 查看财务
python scripts/get_financial.py 600519
```

### 选股分析流程

```bash
# 1. 查看行业热点
stock recommend 半导体

# 2. 获取板块股票列表
# (需要进一步编写脚本)

# 3. 财务筛选
python scripts/get_financial.py <股票代码>
```

---

## 相关资源

- Tushare 文档: https://tushare.pro/document
- 雪球: https://xueqiu.com
- 东方财富: https://eastmoney.com

