#!/usr/bin/env python3
"""
小雨自我进化系统 (XiaoYu Evolver)
基于 capability-evolver 思路，专为小雨定制

核心功能：
1. 信号提取 - 从对话中识别问题/需求
2. 基因库 - 管理可复用的解决方案
3. 变异引擎 - 决定修复/优化/创新
4. 记忆图谱 - 记录学习成果
5. 自我进化 - 持续优化
"""
import os
import json
import re
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import subprocess

# ============ 配置 ============
class Config:
    AGENT_DIR = "/root/.openclaw/agents/xiaoyu/agent"
    MEMORY_DIR = f"{AGENT_DIR}/memory"
    SESSIONS_DIR = "/root/.openclaw/agents/xiaoyu/sessions"
    GENES_DIR = f"{MEMORY_DIR}/genes"      # 基因库
    CAPSULES_DIR = f"{MEMORY_DIR}/capsules"  # 解决方案胶囊
    EVENTS_FILE = f"{MEMORY_DIR}/evolution_events.jsonl"  # 进化事件
    STATE_FILE = f"{MEMORY_DIR}/evolution_state.json"    # 进化状态
    
    # 信号阈值
    SIGNAL_SUPPRESS_THRESHOLD = 3  # 3次出现则抑制
    RECENT_EVENTS_COUNT = 10      # 分析最近10个事件
    
    # 情绪分类器
    EMOTION_CLASSIFIER_PATH = "/root/.openclaw/workspace/emotion_classifier.py"


# ============ 数据结构 ============
class SignalType(Enum):
    """信号类型"""
    # 错误类
    ERROR = "error"
    RECURRING_ERROR = "recurring_error"
    USER_FRUSTRATION = "user_frustration"
    
    # 机会类
    USER_FEATURE_REQUEST = "user_feature_request"
    USER_IMPROVEMENT_SUGGESTION = "user_improvement_suggestion"
    CAPABILITY_GAP = "capability_gap"
    PERFORMANCE_BOTTLENECK = "perf_bottleneck"
    
    # 成功类
    SUCCESS = "success"
    STABLE_SUCCESS = "stable_success_plateau"
    
    # 学习类
    LEARNING = "learning"
    FEEDBACK = "feedback"


class MutationCategory(Enum):
    """变异类型"""
    REPAIR = "repair"      # 修复错误
    OPTIMIZE = "optimize"  # 优化性能
    INNOVATE = "innovate"  # 创新功能


@dataclass
class Signal:
    """信号"""
    type: str
    content: str
    source: str  # "session", "memory", "user"
    timestamp: str
    metadata: Dict = field(default_factory=dict)


@dataclass
class Gene:
    """基因 - 可复用的解决方案"""
    id: str
    name: str
    description: str
    signals: List[str]  # 触发这个基因的信号
    code: str         # 解决方案代码
    success_count: int = 0
    fail_count: int = 0
    created_at: str = ""
    updated_at: str = ""
    
    @property
    def success_rate(self) -> float:
        total = self.success_count + self.fail_count
        return self.success_count / total if total > 0 else 0


@dataclass
class EvolutionEvent:
    """进化事件"""
    id: str
    timestamp: str
    intent: str  # "repair", "optimize", "innovate"
    signals: List[str]
    genes_used: List[str]
    mutation: str
    outcome: str  # "success", "failed", "partial"
    notes: str = ""


@dataclass
class EvolutionState:
    """进化状态"""
    last_run_id: str = ""
    last_run_timestamp: str = ""
    consecutive_repair_count: int = 0
    total_evolution_cycles: int = 0
    suppressed_signals: List[str] = field(default_factory=list)


