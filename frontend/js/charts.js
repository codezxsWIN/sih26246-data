/**
 * charts.js - Lightweight SVG chart rendering
 */
const SVG_NS = "http://www.w3.org/2000/svg";

function svgEl(tag, attrs) {
  const e = document.createElementNS(SVG_NS, tag);
  if (attrs) Object.entries(attrs).forEach(([k, v]) => e.setAttribute(k, v));
  return e;
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

// Adapted from Legion Dev's Evil Charts Hover Trace Bar Chart (MIT).
// https://evilcharts.com/r/hover-trace-bar-chart.json
function renderHoverTrace(container, data, opts = {}, horizontal = false) {
  container.innerHTML = '';
  if (!data?.length) { container.appendChild(Utils.emptyState('No chart data')); return; }
  const key = opts.valueKey || 'demand_score';
  const labelKey = opts.labelKey || 'entity_name';
  const values = data.map(item => Math.max(0, Number(item[key]) || 0));
  const peak = values.indexOf(Math.max(...values));
  const max = Math.max(Number(opts.maxVal) || 0, ...values, 1) * (opts.maxVal ? 1 : 1.12);
  const isMoney = opts.currency || /salary|wage|budget|cost|price|revenue|amount/.test(key);
  const format = value => value.toLocaleString('en-IN', isMoney
    ? { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }
    : { maximumFractionDigits: key === 'estimated_supply' ? 0 : 1 });
  const header = Utils.el('div', {className: 'trace-header'});
  const metric = Utils.el('div');
  metric.appendChild(Utils.el('span', {className: 'trace-caption'}, isMoney ? 'Amount · INR' : key === 'estimated_supply' ? 'Estimated workforce · people' : key.replace(/_/g, ' ')));
  const readout = Utils.el('strong', {className: 'trace-value'}, format(values[peak]));
  metric.appendChild(readout);
  const selection = Utils.el('div', {className: 'trace-selection'});
  const name = Utils.el('strong', null);
  const geography = Utils.el('span');
  selection.append(name, geography);
  header.append(metric, selection);
  container.appendChild(header);
  const scroller = Utils.el('div', {className: 'trace-scroll'});
  container.appendChild(scroller);
  const W = Math.max(container.clientWidth - 40, horizontal ? 560 : data.length * 64, 620);
  const H = horizontal ? Math.max(400, data.length * 40 + 60) : 390;
  const left = horizontal ? 220 : 68, right = 28, top = 28, bottom = horizontal ? 24 : 92;
  const w = W - left - right, h = H - top - bottom;
  const svg = svgEl('svg', {width: W, height: H, viewBox: `0 0 ${W} ${H}`, class: 'trace-chart', role: 'group', 'aria-label': 'Interactive bar chart. Focus a bar or use arrow keys to compare values.'});
  container.closest('.card')?.classList.add('trace-card');
  scroller.appendChild(svg);
  for (let i = 0; i <= 4; i++) {
    const amount = max * i / 4;
    const x = left + w * i / 4, y = top + h - h * i / 4;
    svg.appendChild(svgEl('line', horizontal ? {x1:x,x2:x,y1:top,y2:top+h,class:'trace-grid'} : {x1:left,x2:left+w,y1:y,y2:y,class:'trace-grid'}));
    const text = svgEl('text', horizontal ? {x,y:top-12,'text-anchor':'middle'} : {x:left-12,y:y+4,'text-anchor':'end'});
    text.textContent = format(amount);
    svg.appendChild(text);
  }
  const bars = [], targets = [];
  data.forEach((item, index) => {
    const slot = horizontal ? h/data.length : w/data.length;
    const size = slot * 0.65;
    const length = values[index]/max * (horizontal ? w : h);
    const x = horizontal ? left : left + slot*index + (slot-size)/2;
    const y = horizontal ? top + slot*index + (slot-size)/2 : top+h-length;
    const group = svgEl('g', {tabindex:0, role:'button', 'aria-label': `${item[labelKey]}, ${item.geography_name || ''}: ${format(values[index])}`, class:'trace-bar-target'});
    const hit = svgEl('rect', {x: horizontal ? 0 : x-(slot-size)/2, y: horizontal ? top+slot*index : top, width: horizontal ? W : slot, height: horizontal ? slot : h, fill:'transparent'});
    const bar = svgEl('rect', {x,y,width:horizontal ? length : size,height:horizontal ? size : length,fill:opts.color || 'var(--color-demand)',class:'trace-bar'});
    const label = svgEl('text', horizontal ? {x:left-14,y:y+size/2+4,'text-anchor':'end'} : {x:x+size/2,y:top+h+20,'text-anchor':'end',transform:`rotate(-35 ${x+size/2} ${top+h+20})`});
    label.textContent = String(item[labelKey] || '').slice(0, horizontal ? 28 : 20);
    group.append(hit, bar, label);
    group.addEventListener('pointerenter', () => select(index));
    group.addEventListener('focus', () => select(index));
    group.addEventListener('click', () => select(index));
    group.addEventListener('keydown', event => {
      if (['ArrowRight','ArrowDown','ArrowLeft','ArrowUp'].includes(event.key)) {
        event.preventDefault();
        const next = Math.max(0, Math.min(data.length-1, index + (['ArrowRight','ArrowDown'].includes(event.key) ? 1 : -1)));
        targets[next].focus();
      }
    });
    bars.push(bar); targets.push(group); svg.appendChild(group);
  });
  const trace = svgEl('g', {'pointer-events':'none'});
  const line = svgEl('line', {class:'trace-line','stroke-dasharray':'4 5'});
  const dot = svgEl('circle', {r:4,fill:'var(--ink)'});
  trace.append(line,dot); svg.appendChild(trace);
  let current = values[peak], target = current, frame = null;
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function paint() {
    readout.textContent = format(current);
    if (horizontal) {
      const x = left + current/max*w;
      Object.entries({x1:x,x2:x,y1:top,y2:top+h}).forEach(([k,v]) => line.setAttribute(k,v));
      dot.setAttribute('cx',x); dot.setAttribute('cy',top+h);
    } else {
      const y = top+h-current/max*h;
      Object.entries({x1:left,x2:left+w,y1:y,y2:y}).forEach(([k,v]) => line.setAttribute(k,v));
      dot.setAttribute('cx',left+w); dot.setAttribute('cy',y);
    }
  }
  function animate() {
    if (!container.isConnected) { frame = null; return; }
    current += (target-current)*0.18;
    if (Math.abs(target-current) < Math.max(0.01,max/10000)) current = target;
    paint();
    frame = current !== target ? requestAnimationFrame(animate) : null;
  }
  function select(index) {
    target = values[index];
    name.textContent = data[index][labelKey] || 'Selected category';
    geography.textContent = data[index].geography_name || 'Hover or focus a bar to explore';
    bars.forEach((bar,i) => bar.style.opacity = i === index ? '1' : '0.2');
    if (reduced) { current = target; paint(); }
    else if (frame === null) frame = requestAnimationFrame(animate);
  }
  svg.addEventListener('pointerleave', () => select(peak));
  svg.addEventListener('focusout', event => { if (!svg.contains(event.relatedTarget)) select(peak); });
  container.appendChild(Utils.el('p', {className:'trace-hint'}, 'Hover, tap, or focus a bar to compare · Arrow keys move between bars'));
  select(peak); paint();
}
function renderBarChart(container, data, opts = {}) { renderHoverTrace(container, data, opts); }
function renderHorizontalBarChart(container, data, opts = {}) { renderHoverTrace(container, data, opts, true); }
window.Charts = { renderBarChart, renderHorizontalBarChart, renderShapBars };
