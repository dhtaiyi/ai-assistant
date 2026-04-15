#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书Cookie自动刷新管理器
实现Cookie长期保存和自动刷新
"""

import json
import os
import time
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
import logging

# 配置
COOKIE_FILE = '/home/dhtaiyi/.openclaw/workspace/xiaohongshu-cookies.json'
LOG_FILE = '/home/dhtaiyi/.openclaw/workspace/xiaohongshu-cookie.log'
REFRESH_INTERVAL = 6 * 3600  # 每6小时刷新一次
EXPIRY_THRESHOLD = 24 * 3600  # 24小时过期阈值

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CookieManager:
    """Cookie管理器"""
    
    def __init__(self, cookie_file=COOKIE_FILE):
        self.cookie_file = cookie_file
        self.cookies = {}
        self.last_refresh = None
        self.load_cookies()
    
    def load_cookies(self):
        """加载Cookie"""
        if os.path.exists(self.cookie_file):
            try:
                with open(self.cookie_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.cookies = data.get('cookies', {})
                    self.last_refresh = data.get('last_refresh')
                    logger.info(f"✅ 加载Cookie: {len(self.cookies)} 个")
                    logger.info(f"最后刷新: {self.last_refresh}")
                    return True
            except Exception as e:
                logger.error(f"❌ 加载Cookie失败: {e}")
        return False
    
    def save_cookies(self):
        """保存Cookie"""
        try:
            data = {
                'cookies': self.cookies,
                'last_refresh': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(hours=24)).isoformat()
            }
            with open(self.cookie_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ 保存Cookie: {len(self.cookies)} 个")
            return True
        except Exception as e:
            logger.error(f"❌ 保存Cookie失败: {e}")
            return False
    
    def get_cookies(self):
        """获取Cookie字符串"""
        return '; '.join([f"{k}={v}" for k, v in self.cookies.items()])
    
    def needs_refresh(self):
        """检查是否需要刷新"""
        if not self.last_refresh:
            return True
        
        last_time = datetime.fromisoformat(self.last_refresh)
        elapsed = (datetime.now() - last_time).total_seconds()
        
        return elapsed > REFRESH_INTERVAL
    
    def is_valid(self):
        """检查Cookie是否有效"""
        if not self.cookies:
            return False
        
        # 检查web_session是否存在
        if 'web_session' not in self.cookies:
            return False
        
        # 检查是否过期
        if self.last_refresh:
            last_time = datetime.fromisoformat(self.last_refresh)
            elapsed = (datetime.now() - last_time).total_seconds()
            if elapsed > EXPIRY_THRESHOLD:
                logger.warning("⚠️ Cookie已超过24小时，可能失效")
        
        return True

def refresh_cookies(playwright=None):
    """刷新Cookie"""
    logger.info("🔄 开始刷新Cookie...")
    
    browser = None
    try:
        if not playwright:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                return _do_refresh(browser)
        else:
            browser = playwright.chromium.launch(headless=True)
            return _do_refresh(browser)
    except Exception as e:
        logger.error(f"❌ 刷新失败: {e}")
        return None
    finally:
        if browser:
            browser.close()

def _do_refresh(browser):
    """执行刷新"""
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'
    )
    
    page = context.new_page()
    
    try:
        # 访问小红书
        logger.info("📱 访问小红书...")
        page.goto('https://www.xiaohongshu.com', timeout=20000, wait_until='networkidle')
        
        # 等待用户登录（如果是首次）
        input("\n⚠️ 请在浏览器中确认登录状态...")
        
        # 获取Cookie
        cookies = context.cookies()
        cookie_dict = {c['name']: c['value'] for c in cookies}
        
        logger.info(f"✅ 获取 {len(cookie_dict)} 个Cookie")
        logger.info(f"web_session: {cookie_dict.get('web_session', '未设置')}")
        
        return cookie_dict
        
    except Exception as e:
        logger.error(f"❌ 获取Cookie失败: {e}")
        return None
    finally:
        context.close()

def auto_refresh_loop():
    """自动刷新循环"""
    logger.info("🚀 启动Cookie自动刷新服务...")
    logger.info(f"刷新间隔: {REFRESH_INTERVAL/3600} 小时")
    
    manager = CookieManager()
    
    while True:
        try:
            if manager.needs_refresh():
                logger.info("⏰ 需要刷新Cookie...")
                cookies = refresh_cookies()
                
                if cookies:
                    manager.cookies = cookies
                    manager.save_cookies()
                    logger.info("✅ Cookie已更新")
                else:
                    logger.error("❌ Cookie刷新失败")
            else:
                logger.info("✅ Cookie仍有效，跳过刷新")
            
            # 等待下次检查
            time.sleep(3600)  # 每小时检查一次
            
        except KeyboardInterrupt:
            logger.info("👋 用户中断，退出")
            break
        except Exception as e:
            logger.error(f"❌ 错误: {e}")
            time.sleep(60)

def quick_refresh():
    """快速刷新（用于定时任务）"""
    logger.info("⚡ 快速刷新Cookie...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = context.new_page()
        
        try:
            # 访问小红书
            page.goto('https://www.xiaohongshu.com', timeout=20000, wait_until='networkidle')
            time.sleep(2)
            
            # 获取Cookie
            cookies = context.cookies()
            cookie_dict = {c['name']: c['value'] for c in cookies}
            
            # 保存
            manager = CookieManager()
            manager.cookies = cookie_dict
            manager.save_cookies()
            
            logger.info(f"✅ Cookie已更新: {len(cookie_dict)} 个")
            
        finally:
            browser.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'refresh':
            quick_refresh()
        elif command == 'monitor':
            auto_refresh_loop()
        elif command == 'status':
            manager = CookieManager()
            print(f"\n📊 Cookie状态:")
            print(f"  数量: {len(manager.cookies)}")
            print(f"  最后刷新: {manager.last_refresh}")
            print(f"  有效: {manager.is_valid()}")
            print(f"  需要刷新: {manager.needs_refresh()}")
        elif command == 'test':
            # 测试模式
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                print("📱 访问小红书...")
                page.goto('https://www.xiaohongshu.com', timeout=20000)
                time.sleep(3)
                
                print(f"标题: {page.title()}")
                print(f"URL: {page.url}")
                
                browser.close()
        else:
            print("用法:")
            print("  python3 xiaohongshu-cookie-manager.py refresh  # 刷新Cookie")
            print("  python3 xiaohongshu-cookie-manager.py monitor   # 启动自动刷新")
            print("  python3 xiaohongshu-cookie-manager.py status    # 查看状态")
    else:
        print("用法:")
        print("  python3 xiaohongshu-cookie-manager.py refresh  # 刷新Cookie")
        print("  python3 xiaohongshu-cookie-manager.py monitor   # 启动自动刷新")
        print("  python3 xiaohongshu-cookie-manager.py status    # 查看状态")
