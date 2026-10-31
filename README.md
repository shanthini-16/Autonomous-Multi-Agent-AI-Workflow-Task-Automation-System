# Autonomous Multi-Agent AI Workflow & Task Automation System

An enterprise-grade, fully functional Autonomous Multi-Agent AI Workflow and Task Automation application implemented in Python and modern web technologies.

---

## 🎨 Theme & Color Palette

Designed strictly according to the refined modern dashboard specifications:
- **Mocha Brown (`#5B4632`)**: Card borders, panel headers, and subtle dividers.
- **Champagne Gold (`#F4D9A0`)**: Titles, active highlights, key metrics, and verified deliverable headers.
- **Burnt Amber (`#C87926`)**: Primary action buttons, active agent states, and interactive triggers.

---

## 🏗️ Core Architectural Modules

The application strictly implements all requirements specified in the project specification:

### 1. Multi-Agent Architecture
- **Planning Agent (`backend/agents/planning_agent.py`)**: Analyzes complex user requests, decomposes them into structured dependency-aware task graphs (DAG), identifies input/output requirements, and assigns specialized agents.
- **Research Agent (`backend/agents/research_agent.py`)**: Performs information retrieval, queries structured domain repositories (SEC filings, database metrics, climate time series, CVE databases, sales logs), and executes web searches.
- **Execution Agent (`backend/agents/execution_agent.py`)**: Executes computational algorithms, mathematical modeling (YoY variance, CAGR, ratios), data transformations, and sandboxed Python processing.
- **Verification Agent (`backend/agents/verification_agent.py`)**: Rigorously validates all intermediate and final outputs against strict JSON Schemas, physical sanity bounds, and consistency criteria before approving final synthesis.

### 2. Task Orchestrator & Dependency Resolver (`backend/orchestrator/orchestrator.py`)
- Master coordination engine that manages the workflow lifecycle:
  - Deconstructs requests via the Planning Agent.
  - Dynamically schedules tasks based on dependency completion.
  - Dispatches tasks to designated agents.
  - Provides thread-safe asynchronous and synchronous execution modes.

### 3. Controlled Tool Usage & Access Matrix (`backend/tools/`)
- Centralized tool registry with **strict permission enforcement**:
  - `web_search`, `fetch_url`, `knowledge_query`, `data_extractor` ➔ Authorized only for **Research Agent**.
  - `python_interpreter`, `math_evaluator`, `data_transformer` ➔ Authorized only for **Execution Agent**.
  - `schema_validator`, `sanity_checker`, `consistency_evaluator`, `output_verifier` ➔ Authorized only for **Verification Agent**.
- Any unauthorized tool invocation is immediately intercepted, denied with security alerts, and logged to the audit trail.

### 4. Shared Workflow Context & Blackboard (`backend/orchestrator/context.py`)
- Real-time shared blackboard state where agents deposit structured findings and downstream agents ingest prerequisite data.
- Chronological inter-agent message passing bus tracking every handoff (`TASK_ASSIGNMENT`, `RESULT_TRANSFER`, `RETRY_DIRECTIVE`, `VERIFICATION_PASSED`).

### 5. Validation and Verification Steps (`backend/tools/verification_tools.py`)
- Multi-tier quality assurance verifying data types, required keys, non-negative numbers, physical climate boundaries, and CVSS scale limits.
- Generates composite Verification Scores (0–100%) and rejects outputs falling below quality thresholds.

### 6. Failure Handling & Autonomous Retries
- Robust fault detection wrapping tool calls and agent executions.
- Configurable self-healing retry policy (up to 3 retries) with error context injection and backoff.
- Features a **"Simulate Fault & Test Autonomous Retry Recovery"** mode to demonstrate automated self-healing.

### 7. Real-Time Workflow Status Monitoring
- Live visual pipeline: Planning ➔ Research ➔ Execution ➔ Verification ➔ Delivery.
- Dynamic task cards with live status indicators (`QUEUED`, `RUNNING`, `RETRYING`, `COMPLETED`, `FAILED`), execution timer, and retry counters.
- Live Server-Sent Events (SSE) streaming state changes directly to the client.

### 8. System Evaluation & Real-World Benchmark Suite (`backend/evaluation/`)
- Evaluates the system across **5 real-world multi-step scenarios**:
  1. *Corporate Financial & Valuation Analysis* (AAPL, NVDA, MSFT growth & P/E)
  2. *Distributed Systems & High-Throughput Database Benchmarks* (PostgreSQL, MongoDB, Redis)
  3. *Scientific Climate Observation & Decadal Trend* (2016–2024 anomaly regression)
  4. *Cybersecurity Vulnerability & CVE Exposure Audit* (CVSS v3.1 prioritization)
  5. *E-Commerce Cleansing & Net Revenue Pipeline* (ETL filter & aggregation)
- Computes comprehensive performance metrics: Success Rate, Average Latency, Tool Call Volume, and Fault Resilience.

---

## 🚀 Getting Started

### 1. Prerequisites & Directory Setup
Set the working directory to:
```bash
cd "C:\Users\Shanthini\.gemini\antigravity\scratch\multi_agent_system"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch Application
```bash
python run.py
```
The server will start on:
👉 **`http://127.0.0.1:5000`**

Open this URL in any modern browser to interact with the system.

---

## 📁 Repository Structure

```
multi_agent_system/
├── backend/
│   ├── app.py                     # Flask server with REST & SSE APIs
│   ├── config.py                  # Server configuration and thresholds
│   ├── agents/
│   │   ├── base_agent.py          # Abstract Agent with tool calling & messaging
│   │   ├── planning_agent.py      # Request deconstruction & DAG formulation
│   │   ├── research_agent.py      # Knowledge retrieval & search queries
│   │   ├── execution_agent.py     # Computation, sandbox & transformations
│   │   └── verification_agent.py  # Schema validation & sanity verification
│   ├── tools/
│   │   ├── tool_registry.py       # Permission matrix & audit logger
│   │   ├── retrieval_tools.py     # Search, URL fetcher, knowledge store
│   │   ├── compute_tools.py       # Sandboxed Python interpreter, math evaluator
│   │   └── verification_tools.py  # Schema validator, sanity & consistency checks
│   ├── orchestrator/
│   │   ├── task.py                # Task entity, lifecycle states, retry counts
│   │   ├── context.py             # Shared blackboard & message bus
│   │   └── orchestrator.py        # Master orchestrator & retry supervisor
│   └── evaluation/
│       ├── scenarios.py           # 5 multi-step real-world scenarios
│       └── evaluator.py           # Benchmark runner & metrics aggregator
├── frontend/
│   ├── index.html                 # Single-page dashboard application
│   ├── css/
│   │   └── style.css              # Strictly styled (#171717, #06110C, #A31C1B)
│   └── js/
│       ├── api.js                 # API client & SSE stream connection
│       ├── app.js                 # Navigation & architecture inspector
│       ├── workflow.js            # Live workflow monitor & DAG renderer
│       └── evaluation.js          # Evaluation runner & KPI cards
├── run.py                         # Application launcher script
├── requirements.txt               # Dependencies
└── README.md                      # Documentation
```
