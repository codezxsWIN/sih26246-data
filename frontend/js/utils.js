/**
 * utils.js - DOM helpers and formatters
 */
function $(sel, ctx) { return (ctx || document).querySelector(sel); }
function $$(sel, ctx) { return Array.from((ctx || document).querySelectorAll(sel)); }

function el(tag, attrs, ...children) {
  const e = document.createElement(tag);
  if (attrs) Object.entries(attrs).forEach(([k, v]) => {
    if (k === "className") e.className = v;
    else if (k === "style" && typeof v === "object") Object.assign(e.style, v);
    else if (k.startsWith("on")) e.addEventListener(k.slice(2).toLowerCase(), v);
    else e.setAttribute(k, v);
  });
  children.flat().forEach(c => {
    if (c == null) return;
    e.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
  });
  return e;
}

function fmtNum(n, dec) {
  if (n == null) return "—";
  if (typeof dec === "number") return Number(n).toFixed(dec);
  return Number(n).toLocaleString("en-IN");
}

function fmtScore(n) {
  if (n == null) return "—";
  return Number(n).toFixed(1);
}

function riskBadge(category) {
  if (!category) return el("span", { className: "badge" }, "—");
  const cls = category.includes("Critical") ? "badge--critical"
    : category.includes("Moderate") ? "badge--moderate"
    : category.includes("Oversupply") ? "badge--oversupply"
    : "badge--balanced";
  return el("span", { className: `badge ${cls}` }, category);
}

function priorityBadge(level) {
  if (!level) return el("span", { className: "badge" }, "—");
  const cls = level === "HIGH" ? "badge--prio-high"
    : level === "MEDIUM" ? "badge--prio-medium"
    : "badge--prio-low";
  return el("span", { className: `badge ${cls}` }, level);
}

function scoreBar(val, max, color) {
  max = max || 100;
  val = Math.min(val || 0, max);
  const pct = (val / max * 100).toFixed(0);
  const bar = el("span", { className: "progress-bar" },
    el("span", { className: "progress-bar__fill", style: { width: pct + "%", background: color || "var(--color-demand)" } })
  );
  return el("span", { className: "score-bar" }, bar, fmtScore(val));
}

function loadingState(msg) {
  return el("div", { className: "state-message state-message--loading", role: "status" },
    el("div", { className: "state-message__bar" }),
    el("div", { className: "state-message__text" }, msg || "Loading data...")
  );
}

function errorState(msg) {
  return el("div", { className: "state-message state-message--error", role: "alert" },
    el("div", { className: "state-message__text" }, msg || "Unable to connect to the backend. Make sure the FastAPI server is running on port 8000.")
  );
}

function emptyState(msg) {
  return el("div", { className: "state-message state-message--empty" },
    el("div", { className: "state-message__text" }, msg || "No data available for this selection.")
  );
}

function clearMain() {
  const main = $("#main-content");
  if (main) main.innerHTML = "";
  return main;
}

function tryParseJSON(str) {
  try { return JSON.parse(str); } catch { return null; }
}

window.Utils = { $, $$, el, fmtNum, fmtScore, riskBadge, priorityBadge, scoreBar, loadingState, errorState, emptyState, clearMain, tryParseJSON };
