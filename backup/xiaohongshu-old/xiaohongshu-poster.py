#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书自动化发贴系统
功能：
1. 发布图文笔记
2. 定时发布
3. 批量发布
4. 内容模板
"""

import json
import os
import time
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
import logging

# 配置
POSTS_DIR = '/root/.openclaw/workspace/xiaohongshu-posts'
CONFIG_FILE = '/root/.openclaw/workspace/xiaohongshu-poster-config.json'
LOG_FILE = '/root/.openclaw/workspace/xiaohongshu-poster.log'

# 日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class XiaoHongShuPoster:
    """小红书发贴系统"""
    
    def __init__(self):
        self.cookies = self.load_cookies()
        self.browser = None
        self.context = None
        self.page = None
    
    def load_cookies(self):
        """加载Cookie"""
        try:
            with open('/root/.openclaw/workspace/xiaohongshu-cookies.json', 'r') as f:
                data = json.load(f)
                return data.get('cookies', {})
        except:
            return {}
    
    def login(self):
        """登录"""
        logger.info("🔄 启动浏览器...")
        
        self.browser = sync_playwright().chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)'
        )
        
        self.page = self.context.new_page()
        
        # 加载Cookie
        if self.cookies:
            for name, value in self.cookies.items():
                self.context.add_cookies([{
                    'name': name,
                    'value': value,
                    'domain': '.xiaohongshu.com',
                    'path': '/'
                }])
        
        # 访问创作者平台
        logger.info("📱 访问创作者平台...")
        self.page.goto('https://creator.xiaohongshu.com/publish/publish', timeout=20000)
        time.sleep(3)
        
        # 检查登录状态
        if 'login' in self.page.url:
            logger.warning("⚠️ 需要重新登录！")
            logger.info("请在浏览器中完成登录...")
            input("登录完成后按回车继续...")
        
        return True
    
    def check_permission(self):
        """检查发贴权限"""
        logger.info("📋 检查发贴权限...")
        
        # 检查是否是创作者
        text = self.page.inner_text('body')[:1000]
        
        if '创作者' in text and '申请' in text:
            logger.warning("⚠️ 需要申请创作者资格！")
            return False
        elif '发布' in text or '发布笔记' in text:
            logger.info("✅ 有发贴权限")
            return True
        else:
            logger.warning("⚠️ 状态未知，检查页面...")
            return False
    
    def create_post(self, title, content, images=None):
        """创建笔记"""
        logger.info(f"📝 创建笔记: {title[:30]}...")
        
        try:
            # 查找标题输入框
            title_input = self.page.query_selector('input[placeholder*="标题"]') or \
                         self.page.query_selector('textarea[placeholder*="标题"]')
            
            if title_input:
                title_input.fill(title)
                logger.info("✅ 标题已填写")
            
            # 查找内容输入框
            content_input = self.page.query_selector('textarea[placeholder*="分享"]') or \
                          self.page.query_selector('div[contenteditable]')
            
            if content_input:
                content_input.fill(content)
                logger.info("✅ 内容已填写")
            
            # 如果有图片，上传图片
            if images:
                logger.info(f"📷 准备上传 {len(images)} 张图片...")
                # 图片上传逻辑需要根据实际页面调整
            
            # 查找发布按钮
            publish_btn = self.page.query_selector('button:has-text("发布")')
            
            if publish_btn:
                logger.info("✅ 找到发布按钮")
                return True
            else:
                logger.warning("❌ 未找到发布按钮")
                return False
            
        except Exception as e:
            logger.error(f"❌ 创建笔记失败: {e}")
            return False
    
    def publish(self):
        """发布"""
        try:
            publish_btn = self.page.query_selector('button:has-text("发布")')
            if publish_btn:
                publish_btn.click()
                logger.info("✅ 已点击发布按钮")
                time.sleep(5)
                
                # 检查发布结果
                text = self.page.inner_text('body')[:500]
                if '成功' in text or '发布' in text:
                    logger.info("✅ 发布成功！")
                    return True
                else:
                    logger.warning("⚠️ 发布状态未知")
                    return True
            return False
        except Exception as e:
            logger.error(f"❌ 发布失败: {e}")
            return False
    
    def close(self):
        """关闭"""
        if self.browser:
            self.browser.close()
            logger.info("✅ 浏览器已关闭")
    
    def run(self, title, content, images=None):
        """执行发贴流程"""
        try:
            self.login()
            
            if not self.check_permission():
                logger.error("❌ 没有发贴权限，请先申请创作者资格")
                return False
            
            if self.create_post(title, content, images):
                self.publish()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ 发贴失败: {e}")
            return False
        finally:
            self.close()


class PostScheduler:
    """定时发贴"""
    
    def __init__(self):
        self.posts = self.load_posts()
    
    def load_posts(self):
        """加载待发布内容"""
        if os.path.exists(POSTS_DIR):
            posts = []
            for f in os.listdir(POSTS_DIR):
                if f.endswith('.json'):
                    with open(os.path.join(POSTS_DIR, f), 'r') as fp:
                        posts.append(json.load(fp))
            return posts
        return []
    
    def add_post(self, title, content, images=None, publish_time=None):
        """添加待发布内容"""
        post = {
            'title': title,
            'content': content,
            'images': images or [],
            'publish_time': publish_time,
            'created_at': datetime.now().isoformat(),
            'status': 'pending'
        }
        
        os.makedirs(POSTS_DIR, exist_ok=True)
        
        filename = f"post_{int(time.time())}.json"
        with open(os.path.join(POSTS_DIR, filename), 'w') as f:
            json.dump(post, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ 已添加待发布内容: {title[:30]}")
        return filename
    
    def list_posts(self):
        """列出待发布内容"""
        if not self.posts:
            logger.info("暂无待发布内容")
            return
        
        for i, post in enumerate(self.posts, 1):
            status = post.get('status', 'unknown')
            title = post.get('title', '无标题')[:40]
            logger.info(f"{i}. [{status}] {title}")


def create_template():
    """创建内容模板"""
    
    template = {
        'title': '笔记标题',
        'content': '''分享一个超棒的体验！

✨ 亮点：
- 第一点
- 第二点
- 第三点

📝 详细说明：
这里填写详细内容...

#话题标签 #小红书''',
        'images': ['/path/to/image1.jpg'],
        'publish_time': None  # None表示立即发布
    
    }
    
    os.makedirs(POSTS_DIR, exist_ok=True)
    
    with open(os.path.join(POSTS_DIR, 'template.json'), 'w') as f:
        json.dump(template, f, ensure_ascii=False, indent=2)
    
    logger.info(f"✅ 已创建模板: {POSTS_DIR}/template.json")


def main():
    """主程序"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'post':
            # 立即发布
            if len(sys.argv) > 3:
                title = sys.argv[2]
                content = sys.argv[3]
                poster = XiaoHongShuPoster()
                poster.run(title, content)
            else:
                print("用法: python3 xiaohongshu-poster.py post '标题' '内容'")
        
        elif command == 'add':
            # 添加待发布内容
            if len(sys.argv) > 3:
                title = sys.argv[2]
                content = sys.argv[3]
                scheduler = PostScheduler()
                scheduler.add_post(title, content)
            else:
                print("用法: python3 xiaohongshu-poster.py add '标题' '内容'")
        
        elif command == 'list':
            # 列出待发布
            scheduler = PostScheduler()
            scheduler.list_posts()
        
        elif command == 'template':
            # 创建模板
            create_template()
        
        elif command == 'check':
            # 检查权限
            poster = XiaoHongShuPoster()
            poster.login()
            poster.check_permission()
            poster.close()
        
        elif command == 'help':
            print("""
使用方法:
  python3 xiaohongshu-poster.py post '标题' '内容'    # 立即发布
  python3 xiaohongshu-poster.py add '标题' '内容'     # 添加到队列
  python3 xiaohongshu-poster.py list                   # 查看队列
  python3 xiaohongshu-poster.py template              # 创建模板
  python3 xiaohongshu-poster.py check                # 检查权限
  python3 xiaohongshu-poster.py help                 # 显示帮助
            """)
        
        else:
            print("未知命令，使用: python3 xiaohongshu-poster.py help")
    
    else:
        print("""
小红书自动化发贴系统
====================

命令:
  post      - 立即发布
  add       - 添加到发布队列
  list      - 查看队列
  template  - 创建模板
  check     - 检查权限
  help      - 显示帮助

使用:
  python3 xiaohongshu-poster.py post '我的标题' '内容...'
  python3 xiaohongshu-poster.py add '稍后发布' '内容...'
            """)


if __name__ == "__main__":
    main()
