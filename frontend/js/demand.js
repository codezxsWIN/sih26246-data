/**
 * demand.js - Demand Analysis Page
 */
window.DemandPage = {
  async render() {
    const main = Utils.clearMain();
    main.appendChild(Utils.el("h1", { className: "page-title" }, "Demand Analysis"));
    main.appendChild(Utils.el("p", { className: "page-subtitle" }, "Demand scores for occupations, skills, and sectors across geographies."));

    // Filter bar
    const filterBar = Utils.el("div", { className: "filter-bar" });
    const typeSelect = Utils.el("select", { className: "filter-select", id: "demand-type-filter" },
      Utils.el("option", { value: "" }, "All Types"),
      Utils.el("option", { value: "occupation" }, "Occupations"),
      Utils.el("option", { value: "skill" }, "Skills"),
      Utils.el("option", { value: "sector" }, "Sectors")
    );
    typeSelect.addEventListener("change", () => this.reload());
    filterBar.appendChild(Utils.el("label", null, "Entity Type:"));
    filterBar.appendChild(typeSelect);
    main.appendChild(filterBar);

    const content = Utils.el("div", { id: "demand-content" });
    main.appendChild(content);
    this.reload();
  },

  async reload() {
    const content = Utils.$("#demand-content");
    if (!content) return;
    content.innerHTML = "";
    content.appendChild(Utils.loadingState());

    const typeFilter = Utils.$("#demand-type-filter");
    const params = { limit: 100 };
    if (typeFilter && typeFilter.value) params.entity_type = typeFilter.value;

    try {
      const res = await API.getDemandScores(params);
      const data = res.data || [];
      content.innerHTML = "";

      if (data.length === 0) { content.appendChild(Utils.emptyState()); return; }

      // Chart
      const chartCard = Utils.el("div", { className: "card grid-full" });
      chartCard.appendChild(Utils.el("div", { className: "card__header" }, `Demand Score Distribution (${data.length} records)`));
      const chartBody = Utils.el("div", { className: "card__body chart-container" });
      chartCard.appendChild(chartBody);
      content.appendChild(chartCard);
      setTimeout(() => Charts.renderBarChart(chartBody, data.slice(0, 15), { valueKey: "demand_score", color: "var(--color-demand)" }), 50);

      // Table
      const tableCard = Utils.el("div", { className: "card grid-full" });
      tableCard.appendChild(Utils.el("div", { className: "card__header" }, "Detailed Demand Scores"));
      const tableBody = Utils.el("div", { className: "card__body", style: { overflowX: "auto" } });
      tableBody.appendChild(buildTable(
        ["Entity", "Type", "Geography", "Score", "Growth", "Employers", "PLFS", "Quality"],
        data.map(d => [
          d.entity_name,
          d.entity_type,
          d.geography_name,
          Utils.scoreBar(d.demand_score, 100, "var(--color-demand)"),
          Utils.fmtScore(d.posting_growth_component),
          Utils.fmtScore(d.employer_component),
          Utils.fmtScore(d.plfs_component),
          d.data_quality_grade || "—"
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
