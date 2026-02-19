@echo off
chcp 65001 >nul
REM ========================================
REM 常用操作快捷脚本
REM ========================================

if "%1"=="ths" goto ths
if "%1"=="stock" goto stock
if "%1"=="test" goto test
if "%1"=="help" goto help

REM 默认打开同花顺
echo.
echo ╔═══════════════════════════════════════╗
echo ║    浏览器控制程序                      ║
echo ╚═══════════════════════════════════════╝
echo.
echo 使用方法:
echo.
echo 🌐 打开网页:
echo   quick ths          ^<- 打开同花顺
echo   quick baidu        ^<- 打开百度
echo   quick eastmoney   ^<- 打开东方财富
echo.
echo 📊 获取数据:
echo   quick stock       ^<- 获取股票数据
echo.
echo 🔧 测试:
echo   quick test        ^<- 测试程序
echo.
echo 💡 完整功能:
echo   run -u https://... --stock
echo.

goto end

:ths
python main.py -u https://www.10jqka.com.cn --stock
goto end

:stock
python main.py -u https://www.10jqka.com.cn --stock
goto end

:test
echo 🧪 测试程序...
python main.py -u https://www.10jqka.com.cn --info
echo.
echo ✅ 测试完成
goto end

:help
echo.
echo ╔═══════════════════════════════════════╗
echo ║    常用快捷命令                       ║
echo ╚═══════════════════════════════════════╝
echo.
echo 🌐 打开同花顺:   quick ths
echo 💰 东方财富:    quick eastmoney
echo 📊 获取股票:    quick stock
echo 🧪 测试:        quick test
echo.
echo 💡 完整命令:
echo   run -u URL           ^<- 打开网页
echo   run -u URL --stock   ^<- 获取股票数据
echo   run -u URL -c CSS    ^<- 点击元素
echo.

:end
