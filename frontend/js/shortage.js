/**
 * shortage.js - Shortage Risk Page with SHAP explanations
 */
window.ShortagePage = {
  async render() {
    const main = Utils.clearMain();
    main.appendChild(Utils.el("h1", { className: "page-title" }, "Shortage Risk Analysis"));
    main.appendChild(Utils.el("p", { className: "page-subtitle" }, "Risk classification with SHAP feature contribution analysis."));

    const content = Utils.el("div", { id: "shortage-content" });
    main.appendChild(content);
    content.appendChild(Utils.loadingState());

    try {
      const res = await API.getGaps({ limit: 50 });
      const data = (res.data || []).filter(g => g.shortage_risk_category !== "Balanced" && g.shortage_risk_category !== "Oversupply");
      content.innerHTML = "";

      if (data.length === 0) { content.appendChild(Utils.emptyState("No shortage risks detected.")); return; }

      // Summary stats
      const critical = data.filter(d => d.shortage_risk_category === "Critical Shortage").length;
      const moderate = data.filter(d => d.shortage_risk_category === "Moderate Shortage").length;
      const stats = Utils.el("div", { className: "grid-stats" });
      stats.appendChild(statCard("Critical Shortages", critical, "Immediate action required", "var(--color-critical)"));
      stats.appendChild(statCard("Moderate Shortages", moderate, "Monitoring and planning needed", "var(--color-moderate)"));
      stats.appendChild(statCard("Total At-Risk Entities", data.length, "Occupations and skills"));
      content.appendChild(stats);

      // Risk table with expandable SHAP rows
      const tableCard = Utils.el("div", { className: "card grid-full" });
      tableCard.appendChild(Utils.el("div", { className: "card__header" }, "Risk Assessment with SHAP Drivers"));
      const tableBody = Utils.el("div", { className: "card__body", style: { overflowX: "auto" } });

      const table = Utils.el("table", { className: "data-table" });
      const thead = Utils.el("thead");
      const headerRow = Utils.el("tr");
      ["Entity", "Type", "Geography", "Gap Score", "Gap Ratio", "Risk", "SHAP Drivers"].forEach(h =>
        headerRow.appendChild(Utils.el("th", null, h))
      );
      thead.appendChild(headerRow);
      table.appendChild(thead);

      const tbody = Utils.el("tbody");
      data.forEach(d => {
        const tr = Utils.el("tr");
        [d.entity_name, d.entity_type, d.geography_name,
         Utils.fmtScore(d.gap_score), Utils.fmtScore(d.gap_ratio)].forEach(val => {
          const td = Utils.el("td");
          td.textContent = val == null ? "—" : String(val);
          tr.appendChild(td);
        });
        tr.appendChild(Utils.el("td", null, Utils.riskBadge(d.shortage_risk_category)));

        // SHAP cell
        const shapTd = Utils.el("td");
        const shapData = Utils.tryParseJSON(d.shap_drivers_json);
        if (shapData && typeof shapData === "object") {
          Object.entries(shapData).forEach(([k, v]) => {
            const line = Utils.el("div", { style: { fontSize: "11px", marginBottom: "2px" } },
              Utils.el("span", { style: { color: "var(--color-text-secondary)" } }, k.replace(/_/g, " ") + ": "),
              Utils.el("strong", null, String(Number(v).toFixed(1)))
            );
            shapTd.appendChild(line);
          });
        } else {
          shapTd.textContent = "—";
        }
        tr.appendChild(shapTd);
        tbody.appendChild(tr);
      });
      table.appendChild(tbody);
      tableBody.appendChild(table);
      tableCard.appendChild(tableBody);
      content.appendChild(tableCard);
    } catch (err) {
      content.innerHTML = "";
      content.appendChild(Utils.errorState(err.message));
    }
  }
};
