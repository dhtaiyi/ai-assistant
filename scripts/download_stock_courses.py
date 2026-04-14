#!/usr/bin/env python3
"""从NAS下载股票课程视频"""

import paramiko
import os
import time

def main():
    transport = paramiko.Transport(('192.168.0.107', 22))
    transport.connect(username='xiaoxiaoyu', password='xiaoxiaoyu')
    sftp = paramiko.SFTPClient.from_transport(transport)
    
    base = '/迅雷下载/同步盘/股票课程/'
    local_base = '/home/dhtaiyi/.openclaw/workspace/stock-courses/'
    
    def get_mp4_list(path):
        files = sftp.listdir(path)
        return sorted([f for f in files if '.mp4' in f])
    
    # 获取章节
    ch1_name = ch2_name = None
    for e in sftp.listdir_attr(base):
        if '第一章' in e.filename:
            ch1_name = e.filename
        elif '第二章' in e.filename:
            ch2_name = e.filename
    
    # 下载第一章
    print(f"📚 下载第一章: {ch1_name}")
    ch1_path = base + ch1_name
    ch1_files = get_mp4_list(ch1_path)
    os.makedirs(local_base + 'ch1', exist_ok=True)
    
    for i, f in enumerate(ch1_files):
        local = local_base + 'ch1/' + f
        if os.path.exists(local) and os.path.getsize(local) > 1000000:
            print(f"  [{i+1}/{len(ch1_files)}] 已存在: {f}")
            continue
        remote = ch1_path + '/' + f
        print(f"  [{i+1}/{len(ch1_files)}] 下载中: {f}")
        start = time.time()
        sftp.get(remote, local)
        elapsed = time.time() - start
        size = os.path.getsize(local)
        print(f"      ✅ {size/1024/1024:.1f}MB, {elapsed:.1f}秒")
    
    # 下载第二章
    print(f"\n📚 下载第二章: {ch2_name}")
    ch2_path = base + ch2_name
    ch2_files = get_mp4_list(ch2_path)
    os.makedirs(local_base + 'ch2', exist_ok=True)
    
    for i, f in enumerate(ch2_files):
        local = local_base + 'ch2/' + f
        if os.path.exists(local) and os.path.getsize(local) > 1000000:
            print(f"  [{i+1}/{len(ch2_files)}] 已存在: {f}")
            continue
        remote = ch2_path + '/' + f
        print(f"  [{i+1}/{len(ch2_files)}] 下载中: {f}")
        start = time.time()
        sftp.get(remote, local)
        elapsed = time.time() - start
        size = os.path.getsize(local)
        print(f"      ✅ {size/1024/1024:.1f}MB, {elapsed:.1f}秒")
    
    sftp.close()
    transport.close()
    print("\n🎉 全部下载完成!")

if __name__ == '__main__':
    main()
