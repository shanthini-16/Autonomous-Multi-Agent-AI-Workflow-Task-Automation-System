/**
 * API Client for Autonomous Multi-Agent AI Workflow System
 */
const API_BASE = ""; // Relative paths to match Flask root

const api = {
  async getHealth() {
    const res = await fetch(`${API_BASE}/api/health`);
    return await res.json();
  },

  async getAgents() {
    const res = await fetch(`${API_BASE}/api/agents`);
    return await res.json();
  },

  async getTools() {
    const res = await fetch(`${API_BASE}/api/tools`);
    return await res.json();
  },

  async executeWorkflow(prompt, isAsync = true, simulateFailure = false) {
    const res = await fetch(`${API_BASE}/api/workflow/execute`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        request: prompt,
        async: isAsync,
        simulate_failure: simulateFailure
      })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.error || "Failed to execute workflow");
    }
    return await res.json();
  },

  async getWorkflowStatus(workflowId) {
    const res = await fetch(`${API_BASE}/api/workflow/status/${workflowId}`);
    if (!res.ok) throw new Error("Workflow not found");
    return await res.json();
  },

  subscribeToWorkflow(workflowId, onEvent, onComplete, onError) {
    const eventSource = new EventSource(`${API_BASE}/api/workflow/events/${workflowId}`);

    eventSource.onmessage = (e) => {
      try {
        const payload = JSON.parse(e.data);
        if (onEvent) onEvent(payload);

        if (payload.event_type === "WORKFLOW_COMPLETED" || payload.event_type === "WORKFLOW_FAILED") {
          eventSource.close();
          if (onComplete) onComplete(payload);
        }
      } catch (err) {
        console.error("Error parsing event stream payload:", err);
      }
    };

    eventSource.onerror = (err) => {
      console.warn("EventSource encountered connection interruption:", err);
      eventSource.close();
      if (onError) onError(err);
    };

    return eventSource;
  },

  async getEvalScenarios() {
    const res = await fetch(`${API_BASE}/api/eval/scenarios`);
    return await res.json();
  },

  async runEvaluation(scenarioId = null, simulateRetry = false) {
    const res = await fetch(`${API_BASE}/api/eval/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        scenario_id: scenarioId,
        simulate_retry: simulateRetry
      })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.error || "Evaluation run failed");
    }
    return await res.json();
  },

  async getEvalHistory() {
    const res = await fetch(`${API_BASE}/api/eval/history`);
    return await res.json();
  }
};
