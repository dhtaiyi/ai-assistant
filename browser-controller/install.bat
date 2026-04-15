@echo off
REM 浏览器控制程序 - Windows安装脚本

echo ========================================
echo  浏览器控制程序 - 安装
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python已安装

REM 安装依赖
echo 📦 安装playwright...
pip install playwright

echo 📦 安装Chromium浏览器...
python -m playwright install chromium

echo.
echo ========================================
echo ✅ 安装完成！
echo ========================================
echo.
echo 使用方法:
echo   python main.py -u https://www.10jqka.com.cn
echo.
echo 获取股票数据:
echo   python main.py -u https://www.10jqka.com.cn --stock
echo.
pause
