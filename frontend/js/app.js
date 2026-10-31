/**
 * Main Application Entry Point & Navigation
 * Refactored for clean agent architecture display and expandable tool details
 */

document.addEventListener("DOMContentLoaded", async () => {
  setupNavigation();
  initSystemHealth();
  workflowController.init();
  evaluationController.init();
  await loadArchitectureAndPermissions();
});

function setupNavigation() {
  const tabBtns = document.querySelectorAll(".nav-tab-btn");
  const tabPanes = document.querySelectorAll(".tab-pane");

  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-tab");

      tabBtns.forEach(b => b.classList.remove("active"));
      tabPanes.forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      const targetPane = document.getElementById(targetId);
      if (targetPane) {
        targetPane.classList.add("active");
      }
    });
  });
}

async function initSystemHealth() {
  try {
    const health = await api.getHealth();
    const statusText = document.getElementById("header-status-text");
    const agentsCount = document.getElementById("header-agents-count");
    const toolsCount = document.getElementById("header-tools-count");

    if (statusText) statusText.textContent = "System Operational";
    if (agentsCount) agentsCount.textContent = health.active_agents;
    if (toolsCount) toolsCount.textContent = health.registered_tools;
  } catch (err) {
    console.error("Health check error:", err);
  }
}

async function loadArchitectureAndPermissions() {
  try {
    const [agentsData, toolsData] = await Promise.all([
      api.getAgents(),
      api.getTools()
    ]);

    renderAgentsFleet(agentsData.agents);
    renderPermissionsMatrix(agentsData.agents, toolsData.tools, toolsData.permissions_matrix);
  } catch (err) {
    console.error("Failed to load architecture info:", err);
  }
}

function renderAgentsFleet(agents) {
  const container = document.getElementById("agents-fleet-container");
  if (!container) return;

  container.innerHTML = "";
  agents.forEach(agent => {
    const card = document.createElement("div");
    card.className = "agent-arch-card";

    const hasTools = agent.allowed_tools && agent.allowed_tools.length > 0;
    const toolsTags = hasTools
      ? agent.allowed_tools.map(t => `<span class="tool-tag">${t}</span>`).join(" ")
      : `<span style="color:var(--text-muted);font-size:11px;">Direct Orchestration / Meta-Control (No Direct Execution Tools)</span>`;

    const iconMap = {
      "Planning Agent": "🎯",
      "Research Agent": "🔍",
      "Execution Agent": "⚙️",
      "Verification Agent": "🛡️"
    };

    const icon = iconMap[agent.name] || "🤖";

    card.innerHTML = `
      <div>
        <div class="agent-arch-header">
          <span class="agent-arch-name">${icon} ${agent.name}</span>
          <span class="agent-arch-role">${agent.role}</span>
        </div>
        <div class="agent-arch-desc">${agent.description}</div>
      </div>

      <!-- Expandable Details for Tool Permissions -->
      <details class="agent-arch-tools-details">
        <summary>View Authorized Tools (${agent.allowed_tools.length})</summary>
        <div class="agent-tools-tags-cloud">
          ${toolsTags}
        </div>
      </details>
    `;
    container.appendChild(card);
  });
}

function renderPermissionsMatrix(agents, tools, permissionsMatrix) {
  const tbody = document.getElementById("matrix-table-body");
  if (!tbody) return;

  tbody.innerHTML = "";

  tools.forEach(tool => {
    const tr = document.createElement("tr");

    let agentCells = "";
    agents.forEach(agent => {
      const allowedTools = permissionsMatrix[agent.name] || [];
      const hasPerm = allowedTools.includes(tool.name);
      
      const badge = hasPerm
        ? `<span class="perm-granted">GRANTED</span>`
        : `<span class="perm-denied">DENIED</span>`;

      agentCells += `<td style="text-align:center;">${badge}</td>`;
    });

    tr.innerHTML = `
      <td><strong>${tool.name}</strong></td>
      <td><span class="scenario-tag">${tool.category}</span></td>
      <td style="font-size:11px;color:var(--text-secondary);">${tool.description}</td>
      ${agentCells}
    `;

    tbody.appendChild(tr);
  });
}
