from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import uuid
from .task import Task

class AgentMessage:
    def __init__(self, sender: str, recipient: str, message_type: str, content: Any, task_id: Optional[str] = None):
        self.message_id = str(uuid.uuid4())[:8]
        self.sender = sender
        self.recipient = recipient
        self.message_type = message_type # 'TASK_ASSIGNMENT', 'RESULT_TRANSFER', 'VERIFICATION_FEEDBACK', 'RETRY_DIRECTIVE', 'INFO'
        self.content = content
        self.task_id = task_id
        self.timestamp = datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "message_type": self.message_type,
            "content": self.content,
            "task_id": self.task_id,
            "timestamp": self.timestamp
        }

class WorkflowContext:
    """
    Shared blackboard and communication bus enabling agents to exchange
    task results, maintain execution state, and emit real-time telemetry.
    """
    def __init__(self, workflow_id: Optional[str] = None, user_request: str = ""):
        self.workflow_id = workflow_id or f"wf_{str(uuid.uuid4())[:8]}"
        self.user_request = user_request
        self.status = "INITIALIZING" # INITIALIZING, PLANNING, RUNNING, VERIFYING, COMPLETED, FAILED
        self.blackboard: Dict[str, Any] = {}
        self.tasks: Dict[str, Task] = {}
        self.messages: List[AgentMessage] = []
        self.tool_logs: List[Dict[str, Any]] = []
        self.final_output: Optional[Dict[str, Any]] = None
        self.created_at = datetime.utcnow().isoformat() + "Z"
        self.updated_at = self.created_at
        
        # Telemetry
        self.start_time: Optional[float] = None
        self.total_duration_ms: float = 0.0
        self.total_retries: int = 0
        self.simulated_failure_triggered: bool = False
        
        # Event callbacks for real-time monitoring
        self._listeners: List[Callable[[Dict[str, Any]], None]] = []

    def add_listener(self, callback: Callable[[Dict[str, Any]], None]):
        self._listeners.append(callback)

    def emit_event(self, event_type: str, data: Dict[str, Any]):
        self.updated_at = datetime.utcnow().isoformat() + "Z"
        payload = {
            "workflow_id": self.workflow_id,
            "event_type": event_type,
            "timestamp": self.updated_at,
            "status": self.status,
            "data": data
        }
        for listener in self._listeners:
            try:
                listener(payload)
            except Exception:
                pass

    def set_blackboard_value(self, key: str, value: Any, agent_name: str = "System"):
        self.blackboard[key] = value
        self.emit_event("BLACKBOARD_UPDATED", {
            "key": key,
            "agent": agent_name,
            "preview": str(value)[:150]
        })

    def get_blackboard_value(self, key: str, default: Any = None) -> Any:
        return self.blackboard.get(key, default)

    def add_message(self, sender: str, recipient: str, message_type: str, content: Any, task_id: Optional[str] = None):
        msg = AgentMessage(sender, recipient, message_type, content, task_id)
        self.messages.append(msg)
        self.emit_event("AGENT_MESSAGE", msg.to_dict())
        return msg

    def register_task(self, task: Task):
        self.tasks[task.task_id] = task
        self.emit_event("TASK_REGISTERED", task.to_dict())

    def update_task_status(self, task_id: str, status: str, details: Optional[Dict[str, Any]] = None):
        if task_id in self.tasks:
            task = self.tasks[task_id]
            self.emit_event("TASK_STATUS_CHANGED", {
                "task_id": task_id,
                "status": status,
                "title": task.title,
                "assigned_agent": task.assigned_agent,
                "details": details or {}
            })

    def record_tool_call(self, tool_call_dict: Dict[str, Any]):
        self.tool_logs.append(tool_call_dict)
        self.emit_event("TOOL_CALLED", tool_call_dict)

    def to_dict(self) -> Dict[str, Any]:
        tasks_dict = [t.to_dict() for t in self.tasks.values()]
        completed_tasks = sum(1 for t in self.tasks.values() if t.status.value == "COMPLETED")
        failed_tasks = sum(1 for t in self.tasks.values() if t.status.value == "FAILED")
        
        # Calculate verification average
        verification_scores = [
            t.verification_result.get("verification_score", 0) 
            for t in self.tasks.values() 
            if t.verification_result and "verification_score" in t.verification_result
        ]
        avg_verification_score = round(sum(verification_scores) / len(verification_scores), 1) if verification_scores else 0.0

        return {
            "workflow_id": self.workflow_id,
            "user_request": self.user_request,
            "status": self.status,
            "tasks": tasks_dict,
            "blackboard": self.blackboard,
            "messages": [m.to_dict() for m in self.messages],
            "tool_logs": self.tool_logs,
            "final_output": self.final_output,
            "metrics": {
                "total_tasks": len(self.tasks),
                "completed_tasks": completed_tasks,
                "failed_tasks": failed_tasks,
                "total_retries": self.total_retries,
                "total_duration_ms": round(self.total_duration_ms, 2),
                "avg_verification_score": avg_verification_score,
                "tool_calls_count": len(self.tool_logs)
            },
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
