/**
 * health.js - Backend health monitoring
 */
let healthInterval = null;

async function checkHealth() {
  try {
    const data = await API.getHealth();
    AppState.setState("health", { status: "ok", data });
    updateStatusIndicators("ok");
  } catch (err) {
    AppState.setState("health", { status: "error", error: err.message });
    updateStatusIndicators("error");
  }
}

function updateStatusIndicators(status) {
  const cls = status === "ok" ? "status-dot--ok" : "status-dot--error";
  const label = status === "ok" ? "Connected" : "Offline";

  const dot = Utils.$("#status-backend-dot");
  const text = Utils.$("#status-backend-text");
  if (dot) { dot.className = "status-dot " + cls; }
  if (text) { text.textContent = label; }

  const dbDot = Utils.$("#status-db-dot");
  const dbText = Utils.$("#status-db-text");
  if (dbDot) { dbDot.className = "status-dot " + cls; }
  if (dbText) { dbText.textContent = label; }
}

function startHealthMonitor() {
  checkHealth();
  healthInterval = setInterval(checkHealth, 30000);
}

function stopHealthMonitor() {
  if (healthInterval) clearInterval(healthInterval);
}

window.HealthMonitor = { checkHealth, startHealthMonitor, stopHealthMonitor };
