from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    VERIFYING = "VERIFYING"
    RETRYING = "RETRYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Task:
    def __init__(
        self,
        task_id: str,
        title: str,
        assigned_agent: str,
        description: str,
        dependencies: Optional[List[str]] = None,
        expected_output_type: str = "any",
        validation_rules: Optional[Dict[str, Any]] = None,
        max_retries: int = 3
    ):
        self.task_id = task_id
        self.title = title
        self.assigned_agent = assigned_agent
        self.description = description
        self.dependencies = dependencies or []
        self.expected_output_type = expected_output_type
        self.validation_rules = validation_rules or {}
        self.max_retries = max_retries

        self.status: TaskStatus = TaskStatus.PENDING
        self.inputs: Dict[str, Any] = {}
        self.output: Any = None
        self.verification_result: Optional[Dict[str, Any]] = None
        self.retry_count: int = 0
        self.error_history: List[str] = []
        self.tool_calls: List[Dict[str, Any]] = []
        
        self.started_at: Optional[str] = None
        self.completed_at: Optional[str] = None
        self.execution_time_ms: float = 0.0

    def start(self):
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.utcnow().isoformat() + "Z"

    def record_retry(self, reason: str):
        self.retry_count += 1
        self.status = TaskStatus.RETRYING
        self.error_history.append(f"Retry #{self.retry_count}: {reason}")

    def complete(self, output: Any, verification_result: Optional[Dict[str, Any]] = None, duration_ms: float = 0.0):
        self.output = output
        self.verification_result = verification_result
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.utcnow().isoformat() + "Z"
        self.execution_time_ms = round(duration_ms, 2)

    def fail(self, final_error: str, duration_ms: float = 0.0):
        self.status = TaskStatus.FAILED
        self.error_history.append(f"Fatal Failure: {final_error}")
        self.completed_at = datetime.utcnow().isoformat() + "Z"
        self.execution_time_ms = round(duration_ms, 2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "assigned_agent": self.assigned_agent,
            "description": self.description,
            "dependencies": self.dependencies,
            "expected_output_type": self.expected_output_type,
            "validation_rules": self.validation_rules,
            "status": self.status.value,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "error_history": self.error_history,
            "tool_calls": self.tool_calls,
            "output": self.output,
            "verification_result": self.verification_result,
            "execution_time_ms": self.execution_time_ms,
            "started_at": self.started_at,
            "completed_at": self.completed_at
        }
