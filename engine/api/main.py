from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from engine.config import settings
from engine.db import init_db
from engine.ingest import BaseDataLoader, ExternalDataLoader
from engine.analytics import DemandEngine, SupplyEngine, GapEngine
from engine.ml import DemandForecaster
from engine.policy import PolicyRulesEngine
from engine.api.routes import demand, supply, gap, forecast, policy, copilot, auth, seeker

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Local-first AI-Powered Labour Market Intelligence & Skill Demand-Supply Forecasting Engine API"
)

# Enable CORS for local dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route routers
app.include_router(demand.router)
app.include_router(supply.router)
app.include_router(gap.router)
app.include_router(forecast.router)
app.include_router(policy.router)
app.include_router(copilot.router)
app.include_router(auth.router)
app.include_router(seeker.router)

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "documentation": "/docs"
    }

@app.get("/health")
def health():
    return {"status": "healthy", "database": "connected"}

@app.post("/api/engine/run_pipeline")
def run_full_pipeline():
    conn = init_db()
    
    # 1. Ingestion
    b_res = BaseDataLoader(conn).run_all()
    e_res = ExternalDataLoader(conn).run_all()
    
    # 2. Analytics Core
    d_count = len(DemandEngine(conn).run_scoring_pipeline())
    s_count = len(SupplyEngine(conn).run_supply_pipeline())
    g_count = len(GapEngine(conn).run_gap_pipeline())
    
    # 3. Forecasting ML
    f_count = len(DemandForecaster(conn).run_all_forecasts())
    
    # 4. Policy Engine
    p_count = len(PolicyRulesEngine(conn).run_policy_engine())
    
    return {
        "status": "success",
        "pipeline_summary": {
            "base_ingestion": b_res,
            "external_ingestion": e_res,
            "demand_scores_generated": d_count,
            "supply_estimates_generated": s_count,
            "gap_records_generated": g_count,
            "forecasts_generated": f_count,
            "policy_recommendations_generated": p_count
        }
    }
