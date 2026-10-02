/**
 * dashboard.js - National Overview Dashboard
 */
window.DashboardPage = {
  async render() {
    const main = Utils.clearMain();
    main.appendChild(Utils.el("h1", { className: "page-title" }, "National Overview"));
    main.appendChild(Utils.el("p", { className: "page-subtitle" }, "High-level summary of India's labour market intelligence."));
    main.appendChild(Utils.loadingState("Loading national overview..."));

    try {
      const [demandRes, supplyRes, gapRes, forecastRes, policyRes] = await Promise.all([
        API.getDemandScores({ limit: 100 }),
        API.getSupplyEstimates({ limit: 100 }),
        API.getGaps({ limit: 100 }),
        API.getForecasts({ limit: 100 }),
        API.getPolicyRecommendations({ limit: 100 })
      ]);

      const demand = demandRes.data || [];
      const supply = supplyRes.data || [];
      const gaps = gapRes.data || [];
      const forecasts = forecastRes.data || [];
      const policies = policyRes.data || [];

      const criticalGaps = gaps.filter(g => g.shortage_risk_category === "Critical Shortage");
      const highPolicies = policies.filter(p => p.priority_level === "HIGH");

      main.innerHTML = "";
      main.appendChild(Utils.el("h1", { className: "page-title" }, "National Overview"));
      main.appendChild(Utils.el("p", { className: "page-subtitle" }, "High-level summary of India's labour market intelligence."));

      // Stats grid
      const statsGrid = Utils.el("div", { className: "grid-stats" });
      statsGrid.appendChild(statCard("Total Demand Entities", demand.length, "Scored occupations, skills, sectors"));
      statsGrid.appendChild(statCard("Supply Estimates", supply.length, "Workforce availability records"));
      statsGrid.appendChild(statCard("Critical Shortages", criticalGaps.length, "Immediate intervention needed", "var(--color-critical)"));
      statsGrid.appendChild(statCard("Forecasts Available", forecasts.length, "3, 6, 12-month projections"));
      statsGrid.appendChild(statCard("Policy Interventions", policies.length, `${highPolicies.length} HIGH priority`));
      main.appendChild(statsGrid);

      // Two-column layout
      const grid2 = Utils.el("div", { className: "grid-2col" });

      // Top demand chart
      const demandCard = Utils.el("div", { className: "card" });
      demandCard.appendChild(Utils.el("div", { className: "card__header" }, "Top Demand Scores"));
      const demandChart = Utils.el("div", { className: "card__body chart-container" });
      demandCard.appendChild(demandChart);
      grid2.appendChild(demandCard);

      // Critical gaps table
      const gapCard = Utils.el("div", { className: "card" });
      gapCard.appendChild(Utils.el("div", { className: "card__header" }, `Critical Shortages (${criticalGaps.length})`));
      const gapBody = Utils.el("div", { className: "card__body" });
      if (criticalGaps.length === 0) {
        gapBody.appendChild(Utils.emptyState("No critical shortages detected."));
      } else {
        gapBody.appendChild(buildTable(
          ["Entity", "Geography", "Gap Score", "Risk"],
          criticalGaps.slice(0, 8).map(g => [
            g.entity_name,
            g.geography_name,
            Utils.fmtScore(g.gap_score),
            Utils.riskBadge(g.shortage_risk_category)
          ])
        ));
      }
      gapCard.appendChild(gapBody);
      grid2.appendChild(gapCard);
      main.appendChild(grid2);

      // Render chart after DOM insertion
      setTimeout(() => {
        Charts.renderHorizontalBarChart(demandChart, demand.slice(0, 10), {
          valueKey: "demand_score", color: "var(--color-demand)"
        });
      }, 50);

      // Supply distribution
      const supplyCard = Utils.el("div", { className: "card grid-full" });
      supplyCard.appendChild(Utils.el("div", { className: "card__header" }, "Top Supply Estimates"));
      const supplyChart = Utils.el("div", { className: "card__body chart-container" });
      supplyCard.appendChild(supplyChart);
      main.appendChild(supplyCard);
      setTimeout(() => {
        Charts.renderBarChart(supplyChart, supply.slice(0, 12), {
          valueKey: "estimated_supply", color: "var(--color-supply)", maxVal: null
        });
      }, 80);

    } catch (err) {
      main.innerHTML = "";
      main.appendChild(Utils.errorState(err.message));
    }
  }
};

function statCard(label, value, sub, color) {
  const card = Utils.el("div", { className: "stat-card" });
  card.appendChild(Utils.el("div", { className: "stat-card__label" }, label));
  const valEl = Utils.el("div", { className: "stat-card__value" }, String(value));
  if (color) valEl.style.color = color;
  card.appendChild(valEl);
  card.appendChild(Utils.el("div", { className: "stat-card__sub" }, sub));
  return card;
}

function buildTable(headers, rows) {
  const table = Utils.el("table", { className: "data-table" });
  const thead = Utils.el("thead");
  const headerRow = Utils.el("tr");
  headers.forEach(h => headerRow.appendChild(Utils.el("th", null, h)));
  thead.appendChild(headerRow);
  table.appendChild(thead);
  const tbody = Utils.el("tbody");
  rows.forEach(row => {
    const tr = Utils.el("tr");
    row.forEach(cell => {
      const td = Utils.el("td");
      if (cell instanceof HTMLElement) td.appendChild(cell);
      else td.textContent = cell == null ? "—" : String(cell);
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  return table;
}

window.buildTable = buildTable;
window.statCard = statCard;
