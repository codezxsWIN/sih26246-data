from typing import Optional
from fastapi import APIRouter, Query
from engine.db import get_db_connection, GapRepository

router = APIRouter(prefix="/api/gap", tags=["Demand-Supply Gap Analysis"])

@router.get("/gaps")
def get_gaps(
    risk_category: Optional[str] = Query(None, description="Critical Shortage, Moderate Shortage, Balanced, Oversupply"),
    geography_name: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500)
):
    conn = get_db_connection()
    repo = GapRepository(conn)
    gaps = repo.get_gaps(risk_category=risk_category, geography_name=geography_name, limit=limit)
    return {"status": "success", "count": len(gaps), "data": gaps}
