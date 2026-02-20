#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kubernetes OOM Fix - EvoMap Capsule移植

Asset ID: sha256:7e7ad73ed072df6bfafa0b8f9a464da26f36b2127bb9c4d67a5c498551c9a0f4
GDI Score: 69.3 | Confidence: 0.99

功能：
- 修复Kubernetes pod OOMKilled问题
- 动态堆内存调整
- 使用MaxRAMPercentage
- 容器感知的内存监控
- 防止峰值时内存限制违规

触发条件: OOMKilled, memory_limit, vertical_scaling, JVM_heap, container_memory

注意: 这个Capsule主要针对JVM应用(Python不受直接影响，但内存监控思路可用)
"""

import os
import sys
import resource
import logging
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MemoryConfig:
    """内存配置"""
    max_heap_percent: float = 70.0  # 最大堆内存百分比
    min_heap_mb: int = 128  # 最小堆内存MB
    max_heap_mb: int = 1024  # 最大堆内存MB
    container_memory_limit: Optional[int] = None  # 容器内存限制(字节)
    safety_margin: float = 0.85  # 安全边距


class ContainerMemoryMonitor:
    """
    容器内存监控器
    
    功能:
    - 检测容器内存限制
    - 动态调整内存使用
    - 防止OOMKilled
    """
    
    def __init__(self, config: Optional[MemoryConfig] = None):
        self.config = config or MemoryConfig()
        self.peak_memory = 0
        self.current_memory = 0
        self.oom_warnings = []
    
    def get_container_limits(self) -> Dict[str, int]:
        """获取容器内存限制"""
        limits = {}
        
        # 从cgroup读取
        memory_limit_path = "/sys/fs/cgroup/memory/memory.limit_in_bytes"
        memory_usage_path = "/sys/fs/cgroup/memory/memory.usage_in_bytes"
        
        try:
            if os.path.exists(memory_limit_path):
                with open(memory_limit_path) as f:
                    limits["cgroup_limit"] = int(f.read().strip())
            
            if os.path.exists(memory_usage_path):
                with open(memory_usage_path) as f:
                    limits["cgroup_usage"] = int(f.read().strip())
        except Exception as e:
            logger.warning(f"Cannot read cgroup info: {e}")
        
        # 环境变量
        if "MEMORY_LIMIT" in os.environ:
            limits["env_limit"] = int(os.environ["MEMORY_LIMIT"])
        
        if "CONTAINER_MEMORY_LIMIT" in os.environ:
            limits["container_env"] = int(os.environ["CONTAINER_MEMORY_LIMIT"])
        
        return limits
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """获取当前内存使用"""
        usage = {}
        
        # Python进程内存
        usage["rss_mb"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
        usage["rss_bytes"] = usage["rss_mb"] * 1024 * 1024
        
        # 系统内存(Linux)
        try:
            with open("/proc/memoryinfo") as f:
                for line in f:
                    if "MemTotal" in line:
                        usage["system_total_kb"] = int(line.split()[1])
                        usage["system_total_mb"] = usage["system_total_kb"] / 1024
                    elif "MemAvailable" in line:
                        usage["system_available_kb"] = int(line.split()[1])
                        usage["system_available_mb"] = usage["system_available_kb"] / 1024
        except:
            pass
        
        self.current_memory = usage.get("rss_bytes", 0)
        self.peak_memory = max(self.peak_memory, self.current_memory)
        
        return usage
    
    def get_safe_heap_size(self) -> int:
        """
        计算安全的堆内存大小
        
        Returns:
            堆内存大小(字节)
        """
        limits = self.get_container_limits()
        usage = self.get_memory_usage()
        
        # 确定限制
        limit = limits.get("cgroup_limit", limits.get("env_limit", limits.get("container_env")))
        
        if not limit:
            # 没有限制，使用系统可用内存
            available = usage.get("system_available_mb", 4096) * 1024 * 1024
            limit = available
        
        # 应用安全边距
        safe_limit = int(limit * self.config.safety_margin)
        
        # 计算堆大小
        heap_percent = self.config.max_heap_percent
        heap_size = int(safe_limit * heap_percent / 100)
        
        # 应用min/max限制
        min_heap = self.config.min_heap_mb * 1024 * 1024
        max_heap = self.config.max_heap_mb * 1024 * 1024
        
        heap_size = max(min_heap, min(heap_size, max_heap))
        
        logger.info(
            f"[OOMFix] Container limit: {limit//1024//1024}MB, "
            f"Safe heap: {heap_size//1024//1024}MB"
        )
        
        return heap_size
    
    def check_oom_risk(self) -> Dict[str, Any]:
        """
        检查OOM风险
        
        Returns:
            风险评估结果
        """
        limits = self.get_container_limits()
        usage = self.get_memory_usage()
        
        risk = {
            "status": "safe",  # safe, warning, danger
            "current_mb": 0,
            "limit_mb": 0,
            "usage_percent": 0,
            "warnings": []
        }
        
        limit = limits.get("cgroup_limit", limits.get("env_limit"))
        
        if limit:
            risk["limit_mb"] = limit / 1024 / 1024
            risk["current_mb"] = usage.get("rss_mb", 0)
            risk["usage_percent"] = risk["current_mb"] / risk["limit_mb"] * 100
            
            if risk["usage_percent"] > 80:
                risk["status"] = "warning"
                risk["warnings"].append("Memory usage > 80%")
            
            if risk["usage_percent"] > 90:
                risk["status"] = "danger"
                risk["warnings"].append("Memory usage > 90% - OOM risk!")
        
        # 检查峰值
        if self.peak_memory > 0:
            peak_mb = self.peak_memory / 1024 / 1024
            risk["peak_mb"] = peak_mb
            if peak_mb > risk["limit_mb"] * 0.95:
                risk["warnings"].append(f"Peak {peak_mb:.0f}MB approaching limit {risk['limit_mb']:.0f}MB")
        
        return risk
    
    def should_gc_collect(self) -> bool:
        """判断是否应该执行GC"""
        risk = self.check_oom_risk()
        return risk["status"] in ["warning", "danger"]


class OOMKilledFixer:
    """
    OOMKilled修复器
    
    功能:
    - 动态内存配置
    - 自动扩缩容建议
    - 内存使用优化
    """
    
    def __init__(self):
        self.monitor = ContainerMemoryMonitor()
        self.recommendations = []
    
    def apply_dynamic_heap_config(self) -> Dict[str, Any]:
        """
        应用动态堆内存配置
        
        Returns:
            配置建议
        """
        heap_size = self.monitor.get_safe_heap_size()
        
        # 生成配置
        config = {
            "heap_size_bytes": heap_size,
            "heap_size_mb": heap_size / 1024 / 1024,
            "max_heap_percent": self.monitor.config.max_heap_percent,
            "safety_margin": self.monitor.config.safety_margin,
            "jvm_options": [
                f"-Xmx{heap_size // 1024 // 1024}m",
                f"-XX:MaxRAMPercentage={self.monitor.config.max_heap_percent}",
                "-XX:+UseContainerSupport",
                "-XX:InitialRAMPercentage=50.0",
            ],
            "environment": {
                "JAVA_TOOL_OPTIONS": f"-XX:MaxRAMPercentage={self.monitor.config.max_heap_percent}",
            }
        }
        
        logger.info(f"[OOMFix] Dynamic heap config: {config['heap_size_mb']:.0f}MB")
        
        return config
    
    def analyze_oom(self, pod_status: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析OOM原因
        
        Args:
            pod_status: Pod状态信息
            
        Returns:
            分析结果和建议
        """
        analysis = {
            "cause": "unknown",
            "probability": 0.0,
            "recommendations": [],
            "metrics": {}
        }
        
        # 分析原因
        if "OOMKilled" in pod_status.get("reason", ""):
            analysis["cause"] = "oom_killed"
            analysis["probability"] = 0.95
            analysis["recommendations"].append("Increase memory limit")
            analysis["recommendations"].append("Enable horizontal autoscaling")
            analysis["recommendations"].append("Optimize memory usage patterns")
        
        elif pod_status.get("restartCount", 0) > 0:
            analysis["cause"] = "frequent_restarts"
            analysis["probability"] = 0.7
            analysis["recommendations"].append("Check for memory leaks")
            analysis["recommendations"].append("Review heap settings")
        
        # 收集指标
        analysis["metrics"] = self.monitor.get_memory_usage()
        
        return analysis
    
    def get_scaling_recommendation(self) -> Dict[str, Any]:
        """
        获取扩缩容建议
        
        Returns:
            扩缩容建议
        """
        risk = self.monitor.check_oom_risk()
        
        recommendation = {
            "action": "maintain",  # scale_up, maintain, scale_down
            "current_replicas": 1,
            "suggested_replicas": 1,
            "reason": ""
        }
        
        if risk["status"] == "danger":
            recommendation["action"] = "scale_up"
            recommendation["suggested_replicas"] = 2
            recommendation["reason"] = "High memory usage risk"
        elif risk["status"] == "warning":
            recommendation["reason"] = "Monitor closely"
        
        return recommendation


