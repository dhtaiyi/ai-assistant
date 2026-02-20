#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Universal HTTP Retry - EvoMap Capsule移植

Asset ID: sha256:6c8b2bef4652d5113cc802b6995a8e9f5da8b5b1ffe3d6bc639e2ca8ce27edec
GDI Score: 70.9 | Confidence: 0.96
Created: 2026-02-17

功能：
- HTTP请求的指数退避重试
- AbortController超时控制
- 全局连接池复用
- 处理瞬态网络故障、限流(429)、连接重置
- 提升API调用成功率约30%

触发条件: TimeoutError, ECONNRESET, ECONNREFUSED, 429TooManyRequests
"""

import asyncio
import aiohttp
from typing import Optional, Callable, Any
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HTTPRetryConfig:
    """HTTP重试配置"""
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,      # 基础延迟(秒)
        max_delay: float = 60.0,       # 最大延迟(秒)
        timeout: float = 30.0,          # 请求超时(秒)
        backoff_factor: float = 2.0,   # 退避因子
        jitter: bool = True,           # 添加随机抖动
        retry_on_status: tuple = (429, 500, 502, 503, 504),  # 重试状态码
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.timeout = timeout
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.retry_on_status = retry_on_status


class HTTPRetry:
    """HTTP请求自动重试处理器"""
    
    def __init__(self, config: Optional[HTTPRetryConfig] = None):
        self.config = config or HTTPRetryConfig()
        self._session: Optional[aiohttp.ClientSession] = None
    
    @property
    def session(self) -> aiohttp.ClientSession:
        """获取或创建全局连接池"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            connector = aiohttp.TCPConnector(
                limit=100,           # 全局连接池限制
                limit_per_host=10,   # 每主机连接限制
                ttl_dns_cache=300,   # DNS缓存时间
                keepalive_timeout=30, # 连接保活时间
            )
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector
            )
        return self._session
    
    async def close(self):
        """关闭会话"""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
    
    def _calculate_delay(self, attempt: int) -> float:
        """计算指数退避延迟"""
        delay = self.config.base_delay * (self.config.backoff_factor ** attempt)
        delay = min(delay, self.config.max_delay)
        
        if self.config.jitter:
            import random
            delay = delay * (0.5 + random.random())  # 0.5-1.5倍抖动
        
        return delay
    
    async def fetch(
        self,
        url: str,
        method: str = "GET",
        **kwargs
    ) -> Optional[aiohttp.ClientResponse]:
        """
        带重试的HTTP请求
        
        Args:
            url: 请求URL
            method: HTTP方法
            **kwargs: 其他aiohttp请求参数
            
        Returns:
            Response对象，失败返回None
        """
        last_error = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                # 使用AbortController超时控制
                async with asyncio.timeout(self.config.timeout):
                    resp = await self.session.request(
                        method, url, **kwargs
                    )
                
            # 检查是否需要重试
                if resp and resp.status in self.config.retry_on_status:
                    if attempt < self.config.max_retries:
                        delay = self._calculate_delay(attempt)
                        logger.warning(
                            f"[HTTPRetry] Status {resp.status}, "
                            f"retry in {delay:.2f}s (attempt {attempt + 1})"
                        )
                        await resp.close()
                        await asyncio.sleep(delay)
                        continue
                
                return resp
                
            except asyncio.TimeoutError as e:
                last_error = e
                logger.warning(f"[HTTPRetry] TimeoutError (attempt {attempt + 1})")
                
            except aiohttp.ClientError as e:
                error_type = type(e).__name__
                error_str = str(e)
                
                # 检查是否是可重试的错误
                should_retry = any(x in error_str for x in [
                    "ECONNRESET", "ECONNREFUSED", "Connection error"
                ])
                
                if should_retry and attempt < self.config.max_retries:
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        f"[HTTPRetry] {error_type}: {error_str[:50]}..., "
                        f"retry in {delay:.2f}s"
                    )
                    await asyncio.sleep(delay)
                else:
                    last_error = e
                    logger.error(f"[HTTPRetry] {error_type}: {error_str}")
            
            except Exception as e:
                last_error = e
                logger.error(f"[HTTPRetry] Unexpected error: {e}")
        
        logger.error(f"[HTTPRetry] All retries failed, last error: {last_error}")
        return None


# ============ 便捷函数 ============

async def retry_get(url: str, **kwargs) -> Optional[str]:
    """带重试的GET请求，返回文本"""
    client = HTTPRetry()
    try:
        resp = await client.fetch(url, **kwargs)
        if resp:
            return await resp.text()
        return None
    finally:
        await client.close()


async def retry_get_json(url: str, **kwargs) -> Optional[dict]:
    """带重试的GET请求，返回JSON"""
    client = HTTPRetry()
    try:
        resp = await client.fetch(url, **kwargs)
        if resp:
            return await resp.json()
        return None
    finally:
        await client.close()


async def retry_post(url: str, data: Any = None, **kwargs) -> Optional[str]:
    """带重试的POST请求，返回文本"""
    client = HTTPRetry()
    try:
        resp = await client.fetch(url, method="POST", data=data, **kwargs)
        if resp:
            return await resp.text()
        return None
    finally:
        await client.close()


# ============ 使用示例 ============

if __name__ == "__main__":
    async def demo():
        """演示用法"""
        print("=" * 60)
        print("Universal HTTP Retry - Demo")
        print("=" * 60)
        
        # 创建客户端
        client = HTTPRetry(HTTPRetryConfig(
            max_retries=3,
            base_delay=0.5,
            timeout=10.0
        ))
        
        try:
            # 示例1: 成功请求
            print("\n1. 测试成功请求...")
            resp = await client.fetch("https://httpbin.org/get")
            if resp:
                print(f"   Status: {resp.status}")
                await resp.close()
            
            # 示例3: JSON请求
            print("\n3. 测试JSON API...")
            resp = await client.fetch("https://httpbin.org/json")
            if resp and resp.status == 200:
                data = await resp.json()
                print(f"   Keys: {list(data.keys())}")
            
        finally:
            await client.close()
        
        print("\n" + "=" * 60)
    
    asyncio.run(demo())
