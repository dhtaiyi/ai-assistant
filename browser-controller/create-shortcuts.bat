@echo off
chcp 65001 >nul
REM ========================================
REM 创建桌面快捷方式
REM ========================================

echo.
echo ╔═══════════════════════════════════════╗
echo ║    创建桌面快捷方式                    ║
echo ╚═══════════════════════════════════════╝
echo.

REM 获取脚本所在目录
cd /d "%~dp0"
set SCRIPT_DIR=%cd%

REM 获取Python路径
for /f "delims=" %%i in ('python -c "import sys; print(sys.executable)"') do set PYTHON_PATH=%%i

REM 创建快捷方式
echo 📁 创建快捷方式...

REM 同花顺快捷方式
echo Set oWS = WScript.CreateObject("WScript.Shell") > create_shortcut.vbs
echo sLinkFile = "%USERPROFILE%\Desktop\打开同花顺.lnk" >> create_shortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> create_shortcut.vbs
echo oLink.TargetPath = "%PYTHON_PATH%" >> create_shortcut.vbs
echo oLink.Arguments = """%SCRIPT_DIR%\main.py"" -u https://www.10jqka.com.cn --stock" >> create_shortcut.vbs
echo oLink.WorkingDirectory = "%SCRIPT_DIR%" >> create_shortcut.vbs
echo oLink.Description = "打开同花顺并获取股票数据" >> create_shortcut.vbs
echo oLink.Save >> create_shortcut.vbs

cscript //nologo create_shortcut.vbs
del create_shortcut.vbs

echo ✅ 创建成功!
echo.
echo 📌 桌面已添加:
echo   📊 打开同花顺.lnk
echo.
echo 💡 直接双击即可运行!

pause
