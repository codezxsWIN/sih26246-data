/**
 * app.js - Application Entry Point
 * Initializes the shell, router, and health monitor.
 */
const app = {
    auth: new window.AuthModule(),
    seeker: new window.SeekerDashboardModule(),
    employer: new window.EmployerDashboardModule(),
    state: {
        role: localStorage.getItem('lmi_role') || null,
        setRole(r) { this.role = r; buildSidebar(); }
    },
    router: window.Router // Ensure router is accessible on app
};
window.app = app;

function initApp() {
  buildSidebar();
  HealthMonitor.startHealthMonitor();
  Router.initRouter();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initApp);
} else {
  initApp();
}

function buildSidebar() {
  const nav = Utils.$("#sidebar-nav");
  if (!nav) return;
  nav.innerHTML = "";
  Object.entries(Router.routes).forEach(([path, route]) => {
    // Role-based visibility
    if (route.roles && app.state.role && !route.roles.includes(app.state.role)) {
        return;
    }
    if (route.hideInSidebar || (path === '/auth' && app.state.role)) return;

    const item = Utils.el("a", {
      className: "sidebar-nav__item",
      href: `#${path}`,
      "data-route": path,
      onClick: (e) => {
        e.preventDefault();
        Router.navigate(path);
      }
    },
      Utils.el("span", { className: "sidebar-nav__icon" }, route.icon),
      route.label
    );
    nav.appendChild(item);
  });
}
