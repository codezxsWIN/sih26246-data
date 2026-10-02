from typing import Optional, List
from fastapi import APIRouter, Query, Body
from pydantic import BaseModel
from engine.db import get_db_connection

router = APIRouter(prefix="/api/employer", tags=["Employer Talent Sourcing Intelligence"])

class TalentSearchRequest(BaseModel):
    occupation: Optional[str] = None
    skills: Optional[List[str]] = None
    target_geography: Optional[str] = "All India"

@router.get("/overview")
def get_employer_market_overview():
    """Returns high-level talent market intelligence for employers."""
    conn = get_db_connection()
    
    # 1. Talent Hubs (states with largest supply pool)
    supply_rows = conn.execute("""
        SELECT geography_name, entity_name, MAX(estimated_supply) as supply_pool
        FROM supply_estimates
        WHERE geography_name != 'All India'
        GROUP BY geography_name, entity_name
        ORDER BY supply_pool DESC
        LIMIT 12
    """).fetchall()
    
    # 2. Competitive High-Pressure Roles (Critical Shortages - difficult to hire)
    shortage_rows = conn.execute("""
        SELECT entity_name, geography_name, demand_score, supply_estimate, gap_score, shortage_risk_category
        FROM demand_supply_gaps
        WHERE shortage_risk_category = 'Critical Shortage'
        ORDER BY gap_score DESC
        LIMIT 10
    """).fetchall()
    
    # 3. Available Occupations for filtering
    occupations = [row[0] for row in conn.execute("""
        SELECT DISTINCT entity_name FROM demand_supply_gaps WHERE entity_type = 'occupation'
    """).fetchall()]

    return {
        "status": "success",
        "talent_hubs": [dict(r) for r in supply_rows],
        "high_competition_roles": [dict(r) for r in shortage_rows],
        "available_occupations": occupations
    }

@router.post("/talent-analysis")
def analyze_talent_sourcing(req: TalentSearchRequest = Body(...)):
    """Analyzes talent availability, regional competition, and hiring feasibility for a specific role."""
    conn = get_db_connection()
    
    query = """
        SELECT geography_name, entity_name, supply_estimate, demand_score, gap_score, gap_ratio, shortage_risk_category
        FROM demand_supply_gaps
        WHERE 1=1
    """
    params = []
    
    if req.occupation:
        query += " AND entity_name LIKE ?"
        params.append(f"%{req.occupation}%")
        
    query += " ORDER BY supply_estimate DESC LIMIT 20"
    
    results = conn.execute(query, params).fetchall()
    
    regional_breakdown = []
    for r in results:
        d = dict(r)
        cat = d.get('shortage_risk_category')
        if cat == 'Critical Shortage':
            difficulty = "High Competition"
            badge = "danger"
            recommendation = "High poaching risk. Offer competitive compensation & flexible/remote arrangements."
        elif cat == 'Oversupply':
            difficulty = "Talent Surplus"
            badge = "success"
            recommendation = "Favorable employer market. Faster hiring cycle & lower salary inflation."
        else:
            difficulty = "Balanced"
            badge = "info"
            recommendation = "Steady candidate pipeline. Standard hiring velocity."
            
        d['hiring_difficulty'] = difficulty
        d['difficulty_badge'] = badge
        d['strategic_recommendation'] = recommendation
        regional_breakdown.append(d)
        
    return {
        "status": "success",
        "target_role": req.occupation or "All Roles",
        "regions": regional_breakdown
    }
