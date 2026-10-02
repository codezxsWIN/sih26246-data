/**
 * supply.js - Supply Estimation Page
 */
window.SupplyPage = {
  async render() {
    const main = Utils.clearMain();
    main.appendChild(Utils.el("h1", { className: "page-title" }, "Supply Estimation"));
    main.appendChild(Utils.el("p", { className: "page-subtitle" }, "Estimated labour supply based on PLFS, AISHE, and PMKVY datasets."));

    const content = Utils.el("div", { id: "supply-content" });
    main.appendChild(content);
    content.appendChild(Utils.loadingState());

    try {
      const res = await API.getSupplyEstimates({ limit: 100 });
      const data = res.data || [];
      content.innerHTML = "";

      if (data.length === 0) { content.appendChild(Utils.emptyState()); return; }

      // Chart
      const chartCard = Utils.el("div", { className: "card grid-full" });
      chartCard.appendChild(Utils.el("div", { className: "card__header" }, `Supply Distribution (${data.length} records)`));
      const chartBody = Utils.el("div", { className: "card__body chart-container" });
      chartCard.appendChild(chartBody);
      content.appendChild(chartCard);
      setTimeout(() => Charts.renderBarChart(chartBody, data.slice(0, 15), {
        valueKey: "estimated_supply", color: "var(--color-supply)", maxVal: null
      }), 50);

      // Table
      const tableCard = Utils.el("div", { className: "card grid-full" });
      tableCard.appendChild(Utils.el("div", { className: "card__header" }, "Supply Details"));
      const tableBody = Utils.el("div", { className: "card__body", style: { overflowX: "auto" } });
      tableBody.appendChild(buildTable(
        ["Entity", "Type", "Geography", "Est. Supply", "Education Flow", "Training Flow", "PLFS Baseline", "Confidence"],
        data.map(d => [
          d.entity_name,
          d.entity_type,
          d.geography_name,
          Utils.fmtNum(d.estimated_supply),
          Utils.fmtNum(d.education_flow),
          Utils.fmtNum(d.training_flow),
          Utils.fmtNum(d.plfs_unemployed_baseline),
          Utils.fmtNum(d.confidence_interval, 0)
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
