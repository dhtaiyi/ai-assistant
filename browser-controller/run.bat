@echo off
chcp 65001 >nul
REM ========================================
REM 浏览器控制程序 - 运行入口
REM ========================================

echo.
echo ╔═══════════════════════════════════════╗
echo ║    浏览器控制程序                      ║
echo ╚═══════════════════════════════════════╝
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，请先运行 install.bat
    echo.
    pause
    exit /b 1
)

REM 获取脚本所在目录
cd /d "%~dp0"

REM 运行程序
if "%1"=="" (
    echo 使用方法:
    echo.
    echo 🌐 打开网页:
    echo   run -u https://www.10jqka.com.cn
    echo.
    echo 📊 获取股票数据:
    echo   run -u https://www.10jqka.com.cn --stock
    echo.
    echo 👆 点击元素:
    echo   run -u https://www.10jqka.com.cn -c .btn-primary
    echo.
    echo 💡 提示: 支持直接拖动URL到run.bat
    echo.
) else (
    python main.py %*
)

echo.
pause
