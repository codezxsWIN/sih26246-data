/**
 * state.js - Lightweight global application state with pub/sub
 */
const appState = {
  filters: { entity_type: null, geography_name: null, risk_category: null, priority_level: null, target_state: null, horizon_months: null, limit: 50 },
  health: null,
  loading: {},
  errors: {},
  cache: {}
};

const _subscribers = {};

function getState(key) {
  return key ? appState[key] : appState;
}

function setState(key, value) {
  appState[key] = value;
  notify(key);
}

function setFilter(key, value) {
  appState.filters[key] = value;
  notify("filters");
}

function subscribe(key, fn) {
  if (!_subscribers[key]) _subscribers[key] = [];
  _subscribers[key].push(fn);
}

function notify(key) {
  (_subscribers[key] || []).forEach(fn => fn(appState[key]));
}

function setLoading(page, val) {
  appState.loading[page] = val;
}

function setError(page, err) {
  appState.errors[page] = err;
}

window.AppState = { getState, setState, setFilter, subscribe, notify, setLoading, setError, appState };
