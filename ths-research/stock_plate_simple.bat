@echo off
chcp 65001 >nul
REM ========================================
REM 板块排行查询工具
REM ========================================

echo.
echo ╔═══════════════════════════════════════╗
echo ║    板块排行查询                   ║
echo ╚═══════════════════════════════════════╝
echo.

echo 正在获取数据，请稍候...
echo.

REM 酿酒行业
echo.
echo ╔═══════════════════════════════════════╗
echo ║    酿酒行业                       ║
echo ╚═══════════════════════════════════════╝
python -c "
import urllib.request,time,sys
sys.stdout.reconfigure(encoding='utf-8')
try:
    for c in ['600519','000858','000568','603288','600809']:
        r=urllib.request.urlopen(urllib.request.Request('http://hq.sinajs.cn/list=sh'+c,headers={'User-Agent':'Mozilla'}),timeout=5).read().decode('gbk')
        if '=' in r:
            p=r.split('=')[1].split(',')
            if len(p)>3:
                n=p[0];cp=float(p[3]);yp=float(p[2]);print(f'  {n}: {cp:.2f} ({(cp-yp)/yp*100:+.2f}%)')
        time.sleep(0.3)
except Exception as e:
    print(f'  获取失败: {e}')
"

echo.
pause
