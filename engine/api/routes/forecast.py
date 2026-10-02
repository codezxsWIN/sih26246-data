from typing import Optional
from fastapi import APIRouter, Query
from engine.db import get_db_connection, ForecastRepository

router = APIRouter(prefix="/api/forecast", tags=["Demand Forecasting"])

@router.get("/predictions")
def get_forecasts(
    entity_name: Optional[str] = Query(None),
    horizon_months: Optional[int] = Query(None, description="3, 6, or 12"),
    limit: int = Query(50, ge=1, le=500)
):
    conn = get_db_connection()
    repo = ForecastRepository(conn)
    forecasts = repo.get_forecasts(entity_name=entity_name, horizon_months=horizon_months, limit=limit)
    return {"status": "success", "count": len(forecasts), "data": forecasts}
