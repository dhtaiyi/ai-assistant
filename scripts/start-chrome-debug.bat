@echo off
echo 启动Chrome远程调试...
echo.
echo 按任意键继续...
pause >nul

start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --no-first-run --no-default-browser-check

echo.
echo Chrome已启动，端口9222已打开
echo 按任意键退出...
pause >nul