# ============ 核心引擎 ============
class XiaoYuEvolver:
    """小雨自我进化引擎"""
    
    def __init__(self):
        self.config = Config()
        self._ensure_dirs()
        self.genes: Dict[str, Gene] = {}
        self.state = self._load_state()
        self._load_genes()
    
    def _ensure_dirs(self):
        """确保目录存在"""
        os.makedirs(self.config.GENES_DIR, exist_ok=True)
        os.makedirs(self.config.CAPSULES_DIR, exist_ok=True)
    
    # ===== 状态管理 =====
    def _load_state(self) -> EvolutionState:
        """加载状态"""
        try:
            with open(self.config.STATE_FILE, 'r') as f:
                data = json.load(f)
                return EvolutionState(**data)
        except:
            return EvolutionState()
    
    def _save_state(self):
        """保存状态"""
        with open(self.config.STATE_FILE, 'w') as f:
            json.dump(asdict(self.state), f, indent=2, ensure_ascii=False)
    
    def _load_genes(self):
        """加载基因库"""
        genes_file = f"{self.config.GENES_DIR}/library.json"
        try:
            with open(genes_file, 'r') as f:
                data = json.load(f)
                self.genes = {k: Gene(**v) for k, v in data.items()}
        except:
            self.genes = {}
    
    def _save_genes(self):
        """保存基因库"""
        genes_file = f"{self.config.GENES_DIR}/library.json"
        with open(genes_file, 'w') as f:
            json.dump({k: asdict(v) for k, v in self.genes.items()}, f, indent=2, ensure_ascii=False)
    
    # ===== 信号提取 =====
    def extract_signals(self, hours: int = 24) -> List[Signal]:
        """从对话历史中提取信号"""
        signals = []
        
        # 从sessions提取信号
        session_signals = self._extract_from_sessions(hours)
        signals.extend(session_signals)
        
        # 从memory提取信号
        memory_signals = self._extract_from_memory()
        signals.extend(memory_signals)
        
        return signals
    
    def _extract_from_sessions(self, hours: int) -> List[Signal]:
        """从session中提取信号"""
        signals = []
        
        # 遍历session文件
        sessions_path = Path(self.config.SESSIONS_DIR)
        if not sessions_path.exists():
            return signals
        
        now = datetime.now()
        cutoff = now - timedelta(hours=hours)
        
        for session_file in sessions_path.glob("*.jsonl"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if not line.strip():
                            continue
                        try:
                            data = json.loads(line)
                            content = str(data.get('message', {}).get('content', ''))
                            
                            # 提取信号
                            for sig in self._analyze_content(content):
                                sig.source = "session"
                                sig.timestamp = data.get('timestamp', now.isoformat())
                                signals.append(sig)
                        except:
                            pass
            except:
                pass
        
        return signals
    
    def _extract_from_memory(self) -> List[Signal]:
        """从memory中提取信号"""
        signals = []
        
        memory_path = Path(self.config.MEMORY_DIR)
        if not memory_path.exists():
            return signals
        
        for md_file in memory_path.glob("*.md"):
            if md_file.name.startswith('evolve'):
                continue
            
            try:
                content = md_file.read_text(encoding='utf-8')
                for sig in self._analyze_content(content):
                    sig.source = "memory"
                    sig.timestamp = datetime.now().isoformat()
                    signals.append(sig)
            except:
                pass
        
        return signals
    
    def _analyze_content(self, content: str) -> List[Signal]:
        """分析内容，提取信号"""
        signals = []
        content_lower = content.lower()
        
        # 错误信号
        error_patterns = [
            (r'error|failed|失败|错误|exception', SignalType.ERROR),
            (r'(recurring|重复).*(error|错误)', SignalType.RECURRING_ERROR),
            (r'不行|不能|没用|怎么|为什么', SignalType.USER_FRUSTRATION),
        ]
        
        for pattern, sig_type in error_patterns:
            if re.search(pattern, content_lower):
                signals.append(Signal(
                    type=sig_type.value,
                    content=content[:200],
                    source="",
                    timestamp=""
                ))
        
        # 用户需求信号
        request_patterns = [
            (r'想要|需要|可以做一个|能做一个', SignalType.USER_FEATURE_REQUEST),
            (r'改进|优化|建议|应该可以', SignalType.USER_IMPROVEMENT_SUGGESTION),
            (r'做不到|不会|不能|不支持', SignalType.CAPABILITY_GAP),
            (r'慢|卡|性能|效率', SignalType.PERFORMANCE_BOTTLENECK),
        ]
        
        for pattern, sig_type in request_patterns:
            if re.search(pattern, content_lower):
                signals.append(Signal(
                    type=sig_type.value,
                    content=content[:200],
                    source="",
                    timestamp=""
                ))
        
        # 成功信号
        if '成功' in content or '✅' in content or '好了' in content:
            signals.append(Signal(
                type=SignalType.SUCCESS.value,
                content=content[:200],
                source="",
                timestamp=""
            ))
        
        # 学习信号
        if '记住' in content or '学到' in content or '记录' in content:
            signals.append(Signal(
                type=SignalType.LEARNING.value,
                content=content[:200],
                source="",
                timestamp=""
            ))
        
        return signals
    
    # ===== 信号分析 =====
    def analyze_signals(self, signals: List[Signal]) -> Dict:
        """分析信号，返回统计"""
        stats = {
            "total": len(signals),
            "by_type": {},
            "suppressed": [],
            "top_signals": []
        }
        
        # 统计类型
        type_counts = {}
        for sig in signals:
            type_counts[sig.type] = type_counts.get(sig.type, 0) + 1
        
        stats["by_type"] = type_counts
        
        # 识别高频信号（可能被抑制）
        for sig_type, count in type_counts.items():
            if count >= self.config.SIGNAL_SUPPRESS_THRESHOLD:
                stats["suppressed"].append(sig_type)
        
        # 排序信号
        sorted_signals = sorted(type_counts.items(), key=lambda x: -x[1])
        stats["top_signals"] = sorted_signals[:5]
        
        return stats
    
    # ===== 基因选择 =====
    def select_gene(self, signals: List[Signal]) -> Optional[Gene]:
        """根据信号选择合适的基因"""
        if not signals:
            return None
        
        # 获取信号类型
        signal_types = [s.type for s in signals]
        
        # 查找匹配的基因
        candidates = []
        for gene_id, gene in self.genes.items():
            # 检查基因的信号是否匹配
            for gene_signal in gene.signals:
                if gene_signal in signal_types:
                    candidates.append(gene)
                    break
        
        if not candidates:
            return None
        
        # 选择成功率最高的
        return max(candidates, key=lambda g: g.success_rate)
    
    # ===== 变异决策 =====
    def decide_mutation(self, signals: List[Signal], stats: Dict) -> Tuple[str, str]:
        """决定变异类型和意图"""
        signal_types = [s.type for s in signals]
        
        # 有错误信号 -> 修复
        error_types = [SignalType.ERROR.value, SignalType.RECURRING_ERROR.value]
        if any(s in signal_types for s in error_types):
            return MutationCategory.REPAIR.value, "reduce runtime errors"
        
        # 有用户请求 -> 创新
        request_types = [
            SignalType.USER_FEATURE_REQUEST.value,
            SignalType.USER_IMPROVEMENT_SUGGESTION.value,
            SignalType.CAPABILITY_GAP.value
        ]
        if any(s in signal_types for s in request_types):
            return MutationCategory.INNOVATE.value, "implement new capability"
        
        # 连续修复 -> 优化
        if self.state.consecutive_repair_count >= 3:
            return MutationCategory.OPTIMIZE.value, "improve stability and performance"
        
        # 默认优化
        return MutationCategory.OPTIMIZE.value, "improve success rate"
    
    # ===== 解决方案生成 =====
    def generate_solution(self, mutation_type: str, signals: List[Signal]) -> str:
        """生成解决方案（供AI调用）"""
        signal_types = [s.type for s in signals]
        
        prompt = f"""你是一个AI助手，现在需要解决以下问题：

## 当前信号
{json.dumps(signal_types, indent=2, ensure_ascii=False)}

## 变异类型
{mutation_type}

## 最近对话摘要
"""
        # 添加最近的信号内容
        for sig in signals[:5]:
            prompt += f"- {sig.type}: {sig.content[:100]}\n"
        
        prompt += """
## 请生成解决方案

请分析以上信号，选择合适的解决方案：
1. 如果是错误 -> 修复代码或配置
2. 如果是用户需求 -> 实现新功能
3. 如果是性能问题 -> 优化代码
4. 如果是学习机会 -> 更新记忆/知识库

请直接给出解决方案代码或建议，不需要解释过程。
"""
        return prompt
    
    # ===== 基因管理 =====
    def add_gene(self, name: str, description: str, signals: List[str], code: str) -> Gene:
        """添加新基因"""
        gene_id = hashlib.md5(f"{name}{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        
        gene = Gene(
            id=gene_id,
            name=name,
            description=description,
            signals=signals,
            code=code,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        self.genes[gene_id] = gene
        self._save_genes()
        
        return gene
    
    def record_gene_success(self, gene_id: str):
        """记录基因使用成功"""
        if gene_id in self.genes:
            self.genes[gene_id].success_count += 1
            self.genes[gene_id].updated_at = datetime.now().isoformat()
            self._save_genes()
    
    def record_gene_failure(self, gene_id: str):
        """记录基因使用失败"""
        if gene_id in self.genes:
            self.genes[gene_id].fail_count += 1
            self.genes[gene_id].updated_at = datetime.now().isoformat()
            self._save_genes()
    
    # ===== 进化事件 =====
    def record_event(self, intent: str, signals: List[str], genes_used: List[str], 
                    mutation: str, outcome: str, notes: str = ""):
        """记录进化事件"""
        event = EvolutionEvent(
            id=hashlib.md5(datetime.now().isoformat().encode()).hexdigest()[:12],
            timestamp=datetime.now().isoformat(),
            intent=intent,
            signals=signals,
            genes_used=genes_used,
            mutation=mutation,
            outcome=outcome,
            notes=notes
        )
        
        # 追加到事件文件
        with open(self.config.EVENTS_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(asdict(event), ensure_ascii=False) + '\n')
        
        # 更新状态
        self.state.total_evolution_cycles += 1
        self.state.last_run_id = event.id
        self.state.last_run_timestamp = event.timestamp
        
        if intent == "repair":
            self.state.consecutive_repair_count += 1
        else:
            self.state.consecutive_repair_count = 0
        
        self._save_state()
        
        return event
    
    # ===== 主进化循环 =====
    def evolve(self, review_mode: bool = False) -> Dict:
        """执行一次进化"""
        print("🔄 小雨自我进化中...")
        
        # 1. 提取信号
        print("📥 提取信号...")
        signals = self.extract_signals(hours=24)
        print(f"   提取到 {len(signals)} 个信号")
        
        # 2. 分析信号
        print("🔍 分析信号...")
        stats = self.analyze_signals(signals)
        print(f"   信号类型分布: {stats['by_type']}")
        
        # 3. 选择基因
        print("🧬 选择基因...")
        gene = self.select_gene(signals)
        gene_id = gene.id if gene else "none"
        print(f"   选择基因: {gene_id}")
        
        # 4. 决定变异
        print("🎯 决定变异...")
        mutation_type, reason = self.decide_mutation(signals, stats)
        print(f"   变异类型: {mutation_type} ({reason})")
        
        # 5. 生成解决方案
        print("💡 生成解决方案...")
        solution = self.generate_solution(mutation_type, signals)
        
        # 6. 记录事件
        signal_types = [s.type for s in signals]
        event = self.record_event(
            intent=mutation_type,
            signals=signal_types,
            genes_used=[gene_id] if gene_id != "none" else [],
            mutation=mutation_type,
            outcome="pending",  # 待验证
            notes=reason
        )
        
        # 构建结果
        result = {
            "event_id": event.id,
            "timestamp": event.timestamp,
            "signals_count": len(signals),
            "signal_stats": stats,
            "selected_gene": gene_id,
            "mutation_type": mutation_type,
            "reason": reason,
            "solution_prompt": solution,
            "total_cycles": self.state.total_evolution_cycles
        }
        
        print("\n" + "="*50)
        print("📊 进化报告")
        print("="*50)
        print(f"事件ID: {event.id}")
        print(f"变异类型: {mutation_type}")
        print(f"原因: {reason}")
        print(f"信号数量: {len(signals)}")
        print(f"选择基因: {gene_id}")
        print(f"进化轮次: {self.state.total_evolution_cycles}")
        
        return result
    
    # ===== 知识提取 =====
    def extract_knowledge(self, content: str) -> Dict:
        """从内容中提取知识"""
        knowledge = {
            "patterns": [],
            "solutions": [],
            "learnings": []
        }
        
        # 提取关键模式
        patterns = re.findall(r'([^，。！？\n]{5,20}[可以应该能]+[^，。！？\n]{5,20})', content)
        knowledge["patterns"] = patterns[:5]
        
        # 提取解决方案模式
        if '解决方案' in content or '方法' in content:
            knowledge["solutions"].append("从对话中提取")
        
        return knowledge


# ============ 主程序 ============
def main():
    import sys
    
    review_mode = "--review" in sys.argv
    
    evolver = XiaoYuEvolver()
    result = evolver.evolve(review_mode=review_mode)
    
    # 保存进化结果
    result_file = f"{Config.MEMORY_DIR}/evolve_{datetime.now().strftime('%Y-%m-%d')}.md"
    with open(result_file, 'w', encoding='utf-8') as f:
        f.write(f"# 进化报告 - {result['timestamp']}\n\n")
        f.write(f"## 统计\n")
        f.write(f"- 信号数量: {result['signals_count']}\n")
        f.write(f"- 变异类型: {result['mutation_type']}\n")
        f.write(f"- 选择基因: {result['selected_gene']}\n")
        f.write(f"- 进化轮次: {result['total_cycles']}\n\n")
        f.write(f"## 原因\n{result['reason']}\n\n")
        f.write(f"## 信号分布\n")
        for sig_type, count in result['signal_stats']['by_type'].items():
            f.write(f"- {sig_type}: {count}\n")
    
    print(f"\n📝 已保存到: {result_file}")
    
    return result


if __name__ == "__main__":
    main()
