const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const fetchWithHandling = async (url, options = {}) => {
  try {
    const response = await fetch(`${BASE_URL}${url}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`Error fetching ${url}:`, error);
    throw error;
  }
};

export const api = {
  // Demand
  getDemandScores: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return fetchWithHandling(`/api/demand/scores?${qs}`);
  },

  // Supply
  getSupplyEstimates: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return fetchWithHandling(`/api/supply/estimates?${qs}`);
  },

  // Gap
  getGaps: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return fetchWithHandling(`/api/gap/gaps?${qs}`);
  },

  // Forecast
  getForecasts: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return fetchWithHandling(`/api/forecast/predictions?${qs}`);
  },

  // Policy
  getPolicyRecommendations: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return fetchWithHandling(`/api/policy/recommendations?${qs}`);
  },

  // Copilot
  askCopilot: (query) => {
    return fetchWithHandling(`/api/copilot/query`, {
      method: "POST",
      body: JSON.stringify({ query }),
    });
  },

  // System
  checkHealth: () => {
    return fetchWithHandling(`/health`);
  },
  runPipeline: () => {
    return fetchWithHandling(`/api/engine/run_pipeline`, { method: "POST" });
  }
};
