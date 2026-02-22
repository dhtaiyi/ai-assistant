# 免费股票数据API接口

> 更新时间: 2026-02-22

---

## 国内免费API

### 1. 腾讯财经API ✅ 推荐

| 项目 | 值 |
|------|-----|
| 接口 | `http://qt.gtimg.cn/q=股票代码` |
| 支持 | A股、港股、美股、指数 |
| 频率 | 无明确限制 |
| 状态 | ✅ 正常工作 |

**股票代码格式：**
- 上海: `sh600519` (茅台)
- 深圳: `sz000001` (平安银行)
- 港股: `hk00700` (腾讯)
- 美股: `usAAPL` (苹果)
- 指数: `s_sh000001` (上证指数)

**示例：**
```bash
# 单只股票
curl "http://qt.gtimg.cn/q=sh600519"

# 多只股票
curl "http://qt.gtimg.cn/q=sh600519_sh000001_sz000001"
```

**返回字段说明：**
```
0: 股票名称
2: 股票代码
3: 当前价格
4: 昨收价
5: 今开盘
6: 成交量(手)
7: 成交额(万)
31: 日期
32: 时间
```

---

### 2. 新浪财经API ⚠️

| 项目 | 值 |
|------|-----|
| 接口 | `http://hq.sinajs.cn/list=股票代码` |
| 状态 | ❌ 被封锁 |

---

## 国外免费API

### 3. Yahoo Finance

| 项目 | 值 |
|------|-----|
| 接口 | `https://query1.finance.yahoo.com/v8/finance/chart/代码` |
| 示例 | `AAPL`, `GOOGL`, `MSFT` |

```bash
curl "https://query1.finance.yahoo.com/v8/finance/chart/AAPL"
```

### 4. Alpha Vantage

| 项目 | 值 |
|------|-----|
| 接口 | `https://www.alphavantage.co/query` |
| 需要 | 免费API Key |
| 限制 | 5次/分钟 |

```bash
curl "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&apikey=demo"
```

### 5. Finnhub

| 项目 | 值 |
|------|-----|
| 接口 | `https://finnhub.io/api/v1` |
| 需要 | 免费API Key |
| 限制 | 60次/分钟 |

---

## Python使用示例

```python
import requests

def get_stock_price(codes):
    """获取股票价格"""
    url = f"http://qt.gtimg.cn/q={'_'.join(codes)}"
    response = requests.get(url, timeout=10)
    response.encoding = 'gbk'
    
    stocks = {}
    for line in response.text.split('\n'):
        if '=' in line:
            code = line.split('=')[0].replace('v_', '')
            data = line.split('=')[1].strip('"; ')
            fields = data.split('~')
            
            if len(fields) > 4:
                stocks[code] = {
                    'name': fields[1],
                    'code': fields[2],
                    'price': fields[3],
                    'yesterday': fields[4],
                }
    return stocks

# 使用
stocks = get_stock_price(['sh600519', 'sh601318', 's_sh000001'])
for code, data in stocks.items():
    print(f"{data['name']}: {data['price']}")
```

---

## 已测试可用的代码

```python
# A股
sh600519  # 贵州茅台
sh601318  # 中国平安
sh000858  # 五粮液
sz000001  # 平安银行
sz000002  # 万科A

# 指数
s_sh000001  # 上证指数
s_sz399001  # 深证成指
s_sh000300  # 沪深300

# 港股
hk00700    # 腾讯控股
hk00939    # 建设银行

# 美股
usAAPL     # 苹果
usGOOGL    # 谷歌
usTSLA     # 特斯拉
```

---

## 注意事项

1. **频率限制**: 不要短时间内请求太多
2. **编码问题**: 腾讯API返回GBK编码，需要转换
3. **反爬**: 建议添加适当的请求间隔
4. **仅供学习**: 商用请使用官方API
