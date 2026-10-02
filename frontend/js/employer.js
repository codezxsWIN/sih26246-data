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
            <div class="state-message">
                <div class="state-message__icon"><span class="spinner"></span></div>
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
                <div class="card-glass" style="margin: 20px;">
                    <h3>Unable to load market data</h3>
                    <p class="text-muted">Ensure the local API server is active.</p>
                </div>
            `;
        }
    }

    renderView() {
        const occupations = this.data.available_occupations || [];
        const optionsHtml = occupations.map(o => `<option value="${o}">${o}</option>`).join('');

        this.container.innerHTML = `
            <div class="dashboard-header">
                <div>
                    <h2>Employer Talent Intelligence & Sourcing Hub</h2>
                    <p class="text-muted">Analyze regional talent pools, predict hiring difficulty, and locate high-supply talent hubs.</p>
                </div>
                <button class="btn btn-secondary" onclick="app.auth.logout()">Logout</button>
            </div>

            <!-- Role Sourcing Filter Card -->
            <div class="card-glass" style="margin-bottom: 25px;">
                <h3 style="margin-bottom: 12px;">Target Occupation Intelligence</h3>
                <div style="display: flex; gap: 15px; align-items: center; flex-wrap: wrap;">
                    <div style="flex: 1; min-width: 250px;">
                        <label style="display: block; font-size: 0.85rem; margin-bottom: 5px; color: var(--text-secondary);">Select Target Role</label>
                        <select id="employer-role-select" class="file-input" style="padding: 10px; background: rgba(15,23,42,0.8); color: white; border: 1px solid var(--border-color); width: 100%; border-radius: 8px;">
                            <option value="">-- All Occupations --</option>
                            ${optionsHtml}
                        </select>
                    </div>
                    <div style="margin-top: 20px;">
                        <button class="btn btn-primary" onclick="app.employer.analyzeRole()">Analyze Regional Feasibility</button>
                    </div>
                </div>
            </div>

            <!-- Dynamic Search Results -->
            <div id="employer-analysis-results" style="margin-bottom: 25px;"></div>

            <!-- Overview Grid: Talent Hubs & High Competition -->
            <div class="grid-2">
                <!-- Top Talent Supply Hubs -->
                <div class="card-glass">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                        <h3>Top Regional Talent Pools</h3>
                        <span class="badge badge--balanced">High Supply</span>
                    </div>
                    <p class="text-muted" style="font-size: 0.9rem; margin-bottom: 15px;">Top states with the largest pools of ready workers:</p>
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
                                        <td><strong>${hub.geography_name}</strong></td>
                                        <td>${hub.entity_name}</td>
                                        <td><span class="tag" style="background: rgba(16,185,129,0.15); color: #059669;">${Number(hub.supply_pool).toLocaleString()}</span></td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- High Competition Watchlist -->
                <div class="card-glass">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                        <h3>Hiring Scarcity & Competition Watchlist</h3>
                        <span class="badge badge--critical">Critical Shortage</span>
                    </div>
                    <p class="text-muted" style="font-size: 0.9rem; margin-bottom: 15px;">Roles with intense competition & candidate scarcity:</p>
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
                                        <td><strong>${role.entity_name}</strong></td>
                                        <td>${role.geography_name}</td>
                                        <td>${role.demand_score.toFixed(1)}</td>
                                        <td><span class="badge badge--critical">High Scarcity</span></td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
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
            <div class="card-glass" style="padding: 20px; text-align: center;">
                <span class="spinner"></span> Analyzing hiring feasibility for <strong>${role || "all roles"}</strong>...
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
            resultsContainer.innerHTML = `<div class="card-glass text-muted">Analysis could not be completed.</div>`;
        }
    }

    renderAnalysisResults(data, container) {
        if (!data.regions || data.regions.length === 0) {
            container.innerHTML = `
                <div class="card-glass">
                    <p class="text-muted">No specific regional shortage data found for this selection.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <div class="card-glass">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <h3>Sourcing Feasibility & Strategic Recommendations: <span style="color: var(--accent-blue);">${data.target_role}</span></h3>
                </div>
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
        `;
    }
}

window.EmployerDashboardModule = EmployerDashboardModule;
