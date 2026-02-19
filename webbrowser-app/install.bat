@echo off
chcp 65001 >nul
REM ========================================
REM 嵌入式浏览器 - 安装依赖
REM ========================================

echo.
echo ╔═══════════════════════════════════════╗
echo ║    嵌入式浏览器 - 安装程序          ║
echo ╚═══════════════════════════════════════╝
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python 3
    echo.
    echo 请先安装Python 3.8+:
    echo   https://www.python.org/downloads/
    echo   安装时勾选 "Add Python to PATH"
    pause
    exit /b 1
)

echo ✅ Python已安装
echo.

REM 安装PyQt5
echo 📦 安装 PyQt5...
pip install PyQt5 PyQtWebEngine >nul 2>&1
if errorlevel 1 (
    echo ❌ 安装PyQt5失败
    echo 请手动运行: pip install PyQt5 PyQtWebEngine
    pause
    exit /b 1
)
echo ✅ PyQt5已安装

REM 安装requests
echo 📦 安装 requests...
pip install requests >nul 2>&1
echo ✅ requests已安装

echo.
echo ╔═══════════════════════════════════════╗
echo ║          ✅ 安装完成！              ║
echo ╚═══════════════════════════════════════╝
echo.
echo 使用方法:
echo.
echo 1. 双击 run.bat 启动浏览器
echo 2. 浏览器窗口会自动打开
echo 3. 使用 client.py 控制浏览器
echo.
echo HTTP API:
echo   POST / {command: {type: 'navigate', url: '...'}}
echo   POST / {command: {type: 'click', selector: '...'}}
echo   POST / {command: {type: 'getStockData'}}
echo.
pause
