#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书 API 技能封装
直接调用 xiaohongshu-mcp 的 REST API 接口

作者: OpenClaw
版本: 1.0.0
"""

import argparse
import json
import sys
import requests
from typing import List, Optional


class XiaoHongShuAPI:
    """小红书 API 封装类"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:18060"):
        """
        初始化小红书 API
        
        Args:
            base_url: xiaohongshu-mcp 服务器地址
        """
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api/v1"
    
    def _request(self, method: str, endpoint: str, data: Optional[dict] = None) -> dict:
        """
        发送 API 请求
        
        Args:
            method: HTTP 方法
            endpoint: API 端点
            data: 请求数据
            
        Returns:
            API 响应
        """
        url = f"{self.api_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"不支持的 HTTP 方法: {method}")
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"API 请求失败: {e}"
            }
    
    def check_login(self) -> dict:
        """检查登录状态"""
        return self._request("GET", "/login/status")
    
    def get_qrcode(self) -> dict:
        """获取登录二维码"""
        return self._request("GET", "/login/qrcode")
    
    def delete_cookies(self) -> dict:
        """删除 cookies"""
        return self._request("DELETE", "/login/cookies")
    
    def publish(self, title: str, content: str, images: List[str], 
                video: Optional[str] = None) -> dict:
        """
        发布图文内容
        
        Args:
            title: 标题
            content: 正文内容
            images: 图片路径列表
            video: 视频路径（可选）
        """
        data = {
            "title": title,
            "content": content,
            "images": images
        }
        if video:
            data["video"] = video
        
        return self._request("POST", "/publish", data)
    
    def publish_video(self, title: str, content: str, video: str) -> dict:
        """
        发布视频内容
        
        Args:
            title: 标题
            content: 正文内容
            video: 视频路径
        """
        data = {
            "title": title,
            "content": content,
            "video": video
        }
        return self._request("POST", "/publish_video", data)
    
    def list_feeds(self) -> dict:
        """获取推荐列表"""
        return self._request("GET", "/feeds/list")
    
    def search(self, keyword: str) -> dict:
        """
        搜索内容
        
        Args:
            keyword: 搜索关键词
        """
        return self._request("GET", f"/feeds/search?keyword={keyword}")
    
    def search_post(self, keyword: str) -> dict:
        """搜索内容 (POST)"""
        return self._request("POST", "/feeds/search", {"keyword": keyword})
    
    def get_feed_detail(self, feed_id: str, xsec_token: str) -> dict:
        """
        获取帖子详情
        
        Args:
            feed_id: 帖子 ID
            xsec_token: 安全令牌
        """
        return self._request("POST", "/feeds/detail", {
            "feed_id": feed_id,
            "xsec_token": xsec_token
        })
    
    def post_comment(self, feed_id: str, xsec_token: str, content: str) -> dict:
        """
        发表评论
        
        Args:
            feed_id: 帖子 ID
            xsec_token: 安全令牌
            content: 评论内容
        """
        return self._request("POST", "/feeds/comment", {
            "feed_id": feed_id,
            "xsec_token": xsec_token,
            "content": content
        })
    
    def reply_comment(self, feed_id: str, xsec_token: str, 
                      comment_id: str, content: str) -> dict:
        """
        回复评论
        
        Args:
            feed_id: 帖子 ID
            xsec_token: 安全令牌
            comment_id: 评论 ID
            content: 回复内容
        """
        return self._request("POST", "/feeds/comment/reply", {
            "feed_id": feed_id,
            "xsec_token": xsec_token,
            "comment_id": comment_id,
            "content": content
        })
    
    def get_user_profile(self, user_id: str, xsec_token: str) -> dict:
        """
        获取用户主页
        
        Args:
            user_id: 用户 ID
            xsec_token: 安全令牌
        """
        return self._request("POST", "/user/profile", {
            "user_id": user_id,
            "xsec_token": xsec_token
        })
    
    def get_my_profile(self) -> dict:
        """获取当前用户信息"""
        return self._request("GET", "/user/me")


