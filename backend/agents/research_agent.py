import time
from typing import Dict, Any
from .base_agent import BaseAgent
from ..orchestrator.task import Task
from ..orchestrator.context import WorkflowContext

class ResearchAgent(BaseAgent):
    """
    Specialized agent dedicated to information retrieval, external web queries,
    knowledge repository extraction, and initial data normalization.
    """
    def __init__(self):
        super().__init__(
            name="Research Agent",
            role="Information Retrieval & Knowledge Extraction",
            description="Queries indexed databases, scrapes external URLs, executes web searches, and structures raw facts for downstream analysis."
        )

    def execute_task(self, task: Task, context: WorkflowContext) -> Dict[str, Any]:
        task.start()
        start_time = time.time()
        desc = task.description.lower()
        title = task.title.lower()

        self.send_message(
            context,
            recipient="Execution Agent",
            message_type="RESEARCH_STARTED",
            content=f"Starting data retrieval for '{task.title}'...",
            task_id=task.task_id
        )

        output_data = {}

        # 1. Financial Research Task
        if "financial" in desc or "pe ratio" in desc or "revenue" in desc:
            # Query knowledge store
            q_res = self.call_tool(context, "knowledge_query", domain="financials")
            if q_res.success:
                raw_fin = q_res.output.get("data", {})
                task.tool_calls.append(q_res.to_dict())
                output_data = {
                    "companies": ["AAPL", "NVDA", "MSFT"],
                    "metrics_extracted": raw_fin,
                    "retrieval_source": "Verified Corporate Ledger & SEC Filings",
                    "timestamp": time.time()
                }
            else:
                # Fallback to web search
                s_res = self.call_tool(context, "web_search", query="AAPL NVDA MSFT revenue and PE ratio")
                task.tool_calls.append(s_res.to_dict())
                output_data = {"companies": ["AAPL", "NVDA", "MSFT"], "metrics_extracted": s_res.output}

        # 2. Database Benchmarks Task
        elif "database" in desc or "benchmark" in desc or "iops" in desc:
            q_res = self.call_tool(context, "knowledge_query", domain="databases")
            if q_res.success:
                task.tool_calls.append(q_res.to_dict())
                output_data = {
                    "systems": ["PostgreSQL", "MongoDB", "Redis"],
                    "benchmark_metrics": q_res.output.get("data", {}),
                    "retrieval_source": "Standardized Systems Benchmark Index",
                    "timestamp": time.time()
                }

        # 3. Climate & Environmental Task
        elif "climate" in desc or "temperature" in desc or "co2" in desc:
            q_res = self.call_tool(context, "knowledge_query", domain="climate")
            if q_res.success:
                task.tool_calls.append(q_res.to_dict())
                clim = q_res.output.get("data", {})
                output_data = {
                    "years": clim.get("time_series_years", []),
                    "temperature_anomaly": clim.get("temperature_anomaly_celsius", []),
                    "co2_ppm": clim.get("co2_ppm", []),
                    "sea_ice": clim.get("sea_ice_min_million_sqkm", []),
                    "source": "Global Climate Observation Network"
                }

        # 4. Cybersecurity Vulnerabilities Task
        elif "vulnerability" in desc or "cve" in desc or "security" in desc or "cvss" in desc or "threat" in desc:
            q_res = self.call_tool(context, "knowledge_query", domain="vulnerabilities")
            if q_res.success:
                task.tool_calls.append(q_res.to_dict())
                output_data = {
                    "vulnerabilities_detected": q_res.output.get("data", []),
                    "audit_timestamp": time.time(),
                    "source": "National Vulnerability Database (NVD)"
                }

        # 5. Raw Sales Records Task
        elif "sales" in desc or "order" in desc or "transaction" in desc:
            q_res = self.call_tool(context, "knowledge_query", domain="raw_sales_records")
            if q_res.success:
                task.tool_calls.append(q_res.to_dict())
                output_data = {
                    "raw_records": q_res.output.get("data", []),
                    "record_count": len(q_res.output.get("data", [])),
                    "ingestion_status": "VALID_BATCH"
                }

        # General / Research Investigation Tasks
        else:
            raw_prompt = context.user_request or task.description
            search_query = raw_prompt
            for prefix in ["Conduct research and extract relevant verified information regarding: ", "Research the ", "Research ", "Investigate "]:
                if search_query.startswith(prefix):
                    search_query = search_query[len(prefix):]

            s_res = self.call_tool(context, "web_search", query=search_query)
            task.tool_calls.append(s_res.to_dict())
            
            tool_out = s_res.output if (s_res.success and isinstance(s_res.output, dict)) else {}
            results_list = tool_out.get("results", [])
            sources_list = tool_out.get("sources", [])
            domain_payload = tool_out.get("domain_payload")

            output_data = {
                "query": search_query,
                "findings": results_list,
                "sources": sources_list,
                "retrieved_count": len(results_list)
            }

            if domain_payload and isinstance(domain_payload, dict):
                output_data["title"] = domain_payload.get("title", search_query.title())
                output_data["introduction"] = domain_payload.get("introduction", "")
                output_data["advantages"] = domain_payload.get("advantages", [])
                output_data["disadvantages"] = domain_payload.get("disadvantages", [])
                output_data["comparative_metrics"] = domain_payload.get("comparative_metrics", {})
                output_data["conclusion"] = domain_payload.get("conclusion", "")

        # Save to shared blackboard
        self.write_context(context, "research_data", output_data)
        self.write_context(context, f"research_output_{task.task_id}", output_data)

        # Notify downstream agent
        self.send_message(
            context,
            recipient="Execution Agent",
            message_type="RESULT_TRANSFER",
            content={
                "data_keys": list(output_data.keys()),
                "summary": f"Completed research for {task.title}. Data deposited to shared blackboard."
            },
            task_id=task.task_id
        )

        duration = (time.time() - start_time) * 1000
        task.complete(output_data, duration_ms=duration)
        return output_data
