#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EvoMap Top Capsules - 代码库

来源: evomap.ai (通过代理访问)
获取时间: 2026-02-20

包含6个高质量Capsules:
1. http_retry      - HTTP重试机制
2. k8s_oom_fix     - K8s内存优化
3. anomaly_detection - 异常数据检测
4. self_debug      - AI自检调试
5. error_recovery  - 智能错误恢复
6. swarm_task     - 集群任务处理

使用示例:
    from evomap_capsules import http_retry, anomaly_detection
    
    # HTTP重试
    from evomap_capsules.http_retry import HTTPRetry
    client = HTTPRetry()
    resp = await client.fetch(url)
    
    # 异常检测
    from evomap_capsules.anomaly_detection import MetricAnomalyDetector
    detector = MetricAnomalyDetector(threshold=3.0)
    results = detector.detect([1, 2, 3, 100])
"""

from .http_retry import HTTPRetry, HTTPRetryConfig, retry_get, retry_get_json, retry_post
from .anomaly_detection import MetricAnomalyDetector, AnomalyResult, detect_anomalies, find_anomalies
from .error_recovery import IntelligentRecovery, CircuitBreaker, CircuitState, smart_fetch
from .self_debug import SelfDebugFramework, self_debug, debug_catch, get_debug_stats
from .swarm_task import SwarmTaskProcessor, TaskType, process_swarm_task
from .k8s_oom_fix import ContainerMemoryMonitor, OOMKilledFixer, monitor, check_oom_risk, apply_memory_config

__all__ = [
    # HTTP重试
    "HTTPRetry",
    "HTTPRetryConfig", 
    "retry_get",
    "retry_get_json",
    "retry_post",
    
    # 异常检测
    "MetricAnomalyDetector",
    "AnomalyResult",
    "detect_anomalies",
    "find_anomalies",
    
    # 错误恢复
    "IntelligentRecovery",
    "CircuitBreaker",
    "CircuitState",
    "smart_fetch",
    
    # 自检调试
    "SelfDebugFramework",
    "self_debug",
    "debug_catch",
    "get_debug_stats",
    
    # 集群任务
    "SwarmTaskProcessor",
    "TaskType",
    "process_swarm_task",
    
    # K8s内存
    "ContainerMemoryMonitor",
    "OOMKilledFixer",
    "monitor",
    "check_oom_risk",
    "apply_memory_config",
]

__version__ = "1.0.0"
__author__ = "EvoMap Community"

print("✅ EvoMap Top Capsules loaded")
print("   Available modules: http_retry, anomaly_detection, error_recovery, self_debug, swarm_task, k8s_oom_fix")
