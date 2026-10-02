/**
 * app.js - Application Entry Point
 * Initializes the shell, router, and health monitor.
 */
document.addEventListener("DOMContentLoaded", function () {
  buildSidebar();
  HealthMonitor.startHealthMonitor();
  Router.initRouter();
});

function buildSidebar() {
  const nav = Utils.$("#sidebar-nav");
  if (!nav) return;
  nav.innerHTML = "";
  Object.entries(Router.routes).forEach(([path, route]) => {
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
