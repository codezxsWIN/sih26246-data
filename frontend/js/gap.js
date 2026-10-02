/**
 * gap.js - Gap & Shortage Analysis Page
 */
window.GapPage = {
  async render() {
    const main = Utils.clearMain();
    main.appendChild(Utils.el("h1", { className: "page-title" }, "Gap & Shortage Analysis"));
    main.appendChild(Utils.el("p", { className: "page-subtitle" }, "Demand-supply gaps and shortage risk classification."));

    const filterBar = Utils.el("div", { className: "filter-bar" });
    const riskSelect = Utils.el("select", { className: "filter-select", id: "gap-risk-filter" },
      Utils.el("option", { value: "" }, "All Risk Levels"),
      Utils.el("option", { value: "Critical Shortage" }, "Critical Shortage"),
      Utils.el("option", { value: "Moderate Shortage" }, "Moderate Shortage"),
      Utils.el("option", { value: "Balanced" }, "Balanced"),
      Utils.el("option", { value: "Oversupply" }, "Oversupply")
    );
    riskSelect.addEventListener("change", () => this.reload());
    filterBar.appendChild(Utils.el("label", null, "Risk Category:"));
    filterBar.appendChild(riskSelect);
    main.appendChild(filterBar);

    const content = Utils.el("div", { id: "gap-content" });
    main.appendChild(content);
    this.reload();
  },

  async reload() {
    const content = Utils.$("#gap-content");
    if (!content) return;
    content.innerHTML = "";
    content.appendChild(Utils.loadingState());

    const riskFilter = Utils.$("#gap-risk-filter");
    const params = { limit: 100 };
    if (riskFilter && riskFilter.value) params.risk_category = riskFilter.value;

    try {
      const res = await API.getGaps(params);
      const data = res.data || [];
      content.innerHTML = "";

      if (data.length === 0) { content.appendChild(Utils.emptyState()); return; }

      // Chart
      const chartCard = Utils.el("div", { className: "card grid-full" });
      chartCard.appendChild(Utils.el("div", { className: "card__header" }, `Gap Scores (${data.length} records)`));
      const chartBody = Utils.el("div", { className: "card__body chart-container" });
      chartCard.appendChild(chartBody);
      content.appendChild(chartCard);
      setTimeout(() => Charts.renderBarChart(chartBody, data.slice(0, 15), {
        valueKey: "gap_score", color: "var(--color-critical)", maxVal: null
      }), 50);

      // Table
      const tableCard = Utils.el("div", { className: "card grid-full" });
      tableCard.appendChild(Utils.el("div", { className: "card__header" }, "Detailed Gap Assessment"));
      const tableBody = Utils.el("div", { className: "card__body", style: { overflowX: "auto" } });
      tableBody.appendChild(buildTable(
        ["Entity", "Type", "Geography", "Demand", "Supply", "Gap Score", "Gap Ratio", "Risk"],
        data.map(d => [
          d.entity_name,
          d.entity_type,
          d.geography_name,
          Utils.fmtScore(d.demand_score),
          Utils.fmtNum(d.supply_estimate),
          Utils.fmtScore(d.gap_score),
          Utils.fmtScore(d.gap_ratio),
          Utils.riskBadge(d.shortage_risk_category)
        ])
      ));
      tableCard.appendChild(tableBody);
      content.appendChild(tableCard);
    } catch (err) {
      content.innerHTML = "";
      content.appendChild(Utils.errorState(err.message));
    }
  }
};
