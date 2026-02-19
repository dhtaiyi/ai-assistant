# 同花顺数据采集器

让 OpenClaw 通过浏览器远程读取同花顺行情数据。

## 快速开始

### 1. 准备工作

```bash
# 确保浏览器控制服务器已启动
cd /root/.openclaw/workspace/browser-remote
python server.py
```

### 2. 启动采集

```bash
cd /root/.openclaw/workspace/ths-crawler
python quick_crawl.py --code 600519
```

## 使用方法

### 命令行工具

```bash
# 获取单只股票价格
python quick_crawl.py -c 600519

# 批量查询多只股票
python quick_crawl.py -C 600519 000001 600036

# 获取大盘指数
python quick_crawl.py --index

# 监控股票（每60秒采集一次，共10次）
python quick_crawl.py -m 600519 600036 --interval 60 --count 10

# 导出CSV
python quick_crawl.py -e 600519 600036 000001
```

### Python API

```python
from openclaw_integration import OpenClawBrowser
from ths_crawler import THSCrawler

browser = OpenClawBrowser()
crawler = THSCrawler(browser)

# 获取股票价格
result = crawler.get_stock_price('600519')
print(result)

# 获取大盘
crawler.get_market_summary()
```

### 高级功能

```python
from advanced_crawler import THSAdvancedCrawler

crawler = THSAdvancedCrawler(browser)

# 批量对比
results = crawler.compare_stocks(['600519', '000001', '600036'])

# 查找涨幅股票
rising = crawler.find_rising_stocks(['600519', '000001'], min_rise=5.0)

# 导出报告
crawler.generate_report(results, '股票对比报告')

# 定时监控
crawler.monitor_prices(['600519', '600036'], interval=60, max_iterations=100)
```

## 文件结构

```
ths-crawler/
├── ths_crawler.py        # 基础采集器
├── advanced_crawler.py  # 高级采集器（带缓存、导出）
├── quick_crawl.py        # 命令行工具
├── config.yaml           # 配置文件
├── README.md            # 说明文档
└── data/                # 数据存储目录
    ├── stock_price_20260219.json
    └── stock_price_20260219.csv
```

## 功能列表

| 功能 | 方法 | 说明 |
|------|------|------|
| 实时价格 | `get_stock_price()` | 获取股票最新价、涨跌幅 |
| 基本信息 | `get_stock_info()` | 股票名称、行业 |
| 资金流向 | `get_fund_flow()` | 主力资金流入 |
| 大盘指数 | `get_market_summary()` | 上证、深证、创业板 |
| 股东信息 | `get_stock_holders()` | 十大股东 |
| 批量查询 | `get_realtime_quotes()` | 多只股票同时查询 |
| 数据导出 | `save_to_csv()` / `save_to_json()` | 导出文件 |
| 报告生成 | `generate_report()` | HTML报告 |
| 定时监控 | `monitor_prices()` | 持续采集数据 |

## 注意事项

1. **登录状态**: 部分数据需要登录才能查看
2. **请求频率**: 避免过于频繁的请求（建议间隔1秒以上）
3. **反爬虫**: 同花顺可能有反爬措施，不建议大规模采集
4. **数据准确性**: 网页数据仅供参考，请以官方数据为准

## 常见问题

### Q: 获取数据失败？
A: 检查页面结构是否变化，或尝试刷新页面

### Q: 如何导出Excel？
A: CSV可以用Excel打开，或使用pandas转换

### Q: 能采集历史数据吗？
A: 网页端主要显示实时数据，历史数据建议使用 akshare/tushare

## 相关项目

- [OpenClaw 浏览器控制](../browser-remote/)
- [Tushare 金融数据](../tushare-finance/)
- [Akshare 金融数据](../akshare/)

## License

MIT
