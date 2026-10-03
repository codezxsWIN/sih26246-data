/**
 * employer.js - Employer Talent Sourcing & Market Intelligence Portal
 */
class EmployerDashboardModule {
    constructor() {
        this.container = document.getElementById('main-content');
        this.data = null;
    }

    async render() {
        this.container.innerHTML = `
            <div class="state-message state-message--loading" role="status">
                <div class="state-message__bar"></div>
                <div class="state-message__text">Loading Employer Market Intelligence...</div>
            </div>
        `;

        try {
            const res = await fetch('http://localhost:8000/api/employer/overview');
            this.data = await res.json();
            this.renderView();
        } catch (err) {
            console.error("Employer overview error:", err);
            this.container.innerHTML = `
                <section class="card">
                    <div class="card__header">Unable to load market data</div>
                    <div class="card__body"><p class="text-muted">Ensure the local API server is active.</p></div>
                </section>
            `;
        }
    }

    renderView() {
        const occupations = this.data.available_occupations || [];
        const optionsHtml = occupations.map(o => `<option value="${o}">${o}</option>`).join('');

        this.container.innerHTML = `
            <h1 class="page-title">Employer Talent Intelligence & Sourcing Hub</h1>
            <p class="page-subtitle">Analyze regional talent pools, predict hiring difficulty, and locate high-supply talent hubs.</p>
            <div class="page-actions">
                <button class="btn btn-secondary" onclick="app.auth.logout()">Logout</button>
            </div>

            <!-- Role Sourcing Filter Card -->
            <section class="card">
                <div class="card__header">Target Occupation Intelligence</div>
                <div class="card__body employer-filter">
                    <label class="control">
                        <span class="control__label">Select Target Role</span>
                        <select id="employer-role-select" class="filter-select filter-select--wide">
                            <option value="">-- All Occupations --</option>
                            ${optionsHtml}
                        </select>
                    </label>
                    <button class="btn btn-primary" onclick="app.employer.analyzeRole()">Analyze Regional Feasibility</button>
                </div>
            </section>

            <!-- Dynamic Search Results -->
            <div id="employer-analysis-results"></div>

            <!-- Overview Grid: Talent Hubs & High Competition -->
            <div class="grid-2">
                <!-- Top Talent Supply Hubs -->
                <section class="card">
                    <div class="card__header">
                        <span>Top Regional Talent Pools</span>
                        <span class="badge badge--balanced">High Supply</span>
                    </div>
                    <div class="card__body">
                        <p class="text-muted card__lede">Top states with the largest pools of ready workers:</p>
                        <div class="table-container">
                            <table class="data-table">
                                <thead>
                                    <tr>
                                        <th>State</th>
                                        <th>Occupation</th>
                                        <th>Supply Pool</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${(this.data.talent_hubs || []).slice(0, 7).map(hub => `
                                        <tr>
                                            <td>${hub.geography_name}</td>
                                            <td>${hub.entity_name}</td>
                                            <td><span class="tag">${Number(hub.supply_pool).toLocaleString()}</span></td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </section>

                <!-- High Competition Watchlist -->
                <section class="card">
                    <div class="card__header">
                        <span>Hiring Scarcity & Competition Watchlist</span>
                        <span class="badge badge--critical">Critical Shortage</span>
                    </div>
                    <div class="card__body">
                        <p class="text-muted card__lede">Roles with intense competition & candidate scarcity:</p>
                        <div class="table-container">
                            <table class="data-table">
                                <thead>
                                    <tr>
                                        <th>Role</th>
                                        <th>State</th>
                                        <th>Demand</th>
                                        <th>Competition</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${(this.data.high_competition_roles || []).slice(0, 7).map(role => `
                                        <tr>
                                            <td>${role.entity_name}</td>
                                            <td>${role.geography_name}</td>
                                            <td>${role.demand_score.toFixed(1)}</td>
                                            <td><span class="badge badge--critical">High Scarcity</span></td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </section>
            </div>
        `;

        // Automatically trigger initial analysis for first occupation
        if (occupations.length > 0) {
            this.analyzeRole(occupations[0]);
        }
    }

    async analyzeRole(prefillRole) {
        const select = document.getElementById('employer-role-select');
        const role = prefillRole || (select ? select.value : "");
        if (select && prefillRole) select.value = prefillRole;

        const resultsContainer = document.getElementById('employer-analysis-results');
        if (!resultsContainer) return;

        resultsContainer.innerHTML = `
            <div class="state-message state-message--loading" role="status">
                <div class="state-message__bar"></div>
                <div class="state-message__text">Analyzing hiring feasibility for <strong>${role || "all roles"}</strong>...</div>
            </div>
        `;

        try {
            const res = await fetch('http://localhost:8000/api/employer/talent-analysis', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ occupation: role })
            });

            const data = await res.json();
            this.renderAnalysisResults(data, resultsContainer);
        } catch (err) {
            console.error("Talent analysis error:", err);
            resultsContainer.innerHTML = `<div class="state-message state-message--error" role="alert"><div class="state-message__text">Analysis could not be completed.</div></div>`;
        }
    }

    renderAnalysisResults(data, container) {
        if (!data.regions || data.regions.length === 0) {
            container.innerHTML = `
                <div class="state-message state-message--empty">
                    <div class="state-message__text">No specific regional shortage data found for this selection.</div>
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <section class="card">
                <div class="card__header">
                    <span>Sourcing Feasibility & Strategic Recommendations</span>
                    <span class="card__meta">${data.target_role}</span>
                </div>
                <div class="card__body">
                <div class="table-container">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Region</th>
                                <th>Est. Supply Pool</th>
                                <th>Demand Index</th>
                                <th>Hiring Difficulty</th>
                                <th>Strategic Sourcing Advice</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.regions.slice(0, 8).map(r => `
                                <tr>
                                    <td><strong>${r.geography_name}</strong></td>
                                    <td>${Number(r.supply_estimate).toLocaleString()}</td>
                                    <td>${Number(r.demand_score).toFixed(1)}</td>
                                    <td>
                                        <span class="badge ${r.difficulty_badge === 'danger' ? 'badge--critical' : (r.difficulty_badge === 'success' ? 'badge--balanced' : 'badge--moderate')}">
                                            ${r.hiring_difficulty}
                                        </span>
                                    </td>
                                    <td style="font-size: 0.88rem; color: var(--color-text-secondary);">${r.strategic_recommendation}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
                </div>
            </section>
        `;
    }
}

window.EmployerDashboardModule = EmployerDashboardModule;
