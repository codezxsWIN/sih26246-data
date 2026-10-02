# Frontend Rebuild Plan: Plain HTML/CSS/JS

## 1. Current Frontend Failure Diagnosis

**Root Cause:** The React/Vite frontend renders a blank page in the browser despite returning HTTP 200.

**Evidence:**
- `frontend/index.html` contains only `&lt;div id="root"&gt;&lt;/div&gt;` and a JSX script tag.
- React StrictMode caused an infinite re-render loop (server logs show 50+ duplicate API requests).
- React components reference properties that DO NOT EXIST in the actual API schema:
  - `Dashboard.jsx` accesses `item.total_postings` — actual field is `demand_score`
  - `Supply.jsx` accesses `item.total_supply_estimate` — actual field is `estimated_supply`
  - `Supply.jsx` accesses `item.confidence_score` — actual field is `confidence_interval`
  - `Forecast.jsx` accesses `item.forecasted_value` — actual field is `predicted_demand_score`
  - `Forecast.jsx` accesses `item.model_used` — actual field is `model_type`
- These undefined property accesses crash React rendering, producing a white screen.

## 2. Technology Being Removed

| Component | Package | Reason |
|---|---|---|
| React | react, react-dom | Not required |
| Vite | vite, @vitejs/plugin-react | Build system unnecessary |
| React Router | react-router-dom | Hash routing simpler |
| Recharts | recharts | SVG charts lighter |
| Framer Motion | framer-motion | CSS transitions suffice |
| Lucide React | lucide-react | Plain SVG icons |
| node_modules | ~315 packages | Eliminated |

## 3. Why Plain HTML/CSS/JS

- Zero build step
- 8 GB RAM friendly (Python server ~5 MB vs Vite ~150 MB)
- Government reliability (no npm audit vulnerabilities)
- Instant startup
- View Source shows exactly what runs
- No Node.js dependency

## 4. Backend API Map (Verified)

| Method | Path | Parameters |
|---|---|---|
| GET | /health | none |
| GET | /api/demand/scores | entity_type, geography_name, limit |
| GET | /api/supply/estimates | entity_type, geography_name, limit |
| GET | /api/gap/gaps | risk_category, geography_name, limit |
| GET | /api/forecast/predictions | entity_name, horizon_months, limit |
| GET | /api/policy/recommendations | priority_level, target_state, limit |
| POST | /api/copilot/query | body: {query} |
| POST | /api/engine/run_pipeline | none |

## 5. New File Structure

```
frontend/
  index.html
  css/
    style.css
    layout.css
    components.css
  js/
    app.js
    api.js
    state.js
    router.js
    utils.js
    health.js
    dashboard.js
    demand.js
    supply.js
    gap.js
    forecast.js
    shortage.js
    policy.js
    copilot.js
    charts.js
  README.md
```

## 6. Navigation

Hash-based routing: #/dashboard, #/demand, #/supply, #/gap, #/forecast, #/shortage, #/policy, #/copilot

## 7. State Management

Simple pub/sub: appState object, setState(), subscribe(), notify().

## 8. Chart Strategy

Pure SVG via document.createElementNS. No external libraries.

## 9. Serving

- Frontend: python3 -m http.server 5173 --directory frontend
- Backend: python3 -m uvicorn engine.api.main:app --host 127.0.0.1 --port 8000

## 10. Acceptance Criteria

- start.sh boots both servers
- http://localhost:8000/health returns healthy
- http://localhost:5173 renders visible dashboard
- Sidebar navigation works (all 8 pages)
- API data appears in tables/charts
- No JavaScript console errors
- No CORS errors
- Copilot chat works or shows graceful offline
- Backend tests still pass (8/8)
- No npm/node required for frontend