# ============ 便捷函数 ============

monitor = ContainerMemoryMonitor()
fixer = OOMKilledFixer()


def get_safe_heap_size() -> int:
    """获取安全堆大小"""
    return monitor.get_safe_heap_size()


def check_oom_risk() -> Dict[str, Any]:
    """检查OOM风险"""
    return monitor.check_oom_risk()


def apply_memory_config() -> Dict[str, Any]:
    """应用内存配置"""
    return fixer.apply_dynamic_heap_config()


# ============ 使用示例 ============

if __name__ == "__main__":
    print("=" * 60)
    print("Kubernetes OOM Fix - Demo")
    print("=" * 60)
    
    print("\n1. 容器内存信息:")
    limits = monitor.get_container_limits()
    for key, value in limits.items():
        if isinstance(value, (int, float)):
            print(f"   {key}: {value/1024/1024:.0f} MB")
        else:
            print(f"   {key}: {value}")
    
    print("\n2. 当前内存使用:")
    usage = monitor.get_memory_usage()
    for key, value in usage.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.1f} MB")
        else:
            print(f"   {key}: {value}")
    
    print("\n3. OOM风险检查:")
    risk = check_oom_risk()
    print(f"   状态: {risk['status']}")
    print(f"   当前: {risk['current_mb']:.1f} MB")
    print(f"   限制: {risk['limit_mb']:.0f} MB")
    print(f"   使用率: {risk['usage_percent']:.1f}%")
    if risk.get("warnings"):
        for w in risk["warnings"]:
            print(f"   ⚠️ {w}")
    
    print("\n4. 动态堆配置建议:")
    config = apply_memory_config()
    print(f"   堆大小: {config['heap_size_mb']:.0f} MB")
    print("   JVM选项:")
    for opt in config["jvm_options"]:
        print(f"     {opt}")
    
    print("\n" + "=" * 60)
