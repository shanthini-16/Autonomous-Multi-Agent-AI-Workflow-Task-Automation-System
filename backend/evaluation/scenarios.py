from typing import Dict, Any, List

EVALUATION_SCENARIOS = [
    {
        "id": "scenario_1_financial",
        "title": "Corporate Financial & Valuation Analysis",
        "category": "Quantitative Finance",
        "description": "Multi-step quantitative valuation of tier-1 technology leaders (AAPL, NVDA, MSFT). Ingests SEC revenue numbers, calculates YoY growth rates and valuation metrics, verifies boundaries, and generates executive findings.",
        "prompt": "Conduct a comprehensive financial analysis of AAPL, NVDA, and MSFT. Calculate YoY revenue growth, profit margin percentages, and P/E ratio differentials, verify all financial boundaries, and synthesize an executive valuation report.",
        "expected_stages": ["Planning", "Research", "Execution", "Verification"],
        "target_tools": ["knowledge_query", "math_evaluator", "python_interpreter", "sanity_checker", "schema_validator"],
        "pass_criteria": "Verification score >= 80%, all growth rates non-negative, executive summary generated."
    },
    {
        "id": "scenario_2_db_benchmark",
        "title": "Distributed Systems & Database Benchmarking",
        "category": "Systems Engineering",
        "description": "Comparative benchmark of PostgreSQL, MongoDB, and Redis across IOPS, p99 latencies, and ACID durability. Computes speedup factors, verifies non-negative metrics, and provides an architectural recommendation.",
        "prompt": "Benchmark PostgreSQL, MongoDB, and Redis performance metrics. Calculate IOPS speedup factors, evaluate p99 latency trade-offs, verify non-negative constraints, and produce an architecture selection verdict.",
        "expected_stages": ["Planning", "Research", "Execution", "Verification"],
        "target_tools": ["knowledge_query", "math_evaluator", "sanity_checker", "schema_validator"],
        "pass_criteria": "Latency non-negative, speedup factors calculated, schema validated."
    },
    {
        "id": "scenario_3_climate_analysis",
        "title": "Scientific Climate Observation & Decadal Trend",
        "category": "Environmental Science",
        "description": "Time-series statistical modeling of 2016-2024 global temperature anomalies and CO2 ppm. Computes mean, standard deviation, and linear regression slope for warming rate per decade, verified against planetary physical limits.",
        "prompt": "Analyze 2016-2024 global temperature anomaly time series and CO2 concentration metrics. Calculate mean anomaly, standard deviation, and decadal warming rate via linear regression, verify physical reality bounds, and summarize climate trajectory.",
        "expected_stages": ["Planning", "Research", "Execution", "Verification"],
        "target_tools": ["knowledge_query", "math_evaluator", "python_interpreter", "sanity_checker"],
        "pass_criteria": "Mean and slope within planetary boundaries (-2.0 to 5.0 °C), statistical validity confirmed."
    },
    {
        "id": "scenario_4_security_audit",
        "title": "Cybersecurity Vulnerability & CVE Exposure Audit",
        "category": "Information Security",
        "description": "Threat vulnerability analysis scanning critical infrastructure packages (xz-utils, runc, jenkins). Calculates aggregate threat scores, prioritizes remediation by CVSS score, and verifies compliance against 0-10 CVSS standards.",
        "prompt": "Audit critical enterprise dependencies (xz-utils, runc, jenkins-core) for active CVE vulnerabilities. Calculate mean CVSS risk score, prioritize patch order by severity, verify score bounds against CVSS 3.1 standards, and generate remediation roadmap.",
        "expected_stages": ["Planning", "Research", "Execution", "Verification"],
        "target_tools": ["knowledge_query", "math_evaluator", "sanity_checker"],
        "pass_criteria": "All CVSS scores between 0.0 and 10.0, patch remediation roadmap present."
    },
    {
        "id": "scenario_5_data_pipeline",
        "title": "E-Commerce Transaction Cleansing & Revenue Pipeline",
        "category": "Data Engineering",
        "description": "Multi-stage ETL pipeline processing raw order streams. Discards cancelled transactions, computes post-discount net revenue per line, performs customer tier group aggregations, and validates dataset integrity via strict JSON schema.",
        "prompt": "Process raw sales transaction records. Filter out cancelled orders, compute post-discount net revenue per transaction, aggregate net revenue by customer tier (Enterprise vs Pro), verify JSON schema compliance, and output audited totals.",
        "expected_stages": ["Planning", "Research", "Execution", "Verification"],
        "target_tools": ["knowledge_query", "data_transformer", "schema_validator"],
        "pass_criteria": "Cancelled records discarded, customer tier aggregations verified, zero schema violations."
    }
]

def get_scenario_by_id(scenario_id: str) -> Dict[str, Any]:
    for s in EVALUATION_SCENARIOS:
        if s["id"] == scenario_id:
            return s
    raise ValueError(f"Scenario '{scenario_id}' not found.")
