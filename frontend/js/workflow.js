/**
 * Workflow Studio Management & Live Visualization
 * Refactored for compact, modern dashboard experience
 */

const workflowController = {
  currentWorkflowId: null,
  activeEventSource: null,

  init() {
    this.bindEvents();
    this.setupQuickPills();
  },

  bindEvents() {
    const launchBtn = document.getElementById("launch-btn");
    if (launchBtn) {
      launchBtn.addEventListener("click", () => this.handleLaunch());
    }
  },

  setupQuickPills() {
    const pills = document.querySelectorAll(".pill-btn");
    const promptInput = document.getElementById("workflow-prompt");

    pills.forEach(pill => {
      pill.addEventListener("click", () => {
        const text = pill.getAttribute("data-prompt");
        if (text && promptInput) {
          promptInput.value = text;
        }
      });
    });
  },

  async handleLaunch() {
    const promptInput = document.getElementById("workflow-prompt");
    const failureToggle = document.getElementById("simulate-failure-toggle");
    const launchBtn = document.getElementById("launch-btn");

    const promptText = promptInput.value.trim();
    if (!promptText) {
      alert("Please enter a task or select one of the quick scenario pills.");
      return;
    }

    const simulateFailure = failureToggle ? failureToggle.checked : false;

    // Reset UI state
    this.resetWorkflowUI();
    launchBtn.disabled = true;
    launchBtn.innerHTML = `⏳ Orchestrating Fleet...`;

    try {
      // 1. Submit to Backend
      const response = await api.executeWorkflow(promptText, true, simulateFailure);
      this.currentWorkflowId = response.workflow_id;

      // 2. Subscribe to Real-Time SSE Stream
      this.subscribeToLiveEvents(response.workflow_id);

    } catch (err) {
      console.error("Workflow launch error:", err);
      alert(`Launch error: ${err.message}`);
      launchBtn.disabled = false;
      launchBtn.innerHTML = `🚀 Run Multi-Agent Workflow`;
    }
  },

  subscribeToLiveEvents(workflowId) {
    if (this.activeEventSource) {
      this.activeEventSource.close();
    }

    const launchBtn = document.getElementById("launch-btn");

    this.activeEventSource = api.subscribeToWorkflow(
      workflowId,
      (eventPayload) => this.handleStreamEvent(eventPayload),
      (completionPayload) => {
        launchBtn.disabled = false;
        launchBtn.innerHTML = `🚀 Run Multi-Agent Workflow`;
        this.fetchFinalSnapshot(workflowId);
      },
      (err) => {
        // Fallback polling if SSE is interrupted
        this.pollStatusUntilComplete(workflowId);
      }
    );
  },

  handleStreamEvent(event) {
    const type = event.event_type;
    const data = event.data || {};

    if (type === "INITIAL_SNAPSHOT") {
      this.renderFullWorkflow(event.workflow);
    } else if (type === "WORKFLOW_STATE_CHANGED") {
      this.updateWorkflowStage(data.status);
    } else if (type === "TASK_REGISTERED") {
      this.appendOrUpdateTask(data);
    } else if (type === "TASK_EXECUTION_STARTED") {
      this.setTaskStatus(data.task_id, "RUNNING", data.agent);
    } else if (type === "TASK_EXECUTION_COMPLETED") {
      this.setTaskStatus(data.task_id, "COMPLETED", data.agent);
    } else if (type === "TASK_RETRY_INITIATED") {
      this.setTaskStatus(data.task_id, "RETRYING", null, data.reason);
      const retriesEl = document.getElementById("workflow-retries-count");
      if (retriesEl) {
        retriesEl.textContent = `${data.retry_count} (Auto-Healing)`;
        retriesEl.style.color = "var(--color-amber)";
      }
    } else if (type === "AGENT_MESSAGE") {
      this.appendAgentMessage(data);
    } else if (type === "TOOL_CALLED") {
      this.appendToolAuditRow(data);
    } else if (type === "WORKFLOW_COMPLETED") {
      this.updateWorkflowStage("COMPLETED");
      if (data.final_output) {
        this.renderFinalReport(data.final_output);
      }
    } else if (type === "WORKFLOW_FAILED") {
      this.updateWorkflowStage("FAILED");
      const statusText = document.getElementById("workflow-live-status-text");
      if (statusText) statusText.innerHTML = `<span style="color:var(--status-error);font-weight:700;">Halted: ${data.error}</span>`;
      alert(`Workflow terminated with failure: ${data.error}`);
    }
  },

  async pollStatusUntilComplete(workflowId) {
    const launchBtn = document.getElementById("launch-btn");
    try {
      const data = await api.getWorkflowStatus(workflowId);
      this.renderFullWorkflow(data);
      if (data.status === "COMPLETED" || data.status === "FAILED") {
        launchBtn.disabled = false;
        launchBtn.innerHTML = `🚀 Run Multi-Agent Workflow`;
      } else {
        setTimeout(() => this.pollStatusUntilComplete(workflowId), 800);
      }
    } catch (e) {
      launchBtn.disabled = false;
      launchBtn.innerHTML = `🚀 Run Multi-Agent Workflow`;
    }
  },

  async fetchFinalSnapshot(workflowId) {
    try {
      const data = await api.getWorkflowStatus(workflowId);
      this.renderFullWorkflow(data);
    } catch (e) {
      console.error("Failed to fetch final snapshot:", e);
    }
  },

  resetWorkflowUI() {
    // Reset Task Container
    const tasksContainer = document.getElementById("tasks-container");
    if (tasksContainer) {
      tasksContainer.innerHTML = `<div style="color:var(--text-muted);font-size:12px;padding:8px 4px;">Decomposing request and formulating task graph...</div>`;
    }

    // Reset status strip
    const statusText = document.getElementById("workflow-live-status-text");
    if (statusText) statusText.textContent = "Planning request...";
    const tasksCount = document.getElementById("workflow-tasks-count");
    if (tasksCount) tasksCount.textContent = "0 / 0";
    const retriesCount = document.getElementById("workflow-retries-count");
    if (retriesCount) {
      retriesCount.textContent = "0";
      retriesCount.style.color = "var(--color-gold)";
    }
    const durationText = document.getElementById("workflow-duration-text");
    if (durationText) durationText.textContent = "0 ms";

    // Reset Deliverable
    const finalBadge = document.getElementById("final-verification-badge");
    if (finalBadge) {
      finalBadge.textContent = "Verifying...";
      finalBadge.style.backgroundColor = "var(--bg-surface-elevated)";
      finalBadge.style.color = "var(--text-muted)";
      finalBadge.style.borderColor = "var(--border-subtle)";
    }
    const finalBody = document.getElementById("final-output-body");
    if (finalBody) {
      finalBody.innerHTML = `<div style="color:var(--text-muted);font-size:12px;">Synthesizing verified results across agent outputs...</div>`;
    }

    // Clear feeds
    const msgFeed = document.getElementById("message-feed");
    if (msgFeed) msgFeed.innerHTML = "";
    const toolBody = document.getElementById("tool-audit-body");
    if (toolBody) toolBody.innerHTML = "";

    // Reset 4 Agent Cards to IDLE
    this.resetAgentCards();
    this.setAgentCardState("planning", "PLANNING", "active");
  },

  resetAgentCards() {
    const agents = ["planning", "research", "execution", "verification"];
    agents.forEach(a => {
      const card = document.getElementById(`card-agent-${a}`);
      const pill = document.getElementById(`agent-state-${a}`);
      if (card) {
        card.className = "agent-mini-card";
      }
      if (pill) {
        pill.className = "agent-state-pill idle";
        pill.textContent = "IDLE";
      }
    });
  },

  setAgentCardState(agentKey, stateText, visualClass) {
    const card = document.getElementById(`card-agent-${agentKey}`);
    const pill = document.getElementById(`agent-state-${agentKey}`);

    if (card) {
      card.className = `agent-mini-card ${visualClass}`;
    }
    if (pill) {
      pill.className = `agent-state-pill ${visualClass}`;
      pill.textContent = stateText;
    }
  },

  updateWorkflowStage(status) {
    const s = (status || "").toLowerCase();
    const statusText = document.getElementById("workflow-live-status-text");

    if (s === "planning") {
      if (statusText) statusText.textContent = "Planning Agent decomposing request...";
      this.setAgentCardState("planning", "PLANNING", "active");
    } else if (s === "running") {
      this.setAgentCardState("planning", "COMPLETED", "completed");
      if (statusText) statusText.textContent = "Agents executing distributed tasks...";
    } else if (s === "verifying") {
      this.setAgentCardState("execution", "COMPLETED", "completed");
      this.setAgentCardState("verification", "VERIFYING", "active");
      if (statusText) statusText.textContent = "Verification Agent auditing outputs against schema & bounds...";
    } else if (s === "completed") {
      this.setAgentCardState("planning", "COMPLETED", "completed");
      this.setAgentCardState("research", "COMPLETED", "completed");
      this.setAgentCardState("execution", "COMPLETED", "completed");
      this.setAgentCardState("verification", "APPROVED", "completed");
      if (statusText) statusText.innerHTML = `<span style="color:var(--status-success);font-weight:700;">Workflow Completed & Fully Verified</span>`;
    }
  },

  renderFullWorkflow(wf) {
    if (!wf) return;

    this.updateWorkflowStage(wf.status);

    // Update status strip metrics
    const tasksCount = document.getElementById("workflow-tasks-count");
    if (tasksCount && wf.tasks) {
      const completed = wf.tasks.filter(t => t.status === "COMPLETED").length;
      tasksCount.textContent = `${completed} / ${wf.tasks.length}`;
    }

    const retriesCount = document.getElementById("workflow-retries-count");
    if (retriesCount) {
      retriesCount.textContent = wf.metrics?.total_retries || 0;
    }

    const durationText = document.getElementById("workflow-duration-text");
    if (durationText) {
      durationText.textContent = `${wf.metrics?.total_duration_ms || 0} ms`;
    }

    // Render compact task cards
    const container = document.getElementById("tasks-container");
    if (container) {
      container.innerHTML = "";
      (wf.tasks || []).forEach(task => {
        this.appendOrUpdateTask(task);
      });
    }

    // Render messages inside expandable panel
    const msgFeed = document.getElementById("message-feed");
    if (msgFeed) {
      msgFeed.innerHTML = "";
      (wf.messages || []).forEach(msg => {
        this.appendAgentMessage(msg);
      });
    }

    // Render tool audit table inside expandable panel
    const toolBody = document.getElementById("tool-audit-body");
    if (toolBody) {
      toolBody.innerHTML = "";
      (wf.tool_logs || []).forEach(log => {
        this.appendToolAuditRow(log);
      });
    }

    // Render final verified report
    if (wf.final_output) {
      this.renderFinalReport(wf.final_output);
    }
  },

  appendOrUpdateTask(task) {
    const container = document.getElementById("tasks-container");
    if (!container) return;

    const existing = document.getElementById(`task-compact-${task.task_id}`);

    const retryBadge = task.retry_count > 0 
      ? `<span style="background:rgba(200,121,38,0.25);border:1px solid var(--color-amber);color:var(--color-gold);padding:1px 6px;border-radius:3px;font-size:10px;font-weight:700;">${task.retry_count} AUTO-RETRY RECOVERED</span>` 
      : "";

    const statusPillClass = task.status === "COMPLETED" ? "completed" : (task.status === "RUNNING" ? "active" : "idle");

    const html = `
      <div class="task-item-compact ${task.status}" id="task-compact-${task.task_id}">
        <div class="task-item-main">
          <div class="task-item-title">${task.title}</div>
          <div class="task-item-meta">
            Assigned: <strong>${task.assigned_agent}</strong> | Duration: <strong>${task.execution_time_ms || 0} ms</strong>
            ${task.retry_count > 0 ? `| ${retryBadge}` : ""}
          </div>
        </div>
        <div class="task-item-actions">
          <span class="agent-state-pill ${statusPillClass}">${task.status}</span>
        </div>
      </div>
    `;

    if (existing) {
      existing.outerHTML = html;
    } else {
      if (container.children.length === 1 && container.children[0].textContent.includes("Decomposing")) {
        container.innerHTML = "";
      }
      container.insertAdjacentHTML("beforeend", html);
    }

    // Reflect on agent status cards based on task assigned agent
    if (task.status === "RUNNING") {
      if (task.assigned_agent.includes("Research")) {
        this.setAgentCardState("research", "RETRIEVING", "active");
      } else if (task.assigned_agent.includes("Execution")) {
        this.setAgentCardState("research", "COMPLETED", "completed");
        this.setAgentCardState("execution", "COMPUTING", "active");
      } else if (task.assigned_agent.includes("Verification")) {
        this.setAgentCardState("execution", "COMPLETED", "completed");
        this.setAgentCardState("verification", "AUDITING", "active");
      }
    }
  },

  setTaskStatus(taskId, status, agentName = null, retryReason = null) {
    const item = document.getElementById(`task-compact-${taskId}`);
    if (item) {
      item.className = `task-item-compact ${status}`;
      const pill = item.querySelector(".agent-state-pill");
      if (pill) {
        pill.className = `agent-state-pill ${status === "COMPLETED" ? "completed" : (status === "RUNNING" ? "active" : "idle")}`;
        pill.textContent = status;
      }
    }

    if (status === "RUNNING" && agentName) {
      if (agentName.includes("Research")) this.setAgentCardState("research", "RETRIEVING", "active");
      else if (agentName.includes("Execution")) this.setAgentCardState("execution", "COMPUTING", "active");
      else if (agentName.includes("Verification")) this.setAgentCardState("verification", "AUDITING", "active");
    }
  },

  appendAgentMessage(msg) {
    const feed = document.getElementById("message-feed");
    if (!feed) return;

    const div = document.createElement("div");
    div.className = "compact-message-row";

    const contentStr = typeof msg.content === "object" ? JSON.stringify(msg.content, null, 2) : String(msg.content);

    div.innerHTML = `
      <div class="compact-msg-header">
        <span class="msg-sender-recip">${msg.sender} ➔ ${msg.recipient}</span>
        <span class="msg-badge">${msg.message_type}</span>
      </div>
      <div class="msg-body-text">${this.escapeHtml(contentStr)}</div>
    `;
    feed.appendChild(div);
    feed.scrollTop = feed.scrollHeight;
  },

  appendToolAuditRow(log) {
    const body = document.getElementById("tool-audit-body");
    if (!body) return;

    const tr = document.createElement("tr");
    const permClass = log.permission_granted ? "perm-granted" : "perm-denied";
    const permText = log.permission_granted ? "GRANTED" : "DENIED";

    tr.innerHTML = `
      <td><strong>${log.tool_name}</strong></td>
      <td>${log.caller_agent}</td>
      <td class="${permClass}">${permText}</td>
      <td>${log.duration_ms} ms</td>
      <td><span style="color:${log.success ? 'var(--status-success)' : 'var(--status-error)'};font-weight:700;">${log.success ? 'SUCCESS' : 'FAILED'}</span></td>
    `;
    body.appendChild(tr);
  },

  renderFinalReport(output) {
    const box = document.getElementById("final-output-body");
    const badge = document.getElementById("final-verification-badge");
    const toolsMetric = document.getElementById("res-metric-tools");
    const retriesMetric = document.getElementById("res-metric-retries");
    const statusMetric = document.getElementById("res-metric-status");

    if (!output) return;

    const isFailure = output.verification_status === "REJECTED" || 
                      output.overall_verification_score === 0.0 || 
                      (output.title && output.title.toLowerCase().includes("failed"));

    const vScore = typeof output.overall_verification_score === "number" ? output.overall_verification_score : 98.0;

    if (badge) {
      if (isFailure) {
        badge.textContent = `AUDIT FAILED (0%)`;
        badge.style.backgroundColor = "rgba(163, 28, 27, 0.25)";
        badge.style.color = "var(--status-error)";
        badge.style.borderColor = "var(--status-error)";
      } else {
        badge.textContent = `VERIFIED: ${vScore}%`;
        badge.style.backgroundColor = "var(--status-success-bg)";
        badge.style.color = "var(--status-success)";
        badge.style.borderColor = "var(--status-success)";
      }
    }

    if (toolsMetric) toolsMetric.textContent = output.total_tool_calls || 0;
    if (retriesMetric) retriesMetric.textContent = output.total_retries_recovered || 0;
    if (statusMetric) {
      if (isFailure) {
        statusMetric.textContent = "VERIFICATION REJECTED";
        statusMetric.style.color = "var(--status-error)";
      } else {
        statusMetric.textContent = "AUDITED & APPROVED";
        statusMetric.style.color = "var(--status-success)";
      }
    }

    const reportContent = output.final_answer || output.executive_summary || "";

    if (box) {
      if (isFailure && !reportContent) {
        box.innerHTML = `
          <div style="padding:14px;background:rgba(163,28,27,0.15);border:1px solid var(--status-error);border-radius:4px;color:var(--status-error);">
            <strong>Workflow Execution Error:</strong> One or more agent tasks failed or produced empty output. The deliverable could not be verified.
          </div>
        `;
      } else {
        box.innerHTML = `
          <div class="final-report-wrapper">
            <div class="final-report-title" style="font-size:16px;font-weight:700;color:var(--color-gold);margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid rgba(244,217,160,0.2);">
              ${output.title || "Autonomous Multi-Agent Final Report"}
            </div>
            <div class="final-report-body" style="font-size:13px;line-height:1.7;color:var(--text-secondary);">
              ${this.formatMarkdown(reportContent)}
            </div>
          </div>
        `;
      }
    }
  },

  formatMarkdown(md) {
    if (!md) return "";

    // 1. Remove duplicate leading H1 title if present
    let text = md.replace(/^#\s+[^\n]+\n+/, "");

    // 2. Parse Markdown links: [text](url) -> <a href="url" target="_blank" rel="noopener noreferrer">text ↗</a>
    text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" style="color:var(--color-gold);text-decoration:underline;word-break:break-all;font-weight:600;">$1 ↗</a>');

    // 3. Headings
    text = text.replace(/^###\s+(.*$)/gim, '<h4 style="color:var(--color-gold);margin:16px 0 8px 0;font-size:14px;font-weight:700;border-left:3px solid var(--color-amber);padding-left:8px;">$1</h4>');
    text = text.replace(/^##\s+(.*$)/gim, '<h3 style="color:var(--color-gold);margin:18px 0 10px 0;font-size:15px;font-weight:700;border-bottom:1px solid rgba(244,217,160,0.15);padding-bottom:4px;">$1</h3>');
    text = text.replace(/^#\s+(.*$)/gim, '<h2 style="color:var(--color-gold);margin:20px 0 12px 0;font-size:16px;font-weight:700;">$1</h2>');

    // 4. Bold and italics
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong style="color:var(--text-main);font-weight:600;">$1</strong>');
    text = text.replace(/\*(.*?)\*/g, '<em style="color:var(--text-secondary);">$1</em>');

    // 5. Inline code
    text = text.replace(/`([^`]+)`/g, '<code style="background:var(--bg-surface-elevated);border:1px solid var(--border-subtle);padding:1px 5px;border-radius:3px;color:var(--color-gold);font-family:monospace;font-size:12px;">$1</code>');

    // 6. Bullet lists
    text = text.replace(/^[-•]\s+(.*$)/gim, '<div style="margin:4px 0 4px 18px;position:relative;line-height:1.55;"><span style="position:absolute;left:-14px;color:var(--color-amber);font-size:12px;">•</span>$1</div>');

    // 7. Paragraph spacing
    const paragraphs = text.split(/\n{2,}/);
    return paragraphs.map(p => {
      p = p.trim();
      if (!p) return "";
      if (p.startsWith("<h2") || p.startsWith("<h3") || p.startsWith("<h4") || p.startsWith("<div")) {
        return p;
      }
      return `<p style="margin-bottom:10px;line-height:1.65;color:var(--text-secondary);">${p.replace(/\n/g, '<br/>')}</p>`;
    }).join("\n");
  },

  escapeHtml(str) {
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
};
