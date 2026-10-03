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

const ROLE_LABELS = { policymaker: "Policymaker portal", seeker: "Job seeker portal", employer: "Employer portal" };

function initApp() {
  const logout = Utils.$("#header-logout");
  if (logout) logout.addEventListener("click", () => app.auth.logout());
  const portal = Utils.$("#header-portal");
  if (portal) {
    portal.addEventListener("click", (event) => {
      event.preventDefault();
      app.auth.logout();
    });
  }
  buildSidebar();
  HealthMonitor.startHealthMonitor();
  Router.initRouter();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initApp);
} else {
  initApp();
}

function updateRoleChrome() {
  const role = app.state.role;
  const roleEl = Utils.$("#brand-role");
  if (roleEl) roleEl.textContent = role ? (ROLE_LABELS[role] || role) : "AI-Powered Analytics";
  const portal = Utils.$("#header-portal");
  if (portal) portal.hidden = !role;
  const logout = Utils.$("#header-logout");
  if (logout) logout.hidden = !role;
  document.body.dataset.role = role || "";
}

function buildSidebar() {
  updateRoleChrome();
  const nav = Utils.$("#sidebar-nav");
  if (!nav) return;
  nav.innerHTML = "";
  // Every page needs a role, so there is nothing to navigate to before login.
  if (!app.state.role) return;
  const current = window.location.hash.replace("#", "");
  Object.entries(Router.routes).forEach(([path, route]) => {
    // Role-based visibility
    if (route.roles && app.state.role && !route.roles.includes(app.state.role)) {
        return;
    }
    if (route.hideInSidebar || (path === '/auth' && app.state.role)) return;

    const item = Utils.el("a", {
      className: "sidebar-nav__item" + (path === current ? " sidebar-nav__item--active" : ""),
      href: `#${path}`,
      title: route.label,
      "data-route": path,
      onClick: (e) => {
        e.preventDefault();
        Router.navigate(path);
      }
    },
      route.nav || route.label,
      route.code ? Utils.el("small", null, route.code) : null
    );
    nav.appendChild(item);
  });
}
