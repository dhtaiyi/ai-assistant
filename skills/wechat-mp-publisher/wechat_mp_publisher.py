#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号发布器
Publish articles to WeChat Official Accounts Platform

Requires:
    - WECHAT_APPID
    - WECHAT_APPSECRET

Usage:
    python wechat_mp_publisher.py --title "标题" --content "正文" --image "封面图路径"
"""

import os
import json
import requests
import argparse
from datetime import datetime


class WeChatMPPublisher:
    """微信公众号发布器"""
    
    def __init__(self, appid=None, appsecret=None):
        self.appid = appid or os.getenv('WECHAT_APPID')
        self.appsecret = appsecret or os.getenv('WECHAT_APPSECRET')
        self.access_token = None
        self.token_expires = None
        
        if not self.appid or not self.appsecret:
            raise ValueError("请设置 WECHAT_APPID 和 WECHAT_APPSECRET")
    
    def get_access_token(self):
        """获取 access_token"""
        url = f"https://api.weixin.qq.com/cgi-bin/token"
        params = {
            'grant_type': 'client_credential',
            'appid': self.appid,
            'secret': self.appsecret
        }
        
        response = requests.get(url, params=params, timeout=30)
        result = response.json()
        
        if 'access_token' in result:
            self.access_token = result['access_token']
            print(f"✅ 获取 access_token 成功")
            return self.access_token
        else:
            error_msg = result.get('errmsg', '未知错误')
            print(f"❌ 获取失败: {error_msg}")
            return None
    
    def upload_image(self, image_path, name=None, digest=None):
        """上传图片素材"""
        if not self.access_token:
            self.get_access_token()
        
        url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg"
        params = {'access_token': self.access_token}
        
        with open(image_path, 'rb') as f:
            files = {'media': (name or 'image', f, 'image/jpeg')}
            data = {'filename': name}
            if digest:
                data['digest'] = digest
            
            response = requests.post(url, params=params, files=files, data=data, timeout=60)
            result = response.json()
            
            if 'url' in result:
                print(f"✅ 图片上传成功: {result['url']}")
                return result['url']
            else:
                print(f"❌ 图片上传失败: {result.get('errmsg', result)}")
                return None
    
    def upload_news(self, title, content, thumb_path=None, digest=None, author=None, show_cover_pic=1):
        """上传图文素材"""
        if not self.access_token:
            self.get_access_token()
        
        url = f"https://api.weixin.qq.com/cgi-bin/material/add_news"
        params = {'access_token': self.access_token}
        
        # 构建文章内容（转换HTML为微信可识别格式）
        articles = [{
            "title": title,
            "thumb_media_id": "",  # 如需封面media_id，先上传图片获取
            "author": author or "AI工具爱好者",
            "digest": digest or content[:120],
            "show_cover_pic": show_cover_pic,
            "content": content,
            "content_source_url": ""
        }]
        
        data = {"articles": articles}
        
        response = requests.post(url, params=params, json=data, timeout=60)
        result = response.json()
        
        if 'media_id' in result:
            print(f"✅ 图文素材上传成功! Media ID: {result['media_id']}")
            return result['media_id']
        else:
            print(f"❌ 上传失败: {result.get('errmsg', result)}")
            return None
    
    def publish(self, media_id):
        """发布图文素材到公众号"""
        if not self.access_token:
            self.get_access_token()
        
        url = f"https://api.weixin.qq.com/cgi-bin/freepublish/batchpublish"
        params = {'access_token': self.access_token}
        
        data = {
            "media_id": media_id,
            "publish_type": 0,  # 0: 发布到草稿箱
            "only_fans": 0  # 0: 发送给所有用户
        }
        
        response = requests.post(url, params=params, json=data, timeout=60)
        result = response.json()
        
        if result.get('errcode') == 0:
            print(f"✅ 发布成功!")
            return result
        else:
            print(f"❌ 发布失败: {result.get('errmsg', result)}")
            return result
    
    def get_draft_list(self):
        """获取草稿箱列表"""
        if not self.access_token:
            self.get_access_token()
        
        url = "https://api.weixin.qq.com/cgi-bin/draft/batchget"
        params = {'access_token': self.access_token}
        data = {"offset": 0, "count": 20, "no_content": 0}
        
        response = requests.post(url, params=params, json=data, timeout=30)
        result = response.json()
        
        if 'draft_list' in result:
            return result['draft_list']
        return []


def main():
    parser = argparse.ArgumentParser(description='微信公众号发布器')
    parser.add_argument('--title', '-t', help='文章标题')
    parser.add_argument('--content', '-c', help='文章内容 (支持HTML)')
    parser.add_argument('--image', '-i', help='封面图片路径')
    parser.add_argument('--digest', '-d', help='文章摘要')
    parser.add_argument('--author', '-a', help='作者名')
    parser.add_argument('--check', action='store_true', help='检查登录状态')
    
    args = parser.parse_args()
    
    # 检查状态
    if args.check:
        print("📊 检查公众号配置...")
        publisher = WeChatMPPublisher()
        token = publisher.get_access_token()
        if token:
            print("✅ 账号配置正确")
            drafts = publisher.get_draft_list()
            print(f"📝 草稿箱中有 {len(drafts)} 篇草稿")
        return
    
    # 发布文章
    if args.title and args.content:
        print("📤 准备发布文章...")
        
        publisher = WeChatMPPublisher()
        
        # 1. 上传图文素材
        media_id = publisher.upload_news(
            title=args.title,
            content=args.content,
            thumb_path=args.image,
            digest=args.digest,
            author=args.author
        )
        
        if media_id:
            print(f"\n📝 图文素材已创建: {media_id}")
            print("💡 请登录微信公众平台手动发布")
        return
    
    print(__doc__)
    print("\n📋 使用示例:")
    print("  python wechat_mp_publisher.py --check")
    print("  python wechat_mp_publisher.py --title '标题' --content '正文'")
    print("  python wechat_mp_publisher.py --title '标题' --content '正文' --image '封面.jpg'")


if __name__ == '__main__':
    main()
