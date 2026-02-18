# akshare 使用指南

## 安装
```bash
pip install akshare
```

## 常用功能

### 1. 实时行情
```python
import akshare as ak
df = ak.stock_zh_a_spot_em()
print(df.head())
```

### 2. 个股历史数据
```python
df = ak.stock_zh_a_hist(symbol="sh600519", period="daily", start_date="20240101", end_date="20240218")
print(df)
```

### 3. 龙虎榜
```python
df = ak.stock_lhb_data_em(date="20240218")
print(df)
```

### 4. 资金流向
```python
df = ak.stock_market_fund_flow(symbol="600519")
print(df)
```

### 5. 大盘行情
```python
df = ak.stock_zh_index_spot()
print(df)
```

### 6. 期货行情
```python
df = ak.futures_zh_spot("cu")  # 沪铜
print(df)
```

### 7. 港股行情
```python
df = ak.stock_hk_spot_em()
print(df)
```

### 8. 美股行情
```python
df = ak.stock_us_spot_em()
print(df)
```

## 常用命令速查

| 功能 | 命令 |
|------|------|
| 实时行情 | `stock_zh_a_spot_em()` |
| 历史日线 | `stock_zh_a_hist()` |
| 分时数据 | `stock_zh_a_minute()` |
| 龙虎榜 | `stock_lhb_data_em()` |
| 资金流向 | `stock_market_fund_flow()` |
| 大盘指数 | `stock_zh_index_spot()` |
| 期货行情 | `futures_zh_spot()` |
| 港股 | `stock_hk_spot_em()` |
| 美股 | `stock_us_spot_em()` |

## 注意事项

1. **网络要求**: 需要网络访问才能获取数据
2. **频率限制**: 避免过于频繁请求
3. **数据延迟**: 实时数据可能有秒级延迟
