#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metric Anomaly Detection - EvoMap Capsule移植

Asset ID: sha256:6b8abb2cfe16c1a774c1c7c12da7ed13057fd319f3c04b1abd1ec763abd92f9
GDI Score: 68.9 | Confidence: 0.95

功能：
- 基于中位数的3倍阈值异常检测
- 自动标注异常值与中位数的比值
- 处理边界情况：样本少于3个跳过、中位数为0时跳过
- 生产环境验证（社交媒体指标：浏览、点赞、转发、收藏）

触发条件: metric_outlier, engagement_spike, traffic_anomaly, data_skew
"""

import statistics
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class AnomalyLevel(Enum):
    """异常级别"""
    NORMAL = "normal"
    LOW = "low"      # 1-2倍阈值
    MEDIUM = "medium"  # 2-3倍阈值
    HIGH = "high"    # 3倍以上


@dataclass
class AnomalyResult:
    """异常检测结果"""
    value: float
    median: float
    threshold: float
    ratio: float  # value / median
    level: AnomalyLevel
    is_anomaly: bool
    message: str


class MetricAnomalyDetector:
    """
    基于中位数的3倍阈值异常检测器
    
    使用方法:
        detector = MetricAnomalyDetector(threshold=3.0)
        result = detector.detect([100, 102, 98, 101, 500])
    """
    
    def __init__(
        self,
        threshold: float = 3.0,
        min_samples: int = 3,
        zero_handling: str = "skip"  # "skip", "min", "ignore"
    ):
        """
        Args:
            threshold: 阈值倍数 (默认3倍)
            min_samples: 最小样本数
            zero_handling: 中位数为0时的处理方式
                - "skip": 跳过检测
                - "min": 使用最小非零值
                - "ignore": 不标记异常
        """
        self.threshold = threshold
        self.min_samples = min_samples
        self.zero_handling = zero_handling
    
    def detect(self, values: List[float]) -> List[AnomalyResult]:
        """
        检测异常值
        
        Args:
            values: 数值列表
            
        Returns:
            每个值的异常检测结果列表
        """
        if len(values) < self.min_samples:
            return []
        
        # 计算中位数
        median = statistics.median(values)
        
        # 处理中位数为0的情况
        if median == 0:
            if self.zero_handling == "skip":
                return []  # 跳过整个检测
            elif self.zero_handling == "min":
                median = min([v for v in values if v > 0]) if any(v > 0 for v in values) else 1.0
            else:  # ignore
                # 不标记任何异常
                return [
                    AnomalyResult(
                        value=v,
                        median=0,
                        threshold=self.threshold,
                        ratio=0,
                        level=AnomalyLevel.NORMAL,
                        is_anomaly=False,
                        message="Median is zero, ignoring"
                    )
                    for v in values
                ]
        
        threshold_value = median * self.threshold
        results = []
        
        for v in values:
            ratio = v / median if median != 0 else 0
            is_anomaly = v > threshold_value
            
            # 确定异常级别
            if ratio <= 1.5:
                level = AnomalyLevel.NORMAL
            elif ratio <= 2.0:
                level = AnomalyLevel.LOW
            elif ratio <= 3.0:
                level = AnomalyLevel.MEDIUM
            else:
                level = AnomalyLevel.HIGH
            
            results.append(AnomalyResult(
                value=v,
                median=median,
                threshold=threshold_value,
                ratio=ratio,
                level=level,
                is_anomaly=is_anomaly,
                message=self._make_message(v, median, threshold_value, ratio, is_anomaly)
            ))
        
        return results
    
    def _make_message(
        self,
        value: float,
        median: float,
        threshold: float,
        ratio: float,
        is_anomaly: bool
    ) -> str:
        """生成消息"""
        if is_anomaly:
            return f"⚠️ 异常: {value:.2f} > 阈值 {threshold:.2f} ({ratio:.1f}倍中位数)"
        return f"✅ 正常: {value:.2f}"
    
    def filter_anomalies(
        self,
        values: List[float],
        min_level: AnomalyLevel = AnomalyLevel.LOW
    ) -> List[Tuple[int, AnomalyResult]]:
        """
        过滤出异常值
        
        Returns:
            (索引, 结果) 列表
        """
        results = self.detect(values)
        filtered = []
        
        for i, r in enumerate(results):
            if r.is_anomaly and self._level_value(r.level) >= self._level_value(min_level):
                filtered.append((i, r))
        
        return filtered
    
    def _level_value(self, level: AnomalyLevel) -> int:
        """级别数值化"""
        values = {
            AnomalyLevel.NORMAL: 0,
            AnomalyLevel.LOW: 1,
            AnomalyLevel.MEDIUM: 2,
            AnomalyLevel.HIGH: 3
        }
        return values.get(level, 0)
    
    def get_stats(self, values: List[float]) -> Dict[str, Any]:
        """获取统计信息"""
        if len(values) < self.min_samples:
            return {"error": "Insufficient samples"}
        
        results = self.detect(values)
        anomalies = [r for r in results if r.is_anomaly]
        
        return {
            "count": len(values),
            "median": statistics.median(values),
            "mean": statistics.mean(values),
            "threshold": self.threshold,
            "anomaly_count": len(anomalies),
            "anomaly_ratio": len(anomalies) / len(values) if values else 0,
            "anomaly_indices": [i for i, r in enumerate(results) if r.is_anomaly]
        }


# ============ 便捷函数 ============

def detect_anomalies(values: List[float], threshold: float = 3.0) -> List[AnomalyResult]:
    """便捷异常检测函数"""
    detector = MetricAnomalyDetector(threshold=threshold)
    return detector.detect(values)


def find_anomalies(
    values: List[float],
    threshold: float = 3.0,
    min_level: str = "LOW"
) -> List[Tuple[int, AnomalyResult]]:
    """便捷查找异常函数"""
    detector = MetricAnomalyDetector(threshold=threshold)
    level_map = {"LOW": AnomalyLevel.LOW, "MEDIUM": AnomalyLevel.MEDIUM, "HIGH": AnomalyLevel.HIGH}
    return detector.filter_anomalies(values, level_map.get(min_level, AnomalyLevel.LOW))


# ============ 使用示例 ============

if __name__ == "__main__":
    print("=" * 60)
    print("Metric Anomaly Detection - Demo")
    print("=" * 60)
    
    # 示例数据
    metrics = [100, 102, 98, 101, 500, 97, 103, 95, 200, 101]
    
    print(f"\n输入数据: {metrics}")
    print(f"中位数: {statistics.median(metrics):.2f}")
    print(f"3倍阈值: {statistics.median(metrics) * 3:.2f}")
    
    detector = MetricAnomalyDetector(threshold=3.0)
    results = detector.detect(metrics)
    
    print("\n检测结果:")
    for i, r in enumerate(results):
        flag = "⚠️" if r.is_anomaly else "✅"
        print(f"  {flag} [{i:2d}] {r.value:8.2f} | 中位数: {r.median:.2f} | 倍数: {r.ratio:.2f}x | {r.message}")
    
    # 统计信息
    stats = detector.get_stats(metrics)
    print(f"\n统计: {stats}")
    
    print("\n" + "=" * 60)
