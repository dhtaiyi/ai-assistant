# A股数据分析系统

## 概述

基于 tushare-finance 和 stock-monitor 的A股数据分析系统。

## 组成部分

### 1. tushare-finance
- Tushare Pro API
- 220+ 数据接口
- 支持: A股、港股、美股、基金、期货、债券

### 2. stock-monitor
- 实时价格监控
- 智能板块推荐
- 热点追踪

---

## 安装和配置

### 1. 配置 Tushare Token

```bash
# 注册 Tushare
# 访问 https://tushare.pro 注册账号

# 获取 Token
# 登录后，在个人中心获取 Token

# 配置环境变量
export TUSHARE_TOKEN="your_token_here"
```

### 2. 安装依赖

```bash
pip install tushare pandas
```

---

## 使用方法

### A. 股票价格查询

```bash
# 查询实时价格 (stock-monitor)
stock price 600519  # 贵州茅台
stock price 000001  # 平安银行
stock price 00700   # 腾讯控股
stock price AAPL    # 苹果

# 日线行情 (tushare-finance)
python get_stock_daily.py 600519
```

### B. 实时监控

```bash
# 监控股票价格
stock watch 600519 2000  # 设置目标价2000元提醒
stock watch 00700 400     # 港股400港币

# 查看监控列表
stock list

# 实时行情
stock realtime AAPL
```

### C. 板块分析

```bash
# 行业板块
stock industry

# 概念板块
stock concept

# 今日热点
stock hot

# 智能推荐
stock recommend 半导体
stock recommend AI人工智能
stock recommend 新能源
stock recommend 医药
stock recommend 白酒
```

### D. 财务分析

```bash
# 获取财务指标
python get_financial.py 600519

# 获取利润表
python get_income.py 600519

# 获取ROE等指标
python get_fina_indicator.py 600519
```

### E. 宏观经济

```bash
# GDP数据
python get_gdp.py

# CPI数据
python get_cpi.py
```

---

## 数据接口速查

### 股票数据

| 接口 | 说明 | 示例 |
|-----|------|-----|
| `pro.stock_basic()` | 股票列表 | 所有A股 |
| `pro.daily()` | 日线行情 | 600519近1月 |
| `pro.fina_indicator()` | 财务指标 | ROE、营收增长 |
| `pro.income()` | 利润表 | 净利润、营收 |
| `pro.balancesheet()` | 资产负债表 | 资产、负债 |
| `pro.cashflow()` | 现金流量表 | 经营现金流 |

### 指数数据

| 接口 | 说明 |
|-----|------|
| `pro.index_daily()` | 指数日线 |
| `pro.index_basic()` | 指数列表 |

### 基金和宏观

| 接口 | 说明 |
|-----|------|
| `pro.fund_nav()` | 基金净值 |
| `pro.gdp()` | GDP |
| `pro.cpi()` | CPI |

---

## 脚本示例

### 1. 获取股票日线

```python
# get_stock_daily.py
import tushare as ts
import os

pro = ts.pro_api(os.getenv('TUSHARE_TOKEN'))

# 获取日线数据
df = pro.daily(
    ts_code='600519.SH',
    start_date='20250101',
    end_date='20250131'
)

print(df.head())
```

### 2. 获取财务指标

```python
# get_financial.py
import tushare as ts
import os

pro = ts.pro_api(os.getenv('TUSHARE_TOKEN'))

# 获取财务指标
df = pro.fina_indicator(
    ts_code='600519.SH',
    start_date='20240101',
    end_date='20241231'
)

print(df[['ts_code', 'end_date', 'roe', 'net_profit_ratio', 'gross_profit_margin']])
```

### 3. 监控多只股票

```python
# monitor_stocks.py
import tushare as ts
import os

pro = ts.pro_api(os.getenv('TUSHARE_TOKEN'))

# 股票列表
stocks = ['600519.SH', '000001.SZ', '600036.SH']

for stock in stocks:
    df = pro.daily(ts_code=stock, limit=1)
    if df is not None and len(df) > 0:
        close = df.iloc[0]['close']
        print(f"{stock}: {close}元")
```

---

## 应用场景

### 场景1: 每日复盘
```
1. stock hot  # 查看今日热点
2. stock industry  # 查看行业板块
3. python get_stock_daily.py 600519  # 查看持仓股
```

### 场景2: 选股分析
```
1. stock recommend 半导体  # 行业推荐
2. python get_financial.py 600519  # 财务分析
3. stock watch 600519 1800  # 设置监控
```

### 场景3: 宏观分析
```
1. python get_gdp.py  # GDP数据
2. python get_cpi.py  # CPI数据
3. python get_m2.py  # M2数据
```

### 场景4: 组合监控
```
1. python monitor_stocks.py  # 批量查询
2. stock list  # 查看监控列表
3. stock realtime AAPL  # 实时行情
```

---

## 注意事项

### 1. Tushare Pro 限制
- 免费用户: 100积分/天
- 基础数据: 实时行情延迟15分钟
- 财务数据: T+1更新

### 2. 投资风险
- 数据仅供参考
- 不构成投资建议
- 谨慎决策

---

## 相关文件

- /root/.openclaw/workspace/skills/tushare-finance/
- /root/.openclaw/workspace/skills/stock-monitor/
- /root/.openclaw/workspace/stock-analysis/

