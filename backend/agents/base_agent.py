from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from ..tools import registry, ToolExecutionResult
from ..orchestrator.context import WorkflowContext

class BaseAgent(ABC):
    def __init__(self, name: str, role: str, description: str):
        self.name = name
        self.role = role
        self.description = description
        self.allowed_tools = registry.get_permission_matrix().get(name, [])

    def call_tool(self, context: WorkflowContext, tool_name: str, **kwargs) -> ToolExecutionResult:
        """
        Calls a tool using the centralized controlled tool registry.
        Records telemetry in the shared workflow context.
        """
        result = registry.execute_tool(self.name, tool_name, **kwargs)
        
        # Record in workflow context
        context.record_tool_call(result.to_dict())
        
        # If tool execution was denied due to permission violation, log to context
        if not result.permission_granted:
            context.add_message(
                sender=self.name,
                recipient="Orchestrator",
                message_type="SECURITY_WARNING",
                content=f"Permission Denied: {result.error}"
            )
            
        return result

    def send_message(self, context: WorkflowContext, recipient: str, message_type: str, content: Any, task_id: Optional[str] = None):
        """Send message to another agent or orchestrator via the shared communication bus."""
        return context.add_message(self.name, recipient, message_type, content, task_id)

    def read_context(self, context: WorkflowContext, key: str, default: Any = None) -> Any:
        """Read a variable from the shared blackboard."""
        return context.get_blackboard_value(key, default)

    def write_context(self, context: WorkflowContext, key: str, value: Any):
        """Write a variable to the shared blackboard."""
        context.set_blackboard_value(key, value, agent_name=self.name)

    @abstractmethod
    def execute_task(self, task: Any, context: WorkflowContext) -> Any:
        """Execute assigned task using agent capabilities and allowed tools."""
        pass

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "role": self.role,
            "description": self.description,
            "allowed_tools": self.allowed_tools
        }
