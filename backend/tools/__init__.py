from .tool_registry import registry, ToolRegistry, ToolExecutionResult, ToolPermissionError
from .retrieval_tools import tool_web_search, tool_fetch_url, tool_knowledge_query, tool_data_extractor
from .compute_tools import tool_python_interpreter, tool_math_evaluator, tool_data_transformer
from .verification_tools import tool_schema_validator, tool_sanity_checker, tool_consistency_evaluator, tool_output_verifier

def initialize_tools():
    """Register all available tools in the central registry."""
    # Retrieval Tools
    registry.register_tool(
        name="web_search",
        category="retrieval",
        description="Search web sources and verified domain knowledge stores for information and facts.",
        parameters={"query": "string", "max_results": "integer"},
        handler=tool_web_search
    )
    
    registry.register_tool(
        name="fetch_url",
        category="retrieval",
        description="Perform safe HTTP requests to retrieve live URLs and API responses.",
        parameters={"url": "string", "timeout": "integer"},
        handler=tool_fetch_url
    )
    
    registry.register_tool(
        name="knowledge_query",
        category="retrieval",
        description="Query indexed domain repositories (financials, databases, climate, vulnerabilities, sales).",
        parameters={"domain": "string", "filter_key": "string (optional)"},
        handler=tool_knowledge_query
    )
    
    registry.register_tool(
        name="data_extractor",
        category="retrieval",
        description="Extract structured entities, numbers, and tabular key-values from text/JSON.",
        parameters={"text_or_json": "any", "extraction_type": "string"},
        handler=tool_data_extractor
    )

    # Computation Tools
    registry.register_tool(
        name="python_interpreter",
        category="computation",
        description="Execute algorithmic data processing and analysis inside a secured Python execution environment.",
        parameters={"code": "string", "timeout_seconds": "integer"},
        handler=tool_python_interpreter
    )
    
    registry.register_tool(
        name="math_evaluator",
        category="computation",
        description="High-precision arithmetic, CAGR, statistical measures (mean, stdev, min, max, growth_rate).",
        parameters={"expression": "string (optional)", "operation": "string", "values": "list of floats (optional)"},
        handler=tool_math_evaluator
    )
    
    registry.register_tool(
        name="data_transformer",
        category="computation",
        description="Transform tabular records: filter, compute calculated columns, group aggregate, or sort.",
        parameters={"dataset": "list of dicts", "action": "string", "kwargs": "dict"},
        handler=tool_data_transformer
    )

    # Verification Tools
    registry.register_tool(
        name="schema_validator",
        category="verification",
        description="Validate intermediate outputs and datasets against strict JSON Schema and required keys.",
        parameters={"data": "any", "schema": "dict (optional)", "required_fields": "list of strings (optional)"},
        handler=tool_schema_validator
    )
    
    registry.register_tool(
        name="sanity_checker",
        category="verification",
        description="Validate numerical metrics against physical/logical boundary limits and anomaly detectors.",
        parameters={"metrics": "dict", "bounds": "dict (optional)"},
        handler=tool_sanity_checker
    )
    
    registry.register_tool(
        name="consistency_evaluator",
        category="verification",
        description="Cross-check claims in generated summaries against ground-truth computational numbers.",
        parameters={"claimed_summary": "string", "factual_data": "dict"},
        handler=tool_consistency_evaluator
    )

    registry.register_tool(
        name="output_verifier",
        category="verification",
        description="Authoritative quality and completeness verifier calculating composite verification score (0-100).",
        parameters={"task_result": "any", "expected_type": "string", "validation_rules": "dict (optional)"},
        handler=tool_output_verifier
    )

# Automatically register tools on import
initialize_tools()
