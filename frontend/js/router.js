/**
 * router.js - Hash-based routing
 */
const routes = {
  "/auth": { label: "Login", icon: "🔒", hideInSidebar: true, render: () => app.auth.render() },
  "/seeker": { label: "Job Seeker Portal", icon: "🧑‍💻", roles: ["seeker"], render: () => app.seeker.render() },
  "/employer": { label: "Employer Dashboard", icon: "🏢", roles: ["employer"], render: () => app.employer.render() },
  "/dashboard": { label: "National Overview", icon: "📊", roles: ["policymaker"], render: () => window.DashboardPage.render() },
  "/demand": { label: "Demand Analysis", icon: "📈", roles: ["policymaker"], render: () => window.DemandPage.render() },
  "/supply": { label: "Supply Estimation", icon: "👥", roles: ["policymaker"], render: () => window.SupplyPage.render() },
  "/gap": { label: "Gap & Shortages", icon: "⚡", roles: ["policymaker"], render: () => window.GapPage.render() },
  "/forecast": { label: "Forecast Explorer", icon: "🔮", roles: ["policymaker"], render: () => window.ForecastPage.render() },
  "/shortage": { label: "Shortage Risk", icon: "🎯", roles: ["policymaker"], render: () => window.ShortagePage.render() },
  "/policy": { label: "Policy Recommendations", icon: "📋", roles: ["policymaker"], render: () => window.PolicyPage.render() },
  "/copilot": { label: "AI Policy Copilot", icon: "🤖", roles: ["policymaker"], render: () => window.CopilotPage.render() }
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
  
  if (!app.state.role) {
      navigate('/auth');
  } else if (!window.location.hash || window.location.hash === "#/auth") {
      navigate(getRoute());
  } else {
      handleRoute();
  }
}

window.Router = { routes, navigate, getRoute, handleRoute, initRouter };
