#!/usr/bin/env python3
"""
小红书自动化工作流
- 选题抓取 → 飞书表格
- 图文生成 → 飞书表格  
- 图片上传 → 公网链接 → 飞书表格
- 博主数据 → 自动填充
- 热点资讯 → 自动同步
"""

import os
import json
import time
import requests
from datetime import datetime

# 清除代理
for key in list(os.environ.keys()):
    if 'proxy' in key.lower():
        del os.environ[key]

# ============== 配置 ==============
# 飞书配置
BITABLE_TOKEN = "OSEAbRCpCaCscOsUNfmc3Ijwnrg"  # 小红书选题库
TABLE_ID = "tblpXYJMhW7IyZZm"

# 图片服务配置
IMAGE_SERVER = "http://10.0.0.15:18081"
IMAGE_DIR = "/root/.openclaw/workspace/images"

# 智谱AI配置
ZHIPU_KEY = "bd1e2312f8bc4539ae2ae2645905576d.RISv3Rf49m3C3tCG"

# ============== 飞书API ==============
def get_feishu_token():
    """获取飞书access_token"""
    app_id = "cli_a9117290ae78dbb5"
    app_secret = "KrGR7nzM6k8lN7zHqOahsc5phvgSUYxY"
    
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    data = {"app_id": app_id, "app_secret": app_secret}
    
    resp = requests.post(url, json=data)
    return resp.json().get("tenant_access_token")

def create_record(token, fields):
    """创建飞书表格记录"""
    # 使用table_id而非bitable token
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_TOKEN}/tables/{TABLE_ID}/records"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # 清理字段值
    clean_fields = {}
    for k, v in fields.items():
        if v is None:
            v = ""
        clean_fields[k] = str(v)[:2000]  # 限制长度
    
    data = {"fields": clean_fields}
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        # 尝试解析JSON，如果失败返回原始响应
        try:
            return resp.json()
        except:
            return {"raw": resp.text[:200], "status": resp.status_code}
    except Exception as e:
        print(f"   ❌ 创建记录失败: {e}")
        return {"error": str(e)}

def list_records(token, filter_str=""):
    """查询飞书表格记录"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_TOKEN}/tables/{TABLE_ID}/records"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"filter": filter_str} if filter_str else {}
    
    resp = requests.get(url, headers=headers, params=params)
    try:
        return resp.json()
    except:
        return {"data": {"items": []}}

# ============== 选题抓取 ==============
def fetch_trending_topics():
    """抓取热点选题"""
    # 这里可以接入各种数据源
    # 目前返回模拟数据，实际可接入：
    # - 微博热搜
    # - 抖音热榜
    # - 小红书热门
    
    topics = [
        {
            "选题来源": "热点追踪",
            "关键词": "春季穿搭",
            "标题草稿": "春天穿什么？试试这5套搭配",
            "内容状态": "待生成"
        },
        {
            "选题来源": "热点追踪",
            "关键词": "平价好物",
            "标题草稿": "学生党必看！平价好物分享",
            "内容状态": "待生成"
        }
    ]
    return topics

# ============== 图文生成 ==============
def generate_content(keyword, title_hint):
    """用AI生成正文内容"""
    url = "https://open.bigmodel.cn/api/paas/v4/text/chatcompletion"
    
    headers = {
        "Authorization": f"Bearer {ZHIPU_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""请为小红书写一篇种    
关键词草笔记：
：{keyword}
标题：{title_hint}

要求：
1. 语言生动活泼，符合小红书风格
2. 开头有吸引力
3. 中间分享真实体验
4. 结尾有互动引导
5. 适当添加emoji

正文："""
    
    data = {
        "model": "glm-4",
        "messages": [{"role": "user", "content": prompt}]
    }
    
    resp = requests.post(url, headers=headers, json=data, timeout=60)
    result = resp.json()
    
    if "choices" in result:
        return result["choices"][0]["message"]["content"]
    return "生成失败"

# ============== 图片生成 ==============
def generate_image(prompt):
    """用AI生成图片"""
    url = "https://open.bigmodel.cn/api/paas/v4/images/generations"
    
    headers = {
        "Authorization": f"Bearer {ZHIPU_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "cogview-3",
        "prompt": prompt,
        "size": "1024x1024"
    }
    
    resp = requests.post(url, headers=headers, json=data, timeout=120)
    result = resp.json()
    
    if "data" in result and len(result["data"]) > 0:
        return result["data"][0]["url"]
    return None

# ============== 图片上传 ==============
def upload_to_server(image_url, keyword):
    """下载图片并上传到图片服务器"""
    import urllib.request
    import shutil
    
    # 创建目录
    date_dir = datetime.now().strftime("%Y-%m-%d")
    save_dir = f"{IMAGE_DIR}/auto/{keyword}/{date_dir}"
    os.makedirs(save_dir, exist_ok=True)
    
    # 下载图片
    filename = f"img_{int(time.time())}.png"
    filepath = f"{save_dir}/{filename}"
    
    try:
        urllib.request.urlretrieve(image_url, filepath)
        
        # 返回访问链接
        return f"{IMAGE_SERVER}/images/auto/{keyword}/{date_dir}/{filename}"
    except Exception as e:
        print(f"上传失败: {e}")
        return None

# ============== 完整工作流 ==============
def run_workflow():
    """运行完整工作流"""
    print("=" * 50)
    print("小红书自动化工作流开始")
    print("=" * 50)
    
    # 1. 获取飞书token
    token = get_feishu_token()
    print(f"✅ 飞书Token获取成功")
    
    # 2. 抓取选题
    print("\n📥 抓取热点选题...")
    topics = fetch_trending_topics()
    print(f"   抓取到 {len(topics)} 个选题")
    
    # 3. 处理每个选题
    for topic in topics:
        keyword = topic.get("关键词", "")
        title = topic.get("标题草稿", "")
        
        print(f"\n📝 处理选题: {keyword}")
        
        # 检查是否已处理
        records = list_records(token)
        existing = records.get("data", {}).get("items", [])
        
        # 跳过已处理的
        already_done = False
        for record in existing:
            fields = record.get("fields", {})
            if fields.get("关键词") == keyword and fields.get("内容状态") != "待生成":
                already_done = True
                print(f"   ⏭️ 已处理，跳过")
                break
        
        if already_done:
            continue
        
        # 4. 生成正文
        print(f"   ✍️ 生成正文...")
        content = generate_content(keyword, title)
        
        # 5. 生成配图说明
        image_prompt = f"小红书配图，{keyword}，精致唯美风格，干净背景，高清"
        
        # 6. 生成图片
        print(f"   🖼️ 生成图片...")
        image_url = generate_image(image_prompt)
        
        public_url = ""
        if image_url:
            print(f"   📤 上传图片...")
            public_url = upload_to_server(image_url, keyword)
        
        # 7. 写入表格
        print(f"   💾 写入飞书表格...")
        
        # URL字段需要使用字段ID
        fields = {
            "选题来源": topic.get("选题来源", ""),
            "关键词": keyword,
            "标题草稿": title,
            "正文内容": content[:500] if content else "",
            # 飞书Bitable URL字段格式
            "图片链接": public_url if public_url else "",
            "配图说明": image_prompt if image_prompt else "",
            "内容状态": "已生成"
        }
        
        result = create_record(token, fields)
        print(f"   结果: {result}")
        print(f"   ✅ 完成!")
    
    print("\n" + "=" * 50)
    print("工作流执行完成!")
    print("=" * 50)

if __name__ == "__main__":
    run_workflow()
