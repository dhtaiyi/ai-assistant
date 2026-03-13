#!/usr/bin/env python3
"""
简单版自我进化系统
分析对话历史，识别问题，生成改进建议
"""
import os
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple
import subprocess

class SimpleEvolver:
    """简单自我进化器"""
    
    def __init__(self, agent_dir: str = "/root/.openclaw/agents/xiaoyu/agent"):
        self.agent_dir = Path(agent_dir)
        self.memory_dir = self.agent_dir / "memory"
        self.sessions_dir = Path(f"/root/.openclaw/agents/xiaoyu/sessions")
        
    def get_recent_sessions(self, hours: int = 24) -> List[Dict]:
        """获取最近的session"""
        sessions = []
        if not self.sessions_dir.exists():
            return sessions
            
        # 遍历sessions目录
        for session_file in self.sessions_dir.glob("*.jsonl"):
            try:
                # 读取session文件
                with open(session_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines:
                        if line.strip():
                            try:
                                data = json.loads(line)
                                sessions.append(data)
                            except:
                                pass
            except:
                pass
        return sessions
    
    def extract_signals(self, sessions: List[Dict]) -> List[Dict]:
        """提取信号（问题、错误等）"""
        signals = []
        
        # 定义信号模式
        patterns = {
            "error": [
                r"error",
                r"failed",
                r"失败",
                r"错误",
                r"exception",
                r"traceback",
                r"❌",
            ],
            "user_frustration": [
                r"怎么",
                r"为什么",
                r"不行",
                r"不能",
                r"没用",
                r"还是",
            ],
            "success": [
                r"成功",
                r"✅",
                r"好了",
                r"完成",
            ],
            "learning": [
                r"记住",
                r"记录",
                r"学到",
            ]
        }
        
        for session in sessions:
            content = str(session.get("message", {}).get("content", ""))
            role = session.get("message", {}).get("role", "")
            
            for signal_type, keywords in patterns.items():
                for keyword in keywords:
                    if keyword.lower() in content.lower():
                        signals.append({
                            "type": signal_type,
                            "keyword": keyword,
                            "content": content[:200],
                            "role": role,
                            "timestamp": session.get("timestamp", "")
                        })
                        break
        
        return signals
    
    def analyze_errors(self, sessions: List[Dict]) -> List[Dict]:
        """分析错误"""
        errors = []
        
        for session in sessions:
            content = str(session)
            
            # 检测错误
            if "error" in content.lower() or "failed" in content.lower():
                # 提取错误信息
                error_match = re.search(r'Error[:\s]+(.+)', content, re.IGNORECASE)
                if error_match:
                    errors.append({
                        "error": error_match.group(1)[:100],
                        "context": content[:200]
                    })
                elif "错误" in content or "失败" in content:
                    errors.append({
                        "error": "未知错误",
                        "context": content[:200]
                    })
        
        return errors
    
    def generate_suggestions(self, signals: List[Dict], errors: List[Dict]) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        # 基于错误生成建议
        for error in errors:
            if "token" in error["error"].lower():
                suggestions.append("建议优化token使用，避免浪费")
            elif "api" in error["error"].lower():
                suggestions.append("检查API调用是否正确")
            elif "file" in error["error"].lower():
                suggestions.append("检查文件路径和权限")
        
        # 基于信号生成建议
        signal_counts = {}
        for signal in signals:
            signal_type = signal["type"]
            signal_counts[signal_type] = signal_counts.get(signal_type, 0) + 1
        
        for signal_type, count in signal_counts.items():
            if signal_type == "user_frustration" and count > 3:
                suggestions.append("用户多次表达困惑，建议改进回复清晰度")
            elif signal_type == "error" and count > 5:
                suggestions.append("错误频率较高，建议全面检查代码")
        
        return suggestions
    
    def run(self, review_mode: bool = False) -> Dict:
        """运行进化分析"""
        print("🔄 开始自我进化分析...")
        
        # 1. 获取最近的sessions
        print("📥 收集最近的对话...")
        sessions = self.get_recent_sessions(hours=24)
        print(f"   找到 {len(sessions)} 条对话记录")
        
        # 2. 提取信号
        print("🔍 分析信号...")
        signals = self.extract_signals(sessions)
        print(f"   发现 {len(signals)} 个信号")
        
        # 3. 分析错误
        print("❌ 检查错误...")
        errors = self.analyze_errors(sessions)
        print(f"   发现 {len(errors)} 个错误")
        
        # 4. 生成建议
        print("💡 生成改进建议...")
        suggestions = self.generate_suggestions(signals, errors)
        
        # 5. 输出结果
        result = {
            "timestamp": datetime.now().isoformat(),
            "sessions_analyzed": len(sessions),
            "signals_found": len(signals),
            "errors_found": len(errors),
            "suggestions": suggestions
        }
        
        print("\n" + "="*50)
        print("📊 进化分析报告")
        print("="*50)
        print(f"时间: {result['timestamp']}")
        print(f"分析对话: {result['sessions_analyzed']} 条")
        print(f"发现信号: {result['signals_found']} 个")
        print(f"发现错误: {result['errors_found']} 个")
        
        if suggestions:
            print("\n💡 改进建议:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"   {i}. {suggestion}")
        else:
            print("\n✅ 没有发现需要改进的问题！")
        
        return result
    
    def save_to_memory(self, result: Dict):
        """保存到记忆"""
        memory_file = self.memory_dir / f"evolve_{datetime.now().strftime('%Y-%m-%d')}.md"
        
        content = f"""# 进化分析报告 - {result['timestamp']}

## 统计
- 分析对话: {result['sessions_analyzed']} 条
- 发现信号: {result['signals_found']} 个
- 发现错误: {result['errors_found']} 个

## 改进建议
"""
        for i, suggestion in enumerate(result['suggestions'], 1):
            content += f"{i}. {suggestion}\n"
        
        with open(memory_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n📝 已保存到: {memory_file}")


def main():
    import sys
    
    review_mode = "--review" in sys.argv
    
    evolver = SimpleEvolver()
    result = evolver.run(review_mode=review_mode)
    
    # 保存到记忆
    evolver.save_to_memory(result)
    
    return result


if __name__ == "__main__":
    main()
