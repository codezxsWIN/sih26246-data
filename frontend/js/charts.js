/**
 * charts.js - Lightweight SVG chart rendering
 */
const SVG_NS = "http://www.w3.org/2000/svg";

function svgEl(tag, attrs) {
  const e = document.createElementNS(SVG_NS, tag);
  if (attrs) Object.entries(attrs).forEach(([k, v]) => e.setAttribute(k, v));
  return e;
}

function renderBarChart(container, data, opts = {}) {
  container.innerHTML = "";
  if (!data || data.length === 0) { container.appendChild(Utils.emptyState("No chart data")); return; }
  const W = opts.width || container.clientWidth || 600;
  const H = opts.height || 260;
  const margin = { top: 20, right: 20, bottom: 80, left: 50 };
  const w = W - margin.left - margin.right;
  const h = H - margin.top - margin.bottom;
  const labelKey = opts.labelKey || "entity_name";
  const valueKey = opts.valueKey || "demand_score";
  const color = opts.color || "var(--color-demand)";
  const maxVal = opts.maxVal || Math.max(...data.map(d => d[valueKey] || 0)) * 1.1 || 1;
  const barW = Math.max(12, Math.min(40, w / data.length - 4));
  const gap = (w - barW * data.length) / (data.length + 1);

  const svg = svgEl("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}` });
  const g = svgEl("g", { transform: `translate(${margin.left},${margin.top})` });
  svg.appendChild(g);

  // Y axis ticks
  for (let i = 0; i <= 4; i++) {
    const y = h - (i / 4) * h;
    const val = (maxVal * i / 4).toFixed(0);
    const line = svgEl("line", { x1: 0, y1: y, x2: w, y2: y, stroke: "#e2e8f0", "stroke-width": 1 });
    g.appendChild(line);
    const text = svgEl("text", { x: -8, y: y + 4, fill: "#94a3b8", "font-size": 11, "text-anchor": "end" });
    text.textContent = val;
    g.appendChild(text);
  }

  // Bars
  data.forEach((d, i) => {
    const x = gap + i * (barW + gap);
    const val = d[valueKey] || 0;
    const barH = (val / maxVal) * h;
    const y = h - barH;
    const rect = svgEl("rect", { x, y, width: barW, height: barH, fill: color, rx: 2 });
    g.appendChild(rect);

    // Tooltip title
    const title = svgEl("title");
    title.textContent = `${d[labelKey]}: ${Utils.fmtScore(val)}`;
    rect.appendChild(title);

    // Label
    const label = svgEl("text", {
      x: x + barW / 2, y: h + 12, fill: "#64748b", "font-size": 10,
      "text-anchor": "end", transform: `rotate(-40, ${x + barW / 2}, ${h + 12})`
    });
    label.textContent = (d[labelKey] || "").slice(0, 18);
    g.appendChild(label);
  });

  container.appendChild(svg);
}

function renderHorizontalBarChart(container, data, opts = {}) {
  container.innerHTML = "";
  if (!data || data.length === 0) { container.appendChild(Utils.emptyState("No chart data")); return; }
  const W = opts.width || container.clientWidth || 600;
  const barH = 22;
  const rowH = barH + 8;
  const margin = { top: 10, right: 60, bottom: 10, left: 160 };
  const H = margin.top + margin.bottom + data.length * rowH;
  const w = W - margin.left - margin.right;
  const labelKey = opts.labelKey || "entity_name";
  const valueKey = opts.valueKey || "demand_score";
  const color = opts.color || "var(--color-demand)";
  const maxVal = opts.maxVal || Math.max(...data.map(d => d[valueKey] || 0)) * 1.1 || 1;

  const svg = svgEl("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}` });
  const g = svgEl("g", { transform: `translate(${margin.left},${margin.top})` });
  svg.appendChild(g);

  data.forEach((d, i) => {
    const y = i * rowH;
    const val = d[valueKey] || 0;
    const barW = (val / maxVal) * w;

    // Label
    const label = svgEl("text", { x: -8, y: y + barH / 2 + 4, fill: "#334155", "font-size": 12, "text-anchor": "end" });
    label.textContent = (d[labelKey] || "").slice(0, 22);
    g.appendChild(label);

    // Bar
    const rect = svgEl("rect", { x: 0, y, width: Math.max(barW, 2), height: barH, fill: color, rx: 2 });
    const title = svgEl("title");
    title.textContent = `${d[labelKey]}: ${Utils.fmtScore(val)}`;
    rect.appendChild(title);
    g.appendChild(rect);

    // Value text
    const valText = svgEl("text", { x: barW + 6, y: y + barH / 2 + 4, fill: "#64748b", "font-size": 11 });
    valText.textContent = Utils.fmtScore(val);
    g.appendChild(valText);
  });

  container.appendChild(svg);
}

function renderShapBars(container, shapJSON) {
  const data = Utils.tryParseJSON(shapJSON);
  if (!data || typeof data !== "object") {
    container.textContent = "—";
    return;
  }
  const entries = Object.entries(data).sort((a, b) => b[1] - a[1]);
  const maxVal = Math.max(...entries.map(e => Math.abs(e[1]))) || 1;
  const W = container.clientWidth || 300;
  const rowH = 24;
  const margin = { left: 160, right: 40 };
  const H = entries.length * rowH + 10;
  const w = W - margin.left - margin.right;

  const svg = svgEl("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}` });
  const g = svgEl("g", { transform: `translate(${margin.left}, 5)` });
  svg.appendChild(g);

  entries.forEach(([key, val], i) => {
    const y = i * rowH;
    const barW = (Math.abs(val) / maxVal) * w;
    const color = val > 0 ? "var(--color-critical)" : "var(--color-supply)";
    const label = svgEl("text", { x: -8, y: y + 14, fill: "#334155", "font-size": 11, "text-anchor": "end" });
    label.textContent = key.replace(/_/g, " ");
    g.appendChild(label);
    const rect = svgEl("rect", { x: 0, y, width: Math.max(barW, 2), height: 18, fill: color, rx: 2 });
    g.appendChild(rect);
    const valText = svgEl("text", { x: barW + 6, y: y + 14, fill: "#64748b", "font-size": 11 });
    valText.textContent = val.toFixed(1);
    g.appendChild(valText);
  });

  container.innerHTML = "";
  container.appendChild(svg);
}

window.Charts = { renderBarChart, renderHorizontalBarChart, renderShapBars };
