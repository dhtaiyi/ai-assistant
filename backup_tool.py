#!/usr/bin/env python3
"""
OpenClaw 备份恢复工具
备份配置到GitHub，从GitHub恢复
"""

import os
import json
import subprocess
import datetime

WORKSPACE = "/root/.openclaw/workspace"
CREDENTIALS = "/root/.openclaw/credentials"
BACKUP_DIR = "/tmp/openclaw-backup"

GITHUB_REPO = "your-github-repo"  # 需要配置
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

def run_cmd(cmd):
    """执行命令"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def backup():
    """备份配置"""
    print("📦 开始备份...")
    
    # 创建备份目录
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # 备份文件
    files_to_backup = [
        "/root/.openclaw/openclaw.json",
        "/root/.openclaw/workspace/MEMORY.md",
        "/root/.openclaw/workspace/IDENTITY.md",
        "/root/.openclaw/workspace/SOUL.md",
    ]
    
    # 备份skills
    for root, dirs, files in os.walk("/root/.openclaw/workspace/skills"):
        for f in files:
            if f == "SKILL.md":
                files_to_backup.append(os.path.join(root, f))
    
    # 复制文件
    for f in files_to_backup:
        if os.path.exists(f):
            dest = f.replace("/root/.openclaw/", BACKUP_DIR + "/")
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            os.system(f"cp -r {f} {dest}")
            print(f"  ✅ {f}")
    
    # 创建备份信息
    info = {
        "date": datetime.datetime.now().isoformat(),
        "files": files_to_backup
    }
    with open(BACKUP_DIR + "/backup_info.json", "w") as f:
        json.dump(info, f, indent=2)
    
    print(f"\n📁 备份完成: {BACKUP_DIR}")
    return BACKUP_DIR

def restore(github_token=None, repo=None):
    """从GitHub恢复"""
    print("🔄 从GitHub恢复...")
    
    global GITHUB_TOKEN, GITHUB_REPO
    
    if github_token:
        GITHUB_TOKEN = github_token
    if repo:
        GITHUB_REPO = repo
    
    if not GITHUB_TOKEN or not GITHUB_REPO:
        print("❌ 需要配置 GITHUB_TOKEN 和 GITHUB_REPO")
        return False
    
    # 克隆仓库
    repo_url = f"https://{GITHUB_TOKEN}@github.com/{GITHUB_REPO}.git"
    
    # 检查是否存在
    if os.path.exists(BACKUP_DIR):
        os.system(f"rm -rf {BACKUP_DIR}")
    
    code, out, err = run_cmd(f"git clone {repo_url} {BACKUP_DIR}")
    
    if code != 0:
        print(f"❌ 克隆失败: {err}")
        return False
    
    # 恢复文件
    print("📥 恢复文件...")
    
    for root, dirs, files in os.walk(BACKUP_DIR):
        for f in files:
            src = os.path.join(root, f)
            dest = src.replace(BACKUP_DIR, "/root/.openclaw")
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            os.system(f"cp -r {src} {dest}")
            print(f"  ✅ {dest}")
    
    print("\n✅ 恢复完成!")
    return True

def list_backups():
    """列出可用备份"""
    if not os.path.exists(BACKUP_DIR):
        print("❌ 没有本地备份")
        return
    
    info_file = BACKUP_DIR + "/backup_info.json"
    if os.path.exists(info_file):
        with open(info_file) as f:
            info = json.load(f)
        print(f"📅 备份时间: {info.get('date')}")
        print(f"📁 文件数量: {len(info.get('files', []))}")

def upload_to_github(github_token, repo):
    """上传到GitHub"""
    global GITHUB_TOKEN, GITHUB_REPO
    
    GITHUB_TOKEN = github_token
    GITHUB_REPO = repo
    
    # 初始化git
    os.chdir(BACKUP_DIR)
    
    run_cmd("git config --global user.email 'backup@openclaw'")
    run_cmd("git config --global user.name 'OpenClaw Backup'")
    
    # 添加文件
    run_cmd("git add -A")
    
    # 提交
    msg = f"Backup {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
    run_cmd(f'git commit -m "{msg}"')
    
    # 推送到GitHub
    repo_url = f"https://{GITHUB_TOKEN}@github.com/{GITHUB_REPO}.git"
    code, out, err = run_cmd(f"git push {repo_url} main")
    
    if code == 0:
        print("✅ 已推送到GitHub!")
    else:
        print(f"❌ 推送失败: {err}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("""
🛠️ OpenClaw 备份恢复工具

用法:
    python3 backup_tool.py backup          # 本地备份
    python3 backup_tool.py restore <token> <repo>  # 从GitHub恢复
    python3 backup_tool.py upload <token> <repo>    # 上传到GitHub
    python3 backup_tool.py list             # 查看备份
        """)
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "backup":
        backup()
    elif cmd == "restore" and len(sys.argv) >= 4:
        restore(sys.argv[2], sys.argv[3])
    elif cmd == "upload" and len(sys.argv) >= 4:
        upload_to_github(sys.argv[2], sys.argv[3])
    elif cmd == "list":
        list_backups()
    else:
        print("❌ 命令不正确")
