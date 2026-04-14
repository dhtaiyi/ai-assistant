#!/usr/bin/env python3
"""从NAS下载股票课程视频并转录学习"""

from smb.SMBConnection import SMBConnection
import os
import time

NAS_HOST = '192.168.0.107'
NAS_USER = 'xiaoxiaoyu'
NAS_PASS = 'xiaoxiaoyu'
SHARE = '迅雷下载'
REMOTE_BASE = '/同步盘/股票课程/'
LOCAL_BASE = '/home/dhtaiyi/.openclaw/workspace/stock-courses/'

def connect():
    conn = SMBConnection(NAS_USER, NAS_PASS, 'dhtaiyi', NAS_HOST, use_ntlm_v2=True)
    conn.connect(NAS_HOST, 445)
    return conn

def download_file(conn, remote_path, local_path):
    """下载单个文件"""
    if os.path.exists(local_path):
        size = os.path.getsize(local_path)
        print(f"  已存在: {os.path.basename(local_path)} ({size/1024/1024:.1f}MB)")
        return True
    
    print(f"  下载中: {os.path.basename(local_path)}...")
    try:
        with open(local_path, 'wb') as f:
            conn.retrieveFile(SHARE, remote_path, f)
        print(f"  ✅ 完成!")
        return True
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        return False

def main():
    # 创建本地目录
    os.makedirs(LOCAL_BASE, exist_ok=True)
    
    conn = connect()
    print("✅ 连接NAS成功!")
    
    # 下载第一章
    print("\n📚 下载第一章 - 交易的'术'...")
    chapter1_files = [
        '/第一章-交易的"术"/1.1-主力行为逻辑.mp4',
        '/第一章-交易的"术"/1.2-盘口的重要性以及组成.mp4',
        '/第一章-交易的"术"/1.3-夹板盘的目的及运用.mp4',
        '/第一章-交易的"术"/1.4-压单、托单的目的及运用.mp4',
        '/第一章-交易的"术"/1.5-吃货盘口的典型特征.mp4',
        '/第一章-交易的"术"/1.6-出货盘口的典型特征.mp4',
        '/第一章-交易的"术"/1.7-拆单及对敲的目的及识别.mp4',
        '/第一章-交易的"术"/1.8-如何识别分时结构洗盘.mp4',
        '/第一章-交易的"术"/1.9-识别跌停出货及跌停吃货.mp4',
        '/第一章-交易的"术"/1.10-识别涨停出货及涨停吃货.mp4',
        '/第一章-交易的"术"/1.11-黄白线的关系及初步运用.mp4',
        '/第一章-交易的"术"/1.12-龙虎榜的简单运用.mp4',
        '/第一章-交易的"术"/1.13-集合竞价-集合竞价原理.mp4',
        '/第一章-交易的"术"/1.14-集合竞价-集合竟价在热门股中的运用.mp4',
    ]
    
    os.makedirs(os.path.join(LOCAL_BASE, '第一章-交易的"术"'), exist_ok=True)
    for f in chapter1_files:
        local = LOCAL_BASE + '第一章-交易的"术"' + f.split('/')[-1]
        download_file(conn, REMOTE_BASE + '第一章-交易的"形"' + f, local)
        time.sleep(0.5)
    
    # 下载第二章
    print("\n📚 下载第二章 - 交易的'形'...")
    chapter2_files = [
        '/第二章-交易的"形"/2.1-股价结构及常用辅助线.mp4',
        '/第二章-交易的"形"/2.2-大阳线(一)-意义.mp4',
        '/第二章-交易的"形"/2.3-大阳线(一)一字涨停;实体涨停;推土机大阳线;有影线性质的大阳线;尾盘大阳线.mp4',
        '/第二章-交易的"形"/2.4-大阳线(二)-大阳线启动的有效性.mp4',
        '/第二章-交易的"形"/2.5-大阳线(五)-下降趋势的大阳线.mp4',
        '/第二章-交易的"形"/2.6-大阳线(四)-箱体中大阳线.mp4',
        '/第二章-交易的"形"/2.7-大阳线(五)-多头趋势中的大阳线.mp4',
        '/第二章-交易的"形"/2.8-大阴线(一）-出货阶段的大阴线.mp4',
        '/第二章-交易的"形"/2.9-大阴线（二）-加速赶底大阴线的特征+箱体破位的阴线技术条件.mp4',
        '/第二章-交易的"形"/2.10-大阴线(三）-多头趋势中的大阴线+假阴线的逻辑+调整阴线.mp4',
        '/第二章-交易的"形"/2.11-加速K线和极小线及缺口.mp4',
        '/第二章-交易的"形"/2.12-几种典型的股价结构(一)-黄昏之星+晨星结构+仙人指路.mp4',
        '/第二章-交易的"形"/2.13-几种典型的股价结构(二)-扩散+收敛+旗型++二低点.mp4',
        '/第二章-交易的"形"/2.14-标志性K线形态-高浪线型+高分歧线型+高滞涨线型.mp4',
    ]
    
    os.makedirs(os.path.join(LOCAL_BASE, '第二章-交易的"形"'), exist_ok=True)
    for f in chapter2_files:
        local = LOCAL_BASE + '第二章-交易的"形"' + f.split('/')[-1]
        download_file(conn, REMOTE_BASE + '第二章-交易的"形"' + f, local)
        time.sleep(0.5)
    
    conn.close()
    print("\n✅ 下载完成!")

if __name__ == '__main__':
    main()
