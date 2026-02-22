# stock-selector

股票智能选股工具，基于东方财富免费API筛选符合特定形态的股票。

## 触发条件

用户提及以下任一关键词时激活：
- "选股"
- "股票筛选"
- "形态选股"
- "倍量"
- "上影线"
- "横盘突破"
- "涨速榜"
- "涨幅榜"

## 功能

### 1. 实时行情查询
查询个股实时价格、涨跌幅。

```bash
python3 /root/.openclaw/workspace/skills/stock-selector/realtime.py
```

### 2. 涨速榜
获取涨速最快的股票。

```bash
python3 /root/.openclaw/workspace/skills/stock-selector/zhangsu.py
```

### 3. 横盘突破选股
筛选横盘整理后突破的股票。

```bash
python3 /root/.openclaw/workspace/skills/stock-selector/breakout.py
```

### 4. 放量上影线选股
筛选昨日放量上影线+今日高开的股票。

```bash
python3 /root/.openclaw/workspace/skills/stock-selector/upper_shadow.py
```

### 5. K线形态分析
分析单只股票的K线形态。

```bash
python3 /root/.openclaw/workspace/skills/stock-selector/kline.py <股票代码>
# 示例
python3 /root/.openclaw/workspace/skills/stock-selector/kline.py sh600519
```

## 选股形态说明

| 形态 | 条件 |
|------|------|
| 横盘突破 | 放量突破20日高点 |
| 放量上影线 | 昨日量比≥1.2 + 上影线>实体80% + 今日高开 |
| 倍量上涨 | 成交量是5日均量2倍以上 |

## 数据来源

- 东方财富财经API (免费)
- 腾讯财经API (免费)

## 注意事项

- 数据仅供学习参考，不构成投资建议
- 东方财富API响应较快，约100ms
- 建议控制请求频率
