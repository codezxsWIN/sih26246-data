/**
 * forecast.js - Forecast Explorer Page
 */
window.ForecastPage = {
  async render() {
    const main = Utils.clearMain();
    main.appendChild(Utils.el("h1", { className: "page-title" }, "Forecast Explorer"));
    main.appendChild(Utils.el("p", { className: "page-subtitle" }, "ML-generated demand projections at 3, 6, and 12-month horizons."));

    const filterBar = Utils.el("div", { className: "filter-bar" });
    const horizonSelect = Utils.el("select", { className: "filter-select", id: "forecast-horizon" },
      Utils.el("option", { value: "" }, "All Horizons"),
      Utils.el("option", { value: "3" }, "3 Months"),
      Utils.el("option", { value: "6" }, "6 Months"),
      Utils.el("option", { value: "12" }, "12 Months")
    );
    horizonSelect.addEventListener("change", () => this.reload());
    filterBar.appendChild(Utils.el("label", null, "Forecast Horizon:"));
    filterBar.appendChild(horizonSelect);
    main.appendChild(filterBar);

    const content = Utils.el("div", { id: "forecast-content" });
    main.appendChild(content);
    this.reload();
  },

  async reload() {
    const content = Utils.$("#forecast-content");
    if (!content) return;
    content.innerHTML = "";
    content.appendChild(Utils.loadingState());

    const horizonSelect = Utils.$("#forecast-horizon");
    const params = { limit: 100 };
    if (horizonSelect && horizonSelect.value) params.horizon_months = horizonSelect.value;

    try {
      const res = await API.getForecasts(params);
      const data = res.data || [];
      content.innerHTML = "";

      if (data.length === 0) {
        content.appendChild(Utils.emptyState("Insufficient historical data for reliable forecasting."));
        return;
      }

      // Chart
      const chartCard = Utils.el("div", { className: "card grid-full" });
      chartCard.appendChild(Utils.el("div", { className: "card__header" }, `Predicted Demand Scores (${data.length} forecasts)`));
      const chartBody = Utils.el("div", { className: "card__body chart-container" });
      chartCard.appendChild(chartBody);
      content.appendChild(chartCard);
      setTimeout(() => Charts.renderBarChart(chartBody, data.slice(0, 15), {
        valueKey: "predicted_demand_score", color: "var(--color-forecast)", maxVal: null
      }), 50);

      // Table
      const tableCard = Utils.el("div", { className: "card grid-full" });
      tableCard.appendChild(Utils.el("div", { className: "card__header" }, "Forecast Details & Feature Importance"));
      const tableBody = Utils.el("div", { className: "card__body", style: { overflowX: "auto" } });
      tableBody.appendChild(buildTable(
        ["Entity", "Geography", "Horizon", "Baseline", "Predicted", "Lower", "Upper", "Model", "Top Feature"],
        data.map(d => {
          const features = Utils.tryParseJSON(d.feature_importance_json);
          const topFeature = features ? Object.keys(features)[0] || "—" : "—";
          return [
            d.entity_name,
            d.geography_name,
            `${d.forecast_horizon_months}mo`,
            Utils.fmtScore(d.baseline_demand_score),
            Utils.el("strong", { style: { color: "var(--color-forecast)" } }, Utils.fmtScore(d.predicted_demand_score)),
            Utils.fmtScore(d.lower_bound),
            Utils.fmtScore(d.upper_bound),
            Utils.el("span", { className: "badge badge--forecast" }, d.model_type),
            topFeature.replace(/_/g, " ")
          ];
        })
      ));
      tableCard.appendChild(tableBody);
      content.appendChild(tableCard);
    } catch (err) {
      content.innerHTML = "";
      content.appendChild(Utils.errorState(err.message));
    }
  }
};
