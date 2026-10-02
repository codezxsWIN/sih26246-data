/**
 * router.js - Hash-based routing
 */
const routes = {
  "/auth": { label: "Login", icon: "🔒", hideInSidebar: true, render: () => app.auth.render() },
  "/seeker": { label: "Job Seeker Portal", icon: "🧑‍💻", roles: ["seeker"], render: () => app.seeker.render() },
  "/employer": { label: "Employer Dashboard", icon: "🏢", roles: ["employer"], render: () => { document.getElementById('main-content').innerHTML = "<h2>Employer Portal (Coming Soon)</h2>"; } },
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

function getRoute() {
  const hash = window.location.hash.replace("#", "");
  
  if (!app.state.role) return "/auth";
  if (!hash || hash === "/auth") {
      if (app.state.role === 'seeker') return "/seeker";
      if (app.state.role === 'employer') return "/employer";
      if (app.state.role === 'policymaker') return "/dashboard";
  }
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
    // Check role authorization
    if (r.roles && app.state.role && !r.roles.includes(app.state.role)) {
        navigate(getRoute()); // redirect to default for role
        return;
    }
    r.render();
  } else {
    navigate(getRoute()); // reset to default if not found
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
