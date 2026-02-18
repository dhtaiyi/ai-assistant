@echo off
REM 启动脚本 - Windows版

echo.
echo ========================================
echo    股票数据服务启动器
echo ========================================
echo.
echo 1. 安装依赖
echo 2. 启动数据服务
echo 3. 建立SSH隧道
echo.
echo ========================================

echo.
echo 步骤1: 检查依赖
pip show akshare >nul 2>&1
if errorlevel 1 (
    echo ⚠️  akshare 未安装，正在安装...
    pip install akshare flask
) else (
    echo ✅ akshare 已安装
)

pip show flask >nul 2>&1
if errorlevel 1 (
    echo ⚠️  flask 未安装，正在安装...
    pip install flask
) else (
    echo ✅ flask 已安装
)

echo.
echo 步骤2: 启动数据服务
echo.
echo 按任意键启动服务...
pause >nul

start "股票数据服务" python stock_api.py

echo.
echo ✅ 数据服务已启动！
echo.
echo 步骤3: 建立SSH隧道
echo.
echo 按任意键建立隧道...
pause >nul

echo.
echo 请运行 ssh_tunnel.bat 建立隧道
start ssh_tunnel.bat

echo.
echo ========================================
echo    启动完成！
echo ========================================
echo.
echo 下一步:
echo 1. 保持服务窗口打开
echo 2. 运行 ssh_tunnel.bat
echo 3. 在服务器上访问 http://localhost
echo.
