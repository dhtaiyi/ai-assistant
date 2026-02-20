#!/usr/bin/env python3
"""
SessionMemoryManager - 跨会话记忆管理器

实现EvoMap学习的跨会话记忆连续性技能：
- 24小时滚动事件流 (RECENT_EVENTS.md)
- 每日记录 (memory/YYYY-MM-DD.md)  
- 长期精选 (MEMORY.md)

用法:
    from memory.session_manager import SessionMemoryManager
    
    mgr = SessionMemoryManager()
    mgr.start_session()
    mgr.record_event("task_start", {"task": "EvoMap申诉"})
    mgr.end_session({"status": "completed"})
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

WORKSPACE = "/root/.openclaw/workspace"
MEMORY_DIR = f"{WORKSPACE}/memory"

class SessionMemoryManager:
    """跨会话记忆管理器"""
    
    def __init__(self, workspace: str = WORKSPACE):
        self.workspace = workspace
        self.memory_dir = f"{workspace}/memory"
        self.recent_events_path = f"{self.memory_dir}/RECENT_EVENTS.md"
        self.session_start: Optional[datetime] = None
        self.working_buffer: List[Dict] = []
        self.session_events: List[Dict] = []
        
    def _ensure_memory_dir(self):
        """确保memory目录存在"""
        Path(self.memory_dir).mkdir(parents=True, exist_ok=True)
        
    def start_session(self, session_name: str = "main"):
        """开始新会话"""
        self._ensure_memory_dir()
        self.session_start = datetime.utcnow()
        self.working_buffer = []
        self.session_events = []
        
        # 记录会话开始
        self.record_event("session_start", {
            "session": session_name,
            "time": self.session_start.isoformat()
        })
        
        # 加载最近的上下文
        recent_context = self.load_recent_context()
        return recent_context
        
    def load_recent_context(self) -> Dict[str, Any]:
        """加载最近的上下文（从RECENT_EVENTS.md）"""
        if not os.path.exists(self.recent_events_path):
            return {"recent_events": [], "pending_tasks": []}
            
        context = {
            "recent_events": [],
            "pending_tasks": [],
            "current_projects": [],
            "user_preferences": {}
        }
        
        try:
            with open(self.recent_events_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 解析待办任务
            import re
            pending = re.findall(r'- \[ \] (.+)', content)
            context["pending_tasks"] = pending
            
            # 解析进行中任务
            in_progress = re.findall(r'🔄 (.+)', content)
            context["current_projects"] = in_progress
            
        except Exception as e:
            pass
            
        return context
        
    def record_event(self, event_type: str, data: Dict):
        """记录事件到工作缓冲"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": event_type,
            "data": data
        }
        self.working_buffer.append(event)
        self.session_events.append(event)
        
    def record_decision(self, decision: str, reason: str = ""):
        """记录重要决策"""
        self.record_event("decision", {
            "decision": decision,
            "reason": reason
        })
        
    def record_task(self, task: str, status: str, notes: str = ""):
        """记录任务状态"""
        self.record_event("task_update", {
            "task": task,
            "status": status,
            "notes": notes
        })
        
    def end_session(self, summary: Dict[str, Any] = None):
        """结束会话，固化记忆"""
        # 1. 记录会话结束
        self.record_event("session_end", summary or {})
        
        # 2. 更新RECENT_EVENTS.md
        self._update_recent_events()
        
        # 3. 提取重要内容到长期记忆
        self._extract_to_long_term_memory()
        
        return {
            "events_count": len(self.session_events),
            "consolidated": True
        }
        
    def _update_recent_events(self):
        """更新RECENT_EVENTS.md滚动事件流"""
        # 保留最近24小时的事件
        cutoff = datetime.utcnow() - timedelta(hours=24)
        
        recent_items = []
        for event in self.session_events:
            event_time = datetime.fromisoformat(event["timestamp"])
            if event_time >= cutoff:
                recent_items.append(event)
                
        # 生成新的RECENT_EVENTS.md内容
        new_content = self._generate_recent_events_content(recent_items)
        
        try:
            with open(self.recent_events_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
        except Exception as e:
            print(f"[SessionMemoryManager] Warning: Failed to update RECENT_EVENTS.md: {e}")
            
    def _generate_recent_events_content(self, events: List[Dict]) -> str:
        """生成RECENT_EVENTS.md内容"""
        lines = [
            "# RECENT_EVENTS.md",
            "",
            f"**最后更新:** {datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}",
            "",
            "---",
            "",
            "## 本会话事件",
            ""
        ]
        
        for event in events[-10:]:  # 只保留最近10个
            timestamp = event["timestamp"][:19].replace("T", " ")
            event_type = event["type"]
            data = event.get("data", {})
            
            if event_type == "decision":
                lines.append(f"- **{timestamp}** 决策: {data.get('decision', '')}")
            elif event_type == "task_update":
                status_icon = {"done": "✅", "progress": "🔄", "pending": "⏳"}.get(data.get("status", ""), "📝")
                lines.append(f"- **{timestamp}** {status_icon} {data.get('task', '')} ({data.get('status', '')})")
            elif event_type == "session_start":
                lines.append(f"- **{timestamp}** 🆕 新会话: {data.get('session', '')}")
            elif event_type == "session_end":
                lines.append(f"- **{timestamp}** 🏁 会话结束")
            else:
                lines.append(f"- **{timestamp}** {event_type}: {str(data)[:50]}")
                
        lines.extend([
            "",
            f"*共记录 {len(events)} 个事件*",
            "",
            "---",
            "*此文件24小时滚动更新*"
        ])
        
        return "\n".join(lines)
        
    def _extract_to_long_term_memory(self):
        """提取重要内容到长期记忆（MEMORY.md）"""
        # 从事件中提取决策和知识点
        important_decisions = []
        key_learnings = []
        
        for event in self.session_events:
            if event["type"] == "decision":
                important_decisions.append(event["data"])
                
        # 如果有重要决策，更新MEMORY.md
        if important_decisions:
            self._append_to_memory("decisions", important_decisions)
            
    def _append_to_memory(self, category: str, items: List[Dict]):
        """追加内容到MEMORY.md"""
        memory_path = f"{self.memory_dir}/MEMORY.md"
        
        entry = f"""
### {datetime.utcnow().strftime('%Y-%m-%d')} - {category}
"""
        for item in items:
            entry += f"- {json.dumps(item, ensure_ascii=False)}\n"
            
        try:
            with open(memory_path, 'a', encoding='utf-8') as f:
                f.write(entry)
        except Exception as e:
            print(f"[SessionMemoryManager] Warning: Failed to update MEMORY.md: {e}")
            
    def get_session_summary(self) -> Dict:
        """获取会话摘要"""
        return {
            "start_time": self.session_start.isoformat() if self.session_start else None,
            "events_count": len(self.session_events),
            "buffer_size": len(self.working_buffer),
            "duration_minutes": (
                datetime.utcnow() - self.session_start
            ).total_seconds() / 60 if self.session_start else 0
        }


# 便捷函数
def get_memory_manager() -> SessionMemoryManager:
    """获取全局记忆管理器实例"""
    return SessionMemoryManager()


if __name__ == "__main__":
    # 测试代码
    mgr = SessionMemoryManager()
    
    # 开始会话
    context = mgr.start_session("test-session")
    print("✅ 会话开始")
    print(f"📂 加载上下文: {context}")
    
    # 记录一些事件
    mgr.record_event("task_start", {"task": "测试任务", "priority": "high"})
    mgr.record_decision("使用EvoMap技能", "提升跨会话记忆能力")
    mgr.record_event("task_complete", {"task": "测试任务", "result": "success"})
    
    print("📝 记录了3个事件")
    
    # 结束会话
    result = mgr.end_session({"status": "success"})
    print(f"🏁 会话结束: {result}")
    
    print(f"\n📁 生成的RECENT_EVENTS.md:")
    with open(mgr.recent_events_path, 'r') as f:
        print(f.read())
