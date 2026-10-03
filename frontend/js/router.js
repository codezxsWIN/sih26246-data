/**
 * router.js - Hash-based routing
 */
const routes = {
  "/auth": { label: "Login", icon: "🔒", hideInSidebar: true, render: () => app.auth.render() },
  "/seeker": { label: "Job Seeker Portal", nav: "Seeker portal", icon: "🧑‍💻", roles: ["seeker"], render: () => app.seeker.render() },
  "/employer": { label: "Employer Dashboard", nav: "Employer hub", icon: "🏢", roles: ["employer"], render: () => app.employer.render() },
  "/dashboard": { label: "National Overview", nav: "Overview", code: "S13", icon: "📊", roles: ["policymaker"], render: () => window.DashboardPage.render() },
  "/demand": { label: "Demand Analysis", nav: "Demand", code: "S04", icon: "📈", roles: ["policymaker"], render: () => window.DemandPage.render() },
  "/supply": { label: "Supply Estimation", nav: "Supply", code: "S05", icon: "👥", roles: ["policymaker"], render: () => window.SupplyPage.render() },
  "/gap": { label: "Gap & Shortages", nav: "Gap", code: "S07", icon: "⚡", roles: ["policymaker"], render: () => window.GapPage.render() },
  "/forecast": { label: "Forecast Explorer", nav: "Forecast", code: "S08", icon: "🔮", roles: ["policymaker"], render: () => window.ForecastPage.render() },
  "/shortage": { label: "Shortage Risk", nav: "Risk", code: "S09", icon: "🎯", roles: ["policymaker"], render: () => window.ShortagePage.render() },
  "/policy": { label: "Policy Recommendations", nav: "Policy", code: "S11", icon: "📋", roles: ["policymaker"], render: () => window.PolicyPage.render() },
  "/copilot": { label: "AI Policy Copilot", nav: "Copilot", code: "S12", icon: "🤖", roles: ["policymaker"], render: () => window.CopilotPage.render() }
};

function navigate(hash) {
  window.location.hash = hash;
}

function getDefaultRouteForRole(role) {
  if (role === 'seeker') return "/seeker";
  if (role === 'employer') return "/employer";
  return "/dashboard";
}

function getRoute() {
  const hash = window.location.hash.replace("#", "");
  
  if (!app.state.role) return "/auth";
  if (!hash || hash === "/auth") {
    return getDefaultRouteForRole(app.state.role);
  }
  
  const r = routes[hash];
  if (r && r.roles && !r.roles.includes(app.state.role)) {
    return getDefaultRouteForRole(app.state.role);
  }
  return hash;
}

function handleRoute() {
  const route = getRoute();
  
  // If hash doesn't match authorized route, update hash
  if (window.location.hash.replace("#", "") !== route) {
    navigate(route);
    return;
  }

  const r = routes[route];

  // Drives the page eyebrow (css/layout.css) and the browser tab title
  document.body.dataset.route = route;
  document.title = r ? `${r.label} · AI-Powered Labour Market Intelligence Engine` : "AI-Powered Labour Market Intelligence Engine";

  // Update sidebar active state
  Utils.$$(".sidebar-nav__item").forEach(item => {
    item.classList.toggle("sidebar-nav__item--active", item.dataset.route === route);
  });

  if (r && r.render) {
    r.render();
  } else {
    navigate(getDefaultRouteForRole(app.state.role));
  }
}

function initRouter() {
  window.addEventListener("hashchange", handleRoute);
  
  const target = getRoute();
  if (window.location.hash.replace("#", "") !== target) {
    window.location.hash = target;
  }
  handleRoute();
}

window.Router = { routes, navigate, getRoute, handleRoute, initRouter };
