from typing import Optional
from fastapi import APIRouter, Query
from engine.db import get_db_connection, SupplyRepository

router = APIRouter(prefix="/api/supply", tags=["Supply Estimates"])

@router.get("/estimates")
def get_supply_estimates(
    entity_type: Optional[str] = Query(None),
    geography_name: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500)
):
    conn = get_db_connection()
    repo = SupplyRepository(conn)
    estimates = repo.get_supply_estimates(entity_type=entity_type, geography_name=geography_name, limit=limit)
    return {"status": "success", "count": len(estimates), "data": estimates}
