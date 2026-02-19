# 嵌入式浏览器控制程序

## 简介

独立的浏览器窗口，可通过HTTP API远程控制。

## 特点

- ✅ 独立浏览器窗口（内嵌Chromium）
- ✅ HTTP API 控制（无需Python环境也能调用）
- ✅ 可打包成EXE程序
- ✅ 支持股票数据采集

## 文件结构

```
webbrowser-app/
├── browser_app.py     # 主程序（浏览器窗口）
├── client.py         # 控制客户端
├── install.bat      # 安装依赖
├── run.bat          # 启动程序
├── quick.bat        # 常用命令
└── README.md       # 说明文档
```

## 安装

### 1. 安装依赖

双击 `install.bat` 或运行：
```bash
pip install PyQt5 PyQtWebEngine requests
```

## 使用方法

### 1. 启动浏览器

双击 `run.bat`

会打开一个独立的浏览器窗口。

### 2. 控制浏览器

**方式1：命令行（双击quick.bat）**
```bash
quick ths      # 打开同花顺
quick stock    # 获取股票数据
quick info     # 页面信息
```

**方式2：直接运行**
```bash
python client.py -u https://www.10jqka.com.cn  # 打开网页
python client.py --stock                       # 获取股票数据
python client.py -c .btn-primary              # 点击元素
python client.py -s down                       # 滚动页面
```

**方式3：HTTP请求**
```bash
# 打开网页
curl -X POST http://localhost:8080/ \
  -H "Content-Type: application/json" \
  -d '{"command": {"type": "navigate", "url": "https://www.10jqka.com.cn"}}'

# 获取股票数据
curl -X POST http://localhost:8080/ \
  -H "Content-Type: application/json" \
  -d '{"command": {"type": "getStockData"}}'
```

## HTTP API

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | / | 查看状态 |
| POST | / | 执行命令 |

### 命令格式

```json
{
  "command": {
    "type": "navigate",
    "url": "https://www.10jqka.com.cn"
  }
}
```

### 支持的命令

| 命令 | 参数 | 说明 |
|------|------|------|
| navigate | url | 打开URL |
| click | selector | 点击元素 |
| scroll | direction, amount | 滚动页面 |
| getStockData | - | 获取股票数据 |
| getPageInfo | - | 获取页面信息 |
| evaluate | code | 执行JavaScript |

## 打包成EXE

使用 PyInstaller 打包：

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "OpenClawBrowser" browser_app.py
```

## 常见问题

Q: 启动报错？
A: 运行 `install.bat` 安装依赖

Q: 端口被占用？
A: 修改 browser_app.py 中的端口号

Q: 无法获取股票数据？
A: 确保页面已完全加载
