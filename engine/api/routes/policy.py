from typing import Optional
from fastapi import APIRouter, Query
from engine.db import get_db_connection, PolicyRepository

router = APIRouter(prefix="/api/policy", tags=["Policy Interventions"])

@router.get("/recommendations")
def get_policy_recommendations(
    priority_level: Optional[str] = Query(None, description="HIGH, MEDIUM, LOW"),
    target_state: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500)
):
    conn = get_db_connection()
    repo = PolicyRepository(conn)
    interventions = repo.get_interventions(priority_level=priority_level, target_state=target_state, limit=limit)
    return {"status": "success", "count": len(interventions), "data": interventions}
