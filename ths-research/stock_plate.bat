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

echo 正在获取数据...
echo.

REM 酿酒行业
echo 📊 酿酒行业
python -c "
import urllib.request,time
def g(c):
    try:
        r=urllib.request.urlopen(urllib.request.Request('http://hq.sinajs.cn/list=%27sh%27+c,headers={'User-Agent':'Mozilla'}),timeout=5).read().decode('gbk')
        p=r.split('=')[1].split(',')
        if len(p)>3:
            n=p[0];cp=float(p[3]);yp=float(p[2]);print(f'  {n}: {cp:.2f} ({(cp-yp)/yp*100:+.2f}%)')
    except:pass
g('600519');time.sleep(0.3)
g('000858');time.sleep(0.3)
g('000568');time.sleep(0.3)
g('603288')
"

echo.
pause
