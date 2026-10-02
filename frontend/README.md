# Labour Market Intelligence Engine - Frontend

Plain HTML/CSS/JavaScript dashboard for the AI-Powered Labour Market Intelligence Engine.

## Architecture

- **No frameworks**: Pure HTML, CSS, vanilla JavaScript
- **No build step**: Served as static files via Python
- **No npm/node**: Zero Node.js dependencies

## Running

From the project root:

```bash
./start.sh
```

Or manually:

```bash
# Backend
python3 -m uvicorn engine.api.main:app --host 127.0.0.1 --port 8000

# Frontend
python3 -m http.server 5173 --directory frontend
```

Open: http://localhost:5173

## Pages

| Route | Description |
|---|---|
| #/dashboard | National overview with summary stats |
| #/demand | Demand analysis with entity type filter |
| #/supply | Supply estimation from PLFS/AISHE/PMKVY |
| #/gap | Gap and shortage analysis with risk filter |
| #/forecast | ML forecast explorer with horizon filter |
| #/shortage | Shortage risk with SHAP driver analysis |
| #/policy | Policy recommendations with priority filter |
| #/copilot | AI Policy Copilot chat interface |

## File Structure

- `index.html` - Application shell
- `css/` - Design tokens, layout, components
- `js/api.js` - Centralized API client
- `js/state.js` - Pub/sub state management
- `js/router.js` - Hash-based routing
- `js/charts.js` - SVG chart utilities
- `js/*.js` - Page modules (one per route)
