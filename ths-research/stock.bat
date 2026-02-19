@echo off
chcp 65001 >nul
REM ========================================
REM 股票数据采集器
REM ========================================

echo.
echo ╔═══════════════════════════════════════╗
echo ║    股票数据采集器                   ║
echo ╚═══════════════════════════════════════╝
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python
    echo 请先安装Python 3
    pause
    exit /b 1
)

echo ✅ Python已找到
echo.

REM 获取股票代码
set /p code="请输入股票代码 (直接回车查看默认列表): "

if "%code%"=="" (
    echo.
    echo ╔═══════════════════════════════════════╗
    echo ║    默认股票列表                     ║
    echo ╚═══════════════════════════════════════╝
    echo.
    echo   600519 - 贵州茅台
    echo   000001 - 平安银行
    echo   600036 - 招商银行
    echo   300750 - 宁德时代
    echo   000651 - 格力电器
    echo   600276 - 恒瑞医药
    echo   000858 - 五粮液
    echo   002594 - 比亚迪
    echo.
    echo   000001 - 上证指数
    echo   399001 - 深证成指
    echo   399006 - 创业板指
    echo.
    set /p code="请输入股票代码: "
)

echo.
echo ╔═══════════════════════════════════════╗
echo ║    采集结果                           ║
echo ╚═══════════════════════════════════════╝
echo.

python stock_simple.py

echo.
pause
