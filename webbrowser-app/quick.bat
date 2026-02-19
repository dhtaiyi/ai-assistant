@echo off
chcp 65001 >nul
REM ========================================
REM 常用操作快捷脚本
REM ========================================

if "%1"=="ths" goto ths
if "%1"=="stock" goto stock
if "%1"=="info" goto info
if "%1"=="test" goto test
if "%1"=="help" goto help

echo.
echo ╔═══════════════════════════════════════╗
echo ║    浏览器控制 - 快捷命令           ║
echo ╚═══════════════════════════════════════╝
echo.
echo 使用方法:
echo.
echo 🌐 打开同花顺:   quick ths
echo 📊 获取数据:     quick stock
echo 📄 页面信息:     quick info
echo 🧪 测试连接:     quick test
echo.
echo 💡 提示: 需要先运行 run.bat 启动浏览器
echo.

goto end

:ths
echo 🌐 打开同花顺...
python client.py -u https://www.10jqka.com.cn
goto end

:stock
echo 📊 获取股票数据...
python client.py --stock
goto end

:info
echo 📄 获取页面信息...
python client.py --info
goto end

:test
echo 🧪 测试连接...
python client.py --status
goto end

:help
echo.
echo ╔═══════════════════════════════════════╗
echo ║    快捷命令                         ║
echo ╚═══════════════════════════════════════╝
echo.
echo 🌐 同花顺:   quick ths
echo 💰 东方财富: quick eastmoney
echo 📊 获取数据: quick stock
echo 📄 页面信息: quick info
echo 🧪 测试:     quick test
echo.

:end
