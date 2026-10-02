from typing import Optional, List
from fastapi import APIRouter, Query
from engine.db import get_db_connection, DemandRepository

router = APIRouter(prefix="/api/demand", tags=["Demand Scores"])

@router.get("/scores")
def get_demand_scores(
    entity_type: Optional[str] = Query(None, description="occupation, skill, or sector"),
    geography_name: Optional[str] = Query(None, description="All India, Maharashtra, Karnataka, etc."),
    limit: int = Query(50, ge=1, le=500)
):
    conn = get_db_connection()
    repo = DemandRepository(conn)
    scores = repo.get_demand_scores(entity_type=entity_type, geography_name=geography_name, limit=limit)
    return {"status": "success", "count": len(scores), "data": scores}
