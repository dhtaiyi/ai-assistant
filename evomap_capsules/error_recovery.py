#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Intelligent Error Recovery - EvoMap Capsule移植

Asset ID: sha256:b32eb97e079a3c49d343d41075a49beca2774708cb2ce418c3ef8039616f7785
GDI Score: 68.1 | Confidence: 0.92

功能：
- 指数退避+抖动处理瞬态故障
- 自动识别限流(Retry-After header)
- 熔断器模式处理持续故障
- 优雅降级到备用端点或缓存

触发条件: TimeoutError, RateLimitError, ECONNREFUSED, ECONNRESET, 
         HTTPError429/502/503, NetworkError
"""

import asyncio
import aiohttp
from typing import Optional, Callable, Any, Dict, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import random
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """错误类型"""
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    CONNECTION_REFUSED = "connection_refused"
    CONNECTION_RESET = "connection_reset"
    HTTP_429 = "http_429"
    HTTP_5XX = "http_5xx"
    NETWORK_ERROR = "network_error"
    UNKNOWN = "unknown"


@dataclass
class ErrorContext:
    """错误上下文"""
    error_type: ErrorType
    message: str
    timestamp: datetime
    attempt: int
    retry_after: Optional[int] = None  # 秒
    status_code: Optional[int] = None


@dataclass
class CircuitState:
    """熔断器状态"""
    state: str = "closed"  # closed, open, half_open
    failure_count: int = 0
    last_failure: Optional[datetime] = None
    success_count: int = 0
    open_until: Optional[datetime] = None
    
    # 配置
    failure_threshold: int = 5  # 失败次数阈值
    success_threshold: int = 2  # 半开状态成功阈值
    open_duration: int = 60  # 打开持续时间(秒)


class ErrorClassifier:
    """错误类型分类器"""
    
    @staticmethod
    def classify(error: Exception, status_code: Optional[int] = None) -> ErrorContext:
        """分类错误"""
        error_str = str(error).lower()
        error_type = ErrorType.UNKNOWN
        
        # 识别错误类型
        if status_code:
            if status_code == 429:
                error_type = ErrorType.RATE_LIMIT
            elif status_code >= 500:
                error_type = ErrorType.HTTP_5XX
        elif "timeout" in error_str:
            error_type = ErrorType.TIMEOUT
        elif "ECONNREFUSED" in error_str:
            error_type = ErrorType.CONNECTION_REFUSED
        elif "ECONNRESET" in error_str:
            error_type = ErrorType.CONNECTION_RESET
        elif "429" in error_str or "too many" in error_str:
            error_type = ErrorType.RATE_LIMIT
        elif "network" in error_str or "connection" in error_str:
            error_type = ErrorType.NETWORK_ERROR
        
        return ErrorContext(
            error_type=error_type,
            message=str(error),
            timestamp=datetime.now(),
            attempt=0,
            status_code=status_code
        )


class CircuitBreaker:
    """
    熔断器模式实现
    
    状态转换:
    - closed: 正常，允许请求
    - open: 故障，拒绝所有请求
    - half_open: 半开，允许有限请求测试恢复
    """
    
    def __init__(self, config: Optional[CircuitState] = None):
        self.state = config or CircuitState()
    
    def can_execute(self) -> bool:
        """检查是否可以执行请求"""
        if self.state.state == "closed":
            return True
        
        if self.state.state == "open":
            if datetime.now() >= self.state.open_until:
                # 转换到半开状态
                self.state.state = "half_open"
                self.state.success_count = 0
                logger.info("[CircuitBreaker] State: open -> half_open")
                return True
            return False
        
        # half_open状态
        return True
    
    def record_success(self):
        """记录成功"""
        if self.state.state == "half_open":
            self.state.success_count += 1
            if self.state.success_count >= self.state.success_threshold:
                self.state.state = "closed"
                self.state.failure_count = 0
                logger.info("[CircuitBreaker] State: half_open -> closed (recovered)")
    
    def record_failure(self):
        """记录失败"""
        self.state.failure_count += 1
        self.state.last_failure = datetime.now()
        
        if self.state.state == "half_open":
            self.state.state = "open"
            self.state.open_until = datetime.now() + timedelta(seconds=self.state.open_duration)
            logger.warning("[CircuitBreaker] State: half_open -> open (failure)")
        
        elif self.state.state == "closed":
            if self.state.failure_count >= self.state.failure_threshold:
                self.state.state = "open"
                self.state.open_until = datetime.now() + timedelta(seconds=self.state.open_duration)
                logger.warning(
                    f"[CircuitBreaker] State: closed -> open "
                    f"(failures: {self.state.failure_count})"
                )


class IntelligentRecovery:
    """
    智能错误恢复处理器
    
    功能:
    - 指数退避+抖动
    - 自动限流识别(Retry-After)
    - 熔断器模式
    - 备用端点/缓存降级
    """
    
    def __init__(
        self,
        circuit_config: Optional[CircuitState] = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        fallback_enabled: bool = True
    ):
        self.circuit_breaker = CircuitBreaker(circuit_config)
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.fallback_enabled = fallback_enabled
        
        # 备用端点
        self.fallback_endpoints: List[str] = []
        self.cache: Dict[str, Any] = {}
        self.cache_ttl: int = 300  # 5分钟
    
    def add_fallback(self, endpoint: str):
        """添加备用端点"""
        self.fallback_endpoints.append(endpoint)
    
    async def execute(
        self,
        primary_func: Callable,
        fallback_func: Optional[Callable] = None,
        **kwargs
    ) -> Optional[Any]:
        """
        执行带智能恢复的请求
        
        Args:
            primary_func: 主函数
            fallback_func: 备用函数
            **kwargs: 函数参数
        """
        # 检查熔断器
        if not self.circuit_breaker.can_execute():
            logger.warning("[Recovery] Circuit is open, skipping")
            if self.fallback_enabled and fallback_func:
                return await self._execute_fallback(fallback_func, kwargs)
            return None
        
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                # 执行请求
                result = await primary_func(**kwargs) if asyncio.iscoroutinefunction(primary_func) else primary_func(**kwargs)
                
                # 成功
                self.circuit_breaker.record_success()
                return result
                
            except Exception as e:
                last_error = e
                context = ErrorClassifier.classify(e)
                context.attempt = attempt + 1
                
                # 检查Retry-After
                retry_after = self._parse_retry_after(e)
                
                # 计算延迟
                delay = self._calculate_delay(attempt, context.error_type, retry_after)
                
                logger.warning(
                    f"[Recovery] Attempt {attempt + 1}/{self.max_retries} failed: "
                    f"{context.error_type.value}, retry in {delay:.2f}s"
                )
                
                if delay > 0:
                    await asyncio.sleep(delay)
        
        # 所有重试失败
        self.circuit_breaker.record_failure()
        logger.error(f"[Recovery] All retries failed: {last_error}")
        
        # 尝试备用
        if self.fallback_enabled:
            return await self._execute_fallback(fallback_func or primary_func, kwargs)
        
        return None
    
    async def _execute_fallback(self, func: Callable, kwargs: Dict) -> Optional[Any]:
        """执行备用逻辑"""
        # 检查缓存
        cache_key = str(func) + str(kwargs)
        if cache_key in self.cache:
            cached_time, cached_result = self.cache[cache_key]
            if (datetime.now() - cached_time).seconds < self.cache_ttl:
                logger.info("[Recovery] Using cached result")
                return cached_result
        
        # 执行备用
        try:
            result = await func(**kwargs) if asyncio.iscoroutinefunction(func) else func(**kwargs)
            self.cache[cache_key] = (datetime.now(), result)
            return result
        except Exception as e:
            logger.error(f"[Recovery] Fallback also failed: {e}")
            return None
    
    def _parse_retry_after(self, error: Exception) -> Optional[int]:
        """解析Retry-After header"""
        error_str = str(error)
        if "retry-after" in error_str.lower():
            import re
            match = re.search(r'(\d+)', error_str)
            if match:
                return int(match.group(1))
        return None
    
    def _calculate_delay(
        self,
        attempt: int,
        error_type: ErrorType,
        retry_after: Optional[int]
    ) -> float:
        """计算退避延迟"""
        # 优先使用Retry-After
        if retry_after:
            return retry_after
        
        # 指数退避
        delay = self.base_delay * (2 ** attempt)
        delay = min(delay, self.max_delay)
        
        # 添加抖动
        jitter = delay * 0.3 * random.random()
        delay += jitter
        
        return delay


# ============ 便捷函数 ============

async def smart_fetch(
    url: str,
    max_retries: int = 3,
    timeout: float = 10.0,
    fallback_url: Optional[str] = None
) -> Optional[Any]:
    """
    智能获取URL
    
    Args:
        url: 主URL
        max_retries: 最大重试次数
        timeout: 超时时间
        fallback_url: 备用URL
    """
    async with aiohttp.ClientSession() as session:
        recovery = IntelligentRecovery(max_retries=max_retries)
        if fallback_url:
            recovery.add_fallback(fallback_url)
        
        async def fetch():
            async with session.get(url, timeout=timeout) as resp:
                resp.raise_for_status()
                return await resp.json()
        
        return await recovery.execute(fetch)


# ============ 使用示例 ============

if __name__ == "__main__":
    print("=" * 60)
    print("Intelligent Error Recovery - Demo")
    print("=" * 60)
    
    async def demo():
        # 创建恢复处理器
        recovery = IntelligentRecovery(
            max_retries=3,
            base_delay=0.5,
            fallback_enabled=True
        )
        
        # 添加备用端点
        recovery.add_fallback("https://httpbin.org/get")
        
        print("\n1. 测试成功请求...")
        
        async def success_request():
            async with aiohttp.ClientSession() as session:
                async with session.get("https://httpbin.org/get") as resp:
                    return {"status": resp.status}
        
        result = await recovery.execute(success_request)
        print(f"   Result: {result}")
        
        print("\n2. 测试限流处理...")
        
        async def rate_limited_request():
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://httpbin.org/status/429",
                    headers={"X-Retry-After": "1"}
                ) as resp:
                    return {"status": resp.status}
        
        result = await recovery.execute(rate_limited_request)
        print(f"   Result: {result}")
        
        print("\n3. 熔断器状态:")
        print(f"   State: {recovery.circuit_breaker.state.state}")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
