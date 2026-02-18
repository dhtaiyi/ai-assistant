@echo off
REM SSH 隧道脚本 - Windows版
REM 功能：建立SSH隧道，让服务器访问本地服务

echo.
echo ========================================
echo    SSH 隧道 - 股票数据服务
echo ========================================
echo.
echo 配置信息:
echo   本地端口: 8080
echo   远程端口: 80
echo.
echo 请输入服务器信息:
set /p SERVER="服务器IP: "
set /p USER="用户名 (默认root): "
if "%USER%"=="" set USER=root

echo.
echo 正在连接...
echo 命令: ssh -R 80:localhost:8080 %USER%@%SERVER%
echo.
echo ⚠️  保持此窗口打开，隧道才有效！
echo.
ssh -R 80:localhost:8080 %USER%@%SERVER%

pause