def print_result(result: dict, title: str = "结果"):
    """打印结果"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"{'='*60}\n")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="小红书 API 工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  检查登录状态:
    python3 xiaohongshu-api.py check-login
  
  发布图文:
    python3 xiaohongshu-api.py publish "我的标题" "正文内容" "图片1.jpg,图片2.jpg"
  
  搜索内容:
    python3 xiaohongshu-api.py search "美食"
  
  获取推荐列表:
    python3 xiaohongshu-api.py feeds
  
  获取用户信息:
    python3 xiaohongshu-api.py me
        """
    )
    
    parser.add_argument(
        "--server", "-s",
        default="http://127.0.0.1:18060",
        help="xiaohongshu-mcp 服务器地址 (默认: http://127.0.0.1:18060)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # check-login
    subparsers.add_parser("check-login", help="检查登录状态")
    
    # qrcode
    subparsers.add_parser("qrcode", help="获取登录二维码")
    
    # delete-cookies
    subparsers.add_parser("delete-cookies", help="删除 cookies")
    
    # publish
    publish_parser = subparsers.add_parser("publish", help="发布图文内容")
    publish_parser.add_argument("title", help="帖子标题")
    publish_parser.add_argument("content", help="帖子正文")
    publish_parser.add_argument("images", help="图片路径 (逗号分隔)")
    publish_parser.add_argument("--video", "-v", help="视频路径 (可选)")
    
    # publish-video
    publish_video_parser = subparsers.add_parser("publish-video", help="发布视频内容")
    publish_video_parser.add_argument("title", help="视频标题")
    publish_video_parser.add_argument("content", help="视频描述")
    publish_video_parser.add_argument("video", help="视频文件路径")
    
    # feeds
    subparsers.add_parser("feeds", help="获取推荐列表")
    
    # search
    search_parser = subparsers.add_parser("search", help="搜索内容")
    search_parser.add_argument("keyword", help="搜索关键词")
    
    # detail
    detail_parser = subparsers.add_parser("detail", help="获取帖子详情")
    detail_parser.add_argument("feed_id", help="帖子 ID")
    detail_parser.add_argument("xsec_token", help="安全令牌")
    
    # comment
    comment_parser = subparsers.add_parser("comment", help="发表评论")
    comment_parser.add_argument("feed_id", help="帖子 ID")
    comment_parser.add_argument("xsec_token", help="安全令牌")
    comment_parser.add_argument("content", help="评论内容")
    
    # me
    subparsers.add_parser("me", help="获取当前用户信息")
    
    # version
    subparsers.add_parser("version", help="显示版本信息")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # 创建 API 客户端
    api = XiaoHongShuAPI(base_url=args.server)
    
    # 执行命令
    if args.command == "check-login":
        result = api.check_login()
        print_result(result, "登录状态")
        
    elif args.command == "qrcode":
        result = api.get_qrcode()
        print_result(result, "登录二维码")
        
    elif args.command == "delete-cookies":
        result = api.delete_cookies()
        print_result(result, "删除 cookies")
        
    elif args.command == "publish":
        images = args.images.split(",")
        result = api.publish(args.title, args.content, images, args.video)
        print_result(result, "发布图文")
        
    elif args.command == "publish-video":
        result = api.publish_video(args.title, args.content, args.video)
        print_result(result, "发布视频")
        
    elif args.command == "feeds":
        result = api.list_feeds()
        print_result(result, "推荐列表")
        
    elif args.command == "search":
        result = api.search(args.keyword)
        print_result(result, f"搜索结果: {args.keyword}")
        
    elif args.command == "detail":
        result = api.get_feed_detail(args.feed_id, args.xsec_token)
        print_result(result, "帖子详情")
        
    elif args.command == "comment":
        result = api.post_comment(args.feed_id, args.xsec_token, args.content)
        print_result(result, "发表评论")
        
    elif args.command == "me":
        result = api.get_my_profile()
        print_result(result, "当前用户")
        
    elif args.command == "version":
        print("\n小红书 API 工具 v1.0.0")
        print("作者: OpenClaw")
        print("依赖: xiaohongshu-mcp\n")
        
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
