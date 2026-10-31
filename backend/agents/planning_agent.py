from typing import Dict, Any, List
import re
from .base_agent import BaseAgent
from ..orchestrator.task import Task
from ..orchestrator.context import WorkflowContext

class PlanningAgent(BaseAgent):
    """
    Decomposes complex, multi-faceted user requests into an executable
    dependency-aware task plan with assigned agent roles, inputs, outputs,
    and verification criteria.
    """
    def __init__(self):
        super().__init__(
            name="Planning Agent",
            role="Task Decomposition & Workflow Architecture",
            description="Analyzes complex requests, synthesizes dependency graphs, assigns specialized agents, and defines validation rules."
        )

    def decompose_request(self, user_request: str, context: WorkflowContext) -> List[Task]:
        """
        Decomposes the incoming user request into structured tasks.
        """
        self.send_message(
            context,
            recipient="Orchestrator",
            message_type="PLAN_INITIATED",
            content=f"Deconstructing user request: '{user_request[:120]}...'"
        )

        req_lower = user_request.lower()

        # Scenario 1: Financial & Valuation Analysis
        if any(w in req_lower for w in ["financial", "stock", "pe ratio", "revenue", "aapl", "nvda", "msft", "growth"]):
            tasks = [
                Task(
                    task_id="task_1_research_financials",
                    title="Retrieve Target Financial Metrics",
                    assigned_agent="Research Agent",
                    description="Extract quarterly revenues, net income, P/E ratios, and margins for the specified tech companies.",
                    dependencies=[],
                    expected_output_type="dict",
                    validation_rules={"required_keys": ["companies", "metrics_extracted"]}
                ),
                Task(
                    task_id="task_2_compute_financial_models",
                    title="Compute Growth Rates & Valuations",
                    assigned_agent="Execution Agent",
                    description="Calculate year-over-year revenue growth, profit margin percentages, and valuation differentials.",
                    dependencies=["task_1_research_financials"],
                    expected_output_type="dict",
                    validation_rules={"required_keys": ["growth_rates", "profitability_summary"]}
                ),
                Task(
                    task_id="task_3_verify_financial_data",
                    title="Validate Numerical Accuracy & Boundaries",
                    assigned_agent="Verification Agent",
                    description="Check financial figures against bounds, verify growth calculations, and ensure non-negative ratios.",
                    dependencies=["task_2_compute_financial_models"],
                    expected_output_type="dict",
                    validation_rules={"required_keys": ["verification_score", "verdict"]}
                )
            ]

        # Scenario 2: Database & System Benchmark Comparison
        elif any(w in req_lower for w in ["database", "benchmark", "postgresql", "mongodb", "redis", "latency", "throughput", "iops"]):
            tasks = [
                Task(
                    task_id="task_1_research_db_benchmarks",
                    title="Retrieve System Benchmark Profiles",
                    assigned_agent="Research Agent",
                    description="Fetch IOPS metrics, p99 latencies, ACID properties, and memory footprints for PostgreSQL, MongoDB, and Redis.",
                    dependencies=[],
                    expected_output_type="dict",
                    validation_rules={"required_keys": ["systems", "benchmark_metrics"]}
                ),
                Task(
                    task_id="task_2_compute_performance_indices",
                    title="Calculate Throughput Ratios & Efficiency Scores",
                    assigned_agent="Execution Agent",
                    description="Compute read/write throughput differentials, latency speedup factors, and memory-to-throughput efficiency.",
                    dependencies=["task_1_research_db_benchmarks"],
                    expected_output_type="dict",
                    validation_rules={"required_keys": ["throughput_comparison", "latency_speedup"]}
                ),
                Task(
                    task_id="task_3_verify_benchmark_claims",
                    title="Cross-Verify Architecture Claims & Metric Validity",
                    assigned_agent="Verification Agent",
                    description="Verify that latency values are strictly non-negative and performance comparisons match raw benchmarks.",
                    dependencies=["task_2_compute_performance_indices"],
                    expected_output_type="dict",
                    validation_rules={"required_keys": ["verification_score", "verdict"]}
                )
            ]

        # Scenario 3: Scientific / Climate Time-Series Analysis
        elif any(w in req_lower for w in ["climate", "temperature", "anomaly", "co2", "trend", "scientific", "regression"]):
            tasks = [
                Task(
                    task_id="task_1_research_climate_series",
                    title="Extract Historical Environmental Series",
                    assigned_agent="Research Agent",
                    description="Retrieve 2016-2024 global temperature anomaly, atmospheric CO2 ppm, and Arctic sea ice extent data.",
                    dependencies=[],
                    expected_output_type="dict",
                    validation_rules={"required_keys": ["years", "temperature_anomaly"]}
                ),
                Task(
                    task_id="task_2_compute_climate_statistics",
                    title="Compute Statistical Regression & Decade Rate",
                    assigned_agent="Execution Agent",
                    description="Calculate mean, standard deviation, decade temperature delta, and correlation between CO2 and anomaly.",
                    dependencies=["task_1_research_climate_series"],
                    expected_output_type="dict",
                    validation_rules={"required_keys": ["mean_anomaly", "stdev", "decade_rate"]}
                ),
                Task(
                    task_id="task_3_verify_statistical_bounds",
                    title="Verify Statistical Bounds & P-Values",
                    assigned_agent="Verification Agent",
                    description="Confirm physical reality of temperature boundaries, variance thresholds, and calculation integrity.",
                    dependencies=["task_2_compute_climate_statistics"],
                    expected_output_type="dict",
                    validation_rules={"required_keys": ["verification_score", "verdict"]}
                )
            ]

        # Scenario 4: Cybersecurity Vulnerability & CVE Audit
        elif any(w in req_lower for w in ["security", "vulnerability", "cve", "cvss", "xz-utils", "runc", "audit"]):
            tasks = [
                Task(
                    task_id="task_1_research_cve_threats",
                    title="Query CVE Vulnerability Database",
                    assigned_agent="Research Agent",
                    description="Identify CVSS v3 base metrics, attack vectors, affected package versions, and vendor patches.",
                    dependencies=[],
                    expected_output_type="dict",
                    validation_rules={"required_keys": ["vulnerabilities_detected"]}
                ),
                Task(
                    task_id="task_2_compute_threat_matrix",
                    title="Compute Risk Severity Index & Priority Matrix",
                    assigned_agent="Execution Agent",
                    description="Calculate aggregate threat exposure score, mean CVSS impact, and categorize priority remediation order.",
                    dependencies=["task_1_research_cve_threats"],
                    expected_output_type="dict",
                    validation_rules={"required_keys": ["aggregate_risk_score", "prioritized_remediation"]}
                ),
                Task(
                    task_id="task_3_verify_remediation_integrity",
                    title="Validate CVSS Scores & Schema Compliance",
                    assigned_agent="Verification Agent",
                    description="Ensure CVSS scores lie strictly in the 0.0 - 10.0 scale, CVE formats are valid, and remediation plans exist.",
                    dependencies=["task_2_compute_threat_matrix"],
                    expected_output_type="dict",
                    validation_rules={"required_keys": ["verification_score", "verdict"]}
                )
            ]

        # Scenario 5: Data Transformation & Aggregation Pipeline
        elif any(w in req_lower for w in ["sales", "order", "revenue", "transform", "pipeline", "discount", "aggregate"]):
            tasks = [
                Task(
                    task_id="task_1_research_raw_transactions",
                    title="Ingest Raw Sales Transaction Log",
                    assigned_agent="Research Agent",
                    description="Retrieve raw order records, customer tiers, unit pricing, discounts, and order statuses.",
                    dependencies=[],
                    expected_output_type="dict",
                    validation_rules={"required_keys": ["raw_records"]}
                ),
                Task(
                    task_id="task_2_compute_sales_pipeline",
                    title="Execute Cleansing & Net Revenue Transformation",
                    assigned_agent="Execution Agent",
                    description="Filter cancelled orders, compute post-discount net revenue per row, and aggregate by customer tier.",
                    dependencies=["task_1_research_raw_transactions"],
                    expected_output_type="dict",
                    validation_rules={"required_keys": ["cleaned_data", "tier_aggregates"]}
                ),
                Task(
                    task_id="task_3_verify_pipeline_schema",
                    title="Validate Schema & Financial Consistency",
                    assigned_agent="Verification Agent",
                    description="Verify that net revenue is non-negative, aggregate totals match row sums, and JSON schema is fully compliant.",
                    dependencies=["task_2_compute_sales_pipeline"],
                    expected_output_type="dict",
                    validation_rules={"required_keys": ["verification_score", "verdict"]}
                )
            ]

        # Generic Multi-Step Request Decomposition
        else:
            tasks = [
                Task(
                    task_id="task_1_domain_research",
                    title="Investigate & Retrieve Domain Context",
                    assigned_agent="Research Agent",
                    description=f"Conduct research and extract relevant verified information regarding: {user_request}",
                    dependencies=[],
                    expected_output_type="dict",
                    validation_rules={"required_keys": ["findings"]}
                ),
                Task(
                    task_id="task_2_computational_synthesis",
                    title="Perform Analysis & Computational Processing",
                    assigned_agent="Execution Agent",
                    description="Process extracted data points, apply quantitative formulas, and generate comparative indicators.",
                    dependencies=["task_1_domain_research"],
                    expected_output_type="dict",
                    validation_rules={"required_keys": ["processed_analysis"]}
                ),
                Task(
                    task_id="task_3_quality_verification",
                    title="Rigorous Verification & Fact-Checking",
                    assigned_agent="Verification Agent",
                    description="Audit computational outputs, verify schema completeness, and validate logical consistency before final synthesis.",
                    dependencies=["task_2_computational_synthesis"],
                    expected_output_type="dict",
                    validation_rules={"required_keys": ["verification_score", "verdict"]}
                )
            ]

        # Notify blackboard and agent messaging
        self.write_context(context, "task_plan_count", len(tasks))
        self.send_message(
            context,
            recipient="Orchestrator",
            message_type="PLAN_GENERATED",
            content={
                "total_tasks": len(tasks),
                "tasks": [{"id": t.task_id, "agent": t.assigned_agent, "title": t.title} for t in tasks]
            }
        )

        return tasks

    def execute_task(self, task: Task, context: WorkflowContext) -> Any:
        """Planning agent can synthesize verified findings into the final comprehensive report."""
        task.start()
        
        blackboard = context.blackboard
        task_results = {t_id: t.output for t_id, t in context.tasks.items() if t.output}
        
        report = {
            "title": "Autonomous Multi-Agent Workflow Execution Summary",
            "request": context.user_request,
            "tasks_executed": len(context.tasks),
            "verified_results": task_results,
            "orchestration_status": "SUCCESS"
        }
        
        task.complete(report, duration_ms=25.0)
        return report
