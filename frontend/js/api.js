/**
 * api.js - Centralized API Client for Labour Market Intelligence Engine
 * All backend communication goes through this module.
 */
const API_BASE_URL = window.APP_CONFIG?.API_BASE_URL || "http://localhost:8000";

async function apiFetch(path, options = {}) {
  const url = `${API_BASE_URL}${path}`;
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);
  try {
    const resp = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: { "Content-Type": "application/json", ...options.headers }
    });
    clearTimeout(timeout);
    if (!resp.ok) {
      throw new Error(`API ${resp.status}: ${resp.statusText} for ${path}`);
    }
    return await resp.json();
  } catch (err) {
    clearTimeout(timeout);
    if (err.name === "AbortError") {
      throw new Error(`Request timeout for ${path}`);
    }
    throw err;
  }
}

function qs(params) {
  const p = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== null && v !== undefined && v !== "") p.set(k, v);
  });
  const s = p.toString();
  return s ? `?${s}` : "";
}

const API = {
  getHealth() {
    return apiFetch("/health");
  },
  getDemandScores(params = {}) {
    return apiFetch(`/api/demand/scores${qs(params)}`);
  },
  getSupplyEstimates(params = {}) {
    return apiFetch(`/api/supply/estimates${qs(params)}`);
  },
  getGaps(params = {}) {
    return apiFetch(`/api/gap/gaps${qs(params)}`);
  },
  getForecasts(params = {}) {
    return apiFetch(`/api/forecast/predictions${qs(params)}`);
  },
  getPolicyRecommendations(params = {}) {
    return apiFetch(`/api/policy/recommendations${qs(params)}`);
  },
  queryCopilot(query) {
    return apiFetch("/api/copilot/query", {
      method: "POST",
      body: JSON.stringify({ query })
    });
  },
  runPipeline() {
    return apiFetch("/api/engine/run_pipeline", { method: "POST" });
  }
};

window.API = API;
