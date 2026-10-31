import os
import json
import time
from queue import Queue, Empty
from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS

from .config import Config
from .tools import registry
from .orchestrator import orchestrator, WorkflowContext
from .evaluation import SystemEvaluator, EVALUATION_SCENARIOS

# Initialize Flask application
app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app)

# Initialize System Evaluator
evaluator = SystemEvaluator(orchestrator)

# Event queues map for Server-Sent Events (workflow_id -> List[Queue])
event_subscribers = {}

def get_event_subscribers(workflow_id: str):
    if workflow_id not in event_subscribers:
        event_subscribers[workflow_id] = []
    return event_subscribers[workflow_id]

# --- Frontend Serving Routes ---

@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/css/<path:filename>")
def serve_css(filename):
    return send_from_directory(os.path.join(app.static_folder, "css"), filename)

@app.route("/js/<path:filename>")
def serve_js(filename):
    return send_from_directory(os.path.join(app.static_folder, "js"), filename)

# --- System & Metadata API Endpoints ---

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "HEALTHY",
        "system": "Autonomous Multi-Agent AI Workflow & Task Automation System",
        "python_version": "3.12",
        "active_agents": len(orchestrator.agents_map),
        "registered_tools": len(registry.get_all_tools()),
        "active_workflows": len(orchestrator.active_workflows),
        "timestamp": time.time()
    })

@app.route("/api/agents", methods=["GET"])
def get_agents():
    """Returns specialized agents fleet, assigned roles, and permitted tools."""
    return jsonify({
        "agents": orchestrator.get_agents_info(),
        "permissions_matrix": registry.get_permission_matrix()
    })

@app.route("/api/tools", methods=["GET"])
def get_tools():
    """Returns registered tools categorized with parameter definitions and access permissions."""
    return jsonify({
        "tools": registry.get_all_tools(),
        "permissions_matrix": registry.get_permission_matrix(),
        "recent_audit_log": registry.get_audit_log(20)
    })

# --- Workflow Execution API Endpoints ---

@app.route("/api/workflow/execute", methods=["POST"])
def execute_workflow():
    """
    Submits a complex user request for multi-agent autonomous execution.
    Supports asynchronous execution with live streaming or synchronous mode.
    """
    data = request.get_json() or {}
    user_request = data.get("request", "").strip()
    is_async = data.get("async", True)
    simulate_failure = data.get("simulate_failure", False)

    if not user_request:
        return jsonify({"error": "User request prompt cannot be empty."}), 400

    if is_async:
        context = orchestrator.run_workflow_async(user_request, simulate_failure=simulate_failure)
        
        # Setup event emitter hook to broadcast to SSE clients
        def event_forwarder(event_payload):
            subs = get_event_subscribers(context.workflow_id)
            for q in list(subs):
                try:
                    q.put_nowait(event_payload)
                except Exception:
                    pass

        context.add_listener(event_forwarder)

        return jsonify({
            "workflow_id": context.workflow_id,
            "status": context.status,
            "user_request": user_request,
            "message": "Autonomous workflow initiated successfully."
        })
    else:
        context = orchestrator.run_workflow_sync(user_request, simulate_failure=simulate_failure)
        return jsonify(context.to_dict())

@app.route("/api/workflow/status/<workflow_id>", methods=["GET"])
def get_workflow_status(workflow_id: str):
    """Returns detailed live state, DAG tasks, blackboard, and messages for a workflow."""
    context = orchestrator.get_workflow(workflow_id)
    if not context:
        return jsonify({"error": f"Workflow '{workflow_id}' not found."}), 404
    return jsonify(context.to_dict())

@app.route("/api/workflow/events/<workflow_id>", methods=["GET"])
def stream_workflow_events(workflow_id: str):
    """
    Server-Sent Events (SSE) streaming real-time workflow status,
    task state changes, agent messaging, and tool invocations.
    """
    context = orchestrator.get_workflow(workflow_id)
    if not context:
        return jsonify({"error": f"Workflow '{workflow_id}' not found."}), 404

    event_queue = Queue()
    subs = get_event_subscribers(workflow_id)
    subs.append(event_queue)

    def event_generator():
        # Emit initial state snapshot
        initial_data = json.dumps({
            "event_type": "INITIAL_SNAPSHOT",
            "workflow": context.to_dict()
        })
        yield f"data: {initial_data}\n\n"

        try:
            while True:
                try:
                    event = event_queue.get(timeout=25.0)
                    yield f"data: {json.dumps(event)}\n\n"
                    if event.get("event_type") in ("WORKFLOW_COMPLETED", "WORKFLOW_FAILED"):
                        break
                except Empty:
                    # Keep-alive heartbeat ping
                    yield f": heartbeat {time.time()}\n\n"
        finally:
            if event_queue in subs:
                subs.remove(event_queue)

    return Response(event_generator(), mimetype="text/event-stream")

# --- System Evaluation API Endpoints ---

@app.route("/api/eval/scenarios", methods=["GET"])
def list_eval_scenarios():
    """Lists available multi-step real-world evaluation scenarios."""
    return jsonify({
        "scenarios": evaluator.get_available_scenarios()
    })

@app.route("/api/eval/run", methods=["POST"])
def run_evaluation():
    """
    Runs multi-step real-world benchmark scenario(s) and computes performance metrics.
    """
    data = request.get_json() or {}
    scenario_id = data.get("scenario_id")
    simulate_retry = data.get("simulate_retry", False)

    if scenario_id:
        result = evaluator.run_scenario(scenario_id, simulate_retry=simulate_retry)
        return jsonify({"mode": "single_scenario", "result": result})
    else:
        summary = evaluator.run_full_benchmark(simulate_retry=simulate_retry)
        return jsonify({"mode": "full_benchmark", "summary": summary})

@app.route("/api/eval/history", methods=["GET"])
def get_eval_history():
    """Returns evaluation history and aggregate performance metrics."""
    return jsonify({
        "history": evaluator.get_evaluation_history()
    })

if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
