/**
 * router.js - Hash-based routing
 */
const routes = {
  "/dashboard": { label: "National Overview", icon: "📊", render: () => window.DashboardPage.render() },
  "/demand": { label: "Demand Analysis", icon: "📈", render: () => window.DemandPage.render() },
  "/supply": { label: "Supply Estimation", icon: "👥", render: () => window.SupplyPage.render() },
  "/gap": { label: "Gap & Shortages", icon: "⚡", render: () => window.GapPage.render() },
  "/forecast": { label: "Forecast Explorer", icon: "🔮", render: () => window.ForecastPage.render() },
  "/shortage": { label: "Shortage Risk", icon: "🎯", render: () => window.ShortagePage.render() },
  "/policy": { label: "Policy Recommendations", icon: "📋", render: () => window.PolicyPage.render() },
  "/copilot": { label: "AI Policy Copilot", icon: "🤖", render: () => window.CopilotPage.render() }
};

function navigate(hash) {
  window.location.hash = hash;
}

function getRoute() {
  const hash = window.location.hash.replace("#", "") || "/dashboard";
  return hash;
}

function handleRoute() {
  const route = getRoute();
  const r = routes[route];

  // Update sidebar active state
  Utils.$$(".sidebar-nav__item").forEach(item => {
    item.classList.toggle("sidebar-nav__item--active", item.dataset.route === route);
  });

  if (r && r.render) {
    r.render();
  } else {
    routes["/dashboard"].render();
  }
}

function initRouter() {
  window.addEventListener("hashchange", handleRoute);
  if (!window.location.hash) {
    window.location.hash = "#/dashboard";
  } else {
    handleRoute();
  }
}

window.Router = { routes, navigate, getRoute, handleRoute, initRouter };
