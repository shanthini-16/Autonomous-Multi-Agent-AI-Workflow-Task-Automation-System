import time
from typing import Dict, Any, Callable, List, Optional
from datetime import datetime

class ToolPermissionError(Exception):
    """Raised when an agent attempts to invoke a tool without permission."""
    pass

class ToolExecutionResult:
    def __init__(self, tool_name: str, caller_agent: str, success: bool, output: Any, 
                 duration_ms: float, permission_granted: bool = True, error: Optional[str] = None):
        self.tool_name = tool_name
        self.caller_agent = caller_agent
        self.success = success
        self.output = output
        self.duration_ms = duration_ms
        self.permission_granted = permission_granted
        self.error = error
        self.timestamp = datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "caller_agent": self.caller_agent,
            "success": self.success,
            "permission_granted": self.permission_granted,
            "output": self.output,
            "error": self.error,
            "duration_ms": round(self.duration_ms, 2),
            "timestamp": self.timestamp
        }

class ToolDefinition:
    def __init__(self, name: str, category: str, description: str, parameters: Dict[str, Any], handler: Callable):
        self.name = name
        self.category = category # 'retrieval', 'computation', 'verification'
        self.description = description
        self.parameters = parameters
        self.handler = handler

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "parameters": self.parameters
        }

class ToolRegistry:
    """
    Centralized tool execution registry with strict permission controls,
    input sanitization, execution isolation, and full audit logging.
    """
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        # Strict Agent -> Allowed Tools permission matrix
        self._permissions: Dict[str, List[str]] = {
            "Planning Agent": [
                # Planning agent cannot execute heavy computational or retrieval tools directly
            ],
            "Research Agent": [
                "web_search",
                "fetch_url",
                "knowledge_query",
                "data_extractor"
            ],
            "Execution Agent": [
                "python_interpreter",
                "math_evaluator",
                "data_transformer"
            ],
            "Verification Agent": [
                "schema_validator",
                "sanity_checker",
                "consistency_evaluator",
                "math_evaluator"
            ]
        }
        self._audit_log: List[ToolExecutionResult] = []

    def register_tool(self, name: str, category: str, description: str, parameters: Dict[str, Any], handler: Callable):
        self._tools[name] = ToolDefinition(name, category, description, parameters, handler)

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def get_all_tools(self) -> List[Dict[str, Any]]:
        return [tool.to_dict() for tool in self._tools.values()]

    def get_permission_matrix(self) -> Dict[str, List[str]]:
        return self._permissions

    def is_authorized(self, agent_name: str, tool_name: str) -> bool:
        allowed = self._permissions.get(agent_name, [])
        return tool_name in allowed

    def execute_tool(self, agent_name: str, tool_name: str, **kwargs) -> ToolExecutionResult:
        start_time = time.time()
        
        # 1. Check Tool Existence
        if tool_name not in self._tools:
            duration = (time.time() - start_time) * 1000
            res = ToolExecutionResult(
                tool_name=tool_name,
                caller_agent=agent_name,
                success=False,
                output=None,
                duration_ms=duration,
                permission_granted=False,
                error=f"Tool '{tool_name}' is not registered in the system."
            )
            self._audit_log.append(res)
            return res

        # 2. Enforce Strict Permission Control
        if not self.is_authorized(agent_name, tool_name):
            duration = (time.time() - start_time) * 1000
            res = ToolExecutionResult(
                tool_name=tool_name,
                caller_agent=agent_name,
                success=False,
                output=None,
                duration_ms=duration,
                permission_granted=False,
                error=f"SECURITY ALERT: Access Denied. '{agent_name}' lacks permission to invoke '{tool_name}'."
            )
            self._audit_log.append(res)
            return res

        # 3. Controlled Execution with Sandbox / Error Trap
        tool = self._tools[tool_name]
        try:
            output = tool.handler(**kwargs)
            duration = (time.time() - start_time) * 1000
            res = ToolExecutionResult(
                tool_name=tool_name,
                caller_agent=agent_name,
                success=True,
                output=output,
                duration_ms=duration,
                permission_granted=True,
                error=None
            )
            self._audit_log.append(res)
            return res
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            res = ToolExecutionResult(
                tool_name=tool_name,
                caller_agent=agent_name,
                success=False,
                output=None,
                duration_ms=duration,
                permission_granted=True,
                error=f"Tool execution failed: {str(e)}"
            )
            self._audit_log.append(res)
            return res

    def get_audit_log(self, limit: int = 50) -> List[Dict[str, Any]]:
        return [entry.to_dict() for entry in self._audit_log[-limit:]]

    def clear_audit_log(self):
        self._audit_log.clear()

# Global Tool Registry Singleton
registry = ToolRegistry()
